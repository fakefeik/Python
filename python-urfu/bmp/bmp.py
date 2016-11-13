import argparse
import bmpfile
import steganography


def bits_count(x):
    x = int(x)
    if x < 1 or x > 8:
        raise argparse.ArgumentTypeError("Bits count should be less or equal to 8 and greater than zero.")
    return x


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    encoder_subparser = subparsers.add_parser('encode', help='encoding steganography into bmp files')
    encoder_subparser.add_argument('infile', type=str, help='file to encode data to')
    encoder_subparser.add_argument('file_to_encode', type=str, help='file to get data to encode')
    encoder_subparser.add_argument('bits_count', type=bits_count, help='bits in byte that will be replaced')
    encoder_subparser.add_argument('step', type=int, help='')
    encoder_subparser.add_argument('--outfile', type=str, help='file for writing')

    decoder_subparser = subparsers.add_parser('decode', help='decoding steganography in bmp files')
    decoder_subparser.add_argument('infile', type=str, help='file to decode')
    decoder_subparser.add_argument('outfile', type=str, default='outfile', help='file to write decoded data to')
    decoder_subparser.add_argument('bits_count', type=bits_count, help='number of bits to read')
    decoder_subparser.add_argument('step', type=int, help='')

    searcher_subparser = subparsers.add_parser('search', help='command for detecting steganography in bmp files')
    searcher_subparser.add_argument('infile', type=str, help='file to be searched')
    searcher_subparser.add_argument('bits_count', type=bits_count, help='number of bits to read')
    searcher_subparser.add_argument('step', type=int, help='')

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
    else:
        try:
            bmp = bmpfile.ParsedBMP(args.infile)
        except FileNotFoundError:
            print('Infile does not exist.')
            return
        except IOError:
            print('Incorrect bmp file.')
            return
        if args.command == 'search':
            steganography.search(bmp.rewritable, args.bits_count, args.step)
        elif args.command == 'encode':
            try:
                with open(args.file_to_encode, 'rb') as f:
                    data_to_encode = bytearray(f.read())
            except FileNotFoundError:
                print('file_to_encode does not exist.')
                return
            except IOError:
                print('Incorrect filename.')
                return
            bmp.rewritable = steganography.encode(bmp.rewritable, data_to_encode, args.bits_count, args.step)
            bmp.save(args.outfile)
        else:
            data = steganography.decode(bmp.rewritable, args.bits_count, args.step)
            try:
                with open(args.outfile, 'wb+') as f:
                    f.write(data)
            except IOError:
                print('Incorrect filename.')
                return


if __name__ == '__main__':
    main()