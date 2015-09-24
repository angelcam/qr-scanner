import signal
import sys
import avpy

import Scanner
from  Logger import log
import config

scanner = None

def signal_handler(signal, frame):
    log.log(log.INFO, "signal_handler: SIGINT. Will end.\n")
    if(scanner != None):
        scanner.stop()

def main():

    #configure logging
    log.start("qr-scanner")
    log.set_min_level(log.INFO)
    if(len(sys.argv) >= 4):
        if(sys.argv[3] == "writeDebug"):
            log.set_output_writing(True)
            log.set_min_level(log.DEBUG)
        else:
            level = log.stringToLevel.get(sys.argv[3], None)
            if(level == None):
                log.log(log.INFO, "Unknown debug level as parameter: " + str(sys.argv[3]) + " Setting to level info.")
                log.set_min_level(log.INFO)
            else:
                log.log(log.INFO, "Setting log level to " + sys.argv[3] + " Setting to level info.")
                log.set_min_level(level)
    else:
        avpy.av.lib.av_log_set_level(avpy.av.lib.AV_LOG_VERBOSE)

    log.log(log.INFO, "main: Start of main. Arguments: " + str(sys.argv))

    #get stream address
    if(len(sys.argv) < 2 or len(sys.argv) > 4):
        sys.stderr.write("main: Bad number of parameters. (" + str(len(sys.argv)) + ")\n"
                         "Usage: qr-scanner streamAddress [timeout_seconds] [logger_level]\n"
                         "default_timeout: " + str(config.TIMEOUT_S) + "s."
                         "logger_level: debug, info, error, fatal or writeDebug for debug level syslog and stdout\n")
        log.log(log.FATAL, "main: Bad number of parameters. Usage: qr-scanner streamAddress [timeout_seconds] [logger_level]\n"\
                "default_timeout: " + str(config.TIMEOUT_S) + "s."
                "logger_level: debug, info, error, fatal")
        exit(1)

    streamAddress = sys.argv[1]
    log.set_metadata("address", streamAddress)

    if(len(sys.argv) >= 3):
        config.TIMEOUT_S = int(sys.argv[2])

    #set signal handler
    global scanner
    signal.signal(signal.SIGINT, signal_handler)

    #create scanner
    scanner = Scanner.Scanner(streamAddress)

    #start scanner
    ret  = scanner.start()  #will eat calling thread

    if(scanner.is_running()):
        scanner.stop()
    log.log(log.INFO, "END of main.")

    if(ret):
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()



