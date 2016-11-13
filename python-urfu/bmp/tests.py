import unittest
import bmpfile
import steganography


class TestClass(unittest.TestCase):
    def func(self, file, file_to_encode):
        with open(file_to_encode, 'rb') as f:
            first = bytearray(f.read())
        print()
        print("File:\t\t{}\nFile to encode:\t{}".format(file, file_to_encode))
        bmp = bmpfile.ParsedBMP(file)
        rewritable = steganography.encode(bmp.rewritable, first, bits_count, step)
        second = steganography.decode(rewritable, bits_count, step)
        return first, second

    def test1_bmp(self):
        result = self.func("junk/32.bmp", "junk/test.bmp")
        self.assertEqual(result[0], result[1])

    def test2_txt(self):
        result = self.func("junk/256.bmp", "junk/test.txt")
        self.assertEqual(result[0], result[1])

    def test3_docx(self):
        result = self.func("junk/512.bmp", "junk/test.docx")
        self.assertEqual(result[0], result[1])

    def test4_rar(self):
        result = self.func("junk/1024.bmp", "junk/test.rar")
        self.assertEqual(result[0], result[1])

    def test5_exe(self):
        result = self.func("junk/2048.bmp", "junk/test.exe")
        self.assertEqual(result[0], result[1])

    def test6_png(self):
        result = self.func("junk/wallpaper.bmp", "junk/test.png")
        self.assertEqual(result[0], result[1])

    def test7_jpg(self):
        result = self.func("junk/wallpaper2.bmp", "junk/test.jpg")
        self.assertEqual(result[0], result[1])


if __name__ == "__main__":
    bits_count = 2
    step = 1
    unittest.main()
