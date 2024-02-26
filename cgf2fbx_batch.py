#!/usr/bin/env python

import os, sys, logging, optparse, multiprocessing, subprocess, re
from subprocess import Popen, CalledProcessError, PIPE, STDOUT

script_dir = os.path.abspath(os.path.normpath(os.path.expandvars(os.path.dirname(__file__))))

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

    parser.add_option('-a', '--anim', default=False, action='store_true')
    parser.add_option('--anim_only', default=False, action='store_true')
    parser.add_option('-s', '--save-temp', default=False, action='store_true')
    parser.add_option('--skeleton', default=None, type='string', action='store')
    # parser.add_option('--resolve-collapse-name', default=False, action='store_true', dest='resolve_collapse_name')
    parser.add_option('--copy-textures', default=False, action='store_true', dest='copy_textures')

    parser.add_option('-j', '--join', default=0, action='store', type='int')

    keywords, positional = parser.parse_args(argv)

    if keywords.verbose:
        print('- Input arguments:')
        kws = list(filter(lambda x: not x.startswith('_') and x != 'read_file' and x != 'ensure_value' and x !=
            'read_module', dir(keywords)))
        for k in iter(kws):
            print('  - %s = %s' % (k, keywords.__getattribute__(k)))
        print()
        print('- Positionals:')
        for k in iter(positional):
            print('  - %s' % k)
        print()

    return (parser, keywords, positional)

def get_output_path(src_path, src_dir, dest_dir, follow=False, resolve_collapse_name=False):
    if not follow:
        exts = os.path.splitext(src_path)
        ext = '.cgf'
        if len(exts) > 1:
            ext = exts[1]
        return os.path.join(dest_dir, os.path.basename(src_path)) + ext
    else:
        if src_dir and src_path.startswith(src_dir):
            path = os.path.relpath(src_path, src_dir)
        else:
            path = src_path

        target_path = os.path.join(dest_dir, path)
        if resolve_collapse_name is True:
            exts = os.path.splitext(target_path)
            ext = '.cgf'
            if len(exts) > 1:
                ext = exts[1]

            searchObj = re.search( r'(.*)_(\d{2}\w).*' , os.path.basename(target_path), re.I)

            if searchObj:
                target_path = os.path.join(os.path.dirname(target_path), searchObj.group(1), os.path.basename(target_path)) + ext

        return target_path

def run(argv=None):
    parser, keywords, positional = process_arguments(argv)

    if keywords.verbose:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.ERROR)

    if sys.stdin.isatty():
        if len(positional) == 0:
            parser.print_help()
            return
    else:
        positional = list(map(lambda x: x.rstrip('\n').rstrip('\r'), sys.stdin.readlines()))

    inputs = []
    cgf_lists = []

    inputs.extend(positional)

    for i in range(len(inputs)):
        filepath = inputs[i]
        if filepath.endswith('.lst') and os.path.exists(filepath):
            with open(filepath, 'r') as f:
                cgf_lists.extend(f.readlines())
        elif filepath.endswith('.cgf') or filepath.endswith('.caf'):
            cgf_lists.append(filepath)

    if len(cgf_lists) == 0:
        logging.error('No availiable CGF files processing.')
        return

    cgf_lists = list(map(lambda x: os.path.join(keywords.directory, x), cgf_lists))

    logging.debug('Num of input cgf files: %i' % len(cgf_lists))

    commands = []
    blender_executable = keywords.blender

    global CORES

    if keywords.join > 0:
        CORES = keywords.join

    print('CORES: %d' % CORES)
    print('blender executable: %s' % blender_executable)

    addition_args = []

    if keywords.output_directory:
        keywords.output_directory = os.path.normpath(keywords.output_directory)
        keywords.output_directory = os.path.expanduser(keywords.output_directory)
        addition_args.append('--output-directory=%s' % keywords.output_directory)
    if keywords.directory:
        keywords.directory = os.path.expanduser(keywords.directory)
        keywords.directory = os.path.normpath(keywords.directory)
        addition_args.append('--directory=%s' % keywords.directory)
    if keywords.anim:
        addition_args.append('--anim')
    if keywords.anim_only:
        addition_args.append('--anim_only')
    if keywords.save_temp:
        addition_args.append('--save-temp')
    if keywords.skeleton:
        keywords.skeleton = os.path.expanduser(keywords.skeleton)
        addition_args.append('--skeleton=%s' % keywords.skeleton)
    if keywords.copy_textures:
        addition_args.append('--copy-textures')
    if keywords.keep_structure:
        addition_args.append('--keep-structure')

    if len(cgf_lists):
        for cgf_path in cgf_lists:
            cgf_path = cgf_path.replace('\n', '').replace('\r', '')
            cgf_path = os.path.normpath(cgf_path)
            exists = os.path.exists(cgf_path)
            sign_char = 'x' if os.path.exists(cgf_path) else ' '
            logging.debug('    [%s] %s' % (sign_char, cgf_path))

            if not exists:
                continue

            # output = get_output_path(cgf_path, keywords.directory, keywords.output_directory, keywords.keep_structure, keywords.resolve_collapse_name)

            # if os.path.isfile(output) or output.endswith('.cgf') or output.endswith('.caf') or output.endswith('.cga'):
            #     output_dir = os.path.dirname(output)
            # else:
            #     output_dir = output
            output_dir = keywords.output_directory

            logging.debug('    Output: %s' % output_dir)
            try:
                os.makedirs(output_dir, exist_ok=True)
            except:
                pass

            commands.append([blender_executable, '-b', '--python', os.path.join(script_dir, 'cgf2fbx.py'), '--', cgf_path] + addition_args)

    if len(commands):
        run_commands(commands)

if __name__ == '__main__':
    run()

