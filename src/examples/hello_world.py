#!/usr/bin/python3

import argparse
from qr_scanner import scan

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Stream url')
    parser.add_argument('-t', '--timeout', help='Timeout in seconds', default=60, type=int)
    parser.add_argument('-d', '--debug', help='Use debug mode logs', action='store_true')
    args = parser.parse_args()
    for code in scan(args.url, timeout=args.timeout, debug=args.debug):
        if code == "Hello world!":
            print("Hurray. I found it.")
            break
    else:
        print("Boo. I didn't found it.")