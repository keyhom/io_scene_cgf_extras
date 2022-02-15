#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys, optparse

#  models_dir = '/Volumes/Untitled/Resources/aion_assets'
models_dir = os.path.expanduser('D:/home/keyhom/project/Github/gion/unity/gion/Assets/GameRes')

if not os.path.exists(models_dir):
    raise IOError("Model directory is not fould.")

ext_mappings = {
        ".fbx": ".prefab",
        ".blend": ".prefab",
        ".prefab": ".fbx",
        ".cgf": ".prefab",
        }

def run():
    not_founds = []
    not_found_count = 0
    with open('test.lst', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n').strip('\r')
            filepath = os.path.join(models_dir, line)
            filepath = os.path.normpath(filepath)
            base_filepath, ext = os.path.splitext(filepath)
            if ext in ext_mappings:
                filepath = base_filepath + ext_mappings[ext]
            if not os.path.exists(filepath):
                not_founds.append(line)
                not_found_count = not_found_count + 1
                # print("%s\t%s" % (line, filepath))
        if len(not_founds) > 0:
            for nf in not_founds: print(nf)
        print('Total %d, not found %d' % (len(lines), not_found_count))

    try:
        with open('test-notfound.lst', 'w') as f:
            f.write('\n'.join(not_founds))
    except IOError as e:
        print(e)


if __name__ == '__main__':
    run()
