import sys
import avpy
import logging

from qr_scanner.scanner import Scanner
from qr_scanner.logger import LoggerWithCameraContext


def scan(stream_url, timeout=None, debug=False):

    # create one logger for individual scanning and set camera context
    logger = LoggerWithCameraContext(stream_url)

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler(sys.stdout))
        avpy.av.lib.av_log_set_level(avpy.av.lib.AV_LOG_VERBOSE)
    else:
        avpy.av.lib.av_log_set_level(avpy.av.lib.AV_LOG_QUIET)

    logger.info("Start of scan.")

    # create scanner
    scanner = Scanner(stream_url, logger, timeout=timeout)
    try:
        scanner.start()
        # start scanner
        # will eat calling thread
        for code in scanner.start():
            yield code
    except Exception as e:
        logger.exception("Scanning exit with error")
    finally:
        if scanner.is_running():
            scanner.stop()
        qr_codes = scanner.found_codes
        # we need to collect scanner before end of program or zbar module can cause crash
        del scanner

        logger.info("END of scan.")
        return qr_codes
