# Main class
import sys
import time
import threading
import avpy

from qr_scanner import config, stream_reader, code_reader

SCANNER_STATE_CONNECT = 0
SCANNER_STATE_READ = 1


class Scanner(object):
    def __init__(self, streamAddress, logger, timeout=None):

        avpy.av.lib.av_register_all()
        avpy.av.lib.avcodec_register_all()
        avpy.av.lib.avformat_network_init()

        self._timeout = timeout or config.TIMEOUT_S
        self._streamAddress = streamAddress
        self._streamReader = stream_reader.StreamReader(self._streamAddress, logger)
        self._codeReader = code_reader.CodeReader(logger)
        self._foundCodes = set()
        self._run = threading.Event()
        self._logger = logger

        # frame skipping
        self._lastDtsTime = None
        self._lastScanLen = None

    def start(self):
        self._logger.debug("Scanner.start: Starting scanner.")
        self._run.set()
        return self._main_loop()

    def stop(self):
        self._logger.debug("Scanner.stop: Stopping scanner.")
        self._run.clear()

    def is_running(self):
        return self._run.is_set()

    @property
    def found_codes(self):
        return self._foundCodes

    def _main_loop(self):
        self._logger.debug("Scanner._main_loop: Scanner started.")
        self._run.set()
        startTime = time.time()

        state = SCANNER_STATE_CONNECT

        frameI = 0
        skippedCount = 0
        while (time.time() - startTime < self._timeout and self._run.is_set()):

            if (state == SCANNER_STATE_CONNECT):
                self._logger.debug("Scanner._main_loop: State SCANNER_STATE_CONNECT.")
                self._streamReader.start()
                state = SCANNER_STATE_READ
                self._logger.debug("Scanner._main_loop: Connecting to stream ... ")

            elif (state == SCANNER_STATE_READ):

                # read frame from stream
                if (self._streamReader.try_decode()):

                    # read frame
                    outFrame = self._streamReader.get_out_frame()
                    if (not outFrame):
                        self._logger.debug("Scanner._main_loop: Cannot get ouput frame.", extra={'misc': 'frameI={}'.format(frameI)})
                        continue

                    frame, dtsTime = outFrame

                    # skip frames
                    now = time.time()
                    if (self._lastDtsTime and self._lastScanLen):
                        if (dtsTime < self._lastDtsTime):
                            self._lastDtsTime = dtsTime
                        else:

                            if (dtsTime - self._lastDtsTime < config.SKIP_TIME_S
                                    or dtsTime - self._lastDtsTime < self._lastScanLen):
                                skippedCount += 1
                                continue

                    if (skippedCount > 0):
                        self._logger.debug("Scanner._main_loop: Skipped " + str(skippedCount) + " frames: ")

                    skippedCount = 0
                    self._lastDtsTime = dtsTime

                    frameI += 1
                    self._logger.debug("Scanner._main_loop: State SCANNER_STATE_READ.", extra={'misc': 'frameI={}'.format(frameI)})

                    self._lastScanLen = time.time()
                    codes = self._codeReader.read(frame)
                    self._lastScanLen = time.time() - self._lastScanLen

                    for code in codes:
                        # write code only once
                        if (not code in self._foundCodes):
                            sys.stdout.write(str(code) + "\r\n\r\n")
                            sys.stdout.flush()
                            self._foundCodes.add(code)
                            yield code
            else:
                self._logger.debug("Scanner._main_loop: Unkdnown state.")
                self._streamReader.stop()
                time.sleep(1)
                state = SCANNER_STATE_CONNECT

        # End prints
        # loop ended by timeout
        if (self._run.is_set()):

            # good state
            if (len(self._foundCodes) > 0):
                sys.stdout.write("Timeout.\r\n")
                sys.stdout.flush()
                self._logger.info("Timeout.")
            else:
                # bad states
                if (frameI == 0):
                    if (state == SCANNER_STATE_CONNECT):
                        errMessage = "Timeout. Could not connect to stream (demuxing problem)."
                    else:
                        errMessage = "Timeout. Could not read or decode packets (corrupted stream)."
                else:
                    errMessage = "Timeout. Could not find or decode qr code (code not in stream)."

                self._logger.error(errMessage)
                sys.stderr.write(errMessage + "\n")
                sys.stderr.flush()
        else:
            # Ended by signal?
            self._logger.info("Scanner._main_loop: Scanning interrupted before timeout.")
            sys.stderr.write("Scanning interrupted before timeout.\n")
            sys.stderr.flush()

        # clean after yourself
        self._streamReader.stop()

        self._logger.debug("Scanner.stop: Scanner stopped")
        return (len(self._foundCodes) > 0)
