# Main class

import threading
import sys
import time

import avpy
import config
import StreamReader
import CodeReader

SCANNER_STATE_CONNECT = 0
SCANNER_STATE_READ = 1

class Scanner(object):
    def __init__(self, streamAddress):

        avpy.av.lib.av_register_all()
        avpy.av.lib.avcodec_register_all()

        self._streamAddress = streamAddress
        self._streamReader = StreamReader.StreamReader(self._streamAddress)
        self._codeReader = CodeReader.CodeReader()
        self._run = threading.Event()

    def start(self):
        print("Scanner.start: Starting scanner.")
        self._run.set()
        self._main_loop()

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
                image = self._streamReader.read_image()

                if(image != None):
                    frameI += 1
                    if(frameI % config.SKIP_FRAMES):

                        ret, data = self._codeReader.read(image)
                        if(ret == True):
                            print(data)
                        else:
                            print("Scanner._main_loop: Frame " + str(frameI) + " hasnt readable QR code.")

            else:
                sys.stderr.write("Scanner._main_loop: Unkdnown state.\n")
                return

        if(self._run.is_set()):
            sys.stderr.write("Scanner._main_loop: Timeout.\n")
        else:
            sys.stderr.write("Scanner._main_loop: Interrupted.\n")
