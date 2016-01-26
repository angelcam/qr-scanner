import avpy
import ctypes
import threading
import Queue
import time

from Logger import log
import config
import Demuxer
import Decoder

class StreamReader(object):
    def __init__(self, address):
        self._demuxer = Demuxer.Demuxer(address)
        self._decoder = Decoder.Decoder()
        self._lastPck = None
        self._lastFrame = None
        self._swsCtx = None
        self._swsFrame = None

        #reader - thread
        self._thread = None
        self._run = threading.Event()
        self._packetQueue = Queue.Queue(config.MAX_PACKETS)

    def start(self):
        log.debug("StreamReader.start: Starting streamReader.")
        self._run.set()
        self._thread = threading.Thread(target=self.main_loop)
        self._thread.setDaemon(True)
        self._thread.start()
        log.info("StreamReader.start: StreamReader started.")

    def stop(self):
        log.debug("StreamReader.stop: Stopping streamReader.")
        self._run.clear()
        if(self._thread and self._thread.isAlive()):
            self._thread.join(2.0)
        log.debug("StreamReader.stop: StreamReader stopped ")

    def main_loop(self):

        while(self._run.is_set() and not self._start()):
            self._stop()
            time.sleep(1)

        while(self._run.is_set()):

            packet = self._demuxer.read()

            #something is wrong - try demuxer restart = restart decoder too
            if(not packet):
                log.warn("StreamReader.main_loop: Cannot read packet. Restarting demuxer, decoder.")
                self._stop()
                while(self._run.is_set() and not self._start()):
                    self._stop()
                    time.sleep(1)
                continue

            if(packet.pkt.stream_index != self._demuxer.get_video_stream_id()):
                continue

            try:
                self._packetQueue.put(packet, False)
            except Queue.Full:
                log.debug("StreamReader.main_loop: Reading of input is too fast. Packet buffer is full.")
                continue

        #clean everything used by thread
        self._stop()

    def try_decode(self):

        try:
            self._lastPck = self._packetQueue.get(True, 1.0)
        except Queue.Empty:
            return False

        if(self._lastFrame):
            avpy.av.lib.avcodec_free_frame(ctypes.byref(self._lastFrame))
        self._lastFrame = self._decoder.decode(self._lastPck)

        #first frames will probably not be decoded
        if(self._lastFrame):
            return True
        else:
            return False

    def get_out_frame(self):

        if(not self._lastFrame):
            return None

        #transform last frame to swsFrame (decoder output AVFrame -> desired paraemters AVframe)
        outSliceHeight = avpy.av.lib.sws_scale(self._swsCtx,
                self._lastFrame.contents.data,
                self._lastFrame.contents.linesize,
                0,
                self._lastFrame.contents.height,
                self._swsFrame.contents.data,
                self._swsFrame.contents.linesize)

        return (self._swsFrame, self._lastPck.dtsTime)

    def _stop(self):
        while(not self._packetQueue.empty()):
            self._packetQueue.get()
        self._demuxer.stop()
        self._decoder.stop()

    def _start(self):

        if(not self._demuxer.start()):
            return False

        if(self._decoder.start(self._demuxer.get_context(), self._demuxer.get_video_stream_id())):

            #create sws context
            width = self._decoder.codecCtx.contents.width
            height = self._decoder.codecCtx.contents.height
            outPixFmt = avpy.av.lib.PIX_FMT_GRAY8

            #prepare output resolution
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

            if(not self._swsCtx):
                log.debug("Decoder.start: Cannot create sws context.")
                return False

            self._swsFrame = avpy.av.lib.avcodec_alloc_frame()
            if(not self._swsFrame):
                log.debug("Decoder.start: Cannot create sws frame.")
                return False

            avpy.av.lib.avpicture_alloc(
                    ctypes.cast(self._swsFrame, ctypes.POINTER(avpy.av.lib.AVPicture)),
                    outPixFmt,
                    widthOut,
                    heightOut)

            #set output parameters
            self._swsFrame.contents.width = widthOut
            self._swsFrame.contents.height = heightOut
            self._swsFrame.contents.format = outPixFmt

            return True

    def _output_resolution(self, width, height):
        widthOut = width
        heightOut = height

        if(max(width, height) > config.DECODER_MAX_RESOLUTION):
            widthMul = width / config.DECODER_MAX_RESOLUTION
            heightMul = height / config.DECODER_MAX_RESOLUTION

            if(widthMul > heightMul):
                widthOut = config.DECODER_MAX_RESOLUTION
                heightOut = int(height * config.DECODER_MAX_RESOLUTION / float(width))
            else:
                heightOut = config.DECODER_MAX_RESOLUTION
                widthOut = int(width * config.DECODER_MAX_RESOLUTION / float(height))

        return (widthOut, heightOut)