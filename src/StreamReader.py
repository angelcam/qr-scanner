import threading
import time
import avpy
import ctypes
from PIL import Image
import cStringIO

import Demuxer
import Decoder

class StreamReader(object):
    def __init__(self, address):
        self._demuxer = Demuxer.Demuxer(address)
        self._decoder = Decoder.Decoder()
        self._swsCtx = None
        self._swsFrame = None
        self._runRead = threading.Event()

    def start(self):
        print("StreamReader.start: Starting streamReader.")
        self._runRead.set()
        if(self._start()):
            print("StreamReader.start: StreamReader started ")
            return True

        return False

    def stop(self):
        print("StreamReader.stop: Stopping streamReader.")
        self._runRead.clear()
        self._demuxer.stop()
        self._decoder.stop()
        print("StreamReader.stop: StreamReader stopped ")

    def read_image(self):

        while(self._runRead.is_set()):
            packet = self._demuxer.read()

            if(not packet):
                self._demuxer.stop()
                self._decoder.stop()
                time.sleep(1)
                self._start()
                continue

            if(packet.pkt.stream_index != self._demuxer.get_video_stream_id()):
                continue

            frame = self._decoder.decode(packet)

            #first frames will probably not be decoded
            if(not frame):
                continue

            #convert frame to PIL image
            image = self._avFrame_2_PILImage(frame)

            if(image):
                return image

        return None

    def _start(self):
        while(self._runRead.is_set()):
            ret = self._demuxer.start()
            if(ret):
                break
            else:
                time.sleep(1)

        if(not self._runRead.is_set() or not ret):
            return False

        if(self._decoder.start(self._demuxer.get_context(), self._demuxer.get_video_stream_id())):

            #create sws context
            width = self._decoder.codecCtx.contents.width
            height = self._decoder.codecCtx.contents.height
            outPixFmt = avpy.av.lib.PIX_FMT_RGB24
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
                print("Decoder.start: Cannot create sws context.")
                return False

            self._swsFrame = avpy.av.lib.avcodec_alloc_frame()
            if(not self._swsFrame):
                print("Decoder.start: Cannot create sws frame.")
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

    def _avFrame_2_PILImage(self, frame):

        outSliceHeight = avpy.av.lib.sws_scale(self._swsCtx,
                frame.contents.data,
                frame.contents.linesize,
                0,
                self._decoder.codecCtx.contents.height,
                self._swsFrame.contents.data,
                self._swsFrame.contents.linesize)

        print("out imeage: " + str(self._swsFrame.contents.width) + " " + str(self._swsFrame.contents.height))
        print(outSliceHeight)


        #return frame
        #image = Image.new("RGB", (512,512), "white")
        #image = Image.frombuffer("RGB", (self._swsFrame.contents.width, self._swsFrame.contents.height),
        #                         self._swsFrame.contents.data[0], "raw", "RGB", 0, 1)

        #just crazy solution for now
        charList = []
        for i in range(3 * self._swsFrame.contents.width * self._swsFrame.contents.height):
            char = chr(self._swsFrame.contents.data[0][i])
            charList.append(char)
        stringVal = "".join(charList)
        print("dataString len: " + str(len(stringVal)))
        image = Image.frombytes("RGB", (self._swsFrame.contents.width,self._swsFrame.contents.height), stringVal)


#        values = [100, 200, 250, 1, 2, 3, 100, 200, 250, 56, 45, 15]
#        charList = [chr(c) for c in values]
#        stringVal = "".join(charList)
#        print(len(stringVal))
#        image = Image.fromstring("RGB", (1,4), stringVal)


#        image = Image.frombytes("L", (self._swsFrame.contents.width,self._swsFrame.contents.height), self._swsFrame.contents.data[0])


        image.save("image.png")
        return image

