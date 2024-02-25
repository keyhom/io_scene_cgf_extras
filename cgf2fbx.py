#!/usr/bin/env python

import os, sys, logging, optparse
import importlib

bpy_in_locale ='bpy' in locals()

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

    parser.add_option('-o', '--output-directory',
            type='string', action='store', dest='output_directory',
            )

    parser.add_option('-v', '--verbose',
            default=False, action='store_true'
            )

    parser.add_option('-n', '--no-output', default=False,
            action='store_true', dest='no_output', help='No any output instead.')

    parser.add_option('-s', '--save-temp',
            default=False, action='store_true', dest='save_temp')

    parser.add_option('-k', '--skeleton',
            default=None, type='string', action='store')

    (keywords, positional) = parser.parse_args(argv)

    # Force the render engine to CYCLES
    bpy.context.scene.render.engine = 'CYCLES'

    # Clear the scene first.
    if not bpy_in_locale:
        bpy.ops.object.select_all(action='SELECT') # select all object
        bpy.ops.object.delete() # delete all select objects.

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

    if bIncludeAnimations and sFilePath.endswith('.caf'): # Just a regular animation file, must be provided a skeleton to be driven.
        if keywords.skeleton is None:
            print('Need a skeleton specified by arguments!!')
            exit(1)
        else:
            bSkeletonLoad = True

    if keywords.verbose:
        print("Input file: %s" % sFilePath)
        print("Skeleton: %s" % keywords.skeleton)
        print("Output Directory: %s" % keywords.output_directory)
        print("Anim: %d" % keywords.anim)
        print("AnimOnly: %d" % keywords.anim_only)

    if bSkeletonLoad:
        if os.path.exists(keywords.skeleton) == False:
            print('Invalid skeleton file!!')
            exit(1)
        else:
            bpy.ops.import_scene.cgf(filepath=os.path.abspath(keywords.skeleton), import_animations=False)

    bpy.ops.import_scene.cgf(filepath=sFilePath, import_animations=bIncludeAnimations)

    if bpy_in_locale or keywords.no_output: # No export instead.
        return

    if keywords.output_directory:
        fbx_filepath = os.path.join(os.path.abspath(os.path.expanduser(keywords.output_directory)), \
                os.path.splitext(os.path.basename(sFilePath))[0].lower())
    else:
        fbx_filepath = os.path.splitext(sFilePath)[0].lower()

    output_dir = os.path.dirname(fbx_filepath)

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except:
            pass

    object_types = None

    if keywords.anim_only:
        fbx_filepath += '_animations.fbx'
        object_types = { 'ARMATURE' }
    else:
        fbx_filepath += '.fbx'
        if sFilePath.endswith('.caf'):
            object_types = { 'ARMATURE' }
        else:
            object_types = { 'ARMATURE', 'MESH' }

    # Imported
    # Exported the scene as FBX output.
    bpy.ops.export_scene.fbx(
            filepath=fbx_filepath,
            axis_forward = 'Z',
            axis_up = 'Y',
            bake_space_transform = True,
            object_types = object_types,
            use_mesh_modifiers = True,
            use_mesh_modifiers_render = True,
            add_leaf_bones = True,
            bake_anim = bIncludeAnimations,
            bake_anim_use_all_bones = False,
            bake_anim_use_nla_strips = True,
            bake_anim_use_all_actions = True,
            bake_anim_force_startend_keying = True,
            bake_anim_step = 1,
            bake_anim_simplify_factor = 1,
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

if __name__ == '__main__':
    run()

