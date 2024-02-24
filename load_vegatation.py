#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from __future__ import print_function
import os, sys, optparse, logging, struct

def get_str(bs, end='\x00'):
    idx = bytes(bs).find(end)
    bytes(bs).capitalize()

def unpack(fio, fmt):
    return struct.unpack(fmt, fio.read(struct.calcsize(fmt)))

class Brush:

    _lines = []

    _brush_file = None
    _output_path = None
    _verbose = False

    _parser = None

    def __init__(self):
        pass

    def parse_arguments(self):
        argv = sys.argv[1:]

        parser = optparse.OptionParser()
        parser.add_option('-v', '--verbose', default=False, action='store_true')
        parser.add_option('-o', '--output', default=None, type='string', dest='output')

        self._parser = parser
        self._parser.print_version()

        keywords, positional = parser.parse_args(argv)

        if keywords.verbose:
            self._verbose = True

        if self._verbose:
            logging.root.setLevel(logging.DEBUG)
        else:
            logging.root.setLevel(logging.INFO)


        if not keywords.output: # No specified the output path.
            self._output_path = os.getcwd()
            logging.debug('No specified for output path, so fallback to the cwd: %s' % self._output_path)
        else:
            self._output_path = keywords.output

        if len(positional) > 0:
            self._brush_file = positional[0] # Only first brush file available.

        if self.valid_arguments():
            return (parser, keywords, positional)

        return None

    def valid_arguments(self):
        if self._brush_file is None:
            logging.error("No brush file specified.")
            self._parser.print_usage()
            return None

        return True

    def parse(self):
        with open(self._brush_file, 'rb') as f:
            bytes_total = f.seek(0,2)
            f.seek(0, 0)

            per_size, = unpack(f, '<i')
            logging.debug('Per size unit: %d' % per_size)
            assert((bytes_total - 4) % per_size == 0)
            logging.debug('Total count: %f' % ((bytes_total - 4) / per_size))
            for i in range(0, int((bytes_total - 4) / per_size - 1)):
                #  x, y, z, unk = unpack(f, '<3fi')
                x, y, z, = unpack(f, '<3H')
                id = unpack(f, '<B')
                datas = unpack(f, '<9B')
                #  logging.debug('xyz: %f, %f, %f, unk: %d' % (x, y, z, unk))
                #  logging.debug(datas)
                x = (x / 65535.0) * 2.0 * 1536.0
                y = (y / 65535.0) * 2.0 * 1536.0
                z = (z / 65535.0) * 2.0 * 1536.0
                self._lines.append('%f,%f,%f,' % (x, y, z))
                self._lines.append('%d,' % id)
                self._lines.append('%x,%x,%x,%x,%x,%x,%x,%x,%x\n' % datas)

        basename = os.path.basename(self._brush_file)
        _, output_path = os.path.splitdrive(os.path.normpath(self._brush_file))
        output_path = output_path.replace("\\", "_")
        output_path = output_path.replace("/", "_")

        if output_path.startswith("_"):
            output_path = output_path[1:]

        output_dir = self._output_path
        if os.path.isfile(output_dir):
            output_dir = os.path.dirname(output_dir)

        try:
            logging.info('Write to output file \'%s.csv\'' % (os.path.join(output_dir, output_path)))
            with open(os.path.join(output_dir, '%s.csv' % (output_path)), 'w+') as w:
                w.writelines(self._lines)
        except IOError as e:
            logging.error(e)


def run(argv=None):
    b = Brush()
    if b.parse_arguments():
        b.parse()

if __name__ == '__main__':
    run(sys.argv)
