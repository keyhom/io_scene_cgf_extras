#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import os, sys, logging, struct, subprocess, multiprocessing, shutil, re
import argparse
from commands import CommandExecutor

script_path = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))

class PCPart:

    def __init__(self, name, gender, race):
        self.model_name = name
        self.gender = gender
        self.race = race

    def getModelPaths(self):
        fmt = os.path.join('Objects', 'pc', '%s', 'mesh', '%s%s.cgf')
        model_name = self.model_name.lower()
        raceGender = (self.race[0] + self.gender[0]).lower()

        ret = [ fmt % (raceGender, raceGender, model_name) ]

        if model_name.endswith('foot') or model_name.endswith('hand'):
            ret.append(fmt % (raceGender, raceGender, model_name + 'short'))
        return ret

    def getModelOutputPaths(self):
        fmt = os.path.join('Objects', 'pc', '%s', 'model', '%s%s')
        model_name = self.model_name.lower()
        raceGender = (self.race[0] + self.gender[0]).lower()

        model_dirname = model_name

        matchObj = re.match( r'([0-9a-zA-Z]+)_([0-9a-zA-Z]+).*', model_name, re.M|re.I)
        if matchObj:
            model_dirname = matchObj.group(1) + '_' + matchObj.group(2)

        ret = fmt % (raceGender, raceGender, model_dirname)
        return ret

    def getTexturePaths(self):
        modelPath = self.getModelPaths()[0]
        modelOutputPath = self.getModelOutputPaths()
        modelPath, _ = os.path.splitext(modelPath)

        outputFilePath = os.path.join(modelOutputPath, os.path.basename(modelPath))

        ret = {}

        ret[ '%s.dds' % modelPath ]          = '%s_albedo.dds' % outputFilePath
        ret[ '%s_ddn.dds' % modelPath ]      = '%s_ddn.dds' % outputFilePath
        ret[ '%s_sp.dds' % modelPath ]       = '%s_sp.dds' % outputFilePath
        ret[ '%s_mask.dds' % modelPath ]     = '%s_mask.dds' % outputFilePath
        ret[ '%s_overmask.dds' % modelPath ] = '%s_overmask.dds' % outputFilePath
        ret[ '%s_illum.dds' % modelPath ]    = '%s_illum.dds' % outputFilePath

        return ret

    def __str__(self):
        return '<PCPart %s-%s-%s>: %s' % (self.model_name, self.gender, self.race, id(self))

class Convert:

    def __init__(self):
        self.initArgumentParser()

    def __del__(self):
        self.parser = None

    def initArgumentParser(self):
        self.parser = argparse.ArgumentParser( description = 'Convert the PC cgf/dds/cga, ..etc to fbx for unity.' )

        self.parser.add_argument('models', nargs='+', default=[], help='The model name list.')
        self.parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,
            help='Verbose to output debug')
        self.parser.add_argument('-d', '--directory', help='The game asset directory')
        self.parser.add_argument('-o', '--output-directory', dest='outputDirectory', default=os.getcwd(),
            help='The output root directory.')
        self.parser.add_argument('-b', '--blender', help='The blender executable path')
        self.parser.add_argument('--textures-only', dest='textureOnly',  action='store_true', help='Process the textures only.')
        self.parser.add_argument('-t', '--test', action='store_true', help='Only test the program, no generation or operation')
        self.parser.add_argument('-j', '--join', default=0, type=int, help='')

    def printHelp(self):
        self.parser.print_help()

    def parseArguments(self):
        args = self.parser.parse_args()

        if args.verbose:
            logging.root.setLevel(logging.DEBUG)

        if args.models and len(args.models) > 0:
            pass
        else:
            return False

        if not args.directory:
            logging.error('No game directory specified.')
            return False

        if not args.textureOnly and not args.blender:
            logging.error("No blender executable specified.")
            return False

        args.directory = os.path.abspath(args.directory)
        args.outputDirectory = os.path.abspath(args.outputDirectory)

        self.options = args

        if args.verbose:
            logging.debug('Output the input arguments')
            logging.debug('')
            logging.debug('\tpython executable = %s' % sys.executable)
            for k, v in vars(args).items():
                logging.debug('\t%s = %s' % (k, v))
            logging.debug('')

        return True

    def convert(self):
        if not self.options.models or len(self.options.models) == 0:
            return

        # Collects all the model names.
        model_names = []

        for i, model in enumerate(self.options.models):
            if os.path.isfile(model):
                with open(os.path.abspath(model), 'r') as f:
                    model_names.extend(list(map(lambda x: x.strip(), f.readlines())))
            else:
                model_names.append(model)

        races = ['lf', 'df']
        genders = ['male', 'female']

        parts = []

        for i, model in enumerate(model_names):
            for m, r in enumerate(races):
                for n, g in enumerate(genders):
                    parts.append(PCPart(model, g, r))


        cmd_list = []
        failed_list = []
        texture_dirs = {}

        for i, part in enumerate(parts):
            modelOutputPath = part.getModelOutputPaths()
            for j, relpath in enumerate(part.getModelPaths()):
                cmd = [ self.options.blender, '-b', '--python', os.path.join(script_path, 'cgf2fbx.py'), '--',
                        '--output-directory=%s' % os.path.join(self.options.outputDirectory, modelOutputPath),
                        os.path.join(self.options.directory, relpath)]
                cmd_list.append(cmd)
                logging.debug('CGF2FBX: %s' % ' '.join(cmd))

            for texture_path, texture_output_path in part.getTexturePaths().items():
                source_filepath = os.path.join(self.options.directory, texture_path)
                output_filepath = os.path.join(self.options.outputDirectory, texture_output_path)

                if os.path.exists(source_filepath):
                    output_dir = os.path.dirname(output_filepath)
                    if not self.options.test:
                        if not os.path.exists(output_dir):
                            try:
                                os.makedirs(output_dir)
                            except:
                                pass
                        shutil.copy2(source_filepath, output_filepath)

                    if not output_dir in texture_dirs:
                        texture_dirs[output_dir] = 0
                    cnt = texture_dirs[output_dir]
                    texture_dirs[output_dir] = cnt + 1

                    logging.debug('COPY %s => %s' % (source_filepath, output_filepath))

        for i, texture_dir in enumerate(texture_dirs):
            cmd = [sys.executable, os.path.join(script_path, 'dds2png.py'), '-d', texture_dir]
            logging.debug('Execute DDS2PNG: %s' % ' '.join(cmd))
            cmd_list.append(cmd)

        if not self.options.test:
            ce = CommandExecutor()
            ce.run_commands(cmd_list, self.options.join)

        logging.debug('All Commands done.')

        for i, texture_dir in enumerate(texture_dirs):
            # delete all the dds in the texture directory
            for rootpath, dirs, files in os.walk(texture_dir):
                for file in files:
                    if file.lower().endswith('.dds'):
                        logging.debug('Removing ... %s' % os.path.join(rootpath, file))
                        if not self.options.test:
                            try:
                                os.remove(os.path.join(rootpath, file))
                            except:
                                pass

        if len(failed_list) > 0:
            logging.warning('There %d textures converted failed!' % len(failed_list))
            for i, v in enumerate(failed_list):
                logging.warning('\t%s' % v)

        logging.debug('ALL Done.')


if __name__ == '__main__':
    c = Convert()

    if c.parseArguments():
        c.convert()
    else:
        c.printHelp()
