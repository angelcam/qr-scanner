import avpy
import ctypes
from Logger import log

class Decoder(object):
    def __init__(self):
        self.codecCtx = None
        self._insertedCounter = 0

    def start(self, inFormatContextWrap, videoSId):
        log.log(log.DEBUG, "Decoder.start: Starting decoder.")
        self._insertedCounter = 0

        contextLock, inFormatCtx = inFormatContextWrap

        contextLock.acquire()
        inStream = inFormatCtx.contents.streams[videoSId]

        self.codecCtx = inStream.contents.codec
        decoder = avpy.av.lib.avcodec_find_decoder(inStream.contents.codec.contents.codec_id)
        if(not decoder):
            log.log(log.ERROR, "Decoder.start: Could not find decoder for codec ID: %d" % inStream.contents.codec.contents.codec_id)
            return False

        #if(codec->capabilities & avpy.av.lib.CODEC_CAP_TRUNCATED): ???
        #    codecContext->flags|= avpy.av.lib.CODEC_FLAG_TRUNCATED

        ret = avpy.av.lib.avcodec_open2(self.codecCtx, decoder, None)
        if(ret != 0):
            log.log(log.ERROR, "Decoder.start: Cannot open decoder.")
            return False

        contextLock.release()
        log.log(log.DEBUG, "Decoder.start: Decoder started.")
        return True

    #codec context is from input - demuxer = do not free
    #frame is allocated in codec buffer = do not free
    def stop(self):
        log.log(log.DEBUG, "Decoder.stop: Stopping decoder.")
        self.codecCtx = None
        log.log(log.DEBUG, "Decoder.stop: Decoder stopped.")

    #frame is allocated in codec buffer = do not free
    def decode(self, packetWrap):

        #first frame must be keyframe
        if(self._insertedCounter == 0 and not packetWrap.is_keyframe()):
            return None

        self._insertedCounter += 1

        packet = packetWrap.pkt
        pktRef = ctypes.byref(packet)
        frame = avpy.av.lib.avcodec_alloc_frame()
        decoded = ctypes.c_int(-1)
        decodedRef = ctypes.byref(decoded)
        ret = avpy.av.lib.avcodec_decode_video2(self.codecCtx, frame, decodedRef, pktRef)
        if(ret <= 0):
            log.log(log.ERROR, "Cannot decode packet. error: " + str(ret))
            avpy.av.lib.avcodec_free_frame(ctypes.byref(frame))
            return None
        if(decoded.value == 0):
            avpy.av.lib.avcodec_free_frame(ctypes.byref(frame))
            return None
        else:
            return frame

