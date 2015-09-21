import ctypes
import zbar

class CodeReader(object):
    def __init__(self):
        self._scanner = zbar.ImageScanner()
        self._scanner.parse_config('enable')

    def read(self, avFrame):

        #stringData = ctypes.string_at(self._swsFrame.contents.data[0], self._swsFrame.contents.width * self._swsFrame.contents.height)
        #image = Image.frombytes("L", (self._swsFrame.contents.width,self._swsFrame.contents.height), stringData)
        #image.save("image.png")

        stringData = ctypes.string_at(avFrame.contents.data[0], avFrame.contents.width * avFrame.contents.height)
        zbarImage = zbar.Image(avFrame.contents.width, avFrame.contents.height,"Y800" , stringData)

        self._scanner.scan(zbarImage)

        # extract results
        for symbol in zbarImage:
            # do something useful with results
            print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data

        # clean up
        del(zbarImage)

        return (None,  None)
