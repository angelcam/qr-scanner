import signal
import sys
import avpy

import Logger
from logger import log
import logger
import Scanner
import utils
import config

scanner = None

def signal_handler(signal, frame):
    log.info("signal_handler: SIGINT. Will end.\n")
    if(scanner != None):
        scanner.stop()

def main():
    #configure logging
    log.start("qr-scanner")
    log.set_min_level(config.LOG_LEVEL)

    #adjust logs according to input arguments
    if(len(sys.argv) >= 4):
        if(sys.argv[3].lower() == "writedebug"):
            log.set_output_writing(True)
            log.set_min_level(logger.DEBUG)
            avpy.av.lib.av_log_set_level(avpy.av.lib.AV_LOG_VERBOSE)
        else:
            print("main: Unknown last parameter.")
    else:
        avpy.av.lib.av_log_set_level(avpy.av.lib.AV_LOG_QUIET)
        if config.LOG_LOGGLY_TOKEN:
            log.set_loggly(config.LOG_LOGGLY_TOKEN, "qr-scanner")

    log.info("main: Start of main. Arguments: " + str(sys.argv))

    #get stream address
    if(len(sys.argv) < 2 or len(sys.argv) > 4):
        sys.stderr.write("main: Bad number of parameters. (" + str(len(sys.argv)) + ")\n"
                         "Usage: qr-scanner streamAddress [timeout_seconds] [logger_level]\n"
                         "default_timeout: " + str(config.TIMEOUT_S) + "s."
                         "writedebug: for debug level syslog and stdout\n")
        log.error("main: Bad number of parameters. Usage: qr-scanner streamAddress [timeout_seconds] [logger_level]\n"\
                "default_timeout: " + str(config.TIMEOUT_S) + "s."
                "writeDebug: for debug level syslog and stdout")
        exit(1)

    streamAddress = sys.argv[1]

    if(len(sys.argv) >= 3):
        config.TIMEOUT_S = int(sys.argv[2])

    #set signal handler
    global scanner
    signal.signal(signal.SIGINT, signal_handler)

    #set context to global logger with context
    Logger.log.set_context(camera_url=streamAddress, camera_id=utils.cam_id_from_url(streamAddress))

    #create scanner
    scanner = Scanner.Scanner(streamAddress)

    #start scanner
    ret  = scanner.start()  #will eat calling thread

    if(scanner.is_running()):
        scanner.stop()

    # we need to collect scanner before end of program or zbar module can cause crash
    del scanner

    log.info("END of main.")
    return not ret

if __name__ == "__main__":
    sys.exit(main())
