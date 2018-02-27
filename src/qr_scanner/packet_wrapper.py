import avpy
import ctypes


AV_PKT_FLAG_KEY = 0x0001


class PacketWrapper(object):
    def __init__(self, pyavPacket, logger):
        self.pkt = self._copy(pyavPacket)
        self.preprocessed = False
        self.dtsTime = None
        self._logger = logger

    def __del__(self):
        avpy.av.lib.av_free_packet(ctypes.byref(self.pkt))

    def is_keyframe(self):
        return (self.pkt.flags & AV_PKT_FLAG_KEY != 0)

    def calculate_dts_time(self, formatContext):
        if(formatContext
            and self.pkt.stream_index < formatContext.contents.nb_streams
            and self.pkt.dts != avpy.av.lib.AV_NOPTS_VALUE):
                timebase = formatContext.contents.streams[self.pkt.stream_index].contents.time_base
                self.dtsTime = self.pkt.dts * timebase.num / float(timebase.den)

    #https://libav.org/documentation/doxygen/release/9/structAVPacket.html
    def _copy(self, oldPkt):

        #create new packet
        newPkt = avpy.av.lib.AVPacket()
        newPktRef = ctypes.byref(newPkt)
        ret = avpy.av.lib.av_new_packet(newPktRef, oldPkt.size)
        if(ret != 0):
            self._logger.warning("PacketWrapper._copy: Cannot create new packet.")

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
