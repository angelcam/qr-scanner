import threading
import time

import Demuxer

class StreamReader(object):
    def __init__(self, address):
        self._demuxer = Demuxer.Demuxer(address)
        self._runRead = threading.Event()

    def start(self):
        return self._demuxer.start()

    def stop(self):
        self._runRead.clear()
        self._demuxer.stop()

    def read_video(self):
        self._runRead.set()

        while(self._runRead.is_set()):
            packet = self._demuxer.read()

            if(not packet):
                self._demuxer.stop()
                time.sleep(1)
                self._demuxer.start()
                continue

            if(packet.stream_index == self._demuxer.get_video_stream_id()):
                return packet


