#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys, shutil
import convert_pc_common

if __name__ == '__main__':
    file_lists = []

    for i, raceGender in enumerate([ 'lf', 'lm', 'df', 'dm' ]):
        head_src_dir = os.path.join('Objects', 'pc', raceGender, 'mesh')
        head_dst_dir = os.path.join('Objects', 'pc', raceGender, 'model')

        for rootpath, dirs, files in os.walk(os.path.join(convert_pc_common.directory, head_src_dir)):
            for head_cgf in list(filter(lambda x: x.lower().endswith('_head.cgf'), files)):
                print(head_cgf)
                filename = os.path.splitext(os.path.basename(head_cgf))[0]
                filepath = os.path.join(head_src_dir, filename)
                src_map = {
                    'cgf'    : filepath + '.cgf',
                    'albedo' : filepath + '.dds',
                    'ddn'    : filepath + '_ddn.dds',
                    'illum'  : filepath + '_illum.dds',
                    'mask'   : filepath + '_mask.dds',
                    'sp'     : filepath + '_sp.dds',
                }

                filepath = os.path.join(head_dst_dir, '%s_heads' % raceGender, filename.lower())
                dst_map = {
                    'cgf'    : filepath + '.fbx',
                    'albedo' : filepath + '_albedo.png',
                    'ddn'    : filepath + '_ddn.png',
                    'illum'  : filepath + '_illum.png',
                    'mask'   : filepath + '_mask.png',
                    'sp'     : filepath + '_sp.png',
                }
                file_lists.append((src_map, dst_map))

    file_types = [ 'cgf', 'albedo', 'ddn', 'illum', 'mask', 'sp' ]
    for i, (src, dst) in enumerate(file_lists):
        for ftype in file_types:
            print('%04d | %s => %s' % (i, src[ftype], dst[ftype]))

    convert_pc_common.convert_pc(file_lists, file_types)
