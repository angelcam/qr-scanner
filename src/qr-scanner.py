import signal
import sys

import Scanner
from  Logger import log
import config

scanner = None

def signal_handler(signal, frame):
    log.log(log.INFO, "signal_handler: SIGINT. Will end.\n")
    if(scanner != None):
        scanner.stop()

def main():

    log.start("qr-scanner")
    log.set_min_level(log.INFO)
    log.log(log.INFO, "main: Start of main. Arguments: " + str(sys.argv))

    #get stream address
    if(len(sys.argv) != 2 and len(sys.argv) != 3):
        log.log(log.FATAL, "main: Bad number of parameters. Usage: qr-scanner streamAddress [timeout seconds]\n"\
                "Default timeout " + str(config.TIMEOUT_S) + "s.")
        print()
        exit(1)

    streamAddress = sys.argv[1]
    log.set_metadata("address", streamAddress)

    if(len(sys.argv) == 3):
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



