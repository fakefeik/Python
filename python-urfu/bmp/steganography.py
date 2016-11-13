import math


SIZE_LENGTH = 32
OFFSET = 0


def get_space(len_of_data, bits_count, step):
    return round(len_of_data * bits_count / (8 * 1024 * step), 2)


def encode(byte_arr, data_to_encode, bits_count, step):
    bits_count_bin = (1 << bits_count) - 1
    true = 255 << bits_count
    size_end = math.ceil(SIZE_LENGTH / bits_count) * step
    encode_size(byte_arr, math.ceil(len(data_to_encode) * 8 / bits_count), size_end, bits_count, step)
    could_encode = get_space(len(byte_arr) - size_end, bits_count, step)
    len_data_to_encode = round(len(data_to_encode) / 1024, 2)
    print("Could encode:\t{} Kb\nData to encode:\t{} Kb".format(could_encode, len_data_to_encode))
    if len_data_to_encode > could_encode:
        print("Possible loss of information.")
    index = size_end + OFFSET
    if not bits_count & (bits_count - 1):
        for j, byte in enumerate(data_to_encode):
            for i in range(int(8 / bits_count)):
                new_byte = byte >> 8 - bits_count - i * bits_count
                byte_arr[index] &= true
                byte_arr[index] |= new_byte & bits_count_bin
                index += step
                if index >= len(byte_arr):
                    return byte_arr
    else:
        offset = 0
        new_byte = 0
        for i, byte in enumerate(data_to_encode):
            if offset > 0:
                new_byte |= byte >> 8 - offset
                byte_arr[index] &= true
                byte_arr[index] |= new_byte & bits_count_bin
                index += step
                if index >= len(byte_arr):
                    return byte_arr
            for j in range(8):
                bits_offset = 8 - (j + 1) * bits_count - offset
                if bits_offset >= 0:
                    new_byte = byte >> bits_offset
                    byte_arr[index] &= true
                    byte_arr[index] |= new_byte & bits_count_bin
                    index += step
                    if index >= len(byte_arr):
                        return byte_arr
                else:
                    new_byte = byte << -bits_offset
                    offset = -bits_offset
                    break
                if bits_offset == 0:
                    offset = 0
                    break
        if offset > 0:
            byte_arr[index] &= true
            byte_arr[index] |= new_byte & bits_count_bin

    return byte_arr


def decode(data_to_decode, bits_count, step, size=True):
    bits_count_bin = (1 << bits_count) - 1

    if size:
        size_end = math.ceil(SIZE_LENGTH / bits_count) * step
        size = decode_size(data_to_decode, size_end, bits_count, step)
        end = min(len(data_to_decode), size * step + size_end + OFFSET)
    else:
        size_end = 0
        end = len(data_to_decode)

    decoded_array = bytearray()
    new_byte = 0
    count = 0
    index = size_end + OFFSET

    while index < end:
        byte = data_to_decode[index] & bits_count_bin
        index += step
        count += bits_count
        if count >= 8:
            new_byte <<= bits_count
            new_byte |= byte
            decoded_array.append(new_byte >> count - 8)
            new_byte &= (1 << count - 8) - 1
            count -= 8
        else:
            new_byte <<= bits_count
            new_byte |= byte

    return decoded_array


def search(decoded, bits_count, step):
    formats = {'rar': bytes([0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x00]),
               'zip': bytes([0x50, 0x4B, 0x03, 0x04]),
               'exe': bytes([0x4D, 0x5A, 0x90, 0x00, 0x03, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00]),
               'jpg': bytes([0xFF, 0xD8, 0xFF, 0xE0]),
               'png': bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x00, 0x00, 0x00, 0x0D]),
               'bmp': bytes([0x42, 0x4D, 0x36]),
               'wav': bytes([0x52, 0x49, 0x46, 0x46])}

    decoded = decode(decoded, bits_count, step, size=False)
    text_array = list(detect_ascii(decoded, 30))

    for x in text_array:
        print(x.decode('cp1251'))

    for key, value in formats.items():
        if value in decoded:
            print('found ' + key)


def detect_ascii(byte_arr, min_text_length):
    ret_array = bytearray()
    for i, byte in enumerate(byte_arr):
        if 31 < byte < 127 or byte == 9 or byte == 10 or byte > 191:
            ret_array.append(byte)
        else:
            if len(ret_array) > min_text_length:
                yield ret_array
            ret_array = bytearray()


def encode_size(byte_arr, size, size_end, bits_count=1, step=1):
    bits_count_bin = (1 << bits_count) - 1
    true = 255 << bits_count
    i = size_end - 1
    j = 0
    while i >= 0:
        this_size = size >> j
        byte_arr[i] = byte_arr[i] & true | this_size & bits_count_bin
        j += bits_count
        i -= step


def decode_size(byte_arr, size_end, bits_count=1, step=1):
    size = 0
    bits_count_bin = (1 << bits_count) - 1
    i = size_end - 1
    j = 0
    while i >= 0:
        size_bit = byte_arr[i] & bits_count_bin
        size |= size_bit << j
        j += bits_count
        i -= step
    return size


if __name__ == '__main__':
    pass