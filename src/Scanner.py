# Main class
import sys
import time
import threading

import avpy
import config
import StreamReader
import CodeReader

from Logger import log

SCANNER_STATE_CONNECT = 0
SCANNER_STATE_READ = 1

class Scanner(object):
    def __init__(self, streamAddress):

        avpy.av.lib.av_register_all()
        avpy.av.lib.avcodec_register_all()
        avpy.av.lib.avformat_network_init()

        self._streamAddress = streamAddress
        self._streamReader = StreamReader.StreamReader(self._streamAddress)
        self._codeReader = CodeReader.CodeReader()
        self._foundCodes = dict()
        self._run = threading.Event()

    def start(self):
        log.log(log.DEBUG, "Scanner.start: Starting scanner.")
        self._run.set()
        return self._main_loop()

    def stop(self):
        log.log(log.DEBUG, "Scanner.stop: Stopping scanner.")
        self._run.clear()

    def is_running(self):
        return self._run.is_set()

    def _main_loop(self):
        log.log(log.DEBUG, "Scanner._main_loop: Scanner started.")
        self._run.set()
        startTime = time.time()

        state = SCANNER_STATE_CONNECT

        frameI = 0
        while(time.time() - startTime < config.TIMEOUT_S and self._run.is_set()):

            if(state == SCANNER_STATE_CONNECT):
                log.log(log.DEBUG, "Scanner._main_loop: State SCANNER_STATE_CONNECT.")
                if(self._streamReader.start()):
                    state = SCANNER_STATE_READ
                    log.log(log.INFO, "Scanner._main_loop: Connected to stream.")
                else:
                    self._streamReader.stop()
                    time.sleep(1)

            elif(state == SCANNER_STATE_READ):
                log.log(log.DEBUG, "Scanner._main_loop: State SCANNER_STATE_READ. frameI " + str(frameI))

                #read frame from stream
                if(self._streamReader.try_decode()):
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
                                sys.stdout.flush()
                                self._foundCodes[code] = code
                                #this will be usefull for testing purposes
                                #stringData = ctypes.string_at(frame.contents.data[0], frame.contents.width * frame.contents.height)
                                #image = Image.frombytes("L", (frame.contents.width, frame.contents.height), stringData)
                                #image.save("image.png")
                            #else ignored
            else:
                log.log(log.ERROR, "Scanner._main_loop: Unkdnown state.")
                self._streamReader.stop()
                time.sleep(1)
                state = SCANNER_STATE_CONNECT

        #clean after yourself
        self._streamReader.stop()

        #End prints
        #loop ended by timeout
        retVal = False
        if(self._run.is_set()):

            #good state
            if(len(self._foundCodes) > 0):
                sys.stdout.write("Timeout.\r\n")
                sys.stdout.flush()
                log.log(log.INFO, "Timeout.")
                return True

            #bad states
            if(frameI == 0):
                if(state == SCANNER_STATE_CONNECT):
                    errMessage = "Timeout. Could not connect to stream (demuxing problem)."
                else:
                    errMessage = "Timeout. Could not read or decode packets (corrupted stream)."
            else:
                errMessage = "Timeout. Could not find or decode qr code (code not in stream)."

            log.log(log.ERROR, errMessage)
            sys.stderr.write(errMessage + "\n")
            sys.stderr.flush()
        else:
            #Ended by signal?
            log.log(log.INFO, "Scanner._main_loop: Scanning interrupted before timeout.")
            sys.stderr.write("Scanning interrupted before timeout.\n")
            sys.stderr.flush()
            retVal = (len(self._foundCodes) > 0)

        log.log(log.DEBUG, "Scanner.stop: Scanner stopped")
        return retVal
