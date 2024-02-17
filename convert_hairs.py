#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys, shutil
import convert_pc_common

if __name__ == '__main__':
    file_lists = []
    for i, raceGender in enumerate([ 'lf', 'lm', 'df', 'dm' ]):
        for j in range(1, 50):
            fmt = os.path.join('Objects', 'pc', '%s', 'mesh', '%s%03d_hair')
            src_map = {
                'cgf'    : (fmt % (raceGender, raceGender, j)) + '.cgf',
                'albedo' : (fmt % (raceGender, raceGender, j)) + '.dds',
                'ddn'    : (fmt % (raceGender, raceGender, j)) + '_ddn.dds',
                'illum'  : (fmt % (raceGender, raceGender, j)) + '_illum.dds',
                'mask'   : (fmt % (raceGender, raceGender, j)) + '_mask.dds',
                'sp'     : (fmt % (raceGender, raceGender, j)) + '_sp.dds',
            }
            fmt = os.path.join('Objects', 'pc', '%s', 'model', '%s_hairs', '%s%03d_hair')
            dst_map = {
                'cgf'    : (fmt % (raceGender, raceGender, raceGender, j)) + '.fbx',
                'albedo' : (fmt % (raceGender, raceGender, raceGender, j)) + '_albedo.png',
                'ddn'    : (fmt % (raceGender, raceGender, raceGender, j)) + '_ddn.png',
                'illum'  : (fmt % (raceGender, raceGender, raceGender, j)) + '_illum.png',
                'mask'   : (fmt % (raceGender, raceGender, raceGender, j)) + '_mask.png',
                'sp'     : (fmt % (raceGender, raceGender, raceGender, j)) + '_sp.png',
            }
            file_lists.append((src_map, dst_map))

    convert_pc(file_lists)
