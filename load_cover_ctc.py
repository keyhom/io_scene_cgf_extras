#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from __future__ import print_function
import os, sys, optparse, logging, struct, math
from os.path import expanduser
from PIL import Image

def get_str(bs, end='\x00'):
    idx = bytes(bs).find(end)
    bytes(bs).capitalize()

class CoverCTC:

    _input_file = None
    _output_path = None
    _verbose = False
    _datas = None
    _headers = None
    _decode_needed = False

    _width = 0
    _height = 0
    _mipmap_count = 0

    def __init__(self):
        self._headers = bytearray(128)

    def _get_default_header(self):
        _headers = bytearray(128)
        i = [0]
        self.pack('<3sB', _headers, i, bytes('DDS', 'utf8'), 0x20)
        self.pack('<i', _headers, i, 0x7c)
        self.pack('<i', _headers, i, 0x00021007)
        self.pack('<i', _headers, i, self._width)
        self.pack('<i', _headers, i, self._height)
        self.pack('<i', _headers, i, 0)
        self.pack('<i', _headers, i, 0)
        self.pack('<i', _headers, i, self._mipmap_count)
        self.pack('<%dx' % (11 * 4), _headers, i)
        # pixel format
        self.pack('<3i%dx' % (5 * 4), _headers, i, 0x20, 0x04, 0x31545844)
        self.pack('<i%dx' % (3 * 4), _headers, i, 0x401008)
        return _headers

    def _write_to_test(self):
        i = [0]
        self.pack('<3sB', self._headers, i, bytes('DDS', 'utf8'), 0x20)
        self.pack('<i', self._headers, i, 0x7c)
        self.pack('<i', self._headers, i, 0x00021007)
        self.pack('<i', self._headers, i, self._width)
        self.pack('<i', self._headers, i, self._height)
        self.pack('<i', self._headers, i, 0)
        self.pack('<i', self._headers, i, 0)
        self.pack('<i', self._headers, i, self._mipmap_count)
        self.pack('<%dx' % (11 * 4), self._headers, i)
        # pixel format
        self.pack('<3i%dx' % (5 * 4), self._headers, i, 0x20, 0x04, 0x31545844)
        self.pack('<i%dx' % (3 * 4), self._headers, i, 0x401008)

        with open('C:/Users/keyhom/Desktop/test.dds', 'wb+') as o:
            o.write(self._headers)
            o.write(self._datas)
            o.write(struct.pack('<ib', 0, 0x0a))

    def parse_arguments(self):
        argv = sys.argv[1:]

        parser = optparse.OptionParser()
        parser.add_option('-v', '--verbose', default=False, action='store_true')
        parser.add_option('-o', '--output', default=None, type='string', dest='output')
        parser.add_option('--decode', default=False, action='store_true')

        self._parser = parser
        self._parser.print_version()

        keywords, positional = parser.parse_args(argv)

        if keywords.verbose:
            logging.root.setLevel(logging.DEBUG)
        else:
            logging.root.setLevel(logging.INFO)


        if not keywords.output: # No specified the output path.
            self._output_path = os.getcwd()
            logging.debug('No specified for output path, so fallback to the cwd: %s' % self._output_path)
        else:
            self._output_path = keywords.output

        if keywords.verbose:
            self._verbose = True

        if keywords.decode:
            self._decode_needed = True

        if len(positional) > 0:
            self._input_file = positional[0] # Only first brush file available.

        if self.valid_arguments():
            return (parser, keywords, positional)

        return None

    def valid_arguments(self):
        if self._input_file is None:
            logging.error("No input file specified.")
            self._parser.print_usage()
            return None

        return True

    def test_data_hold(self, filesize):
        filesize = filesize - 4 # remove the header
        print('filesize: %d' % filesize)
        print('per tile size: ', (filesize / 256))
        print('per tile actual size: ', (self.calc_tile_size(6, 64, 64, 8) * 4))
        tex_cnt = 4
        print("The splat texture count: %d" % tex_cnt)
        print("The splat texture size:", (filesize / tex_cnt))
        print(self.calc_dxt1_size(512))

    def calc_dxt1_size(self, worh, dxtx = 1):
        width = height = worh
        if worh == 0:
            width = height = 1

        if dxtx == 1:
            blockSize = 8
        else:
            blockSize = 16

        size = (( width + 3 ) / 4) * (( height + 3 ) / 4 ) * blockSize
        return size

    def calc_tile_size(self, mpcnt, w, h, block_size):
        data_len = 0
        for i in range(mpcnt):
            if w == 0 and h == 0:
                break
            if w == 0: w = 1
            if h == 0: h = 1

            data_len = data_len + int( ((w + 3)/4) * ((h + 3)/4) * block_size )

            w = w >> 1
            h = h >> 1

        return data_len

    def unpack(self, fmt, data, offset):
        size = struct.calcsize(fmt)
        ret = struct.unpack_from(fmt, data, offset[0])
        offset[0] = offset[0] + size
        return ret

    def pack(self, fmt, data, offset, *v):
        size = struct.calcsize(fmt)
        struct.pack_into(fmt, data, offset[0], *v)
        offset[0] = offset[0] + size

    def s3tc_decode(self, encode_datas, decode_datas, pixels_width, pixels_height, decode_flag):
        block_y = 0
        block_x = 0

        encode_data, encode_offset = encode_datas
        decode_data, decode_offset = decode_datas

        encode_offset = [encode_offset]
        decode_offset = [decode_offset]

        while True:
            if block_y >= pixels_height / 4:
                break

            while True:
                if block_x >= pixels_width / 4:
                    break

                # block deocding.
                alpha = 0
                one_bit_alpha_flag = 1
                init_alpha = ((1 - one_bit_alpha_flag) * int(255)) << 24
                colors = [int(0), int(0), int(0), int(0)]

                color_values = self.unpack('<hh', encode_data, encode_offset)

                rb0 = (color_values[0] << 19 | color_values[0] >> 8) & 0xf800f8
                rb1 = (color_values[1] << 19 | color_values[1] >> 8) & 0xf800f8
                g0 = (color_values[0] << 5) & 0x00fc00
                g1 = (color_values[1] << 5) & 0x00fc00
                g0 = g0 + (g0 >> 6) & 0x000300
                g1 = g1 + (g1 >> 6) & 0x000300

                colors[0] = rb0 + g0 + init_alpha
                colors[1] = rb1 + g1 + init_alpha

                # interpolate the other two color values
                if (color_values[0] > color_values[1] or one_bit_alpha_flag):
                    rb2 = (((2 * rb0 + rb1) * 21) >> 6) & 0xff00ff
                    rb3 = (((2 * rb1 + rb0) * 21) >> 6) & 0xff00ff
                    g2 = (((2 * g0 + g1) * 21) >> 6) & 0x00ff00
                    g3 = (((2 * g1 + g0) * 21) >> 6) & 0x00ff00
                    colors[3] = rb3 + g3 + init_alpha
                else:
                    rb2 = ((rb0 + rb1) >> 1) & 0xff00ff
                    g2 = ((g0 + g1) >> 1) & 0x00ff00
                    colors[3] = 0

                colors[2] = rb2 + g2 + init_alpha

                pixels_index, = self.unpack('<i', encode_data, encode_offset)

                for y in range(4):
                    for x in range(4):
                        init_alpha = (int(alpha) & 0x0f) << 28
                        init_alpha = init_alpha + init_alpha >> 4
                        v = int(init_alpha + colors[ pixels_index & 3])
                        struct.pack_into('<i', decode_data, decode_offset[0] + x * 4, v)
                        pixels_index = pixels_index >> 2
                        alpha = alpha >> 4
                    decode_offset[0] = decode_offset[0] + pixels_width * 4

                block_x = block_x + 1
                # decode block data += 4
                decode_offset[0] = decode_offset[0] + 4 * 4

            block_y = block_y + 1
            # decode block data += 3 * pixels_width
            decode_offset[0] = decode_offset[0] + (3 * pixels_width) * 4

        print(decode_offset[0], encode_offset[0])

    def parse(self):
        with open(self._input_file, 'rb') as f:
            f.seek(0, 2)
            filesize = f.tell()
            f.seek(0, 0)

            pixel_data = f.read()

            encode_offset = 0
            decode_offset = 0

            self._width = 1024
            self._height = 1024

            #  self._width = 2048
            #  self._height = 2048

            self._width = 1024 >> 4
            self._height = 1024 >> 4

            numberOfMipmaps = int(max(math.log2(self._width), math.log2(self._height))) + 1
            self._mipmap_count = numberOfMipmaps

            print('numberOfMipmaps is %d' % self._mipmap_count)

            assert struct.unpack_from('<i', pixel_data, encode_offset)[0] == 64

            encode_offset = encode_offset + 4

            per_file_size = 0

            w = self._width
            h = self._height
            data_len = 0

            # calc data length.
            for i in range(numberOfMipmaps):
                if w == 0 and h == 0:
                    break
                if w == 0: w = 1
                if h == 0: h = 1

                if self._decode_needed:
                    data_len = data_len + (h * w * 4)
                else:
                    data_len = data_len + int( ((w + 3)/4) * ((h + 3)/4) * 8 )

                w = w >> 1
                h = h >> 1

            if data_len > 0:
                print('alloc data length: %d' % data_len)
                self._datas = bytearray(data_len)

            print('len of pixel data: %d' % len(pixel_data))

            w = self._width
            h = self._height

            for i in range(numberOfMipmaps):
                if w == 0 and h == 0:
                    break

                if w == 0: w = 1
                if h == 0: h = 1

                size = int(((w + 3)/4) * ((h + 3)/4) * 8)
                per_file_size = per_file_size + size

                byte_per_pixel = 4
                stride = w * byte_per_pixel

                if self._decode_needed:
                    # DDS DXT1
                    self.s3tc_decode((pixel_data, encode_offset), (self._datas, decode_offset), w, h, 1)
                    decode_offset = decode_offset + (stride * h)
                else:
                    dd, = struct.unpack_from('<%ds' % (size), pixel_data, encode_offset)
                    print(len(dd), len(self._datas), decode_offset)
                    struct.pack_into('<%ds' % (size), self._datas, decode_offset, dd)
                    decode_offset = decode_offset + size

                encode_offset = encode_offset + size

                w = w >> 1
                h = h >> 1

    def parse_tile(self):

        with open(self._input_file, 'rb') as f:
            f.seek(0, 2)
            file_size = f.tell()
            f.seek(0, 0)

            self.test_data_hold(file_size)

            tile_size, = struct.unpack('<i', f.read(struct.calcsize('<i')))
            tile_size = 1024 >> 4

            self._width = self._height = tile_size
            self._mipmap_count = int(max( math.log2( self._width ), math.log2( self._height ))) + 1
            #  self._mipmap_count = int(max( math.log2( self._width ), math.log2( self._height )))
            #  self._mipmap_count = 6

            w = self._width
            h = self._height
            data_len = 0
            block_size = 8
            #  block_size = 8 * 2

            # calc data length.
            for i in range(self._mipmap_count):
                if w == 0 and h == 0:
                    break
                if w == 0: w = 1
                if h == 0: h = 1

                data_len = data_len + int( ((w + 3)/4) * ((h + 3)/4) * block_size )

                w = w >> 1
                h = h >> 1

            test_output_dir = os.path.expanduser('~/Desktop/test-covers')

            for i in range(257):
                result = bytearray(128 + data_len + 5)
                dd = f.read(data_len - 4)
                headers = self._get_default_header()
                struct.pack_into('<128s', result, 0, headers)
                struct.pack_into('<%ds' % data_len, result, 128, dd)
                #  struct.pack_into('<4xb', result, 128 + data_len, 0x0a)
                if not os.path.exists(test_output_dir):
                    os.makedirs(test_output_dir, exist_ok=True)
                with open(os.path.join(test_output_dir, 'test-%d.dds' % i), 'wb+') as o:
                    o.write(result)

def run(argv=None):
    b = CoverCTC()
    if b.parse_arguments():
        b.parse_tile()

if __name__ == '__main__':
    run(sys.argv)
