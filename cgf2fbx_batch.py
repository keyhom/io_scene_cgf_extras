#!/usr/bin/env python

import os, sys, logging, optparse, multiprocessing, subprocess
from subprocess import Popen, CalledProcessError, PIPE, STDOUT

stdout = None
stderr = None

def call_process(cmd):
    print(cmd)

    proc = Popen(cmd, stdout=stdout, stderr=stderr)
    proc.communicate()
    if proc.returncode != 0:
        # Deliberately do not use CalledProcessError, see issue #2944
        raise Exception('Command \'%s\' returned non-zero exit status %s' %
                (' '.join(cmd), proc.returncode))

CORES = multiprocessing.cpu_count()

def run_commands(commands):
    cores = min(len(commands), CORES)
    if cores <= 1:
        for command in commands:
            call_process(command)
    else:
        pool = multiprocessing.Pool(processes = cores)
        pool.map(call_process, commands, chunksize = 1)

def process_arguments(argv):
    if not argv:
        argv = sys.argv[1:]

    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose',
            default=False,
            action='store_true'
            )

    parser.add_option('-d', '--directory',
            default='',
            dest='directory', type='string', action='store')

    parser.add_option('-o', '--output-directory', default='',
            dest='output_directory', type='string', action='store')

    parser.add_option('-k', '--keep-structure',
            default=False, dest='keep_structure', action='store_true')

    parser.add_option('-b', '--blender', default='blender',
            action='store')

    parser.add_option('-j', '--join', default=0, action='store', type='int')

    keywords, positional = parser.parse_args(argv)

    return (parser, keywords, positional)

def get_output_path(src_path, src_dir, dest_dir, follow=False):
    if not follow:
        return os.path.join(dest_dir, os.path.basename(src_path)) + '.cgf'
    else:
        if src_dir and src_path.startswith(src_dir):
            path = os.path.relpath(src_path, src_dir)
        else:
            path = src_path

        return os.path.join(dest_dir, path)

def run(argv=None):
    parser, keywords, positional = process_arguments(argv)

    if keywords.verbose:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.ERROR)

    if len(positional) == 0:
        parser.print_help()
        return

    inputs = []
    cgf_lists = []

    inputs.extend(positional)

    for i in range(len(inputs)):
        filepath = inputs[i]
        if filepath.endswith('.lst') and os.path.exists(filepath):
            with open(filepath, 'r') as f:
                cgf_lists.extend(f.readlines())
        elif filepath.endswith('.cgf'):
            cgf_lists.append(filepath)

    if len(cgf_lists) == 0:
        logging.ERROR('No availiable CGF files processing.')
        return

    cgf_lists = list(map(lambda x: os.path.join(keywords.directory, x), cgf_lists))

    logging.debug('Num of input cgf files: %i' % len(cgf_lists))

    commands = []
    blender_executable = keywords.blender

    global CORES

    if keywords.join > 0:
        CORES = keywords.join

    print('CORES: %d' % CORES)

    if len(cgf_lists):
        for cgf_path in cgf_lists:
            cgf_path = cgf_path.replace('\n', '').replace('\r', '')
            exists = os.path.exists(cgf_path)
            sign_char = 'x' if os.path.exists(cgf_path) else ' '
            logging.debug('    [%s] %s' % (sign_char, cgf_path))

            if not exists:
                continue

            output = get_output_path(cgf_path, keywords.directory, keywords.output_directory, keywords.keep_structure)

            if os.path.isfile(output) or output.endswith('.cgf'):
                output_dir = os.path.dirname(output)
            else:
                output_dir = output

            logging.debug('    Output: %s' % output_dir)
            try:
                os.makedirs(output_dir)
            except:
                pass

            commands.append([blender_executable, '-b', '--python', 'cgf2fbx.py', '--', '--output-directory=%s' % output_dir, cgf_path])

    if len(commands):
        run_commands(commands)

if __name__ == '__main__':
    run()

