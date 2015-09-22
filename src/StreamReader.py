import avpy
import ctypes
from Logger import log

import Demuxer
import Decoder

class StreamReader(object):
    def __init__(self, address):
        self._demuxer = Demuxer.Demuxer(address)
        self._decoder = Decoder.Decoder()
        self._lastFrame = None
        self._swsCtx = None
        self._swsFrame = None

    def start(self):
        log.log(log.DEBUG, "StreamReader.start: Starting streamReader.")
        if(self._start()):
            log.log(log.INFO, "StreamReader.start: StreamReader started.")
            return True
        else:
            log.log(log.INFO, "StreamReader.start: Starting streamReader failed.")
            return False

    def stop(self):
        log.log(log.DEBUG, "StreamReader.stop: Stopping streamReader.")
        self._demuxer.stop()
        self._decoder.stop()
        log.log(log.DEBUG, "StreamReader.stop: StreamReader stopped ")

    def read_image(self):

        packet = self._demuxer.read()

        if(not packet):
            return False

        if(packet.pkt.stream_index != self._demuxer.get_video_stream_id()):
            return False

        self._lastFrame = self._decoder.decode(packet)

        #first frames will probably not be decoded
        if(self._lastFrame):
            return True
        else:
            return False

    def get_out_frame(self):

        if(not self._lastFrame):
            return None

        outSliceHeight = avpy.av.lib.sws_scale(self._swsCtx,
                self._lastFrame.contents.data,
                self._lastFrame.contents.linesize,
                0,
                self._decoder.codecCtx.contents.height,
                self._swsFrame.contents.data,
                self._swsFrame.contents.linesize)

        return self._swsFrame

    def _start(self):

        if(not self._demuxer.start()):
            return False

        if(self._decoder.start(self._demuxer.get_context(), self._demuxer.get_video_stream_id())):

            #create sws context
            width = self._decoder.codecCtx.contents.width
            height = self._decoder.codecCtx.contents.height
            outPixFmt = avpy.av.lib.PIX_FMT_GRAY8
            nullSwsCtx = ctypes.cast(None, ctypes.POINTER(avpy.av.lib.SwsContext))
            self._swsCtx = avpy.av.lib.sws_getCachedContext(
                    nullSwsCtx,
                    width,
                    height,
                    self._decoder.codecCtx.contents.pix_fmt,
                    width,
                    height,
                    outPixFmt,
                    avpy.av.lib.SWS_BILINEAR,
                    None,
                    None,
                    None)

            if(not self._swsCtx):
                log.log(log.DEBUG, "Decoder.start: Cannot create sws context.")
                return False

            self._swsFrame = avpy.av.lib.avcodec_alloc_frame()
            if(not self._swsFrame):
                log.log(log.DEBUG, "Decoder.start: Cannot create sws frame.")
                return False

            avpy.av.lib.avpicture_alloc(
                    ctypes.cast(self._swsFrame, ctypes.POINTER(avpy.av.lib.AVPicture)),
                    outPixFmt,
                    width,
                    height)

            #set output parameters
            self._swsFrame.contents.width = width
            self._swsFrame.contents.height = height
            self._swsFrame.contents.format = outPixFmt

            return True
