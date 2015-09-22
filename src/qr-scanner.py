import signal
import sys
import config

import Scanner

scanner = None

def signal_handler(signal, frame):
    if(scanner != None):
        scanner.stop()

def main():

    print("START of main.")

    #get stream address
    if(len(sys.argv) != 2 and len(sys.argv) != 3):
        print("main: Bad number of parameters. Usage: qr-scanner streamAddress [timeout seconds]")
        print("Default timeout " + str(config.TIMEOUT_S) + "s.")
        exit(1)

    streamAddress = sys.argv[1]
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
    print("END of main.")
    exit(ret)

if __name__ == "__main__":
    main()



