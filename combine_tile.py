#!/usr/bin/env python

from __future__ import absolute_import
import os, sys, shutil, optparse, logging
from PIL import Image

__rootpath__ = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))

def process_options(parser = None):
    if parser is None:
        parser = optparse.OptionParser(
                usage = "Usage: %prog [OPTIONS] input files ...",
                epilog = ""
                )
    parser.add_option('-v', '--verbose',
            default = False,
            action = 'store_true',
            help = 'Verbose logging trace.')

    parser.add_option('-x',
            dest = 'tile_size',
            default = '10x10',
            help = 'Row X Column tiles.')

    parser.add_option('-d', '--directory',
            dest = 'working_dir',
            help = 'Directory where the tile located.')

    parser.add_option('-p', '--pattern',
            default = '%x_%y',
            help = 'Tile pattern.')

    parser.add_option('-o', '--output',
            dest = 'output_file',
            default = 'output.png',
            help = 'Specify output path.')

    return parser

def run(args = None):
    if args is None:
        args = sys.argv[1:]

    parser = process_options()
    keywords, positional = parser.parse_args(args)

    input_files = []

    if len(positional) > 0:
        input_files = input_files  + positional

    #  if len(input_files) == 0:
        #  parser.print_help()
        #  return

    logging.root.setLevel(logging.INFO)

    if keywords.verbose:
        logging.root.setLevel(logging.DEBUG)

    tile_size = keywords.tile_size.split('x')
    tx = int(tile_size[0])
    ty = int(tile_size[1])
    ta = tx * ty

    logging.debug("Tile size is %d x %d = %d" % (tx, ty, ta))

    tw = None
    th = None

    output_image = None

    xi = yi = 0

    for i in range(0, ta):
        tile_filepath = os.path.join(keywords.working_dir, (keywords.pattern % i))
        logging.debug("Reading image tile %d => %s" % (i, tile_filepath))
        im = Image.open(tile_filepath)
        if tw is None:
            tw = im.width
        if th is None:
            th = im.height


        if output_image is None:
            output_image = Image.new('RGBA', ( tw * tx, th * ty ))

        output_image.paste(im, (xi * tw, yi * th))

        logging.debug("Image tile resolution: %d x %d" % (im.width, im.height))

        im.close()

        yi = yi + 1
        if yi == tx:
            xi = xi + 1
            yi = 0


    if output_image:
        output_image.save(keywords.output_file)
        output_image.close()

if __name__ == '__main__':
    run()

