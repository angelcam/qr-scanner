import signal
import sys

import Scanner

scanner = None

def signal_handler(signal, frame):
    if(scanner != None):
        scanner.stop()

def main():

    print("START of main.")
    
    #get stream address
    if(len(sys.argv) != 2):
        print("main: This program needs exactly one parameter. Stream address.")
        exit(1)
    streamAddress = sys.argv[1]

    #set signal handler
    global scanner
    signal.signal(signal.SIGINT, signal_handler)

    #create scanner
    scanner = Scanner.Scanner(streamAddress)

    #start scanner
    scanner.start()  #will eat calling thread

    if(scanner.is_running()):
        scanner.stop()
    print("END of main.")

if __name__ == "__main__":
    main()



