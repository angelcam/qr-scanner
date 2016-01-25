import ctypes

import zbar
from Logger import log
import Image
import config

class CodeReader(object):
    def __init__(self):
        self._scanner = zbar.ImageScanner()
        self._scanner.set_config(0, 0, 0)
        self._scanner.set_config(zbar.Symbol.QRCODE, 0, 1)

    def read(self, avFrame):

        stringData = ctypes.string_at(avFrame.contents.data[0], avFrame.contents.width * avFrame.contents.height)

        image = Image.frombytes("L", (avFrame.contents.width,avFrame.contents.height), stringData)
        mirrored = image.transpose(Image.FLIP_LEFT_RIGHT)

        outputData = self._read(image) + self._read(mirrored)

        if(len(outputData) > 0):
            for code in outputData:
                log.debug("Found QR code: " + str(code))
        else:
            log.debug("QR code not found.")

        return outputData

    #takes Image and returns list of detected strings
    def _read(self, image):
        outputData = []

        zbarImage = zbar.Image(image.size[0], image.size[1], "Y800" , image.tostring())

        self._scanner.scan(zbarImage)

        for symbol in zbarImage:
            outputData.append(symbol.data)

        # clean up
        del(zbarImage)

        return outputData