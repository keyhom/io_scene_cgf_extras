#!/usr/bin/env python

import os, sys, logging, optparse, struct

default_options={
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

    parser.add_option('-x', '--resolution', action='store', type='string',
            help="Specified the width & height.")

    parser.add_option('-v', '--verbose', action='store_true', default=False,
            help='Verbose logging trace')

    keywords, positional = parser.parse_args(argv)

    if keywords.verbose:
        logging.root.setLevel(logging.DEBUG)

    if not keywords.output:
        logging.debug('No output destination specified!')

    if not keywords.resolution:
        logging.debug('No resolution specified, use %s by default.' % default_options['resolution'])

    if len(positional) == 0:
        logging.debug('No input file specified!')

    for k in default_options.keys():
        if not keywords.__getattribute__(k):
            keywords.__setattr__(k, default_options[k])

    return (parser, keywords, positional)

def unpack(f, fmt):
    return struct.unpack(fmt, f.read(struct.calcsize(fmt)))

def pack(fmt, **args):
    return struct.pack(fmt, **args)

def read_h32(a_file, width, height):
    with open(a_file, 'rb') as f:
        f.seek(0, 2)
        bufsize = f.tell()
        f.seek(0, 0)

        logging.debug('File size: %i' % bufsize)
        bufread = 0
        data = []

        for x in range(width):
            for y in range(height):
                r, g, b = unpack(f, '<3B')
                bufread = bufread + 3

                h = g * 1.0 / 255.0 + r * 1.0 / 255.0 / 255.0 + b * 1.0 / 255.0 / 255.0 / 255.0 # GRB => Height(0~1)
                h = int(h * 65535.0) # Range to unsigned short
                data.append(h)

        assert bufread == bufsize, "There're remaining %i buffer size, incorrect resolution specified?" % (bufsize - bufread)
        return data
    return None

def do_convert(input_file, width, height, output_file):
    data = read_h32(input_file, width, height)

    if data:
        with open(output_file, 'wb') as f:
            for x in range(width):
                for y in range(height):
                    f.write(struct.pack('<H', data[x * width + y]))

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

    do_convert(positional[0], int(width), int(height), keywords.output)


if __name__ == '__main__':
    run()

