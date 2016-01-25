import ctypes
import zbar
from Logger import log
import Image

class CodeReader(object):
    def __init__(self):
        self._scanner = zbar.ImageScanner()
        self._scanner.parse_config('enable')

    def read(self, avFrame):

        stringData = ctypes.string_at(avFrame.contents.data[0], avFrame.contents.width * avFrame.contents.height)

        image = Image.frombytes("L", (avFrame.contents.width,avFrame.contents.height), stringData)
        mirrored = image.transpose(Image.FLIP_LEFT_RIGHT)

        outputData = self._read(image) + self._read(mirrored)

        return outputData

    #takes Image and returns list of detected strings
    def _read(self, image):
        outputData = []

        zbarImage = zbar.Image(image.size[0], image.size[1], "Y800" , image.tostring())

        self._scanner.scan(zbarImage)

        for symbol in zbarImage:
            log.debug("Found QR code: " + str(symbol.data))
            outputData.append(symbol.data)

        if(len(outputData) == 0):
            log.debug("QR code not found.")

        # clean up
        del(zbarImage)

        return outputData