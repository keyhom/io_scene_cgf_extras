#!/usr/bin/env python

from __future__ import absolute_import, print_function
import os, sys, optparse, subprocess, re, time, string, logging
from subprocess import PIPE, Popen, STDOUT
from PIL import Image


curdir = os.path.abspath(os.path.dirname(__file__))

LOG = logging.getLogger('dds2png')

def run(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = optparse.OptionParser(
            usage="usage: %prog [OPTIONS] files ...",
            description=("dds2png is a script to convert any DDS file format to PNG."),
            epilog=''
            )

    parser.add_option('-d', '--directory', type='string', default=None,
            action='store',
            help='Searching for DDS.')

    parser.add_option('-v', '--verbose',
            default=False,
            action='store_true',
            help='Verbose logging trace')

    keywords, positional = parser.parse_args(args)

    input_lines = []

    directory = keywords.directory

    if not directory and len(positional) == 0:
        parser.print_help()
        exit(0)
    elif directory and len(positional) == 0:
        for root, dirs, files in os.walk(directory):
            # ignore dirs, filtering .dds
            for f in files:
                if f.endswith('.dds') and not f.startswith('_') and not f.startswith('.'):
                    input_lines.append(os.path.join(root, f))
    elif positional[0] == '-':
        # read from the stdin
        input_lines = sys.stdin.readlines()
        positional = positional[1:]


    if keywords.verbose:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.INFO)

    LOGGING_FORMAT = '%(asctime)-15s %(levelname)8s | %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)

    filenames = []
    if len(input_lines) > 0:
        filenames.extend(input_lines)
    else:
        filenames.extend(positional)

    if len(filenames):
        filenames = list(map(lambda x: os.path.abspath(x.replace('\r', '').replace('\n', '')), filenames))


    error_converts = []

    for filename in filenames:
        (base_filename, filename_ext) = os.path.splitext(filename)
        output_filename = base_filename + '.png'
        try:
            with Image.open(filename) as im:
                LOG.debug('%s - %s - %s' % (im.format, im.size, im.mode))
                LOG.info('Converting %s to %s' % (filename, output_filename))
                try:
                    im.save(output_filename)
                except:
                    error_converts.append(filename)
                    LOG.error("Can not convert %s to %s" % (filename, output_filename))
                LOG.info('Converted %s' % (output_filename))
        except:
            error_converts.append(filename)
            pass

    LOG.info('Done')

    if len(error_converts):
        LOG.warning('Several convertion error caughts:')
    for fn in error_converts:
        LOG.warning(fn)

if __name__ == '__main__':
    # Execute the main entrance.
    run()

