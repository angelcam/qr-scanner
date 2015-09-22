import avpy
import ctypes

from Logger import log

AV_PKT_FLAG_KEY = 0x0001

class PacketWrapper(object):
    def __init__(self, pyavPacket):
        self.pkt = self._copy(pyavPacket)
        self.preprocessed = False

    def __del__(self):
        avpy.av.lib.av_free_packet(ctypes.byref(self.pkt))

    def is_keyframe(self):
        return (self.pkt.flags & AV_PKT_FLAG_KEY != 0)

    #https://libav.org/documentation/doxygen/release/9/structAVPacket.html
    def _copy(self, oldPkt):

        #create new packet
        newPkt = avpy.av.lib.AVPacket()
        newPktRef = ctypes.byref(newPkt)
        ret = avpy.av.lib.av_new_packet(newPktRef, oldPkt.size)
        if(ret != 0):
            log.log(log.ERROR, "PacketWrapper._copy: Cannot create new packet.")

        #copy fields
        newPkt.pts = oldPkt.pts
        newPkt.dts = oldPkt.dts
        newPkt.stream_index = oldPkt.stream_index
        newPkt.flags = oldPkt.flags
        newPkt.duration = oldPkt.duration
        newPkt.pos = oldPkt.pos
        newPkt.convergence_duration = oldPkt.convergence_duration

        #copy data
        ctypes.memmove(newPkt.data, oldPkt.data, oldPkt.size)

        return newPkt
