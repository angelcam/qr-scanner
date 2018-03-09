import ctypes
import numpy as np
import logging
import zbar

logger = logging.getLogger(__name__)


class CodeReader(object):
    def __init__(self):
        config = [('ZBAR_NONE', 'ZBAR_CFG_ENABLE', 0),
                  ('ZBAR_QRCODE', 'ZBAR_CFG_ENABLE', 1)]
        self._scanner = zbar.Scanner(config)

    def read(self, avFrame):

        stringData = ctypes.string_at(avFrame.contents.data[0], avFrame.contents.width * avFrame.contents.height)
        image1d = np.fromstring(stringData, dtype=np.uint8, count=avFrame.contents.width * avFrame.contents.height)
        image = np.reshape(image1d, (avFrame.contents.height, avFrame.contents.width))

        outputData = self._read(image)

        flipped = np.fliplr(image)

        # XXX: this is needed to overcome a bug in zbar-py
        flipped = np.ascontiguousarray(flipped)

        outputData += self._read(flipped)

        if outputData:
            for code in outputData:
                logger.debug("Found QR code: " + str(code))
        else:
            logger.debug("QR code not found.")

        return outputData

    # takes Image and returns list of detected strings
    def _read(self, image):
        scanResults = self._scanner.scan(image)

        outputData = []
        for symbol in scanResults:
            outputData.append(symbol.data.decode())

        return outputData
