import os, sys, logging, optparse
import bpy
import bpy.props
import bpy_extras
import mathutils

from mathutils import Vector, Matrix
from bpy.props import(
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        CollectionProperty,
        )

from bpy_extras.io_utils import (
        ImportHelper,
        orientation_helper_factory,
        path_reference_mode,
        axis_conversion,
        _check_axis_conversion
        )

curdir = os.path.abspath(os.path.dirname(__file__))

def setup_env():
    sys.path.append(os.path.expanduser('~/Projects/github/pyffi/build/lib'))
    sys.path.append(os.path.abspath(os.path.join(curdir, '..', 'io_scene_cgf')))
    import import_cgf
    filename = os.path.abspath(os.path.join(curdir, '..', 'io_scene_cgf', '__init__.py'))
    exec(compile(open(filename, 'rb').read(), filename, 'exec'))

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

    #  print('System argv: ')
    #  print(argv)

    (keywords, positional) = parser.parse_args(argv)

    # setup_env()

    # Force the render engine to CYCLES
    bpy.context.scene.render.engine = 'CYCLES'

    # Clear the scene first.
    bpy.ops.object.select_all(action='SELECT') # select all object
    bpy.ops.object.delete() # delete all select objects.

    #  sFilePath = '/Users/jeremy/Projects/aion_assets/Objects/monster/phiviyong/phiviyong.cgf'
    sFilePath = positional[0] if len(positional) > 0 else None
    bIncludeAnimations = keywords.anim

    if sFilePath is None:
        return

    bpy.ops.import_scene.cgf(filepath=sFilePath, import_animations=bIncludeAnimations)

    fbx_filepath = os.path.splitext(sFilePath)[0]
    object_types = None

    if keywords.anim_only:
        fbx_filepath += '_animations.fbx'
        object_types = { 'ARMATURE' }
    else:
        fbx_filepath += '.fbx'
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
            add_leaf_bones = False,
            bake_anim = bIncludeAnimations,
            bake_anim_use_all_bones = False,
            bake_anim_use_nla_strips = False,
            bake_anim_use_all_actions = True,
            bake_anim_force_startend_keying = False,
            bake_anim_step = 1,
            bake_anim_simplify_factor = 0,
            use_anim = True,
            use_anim_action_all = True,
            use_default_take = True,
            use_anim_optimize = True,
            anim_optimize_precision = 6,
        )

if __name__ == '__main__':
    run()

