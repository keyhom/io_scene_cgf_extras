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

        image = None
        #  image = Image.new('RGB', (width, height))

        #  for x in range(width):
        #  for y in range(height):
        #  r, g, b = unpack(f, '<3B')
        #  bufread = bufread + 3
        #  image.paste((r, g, b), (y, x, y + 1, x + 1));
        # image.paste((r, g, b), (x, y, x + 1, y + 1));

        #  w  = int(image.size[0] * (2048.0/width))
        #  h = int(image.size[1] * (2048.0/height))
        #  image = image.resize((w, h))

        #  for x in range(2048):
        #  for y in range(2048):
        #  r, g, b = image.getpixel((x, y))
        #  h = g * 1.0 / 255.0 + r * 1.0 / 255.0 / 255.0 + b * 1.0 / 255.0 / 255.0 / 255.0 # GRB => Height(0~1)
        #  h = int(h * 65535.0) # Range to unsigned short
        #  data.append(h)

        if for_unity:
            x2 = math.ceil(math.log2(width))
            x2 = int(math.pow(2, x2)) + 1
            y2 = math.ceil(math.log2(height))
            y2 = int(math.pow(2, y2)) + 1
        else:
            x2 = width
            y2 = height

        print('Extract to: %d x %d' % (x2, y2))

        for x in range(x2):
            if x >= width:
                for y in range(y2):
                    data.append(0)
            else:
                for y in range(y2):
                    if y >= height:
                        data.append(0)
                    else:
                        r, g, b = unpack(f, '<3B')
                        bufread = bufread + 3

                        h = g * 1.0 / 255.0 + r * 1.0 / 255.0 / 255.0 + b * \
                            1.0 / 255.0 / 255.0 / 255.0  # GRB => Height(0~1)
                        h = int(h * 65535.0)  # Range to unsigned short
                        data.append(h)

        # assert bufread == bufsize, "There're remaining %i buffer size, incorrect resolution specified?" % (bufsize - bufread)
        return data, image, x2, y2
    return None


def do_convert(input_file, width, height, for_unity, output_file):
    data, image, x2, y2 = read_h32(input_file, width, height, for_unity)

    if image:
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
