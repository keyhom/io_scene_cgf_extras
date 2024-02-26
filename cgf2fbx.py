#!/usr/bin/env python

import os
import shutil
import sys
import logging
import optparse
import importlib
import re

bpy_in_locale = 'bpy' in locals()

if not bpy_in_locale:
    try:
        importlib.import_module('bpy')
        bpy_in = True
    except:
        bpy_in = False
else:
    bpy_in = True

if bpy_in:
    import bpy
    import bpy_extras
    import mathutils

try:
    curdir = os.path.abspath(os.path.dirname(__file__))
except:
    curdir = ''

def get_output_path(src_path, src_dir, dest_dir, follow=False, resolve_collapse_name=False):
    src_path = os.path.normpath(src_path)
    src_dir = os.path.normpath(src_dir)
    dest_dir = os.path.normpath(dest_dir)

    print(f'src_path: {src_path}')
    print(f'src_dir: {src_dir}')
    print(f'dest_dir: {dest_dir}')

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

        print(f'relpath: {path}')

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
    if argv is None:
        idx = 1
        for i, v in enumerate(sys.argv):
            if v == '--':
                idx = i
                break

        argv = sys.argv[idx+1:]

    parser = optparse.OptionParser()
    parser.add_option('-a', '--anim',
                      default=False,
                      action='store_true')

    parser.add_option('--anim_only',
                      default=False,
                      action='store_true')

    parser.add_option('-d', '--directory',
                      default='',
                      dest='directory', type='string', action='store')

    parser.add_option('-o', '--output-directory',
                      type='string', action='store', dest='output_directory',
                      )

    parser.add_option('--keep-structure',
                      default=False, dest='keep_structure', action='store_true')

    parser.add_option('-v', '--verbose',
                      default=False, action='store_true'
                      )

    parser.add_option('-n', '--no-output', default=False,
                      action='store_true', dest='no_output', help='No any output instead.')

    parser.add_option('-s', '--save-temp',
                      default=False, action='store_true', dest='save_temp')

    parser.add_option('-k', '--skeleton',
                      default=None, type='string', action='store')

    parser.add_option('--copy-textures', dest='copy_textures', default=False,
                      action='store_true', help='Copy the material textures to the output directory')

    (keywords, positional) = parser.parse_args(argv)

    # Force the render engine to CYCLES
    # bpy.context.scene.render.engine = 'CYCLES'

    # Clear the scene first.
    if not bpy_in_locale:
        bpy.ops.object.select_all(action='SELECT')  # select all object
        bpy.ops.object.delete()  # delete all select objects.

    if bpy_in_locale:
        sFilePath = cgf_file
    else:
        sFilePath = positional[0] if len(positional) > 0 else None

    if sFilePath is None:
        print('No input files specified.')
        return

    if sFilePath.endswith('.caf'):
        keywords.anim = True

    bIncludeAnimations = keywords.anim
    bSkeletonLoad = False
    bSaveTemp = keywords.save_temp

    # Just a regular animation file, must be provided a skeleton to be driven.
    if bIncludeAnimations and sFilePath.endswith('.caf'):
        if keywords.skeleton is None:
            print('Need a skeleton specified by arguments!!')
            exit(1)
        else:
            bSkeletonLoad = True

    if keywords.directory:
        keywords.directory = os.path.normpath(keywords.directory)

    if keywords.output_directory:
        keywords.output_directory = os.path.normpath(keywords.output_directory)

    if keywords.verbose:
        print("Input file: %s" % sFilePath)
        print("Skeleton: %s" % keywords.skeleton)
        print("Input Directory: %s" % keywords.directory)
        print("Output Directory: %s" % keywords.output_directory)
        print("Keep Structure: %d" % keywords.keep_structure)
        print("Anim: %d" % keywords.anim)
        print("AnimOnly: %d" % keywords.anim_only)
        print("Copy Textures: %d" % keywords.copy_textures)

    if bSkeletonLoad:
        if os.path.exists(keywords.skeleton) == False:
            print('Invalid skeleton file!!')
            exit(1)
        else:
            bpy.ops.import_scene.cgf(filepath=os.path.abspath(
                keywords.skeleton), import_animations=False)

    bpy.ops.import_scene.cgf(filepath=sFilePath, import_animations=bIncludeAnimations,
                             convert_dds_to_png=True, reuse_materials=True, reuse_images=True)

    if bpy_in_locale or keywords.no_output:  # No export instead.
        return

    if keywords.output_directory:
        sFilePath = os.path.normpath(sFilePath)
        print(f'NormPath for sFilePath: {sFilePath}')
        fbx_filepath = get_output_path(sFilePath, keywords.directory, keywords.output_directory, keywords.keep_structure)
        # fbx_filepath = os.path.join(os.path.abspath(os.path.expanduser(keywords.output_directory)),
                                    # os.path.splitext(os.path.basename(sFilePath))[0].lower())
    fbx_filepath = os.path.splitext(fbx_filepath)[0]

    output_dir = os.path.dirname(fbx_filepath)

    # lower the basename by default.
    fbx_filepath = os.path.normpath(os.path.join(output_dir, os.path.basename(fbx_filepath).lower()))

    print(f'fbx_filepath: {fbx_filepath}')

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except:
            pass

    object_types = None

    if keywords.anim_only:
        fbx_filepath += '_animations.fbx'
        object_types = {'ARMATURE'}
    else:
        fbx_filepath += '.fbx'
        if sFilePath.endswith('.caf'):
            object_types = {'ARMATURE'}
        else:
            object_types = {'ARMATURE', 'MESH'}

    # Imported
    # Exported the scene as FBX output.
    bpy.ops.export_scene.fbx(
        filepath=fbx_filepath,
        axis_forward='Z',
        axis_up='Y',
        bake_space_transform=True,
        object_types=object_types,
        use_mesh_modifiers=True,
        use_mesh_modifiers_render=True,
        add_leaf_bones=True,
        bake_anim=bIncludeAnimations,
        bake_anim_use_all_bones=False,
        bake_anim_use_nla_strips=True,
        bake_anim_use_all_actions=True,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1,
        bake_anim_simplify_factor=1,
        # use_anim = True,
        # use_anim_action_all = True,
        # use_default_take = True,
        # use_anim_optimize = True,
        # anim_optimize_precision = 6,
    )

    if bSaveTemp:
        savetemp_file = os.path.splitext(fbx_filepath)[0] + '.blend'
        print('Save as temp blend: %s' % savetemp_file)
        bpy.ops.wm.save_as_mainfile(filepath=savetemp_file)

    if keywords.copy_textures is True:
        '''
        Copy the materials texture to the destination, keep the texture's raw tree structure.
        '''
        for im in bpy.data.images:
            if im.source == 'FILE' and im.type == 'IMAGE' and len(im.filepath_raw) > 0:
                filepath_raw = os.path.normpath(im.filepath_raw)
                print(f'[{im.name}] ({im.source}) {filepath_raw}')
                dir_path = None
                if keywords.directory:
                    if filepath_raw.lower().startswith(keywords.directory.lower()):
                        rel_path = filepath_raw[len(keywords.directory):]
                        while rel_path.startswith(os.path.sep):
                            rel_path = rel_path[1:]
                        if keywords.output_directory:
                            dir_path = os.path.join(
                                keywords.output_directory, os.path.dirname(rel_path))
                        else:
                            dir_path = output_dir
                else:
                    dir_path = output_dir

                os.makedirs(dir_path, exist_ok=True)
                filepath_target = os.path.join(dir_path, os.path.basename(filepath_raw))
                print(f'Copy the src "{filepath_raw}" to the dest "{filepath_target}"')
                try:
                    shutil.copy2(filepath_raw, filepath_target)
                    print(f'Successfully copied and overwrote {filepath_raw} to {filepath_target}')
                except FileNotFoundError:
                    print(f'Error: The source file {filepath_raw} does not exist.')
                except Exception as e:
                    print(f'Error: {e}')


if __name__ == '__main__':
    run()
