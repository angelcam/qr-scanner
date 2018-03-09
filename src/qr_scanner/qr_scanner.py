import sys
import avpy
import logging

from qr_scanner.scanner import Scanner

logger = logging.getLogger(__name__)


def scan(stream_url, timeout=None, debug=False, log_extra=None):
    if debug:
        logger.setLevel(logging.DEBUG)
        avpy.av.lib.av_log_set_level(avpy.av.lib.AV_LOG_VERBOSE)
    else:
        avpy.av.lib.av_log_set_level(avpy.av.lib.AV_LOG_QUIET)

    logger.info("Start of scan.", extra=log_extra)

    # create scanner
    scanner = Scanner(stream_url, timeout=timeout)
    try:
        scanner.start()
        # start scanner
        # will eat calling thread
        for code in scanner.start():
            yield code
    except Exception as e:
        logger.exception("Scanning exit with error", extra=log_extra)
    finally:
        if scanner.is_running():
            scanner.stop()
        qr_codes = scanner.found_codes
        # we need to collect scanner before end of program or zbar module can cause crash
        del scanner

        logger.info("END of scan.", extra=log_extra)
        return qr_codes
