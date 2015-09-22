# Main class

import threading
import sys
import time

import avpy
import config
import StreamReader
import CodeReader

from PIL import Image
import ctypes

SCANNER_STATE_CONNECT = 0
SCANNER_STATE_READ = 1

class Scanner(object):
    def __init__(self, streamAddress):

        avpy.av.lib.av_register_all()
        avpy.av.lib.avcodec_register_all()

        self._streamAddress = streamAddress
        self._streamReader = StreamReader.StreamReader(self._streamAddress)
        self._codeReader = CodeReader.CodeReader()
        self._foundCodes = dict()
        self._run = threading.Event()

    def start(self):
        print("Scanner.start: Starting scanner.")
        self._run.set()
        return self._main_loop()

    def stop(self):
        print("Scanner: Stopping scanner.")
        self._run.clear()
        self._streamReader.stop()

        print("Scanner.stop: Scanner stopped")

    def is_running(self):
        return self._run.is_set()

    def _main_loop(self):
        print("Scanner._main_loop: Scanner started.")
        self._run.set()
        startTime = time.time()

        state = SCANNER_STATE_CONNECT

        frameI = 0
        while(time.time() - startTime < config.TIMEOUT_S and self._run.is_set()):

            if(state == SCANNER_STATE_CONNECT):
                print("Scanner._main_loop: State SCANNER_STATE_CONNECT.")
                if(self._streamReader.start()):
                    state = SCANNER_STATE_READ
                    frameI = 0
                else:
                    self._streamReader.stop()
                    time.sleep(1)

            elif(state == SCANNER_STATE_READ):
                print("Scanner._main_loop: State SCANNER_STATE_READ.")
                print("Scanner._main_loop: frameI " + str(frameI))

                #read frame from stream
                if(self._streamReader.read_image()):
                    frameI += 1
                    if(frameI % config.SKIP_FRAMES == 0):

                        frame = self._streamReader.get_out_frame()
                        if(not frame):
                            continue

                        codes = self._codeReader.read(frame)
                        for code in codes:
                            #write code only once
                            if(not code in self._foundCodes):
                                sys.stdout.write(str(code) + "\r\n\r\n")
                                self._foundCodes[code] = code
                                #this will be usefull for testing purposes
                                #stringData = ctypes.string_at(frame.contents.data[0], frame.contents.width * frame.contents.height)
                                #image = Image.frombytes("L", (frame.contents.width, frame.contents.height), stringData)
                                #image.save("image.png")
                            #else ignored

            else:
                sys.stderr.write("Scanner._main_loop: Unkdnown state.\n")
                return

        if(self._run.is_set()):
            sys.stderr.write("Scanner._main_loop: Timeout.\n")
            sys.stdout.write("Timeout.\r\n")
        else:
            sys.stderr.write("Scanner._main_loop: Interrupted.\n")
