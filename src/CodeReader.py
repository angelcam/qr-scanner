import ctypes
import zbar
from Logger import log

class CodeReader(object):
    def __init__(self):
        self._scanner = zbar.ImageScanner()
        self._scanner.parse_config('enable')

    def read(self, avFrame):

        stringData = ctypes.string_at(avFrame.contents.data[0], avFrame.contents.width * avFrame.contents.height)
        zbarImage = zbar.Image(avFrame.contents.width, avFrame.contents.height,"Y800" , stringData)

        self._scanner.scan(zbarImage)

        # extract results
        outputData = []
        for symbol in zbarImage:
            log.log(log.DEBUG, "Found QR code: " + str(symbol.data))
            outputData.append(symbol.data)

        if(len(outputData) == 0):
            log.log(log.DEBUG, "QR code not found.")

        # clean up
        del(zbarImage)

        return outputData
