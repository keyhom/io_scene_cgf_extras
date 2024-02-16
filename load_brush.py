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
    _unk1_s = []
    _cgf_filenames = []
    _lines = []
    _line2s = []

    _brush_file = None
    _output_path = None
    _verbose = False

    _parser = None

    def __init__(self):
        self._lines.append('#,fileName,collision type?,bb_x1,bb_y1,bb_z1,bb_x2,bb_y2,bb_z2\n')
        self._line2s.append('#,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n')

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

            signature, a, b, unk1_len = unpack(f, '<3siii')
            logging.debug('Unk1 len %d' % unk1_len)
            for i in range(unk1_len):
                sl, = unpack(f, '<i')
                unk1_segment, = unpack(f, '<%ds' % (sl - 4))
                unk1_str = unk1_segment[:unk1_segment.find(0x00)]
                self._unk1_s.append(unk1_str.decode())
                logging.debug('unk1_s[%d] = %s' % (i, self._unk1_s[i]))

            unk2_len, = unpack(f, '<i')
            logging.debug('Unk2 len %d' % unk2_len)
            for i in range(unk2_len):
                sl, = unpack(f, '<i')
                s2 = sl - 128 - 4
                filename_raw, unk2_segment = unpack(f, '<128s%ds' % s2)
                filename = filename_raw[:filename_raw.find(0x00)]

                buf = unk2_segment
                # t, maybe the type of respected.
                # f1 - f6, the bouding-box squre meaning.
                t, f1, f2, f3, f4, f5, f6 = struct.unpack_from('<iffffff', buf)
                self._cgf_filenames.append(filename.decode())

                self._lines.append('%d,%s,%d,%f,%f,%f,%f,%f,%f\n' % (i + 1, filename.decode(), t, f1, f2, f3, f4, f5, f6))

            unk3_len, = unpack(f, '<i')
            logging.debug('CurPos: %d, Remaining %d bytes' % (f.tell(), bytes_total - f.tell()), unk3_len)
            for i in range(unk3_len):
                unk3_segment, = unpack(f, '<88s')
                datas = struct.unpack_from('<iii4B4Bi12f4i', unk3_segment)
                # logging.debug(len(datas))
                # logging.debug(datas)
                line_val = ',%d,%d,%d,%x,%x,%x,%x,%x,%x,%x,%x,%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d\n' % datas
                line_val = '%d,%s%s' % (i + 1, self._cgf_filenames[datas[2]], line_val)
                self._line2s.append(line_val)

            if bytes_total - f.tell() == 0:
                logging.info('All bytes parsed.')
            else:
                logging.warn('There are remaining data would not be parsed!')

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

        try:
            logging.info('Write to output file \'%s-2.csv\'' % (os.path.join(output_dir, output_path)))
            with open(os.path.join(output_dir, '%s-2.csv' % output_path), 'w+') as w:
                w.writelines(self._line2s)
        except IOError as e:
            logging.error(e)


def run(argv=None):
    b = Brush()
    if b.parse_arguments():
        b.parse()

if __name__ == '__main__':
    run(sys.argv)
