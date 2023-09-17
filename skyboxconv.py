#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import os, sys, optparse, logging, struct
from PIL import Image

class SkyboxConv:

    _usage = '%prog [options] (skybox file(s) ... | directory holding the skybox files.)'
    _output_directory = None
    _gameroot = None
    _follow = True
    _verbose = False
    _inputs = []
    _filelist = []

    def __init__(self):
        pass

    def parse_args(self):
        parser = optparse.OptionParser(self._usage)
        parser.add_option('-v', '--verbose', default=False, action='store_true')
        parser.add_option('-d', '--directory', default=None, type='string', help="The root directory of the gamesrc.")
        parser.add_option('-f', '--follow', default=False, action='store_true', help="follow the source directory structures")
        parser.add_option('-o', '--output', type='string', default=None, help="the destination root directory")

        options, inputs = parser.parse_args(sys.argv[1:])

        if options.verbose:
            logging.root.setLevel(logging.DEBUG)
        else:
            logging.root.setLevel(logging.INFO)

        if len(inputs) == 0:
            parser.print_usage()
            return False

        self._gameroot = options.directory
        self._follow = options.follow

        if options.output is None:
            logging.debug("No output path specified, redirect to current working directory.")
            self._output_directory = os.getcwd()
        else:
            if os.path.isdir(options.output):
                self._output_directory = os.path.normpath(os.path.abspath(options.output))
            else:
                self._output_directory = os.path.normpath(os.path.abspath(os.path.dirname(options.output)))

        self._inputs = list(map(lambda x: os.path.normpath(os.path.abspath(x)), inputs))

        for pathstr in iter(self._inputs):
            if os.path.isfile(pathstr): # is file
                self._filelist.append(pathstr) # add to process list.
            else: # is directory
                # walk through sub-dirs
                for root, dirs, files in os.walk(pathstr):
                    files = filter(lambda x: x.lower().endswith('.dds') and not x.startswith('._'), files)
                    self._filelist.extend(list(map(lambda x: os.path.join(root, x), files)))

        return True

    def _get_output_path(self, filepath, variant):
        output_path = None
        if self._follow:
            output_path = os.path.join(self._output_directory, os.path.dirname(os.path.relpath(filepath, self._gameroot)))
        else:
            output_path = self._output_directory
        filename_parts = os.path.basename(filepath).rsplit('_', 1)
        return os.path.join(output_path, ('%s_{}.png' % filename_parts[0]).format(variant))

    def do_convert(self, filepath, variant):
        output = self._get_output_path(filepath, variant)
        os.makedirs(os.path.dirname(output), exist_ok=True)

        if variant == 'clouds' or variant == '5' or variant == '6':
            # convert the dds to png instead.
            with Image.open(filepath) as img:
                img.save(output)
        elif variant == '12' or variant == '34':
            output_1 = self._get_output_path(filepath, variant[0])
            output_2 = self._get_output_path(filepath, variant[1])

            with Image.open(filepath) as im:
                im_b = im.crop((0, im.size[1] / 2, im.size[0], im.size[1]))
                im_2 = Image.new(im.mode, im.size, "#000000")
                im_2.paste(im_b.transpose(Image.FLIP_TOP_BOTTOM), (0, 0, im_b.size[0], im_b.size[1]))
                im_2.save(output_2)
                im_2.close()

                im_t = im.crop((0, 0, im.size[0], im.size[1] / 2))
                im_1 = Image.new(im.mode, im.size, "#000000")
                im_1.paste(im_t, (0, 0, im_t.size[0], im_t.size[1]))
                im_1.save(output_1)
                im_1.close()

        print(self._get_output_path(filepath, variant))

    def convert(self):
        # resolve the inputs.
        for filepath in self._filelist:
            # print('- {}'.format(os.path.relpath(filepath, self._gameroot)))
            filename_parts = os.path.basename(filepath).rsplit('_', 1)
            if len(filename_parts) > 1:
                variant, _ = filename_parts[1].rsplit('.')
            print(filename_parts[0], variant)
            self.do_convert(filepath, variant)

    def save_output(self):
        # TODO: save the convertion results.
        pass

if __name__ == "__main__":
    o = SkyboxConv()
    if o.parse_args():
        o.convert()
        o.save_output()
