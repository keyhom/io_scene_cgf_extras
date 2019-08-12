#!/usr/bin/env python

import os, sys

#  models_dir = '/Volumes/Untitled/Resources/aion_assets'
models_dir = os.path.expanduser('~/Projects/github/gion/unity/gion/Assets')

ext_mappings = {
        ".fbx": ".prefab",
        ".blend": ".prefab",
        ".prefab": ".fbx",
        }

def run():
    with open('test.lst', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n').strip('\r')
            filepath = os.path.join(models_dir, line)
            base_filepath, ext = os.path.splitext(filepath)
            if ext in ext_mappings:
                filepath = base_filepath + ext_mappings[ext]
            if not os.path.exists(filepath):
                print("%s\t%s" % (line, filepath))

if __name__ == '__main__':
    run()
