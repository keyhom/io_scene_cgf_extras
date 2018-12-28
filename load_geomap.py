#!/usr/bin/env python

import os, sys, optparse, logging, struct
import importlib

bpy_in='bpy' in locals()

if not bpy_in:
    try:
        importlib.import_module('bpy')
        bpy_in=True
    except:
        # Non bpy module, so run this script by standalone, not run in blender.
        bpy_in=False
        pass

if bpy_in:
    import bpy
    import bpy_extras
    import mathutils

try:
    __rootpath__ = os.path.abspath(os.path.dirname(__file__))
except:
    __rootpath__ = ''

def unpack(fio, fmt):
    return struct.unpack(fmt, fio.read(struct.calcsize(fmt)))

def read_map(map_file):
    with open(map_file, 'rb') as mf:
        mf.seek(0, 2)
        bufsize = mf.tell()
        mf.seek(0, 0)

        logging.debug('========================================')
        logging.debug('Map File: %s' % os.path.basename(map_file))
        logging.debug("File Size: %i" % bufsize)
        logging.debug('========================================')

        geo_count, = unpack(mf, '<i')
        logging.debug('Geometry Count: %i' % geo_count)

        min_x = None
        min_y = None
        min_z = None
        max_x = None
        max_y = None
        max_z = None

        geo_lists = []

        for i in range(geo_count):
            name_len = unpack(mf, '<h')
            name, x, y, z = unpack(mf, '<%ds3f' % name_len)
            #  logging.debug('Geometry Name: %s' % name.decode())
            #  logging.debug('Geometry Local Axis: %.4f, %.4f, %.4f' % (x, y, z))
            m00, m01, m02, \
            m10, m11, m12, \
            m20, m21, m22 = unpack(mf, '<9f')
            _, = unpack(mf, '<i') # unknown
            if min_x is None: min_x = x
            if min_y is None: min_y = y
            if min_z is None: min_z = z
            if max_x is None: max_x = x
            if max_y is None: max_y = y
            if max_z is None: max_z = z

            min_x = min(x, min_x)
            min_y = min(y, min_y)
            min_z = min(z, min_z)
            max_x = max(x, max_x)
            max_y = max(y, max_y)
            max_z = max(z, max_z)

            geo_lists.append((name, x, y, z, m00, m01, m02, m10, m11, m12, m20, m21, m22))

        logging.debug('minXYZ: %.4f, %.4f, %.4f' % (min_x, min_y, min_z))
        logging.debug('maxXYZ: %.4f, %.4f, %.4f' % (max_x, max_y, max_z))
        return geo_lists
    return []

def read_geometry(geo_file):
    with open(geo_file, 'rb') as gf:
        gf.seek(0, 2)
        bufsize = gf.tell()
        gf.seek(0, 0)

        logging.debug('========================================')
        logging.debug('Geometry File: %s' % os.path.basename(geo_file))
        logging.debug("File Size: %i" % bufsize)
        logging.debug('========================================')

        verts = []
        indexes = []

        model_name, model_type, vert_count = unpack(gf, '<256s2i')
        for i in range(vert_count):
            x, y, z = unpack(gf, '<3f')
            verts.append((x, y, z))

        triangle_cnt, = unpack(gf, '<i')
        for i in range(triangle_cnt):
            i1, i2, i3 = unpack(gf, '<3H')
            indexes.append((i1, i2, i3))

        logging.debug("Vertex count: %i" % len(verts))
        logging.debug('Triangle count: %i' % len(indexes))

        assert gf.tell() == bufsize, "There're remaining buffer instead."
        return (verts, indexes)
    return (None, None)

model_names = []

def load_terrain_mesh(name, models_dir=None):
    me = bpy.data.meshes.get(name)
    if me:
        return me

    verts, indexes = read_geometry(os.path.join(models_dir, name))
    if verts and indexes:
        # New mesh
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], indexes)
        me.validate()
        me.update()
        return me
    return None

def load_models(models_dir):
    assert os.path.exists(models_dir)
    model_names = os.listdir(models_dir)
    for mf_name in model_names:
        load_terrain_mesh(mf_name, models_dir)

def load_map(map_file_path, models_dir=None):
    if not os.path.exists(map_file_path) or not os.path.isfile(map_file_path):
        print(stderr, 'Non exists map file ...')
        return

    geo_list = read_map(map_file_path)
    name_groups = []

    for geo in geo_list:
        geo_name, x, y, z, \
        m00, m01, m02, \
        m10, m11, m12, \
        m20, m21, m22 = geo
        mat = mathutils.Matrix(((m00, m01, m02), (m10, m11, m12), (m20, m21, m22))).transposed()
        geo_name = geo_name.decode()
        geo_name = geo_name.replace('\\', os.path.sep)
        geo_path = os.path.join(models_dir, os.path.basename(geo_name))

        if os.path.exists(geo_path):
            me = load_terrain_mesh(os.path.basename(geo_name), models_dir)
            if me:
                name_prefix = me.name.split('_', 1)[0].lower()
                layer_idx = 0
                if name_prefix not in name_groups:
                    name_groups.append(name_prefix)
                layer_idx = name_groups.index(name_prefix)
                ob = bpy.data.objects.new(me.name, me)
                ob.location = (x, y, z)
                ob.rotation_quaternion = mat.to_quaternion()
                bpy.context.scene.objects.link(ob)
                ob.layers[layer_idx] = True
                ob.layers[0] = False
        else:
            logging.warning('Non exists geometry: %s' % geo_path)

    for i in range(len(name_groups)):
        bpy.context.scene.layers[i] = True
    bpy.context.scene.update()

def clear_all_data():
    for k in bpy.data.objects.values():
        bpy.data.objects.remove(k)

    for k in bpy.data.meshes.values():
        bpy.data.meshes.remove(k)

def parse_arguments(argv):
    if not argv:
        argv = sys.argv[1:]

    parser = optparse.OptionParser(
            usage='%prog [OPTIONS] files ...',
            )

    parser.add_option('-v', '--verbose',
            default=False,
            action='store_true',
            help=('Verbose logging trace'))

    #  parser.add_option('-m', '--map',
            #  default=False,
            #  action='store_true',
            #  help='Specified the input file is a map.')

    #  parser.add_option('-g', '--geometry',
            #  default=False,
            #  action='store_true',
            #  help='Specified the input file is a geometry.')

    parser.add_option('-d', '--geometry-dir',
            action='store', type='string', dest='geometry_dir',
            help='Specified the geometry searching directory.')

    keywords, positional = parser.parse_args(argv)

    if len(positional) == 0:
        parser.print_help()
        return

    #  if not keywords.map and not keywords.geometry:
        #  parser.print_help()
        #  return

    if keywords.verbose:
        logging.root.setLevel(logging.DEBUG)

    logging.debug('Geometry Dir: %s' % keywords.geometry_dir)
    logging.debug('Map file: %s' % positional[0])

    return (keywords, positional)

def run_in_blender(argv=None, clean=False):
    if not argv:
        idx = sys.argv.index('--')
        if idx > -1:
            argv = sys.argv[idx+1:]

    keywords, positional = parse_arguments(argv)

    if clean:
        clear_all_data()

    load_map(positional[0], keywords.geometry_dir)

def run(argv=None):
    keywords, positional = parse_arguments(argv)

    logging.debug('Run script for processing now on ...')

    for i, input_file in enumerate(positional):
        if not os.path.exists(os.path.abspath(input_file)):
            logging.warning("Non exist input file: %s" % input_file)
            continue

        read_map(os.path.abspath(input_file))
        #  if keywords.map:
            #  read_map(os.path.abspath(input_file))
        #  elif keywords.geometry:
            #  read_geometry(os.path.abspath(input_file))

    logging.debug('Done!')

if __name__ == '__main__':
    if bpy_in:
        run_in_blender(clean=True)
    else:
        run()

