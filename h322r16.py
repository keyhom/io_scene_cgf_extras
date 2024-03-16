#!/usr/bin/env python

import os
import sys
import logging
import optparse
import struct
import math
from PIL import Image

default_options = {
    'resolution': '1536x1536'
}

def process_options(argv=None):
    if not argv:
        argv = sys.argv[1:]

    parser = optparse.OptionParser(
        usage='%prog [OPTIONS] input files ...',
        description='A tool for converting .h32 into .r16',
    )

    parser.add_option('-o', '--output', action='store', type='string',
                      help="Specified the output destination!")

    parser.add_option('-x', '--resolution', action='store', type='string', default='1536x1536',
                      help="Specified the width & height.")

    parser.add_option('-u', '--unity', action='store_true',
                      default=False, help='Specified compatible with unity engine.')

    parser.add_option('-v', '--verbose', action='store_true', default=False,
                      help='Verbose logging trace')

    keywords, positional = parser.parse_args(argv)

    if keywords.verbose:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    if not keywords.output:
        logging.debug('No output destination specified!')

    if not keywords.resolution:
        logging.debug('No resolution specified, use %s by default.' %
                      default_options['resolution'])

    if len(positional) == 0:
        logging.debug('No input file specified!')

    #  for k in default_options.keys():
        #  if not keywords.__getattribute__(k):
        #  keywords.__setattr__(k, default_options[k])

    return (parser, keywords, positional)


def unpack(f, fmt):
    return struct.unpack(fmt, f.read(struct.calcsize(fmt)))


def pack(fmt, **args):
    return struct.pack(fmt, **args)


def read_h32(a_file, width, height, for_unity=False):
    with open(a_file, 'rb') as f:
        f.seek(0, 2)
        bufsize = f.tell()
        f.seek(0, 0)

        logging.debug('File size: %i' % bufsize)
        bufread = 0
        data = []

        if for_unity:
            x2 = math.ceil(math.log2(width))
            x2 = int(math.pow(2, x2)) + 1
            y2 = math.ceil(math.log2(height))
            y2 = int(math.pow(2, y2)) + 1
        else:
            x2 = width
            y2 = height

        #  image = None
        if for_unity:
            image = Image.new('RGB', (x2 - 1, y2 - 1))
        else:
            image = Image.new('RGB', (x2, y2))

        print('Extract to: %d x %d' % (x2, y2))

        for x in range(x2):
            if x >= width:
                for y in range(y2):
                    data.append(0)
                    if for_unity and (y < y2 - 1 and x < x2 - 1):
                        image.putpixel((y, x), (0, 0, 0))
                    elif not for_unity:
                        image.putpixel((y, x), (0, 0, 0))
            else:
                for y in range(y2):
                    if y >= height:
                        data.append(0)
                        if for_unity and (y < y2 - 1 and x < x2 - 1):
                            image.putpixel((y, x), (0, 0, 0))
                        elif not for_unity:
                            image.putpixel((y, x), (0, 0, 0))
                    else:
                        # b & g is a h16 value, r is a gray level range for detail layers index
                        b, g, r = unpack(f, '<3B')
                        bufread = bufread + 3
                        h = (b & 0xFF) | ((g << 8) & 0xFF00)

                        image.putpixel((y, x), (r, 0, 0))

                        #  h = g * 1.0 / 255.0 + r * 1.0 / 255.0 / 255.0 + b * 1.0 / 255.0 / 255.0 / 255.0  # GRB => Height(0~1)
                        #  h = int(h * 65535.0)  # Range to unsigned short
                        data.append(h)

        # assert bufread == bufsize, "There're remaining %i buffer size, incorrect resolution specified?" % (bufsize - bufread)
        return data, image, x2, y2
    return None


def do_convert(input_file, width, height, for_unity, output_file):
    data, image, x2, y2 = read_h32(input_file, width, height, for_unity)

    if image:
        # Split as splat maps.
        splat_maps = {}
        for x in range(image.width):
            for y in range(image.height):
                r, g, b = image.getpixel((x, y))
                a = 0
                splat_idx = int(math.floor(r / 4))

                if r >= 32:
                    continue

                splat_sub_idx = r % 4
                if splat_sub_idx == 1:
                    r = 0
                    g = 255
                    b = 0
                    a = 0
                elif splat_sub_idx == 2:
                    r = 0
                    g = 0
                    b = 255
                    a = 0
                elif splat_sub_idx == 3:
                    r = 0
                    g = 0
                    b = 0
                    a = 255
                else:
                    r = 255
                    g = 0
                    b = 0
                    a = 0

                if not splat_idx in splat_maps:
                    splat_maps[splat_idx] = Image.new('RGBA', (image.width, image.height))
                splat_maps[splat_idx].putpixel((x, y), (r, g, b, a))

        for i, v in splat_maps.items():
            v = v.rotate(90)
            v.save('%s_s%d.png' % (output_file, i))

        image = image.rotate(90)
        image.save(output_file + '.png')

    if data:
        logging.debug("The final output path is: %s" % output_file)

        with open(output_file, 'wb') as f:
            for x in range(x2):
                for y in range(y2):
                    f.write(struct.pack('<H', data[y * x2 + x]))
                    #  f.write(struct.pack('<H', data[x * width + y]))

            logging.debug('Done!')


def run(argv=None):
    parser, keywords, positional = process_options(argv)

    if len(positional) == 0:
        parser.print_help()
        return

    if not keywords.output:
        keywords.output = os.path.splitext(positional[0])[0] + '.raw'

    if not os.path.exists(positional[0]):
        logging.error('Non exists input file: %s' % positional[0])
        return

    width, height = keywords.resolution.split('x')

    logging.debug('Resolution on working: %sx%s' % (width, height))
    logging.debug('The output file: %s' % keywords.output)

    do_convert(positional[0], int(width), int(height), keywords.unity, keywords.output)


if __name__ == '__main__':
    run()
