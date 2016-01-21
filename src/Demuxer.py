import avpy
import ctypes
import threading
import time

import config
import PacketWrapper
import logger


class Demuxer(object):
    def __init__(self, address):
        self._log = logger.Logger(stream_url=address, camera_id=None)

        self._inFormatCtx = None
        self._ctxLock = threading.Lock()
        self._address = address
        self._timeoutCB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)(self._timeout_check)
        self._timeout_time = None
        self.timeout_signal = False

    def start(self):
        self._log.debug("Demuxer.start: Connecting to source.")

        self._ctxLock.acquire()
        self._inFormatCtx = avpy.av.lib.avformat_alloc_context()
        if(not self._inFormatCtx):
            self._log.error("Demuxer.start: Cannot alloc input format context.")
            self._ctxLock.release()
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
                 self._log.error("Demuxer.start: Could not open input. Timeout. " + str(config.DEMUXER_TIMEOUT_OPEN_INPUT) + "s.")
            else:
                self._log.error("Demuxer.start: Could not open input. Libav error: " + str(avpy.avMedia.avError(ret)))
            self._ctxLock.release()
            return False

        ret = avpy.av.lib.avformat_find_stream_info(self._inFormatCtx, None)
        if(ret < 0):
            self._log.error("Demuxer.start: Failed to obtain input stream information of address. Libav error: " + str(avpy.avMedia.avError(ret)))
            self._ctxLock.release()
            return False
        self._ctxLock.release()

        self._log.info("Demuxer.start: Demuxer started.")

        return True

    def stop(self):
        self._log.debug("Demuxer.stop: Stopping demuxer.")
        self._ctxLock.acquire()
        if(self._inFormatCtx):
            avpy.av.lib.avformat_close_input(ctypes.byref(self._inFormatCtx))
            self._inFormatCtx = None
        self._ctxLock.release()
        self._log.info("Demuxer.stop: Demuxer stopped.")

    def get_context(self):
        return (self._ctxLock, self._inFormatCtx)

    def get_video_stream_id(self):
        self._ctxLock.acquire()
        for i in range(self._inFormatCtx.contents.nb_streams):
            if(self._inFormatCtx.contents.streams[i].contents.codec.contents.codec_type == avpy.av.lib.AVMEDIA_TYPE_VIDEO):
                self._ctxLock.release()
                return i
        self._ctxLock.release()
        return None

    #Is it necessary alloc new packets all the time?
    def read(self):
        packet = avpy.av.lib.AVPacket()
        packetRef = ctypes.byref(packet)

        #set timeout
        self._set_timeout(config.DEMUXER_TIMEOUT_READ_FRAME)
        self._ctxLock.acquire()
        ret = avpy.av.lib.av_read_frame(self._inFormatCtx, packetRef)
        self._ctxLock.release()

        if(ret != 0):
            if(self.timeout_signal):
                self._log.error("Demuxer.read: Cannot read packet. Timeout. " + str(config.DEMUXER_TIMEOUT_READ_FRAME) + "s.")
            else:
                self._log.error("Demuxer.read: Cannot read packet. Libav error: " + str(avpy.avMedia.avError(ret)))
            avpy.av.lib.av_free_packet(ctypes.byref(packet))
            return None

        wrap = PacketWrapper.PacketWrapper(packet)

        #release original packet
        avpy.av.lib.av_free_packet(ctypes.byref(packet))

        return wrap

    def _set_timeout(self, timeS):
        self._timeout_time = time.time() + timeS
        self.timeout_signal = False

    #timeout check return 0 to continue, return 1 to stop blocking function
    def _timeout_check(self, context):
        if(time.time() > self._timeout_time):
            self.timeout_signal = True
            return 1
        else:
            return 0