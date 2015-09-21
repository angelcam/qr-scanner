import avpy
import ctypes

class Decoder(object):
    def __init__(self):
        self.codecCtx = None

    def start(self, inFormatContextWrap, videoSId):
        print("Decoder.start: Starting decoder.")
        contextLock, inFormatCtx = inFormatContextWrap

        contextLock.acquire()
        inStream = inFormatCtx.contents.streams[videoSId]

        self.codecCtx = inStream.contents.codec
        decoder = avpy.av.lib.avcodec_find_decoder(inStream.contents.codec.contents.codec_id)
        if(not decoder):
            print("Decoder.start: Could not find decoder for codec ID: %d" % inStream.contents.codec.contents.codec_id)
            return False

        #if(codec->capabilities & avpy.av.lib.CODEC_CAP_TRUNCATED): ???
        #    codecContext->flags|= avpy.av.lib.CODEC_FLAG_TRUNCATED

        ret = avpy.av.lib.avcodec_open2(self.codecCtx, decoder, None)
        if(ret != 0):
            print("Decoder.start: Cannot open decoder.")
            return False

        contextLock.release()
        print("Decoder.start: Decoder started.")
        return True

    def stop(self):
        print("Decoder.stop: Stopping decoder.")
        #TODO free stuff avpy.av.lib.avcodec_close(stream.contents.codec) ???
        print("Decoder.stop: Decoder stopped.")

    def decode(self, packetWrap):
        packet = packetWrap.pkt
        pktRef = ctypes.byref(packet)
        frame = avpy.av.lib.avcodec_alloc_frame()
        decoded = ctypes.c_int(-1)
        decodedRef = ctypes.byref(decoded)
        ret = avpy.av.lib.avcodec_decode_video2(self.codecCtx, frame, decodedRef, pktRef)
        if(ret <= 0):
            print("Cannot decode packet. error: " + str(ret))
            return None
        if(decoded.value == 0):
            return None
        else:
            return frame

