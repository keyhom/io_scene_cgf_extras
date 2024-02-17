#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys, shutil
from commands import CommandExecutor

curdir = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))
#  blender = '/Volumes/Untitled/Applications/blender-2.79-macOS-10.6/blender.app/Contents/MacOS/blender'
#  directory = '/Volumes/Untitled/Resources/aion_assets'
#  output_directory = '/Volumes/NetShares/GionRes/Temp'
blender = 'g:\\Program Files\\Blender Foundation\\Blender\\blender-2.79b-windows64\\blender.exe'
directory = 'g:/aion_assets'
#  output_directory = 'z:/GionRes/Temp'
output_directory = 'h:/Temp'

def convert_pc(file_lists, file_types = ['cgf']):
    # checks the source files.
    src_non_exists = []
    src_exists = []

    def _filtered(pairs):
        src, dst = pairs

        status = list(map(lambda x: True, file_types))
        all_lost = False
        for i, ftype in enumerate(file_types):
            status[i] = os.path.exists(os.path.join(directory, src[ftype]))
            if ftype == 'cgf' and not status[i]:
                all_lost = True # all lost if the cgf file non-exists.

        print(all_lost)

        if all_lost is False:
            for i, s in enumerate(status):
                if s is False:
                    src_non_exists.append(file_types[i])
                else:
                    src_exists.append(file_types[i])
            return True
        return False

    file_lists = list(filter(_filtered, file_lists))

    print(len(file_lists))

    cmd_list = []
    dds2png_dirs = {}

    for i, (src, dst) in enumerate(file_lists):
        for ftype in file_types:
            src_file = os.path.normpath(os.path.join(directory, src[ftype]))
            output_dir = os.path.normpath(os.path.join(output_directory, os.path.dirname(dst[ftype])))

            if ftype == 'cgf':
                cmd = [ blender, '-b', '--python', os.path.join(curdir, 'cgf2fbx.py'), '--', '--output-directory=%s' %
                    output_dir, src_file ]
                cmd_list.append(cmd)
            else:
                if not output_dir in dds2png_dirs:
                    dds2png_dirs[output_dir] = True

                try:
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                except:
                    pass

                try:
                    shutil.copy2(src_file, os.path.normpath(os.path.join(output_directory,
                        os.path.splitext(dst[ftype])[0] + ".dds"
                        )))
                except:
                    pass


    for k, v in dds2png_dirs.items():
        cmd = [ sys.executable, os.path.join(curdir, 'dds2png.py'), '-d', k ]
        cmd_list.append(cmd)

    executor = CommandExecutor()
    executor.run_commands(cmd_list)

    for i, (src, dst) in enumerate(file_lists):
        for ftype in file_types:
            if ftype == 'cgf':
                continue

            temp_dds = os.path.normpath(os.path.join(output_directory, os.path.splitext(dst[ftype])[0] + '.dds'))
            if os.path.exists(temp_dds):
                os.remove(temp_dds)

    print('All done.')
