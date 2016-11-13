class ParsedBMP:
    def __init__(self, path):
        self.filename = path
        with open(path, 'rb') as f:
            self.file = f.read()
        self.header = self.file[:54]
        if self.header[:2] != b'BM':
            raise IOError('Not a correct BMP file.')

        self.data_pos = self._get_int_from_addr(0x0A)
        self.image_size = self._get_int_from_addr(0x22)
        self.width = self._get_int_from_addr(0x12)
        self.height = self._get_int_from_addr(0x16)

        if self.image_size == 0:
            self.image_size = self.width * self.height * 3
        if self.data_pos == 0:
            self.data_pos = 54
        self._not_rewritable = self.file[:self.data_pos]
        self.rewritable = bytearray(self.file[self.data_pos:])

    def _get_int_from_addr(self, addr):
        result = self.header[addr + 3]
        for i in range(3):
            result <<= 8
            result |= self.header[addr + 3 - i - 1]
        return result

    def save(self, filename):
        if not filename:
            filename = self.filename
        with open(filename, 'wb+') as f:
            f.write(self._not_rewritable + bytes(self.rewritable))

    def __str__(self):
        return "Parsed BMP file: Width: {}; Height: {}; Size: {}; Data Position: {}.".format(self.width,
                                                                                             self.height,
                                                                                             self.image_size,
                                                                                             self.data_pos)

if __name__ == '__main__':
    import sys
    try:
        bmp = ParsedBMP(sys.argv[1])
        print(bmp)
        bmp.save(None)
    except IOError:
        print('Not a correct BMP file.')
