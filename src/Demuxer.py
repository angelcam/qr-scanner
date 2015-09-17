import avpy
import ctypes
import threading

class Demuxer(object):
    def __init__(self, address):
        self._inFormatCtx = None
        self._ctxLock = threading.Lock()
        self._address = address

    def start(self):
        print("Demuxer.start: Connecting to " + self._address)

        self._ctxLock.acquire()
        self._inFormatCtx = ctypes.POINTER(avpy.av.lib.AVFormatContext)()
        ret = avpy.av.lib.avformat_open_input(self._inFormatCtx, self._address, None, None)
        if(ret < 0):
            print("Demuxer.start: Could not open input " + self._address)
            self._ctxLock.release()
            return False
        ret = avpy.av.lib.avformat_find_stream_info(self._inFormatCtx, None)
        if(ret < 0):
            print("Demuxer.start: Failed to retrieve input stream information of address " + self._address)
            self._ctxLock.release()
            return False
        self._ctxLock.release()

        print("Demuxer.start: Connected to " + self._address)
        return True

    def stop(self):
        self._ctxLock.acquire()
        if(self._inFormatCtx != None):
            if(self._inFormatCtx): #TODO continue NULL pointer access
                avpy.av.lib.avformat_close_input(self._inFormatCtx)
                self._inFormatCtx = None
        print("Demuxer.stop: Stopped demuxer for address " + self._address)
        self._ctxLock.release()

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

    def read(self):
        packet = avpy.av.lib.AVPacket()
        packetRef = ctypes.byref(packet)
        self._ctxLock.acquire()
        ret = avpy.av.lib.av_read_frame(self._inFormatCtx, packetRef)
        self._ctxLock.release()
        if(ret != 0):
            print("Cannot read packet.")
            return None

        return packet