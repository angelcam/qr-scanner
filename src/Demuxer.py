import avpy
import ctypes
import threading
import time

import config
import PacketWrapper
from Logger import log


class Demuxer(object):
    def __init__(self, address):
        self._inFormatCtx = None
        self._ctxLock = threading.Lock()
        self._run = threading.Event()
        self._address = address
        self._timeoutCB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)(self._timeout_check)
        self._timeout_time = None
        self._videoStreamId = None

        self.timeout_signal = False

    def start(self):
        log.debug("Demuxer.start: Connecting to source.")

        self._run.set()

        self._ctxLock.acquire()
        self._inFormatCtx = avpy.av.lib.avformat_alloc_context()
        if(not self._inFormatCtx):
            log.error("Demuxer.start: Cannot alloc input format context.")
            self._ctxLock.release()
            self._run.clear()
            return False

        #set timeout check callback
        interruptStruct = avpy.av.lib.AVIOInterruptCB()
        interruptStruct.callback = self._timeoutCB
        interruptStruct.opaque = None
        self._inFormatCtx.contents.interrupt_callback = interruptStruct

        self._set_timeout(config.DEMUXER_TIMEOUT_OPEN_INPUT)
        ret = avpy.av.lib.avformat_open_input(ctypes.byref(self._inFormatCtx), self._address, None, None)
        if(ret < 0):
            if(self.timeout_signal):
                 log.error("Demuxer.start: Could not open input. Timeout. " + str(config.DEMUXER_TIMEOUT_OPEN_INPUT) + "s.")
            else:
                log.error("Demuxer.start: Could not open input. Libav error: " + str(avpy.avMedia.avError(ret)))
            self._ctxLock.release()
            self._run.clear()
            return False

        ret = avpy.av.lib.avformat_find_stream_info(self._inFormatCtx, None)
        if(ret < 0):
            log.error("Demuxer.start: Failed to obtain input stream information of address. Libav error: " + str(avpy.avMedia.avError(ret)))
            self._ctxLock.release()
            self._run.clear()
            return False
        self._ctxLock.release()

        log.info("Demuxer.start: Demuxer started.")

        return True

    def stop(self):
        if(not self._run.is_set()):
            return

        log.debug("Demuxer.stop: Stopping demuxer.")

        #stop actually running read
        self._run.clear()

        #release context
        self._ctxLock.acquire()
        if(self._inFormatCtx):
            avpy.av.lib.avformat_close_input(ctypes.byref(self._inFormatCtx))
            self._inFormatCtx = None
        self._ctxLock.release()
        log.info("Demuxer.stop: Demuxer stopped.")

    def get_context(self):
        return (self._ctxLock, self._inFormatCtx)

    def get_video_stream_id(self):
        if(not self._videoStreamId):
            self._ctxLock.acquire()
            for i in range(self._inFormatCtx.contents.nb_streams):
                if(self._inFormatCtx.contents.streams[i].contents.codec.contents.codec_type == avpy.av.lib.AVMEDIA_TYPE_VIDEO):
                    self._videoStreamId = i
                    break
            self._ctxLock.release()
        return self._videoStreamId

    #Is it necessary alloc new packets all the time?
    def read(self):

        if(not self._run.is_set()):
            return None

        packet = avpy.av.lib.AVPacket()
        packetRef = ctypes.byref(packet)

        #set timeout
        self._set_timeout(config.DEMUXER_TIMEOUT_READ_FRAME)
        self._ctxLock.acquire()
        ret = avpy.av.lib.av_read_frame(self._inFormatCtx, packetRef)

        if(ret != 0):
            if(self.timeout_signal):
                log.error("Demuxer.read: Cannot read packet. Timeout. " + str(config.DEMUXER_TIMEOUT_READ_FRAME) + "s.")
            elif(self._run.is_set()):
                log.error("Demuxer.read: Cannot read packet. Libav error: " + str(avpy.avMedia.avError(ret)))
            avpy.av.lib.av_free_packet(ctypes.byref(packet))
            self._ctxLock.release()
            return None

        wrap = PacketWrapper.PacketWrapper(packet)
        wrap.calculate_dts_time(self._inFormatCtx)
        self._ctxLock.release()

        #release original packet
        avpy.av.lib.av_free_packet(ctypes.byref(packet))

        return wrap

    def _set_timeout(self, timeS):
        self._timeout_time = time.time() + timeS
        self.timeout_signal = False

    #timeout check return 0 to continue, return 1 to stop blocking function
    def _timeout_check(self, context):

        if(not self._run.is_set()):
            return 1

        if(time.time() > self._timeout_time):
            self.timeout_signal = True
            return 1
        else:
            return 0