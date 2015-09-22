import ctypes
import zbar

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
            outputData.append(symbol.data)

        # clean up
        del(zbarImage)

        return outputData
