import avpy
import ctypes
import threading
import queue
import time
import logging

from qr_scanner import config, demuxer, decoder

logger = logging.getLogger(__name__)


class StreamReader(object):
    def __init__(self, address):
        self._demuxer = demuxer.Demuxer(address)
        self._decoder = decoder.Decoder()
        self._lastPck = None
        self._lastFrame = None
        self._swsCtx = None
        self._swsFrame = None

        # reader - thread
        self._thread = None
        self._run = threading.Event()
        self._packetQueue = queue.Queue(config.MAX_PACKETS)

    def start(self):
        logger.debug("StreamReader.start: Starting streamReader.")
        self._run.set()
        self._thread = threading.Thread(target=self.main_loop)
        self._thread.setDaemon(True)
        self._thread.start()
        logger.info("StreamReader.start: StreamReader started.")

    def stop(self):
        if (not self._run.is_set()):
            return

        logger.debug("StreamReader.stop: Stopping streamReader.")
        # stop thread
        self._run.clear()

        # stop demuxer - will abort reading
        self._demuxer.stop()

        # join thread
        if (self._thread and self._thread.isAlive()):
            self._thread.join()

        # release memory
        self._stop()
        logger.debug("StreamReader.stop: StreamReader stopped ")

    def main_loop(self):

        while (self._run.is_set() and not self._start()):
            self._stop()
            time.sleep(1)

        while (self._run.is_set()):

            packet = self._demuxer.read()

            # something is wrong - try demuxer restart = restart decoder too
            if (not packet):

                # should program countinue? Or jump to while and stop?
                if (self._run.is_set()):
                    logger.warning("StreamReader.main_loop: Cannot read packet. Restarting demuxer, decoder.")
                    self._stop()
                    while (self._run.is_set() and not self._start()):
                        self._stop()
                        time.sleep(5)
                continue

            if (packet.pkt.stream_index != self._demuxer.get_video_stream_id()):
                continue

            try:
                self._packetQueue.put(packet, False)
            except queue.Full:
                logger.debug("StreamReader.main_loop: Reading of input is too fast. Packet buffer is full.")
                continue

    def try_decode(self):

        try:
            self._lastPck = self._packetQueue.get(True, 1.0)
        except queue.Empty:
            return False

        if (self._lastFrame):
            avpy.av.lib.avcodec_free_frame(ctypes.byref(self._lastFrame))
        self._lastFrame = self._decoder.decode(self._lastPck)

        # first frames will probably not be decoded
        if (self._lastFrame):
            return True
        else:
            return False

    def get_out_frame(self):

        if not (self._lastFrame and self._swsFrame):
            return None

        # transform last frame to swsFrame (decoder output AVFrame -> desired paraemters AVframe)
        outSliceHeight = avpy.av.lib.sws_scale(self._swsCtx,
                                               self._lastFrame.contents.data,
                                               self._lastFrame.contents.linesize,
                                               0,
                                               self._lastFrame.contents.height,
                                               self._swsFrame.contents.data,
                                               self._swsFrame.contents.linesize)

        return (self._swsFrame, self._lastPck.dtsTime)

    def _stop(self):
        while (not self._packetQueue.empty()):
            self._packetQueue.get()

        self._demuxer.stop()
        self._decoder.stop()

        if (self._swsCtx != None):
            avpy.av.lib.sws_freeContext(self._swsCtx)
            self._swsCtx = None

        if (self._swsFrame != None):
            avpy.av.lib.avcodec_free_frame(self._swsFrame)
            self._swsFrame = None

        if (self._lastFrame != None):
            avpy.av.lib.avcodec_free_frame(self._lastFrame)
            self._lastFrame = None

        self._lastPck = None

    def _start(self):

        if (not self._demuxer.start()):
            logger.debug("Decoder.start: Cannot start demuxer.")
            return False

        if (self._decoder.start(self._demuxer.get_context(), self._demuxer.get_video_stream_id())):

            # create sws context
            width = self._decoder.codecCtx.contents.width
            height = self._decoder.codecCtx.contents.height
            outPixFmt = avpy.av.lib.AV_PIX_FMT_GRAY8

            # prepare output resolution
            widthOut, heightOut = self._output_resolution(width, height)

            nullSwsCtx = ctypes.cast(None, ctypes.POINTER(avpy.av.lib.SwsContext))
            self._swsCtx = avpy.av.lib.sws_getCachedContext(
                nullSwsCtx,
                width,
                height,
                self._decoder.codecCtx.contents.pix_fmt,
                widthOut,
                heightOut,
                outPixFmt,
                avpy.av.lib.SWS_BILINEAR,
                None,
                None,
                None)

            if (not self._swsCtx):
                logger.debug("Decoder.start: Cannot create sws context.")
                return False

            self._swsFrame = avpy.av.lib.avcodec_alloc_frame()
            if (not self._swsFrame):
                logger.debug("Decoder.start: Cannot create sws frame.")
                return False

            avpy.av.lib.avpicture_alloc(
                ctypes.cast(self._swsFrame, ctypes.POINTER(avpy.av.lib.AVPicture)),
                outPixFmt,
                widthOut,
                heightOut)

            # set output parameters
            self._swsFrame.contents.width = widthOut
            self._swsFrame.contents.height = heightOut
            self._swsFrame.contents.format = outPixFmt

            return True

    def _output_resolution(self, width, height):
        widthOut = width
        heightOut = height

        if (max(width, height) > config.DECODER_MAX_RESOLUTION):
            widthMul = width / config.DECODER_MAX_RESOLUTION
            heightMul = height / config.DECODER_MAX_RESOLUTION

            if (widthMul > heightMul):
                widthOut = config.DECODER_MAX_RESOLUTION
                heightOut = int(height * config.DECODER_MAX_RESOLUTION / float(width))
            else:
                heightOut = config.DECODER_MAX_RESOLUTION
                widthOut = int(width * config.DECODER_MAX_RESOLUTION / float(height))

        return (widthOut, heightOut)
