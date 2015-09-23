import signal
import sys

import Scanner
from  Logger import log
import config

PRINT_LOGS = False

scanner = None

def signal_handler(signal, frame):
    log.log(log.INFO, "signal_handler: SIGINT. Will end.\n")
    if(scanner != None):
        scanner.stop()

def main():

    log.set_output_writing(PRINT_LOGS)
    log.set_min_level(log.INFO)
    log.start("qr-scanner")

    log.log(log.INFO, "main: Start of main. Arguments: " + str(sys.argv))

    #get stream address
    if(len(sys.argv) < 2 or len(sys.argv) > 4):
        sys.stderr.write("main: Bad number of parameters. Usage: qr-scanner streamAddress [timeout_seconds] [logger_level]\n"\
                "default_timeout: " + str(config.TIMEOUT_S) + "s."\
                "logger_level: debug, info, error, fatal\n")
        log.log(log.FATAL, "main: Bad number of parameters. Usage: qr-scanner streamAddress [timeout_seconds] [logger_level]\n"\
                "default_timeout: " + str(config.TIMEOUT_S) + "s."\
                "logger_level: debug, info, error, fatal")
        print()
        exit(1)

    streamAddress = sys.argv[1]
    log.set_metadata("address", streamAddress)

    if(len(sys.argv) == 3):
        config.TIMEOUT_S = int(sys.argv[2])

    if(len(sys.argv) == 4):
        level = log.stringToLevel.get(sys.argv[3], None)
        if(level == None):
            log.log(log.INFO, "Unknown debug level as parameter: " + str(sys.argv[3]) + " Setting to level info.")
            log.set_min_level(log.INFO)
        else:
            log.log(log.INFO, "Setting log level to " + sys.argv[3] + " Setting to level info.")
            log.set_min_level(level)

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



