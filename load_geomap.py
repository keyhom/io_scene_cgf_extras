#!/usr/bin/env python

from __future__ import print_function
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

name_resolves = {}

def parse_geoname(geo_name, game_dir):
    if game_dir is None or not os.path.exists(game_dir):
        return geo_name
    if geo_name.lower().startswith(b'terrain_models\\') or geo_name.lower().endswith(b'.bin'):
        return geo_name
    if not geo_name.lower().endswith(b'.cgf'):
        return geo_name

    if geo_name.lower().startswith(b'models\\'):
        geo_name = geo_name[7:]


    name = geo_name.lower()

    try:
        name = name.decode()
    except:
        pass

    if name in name_resolves:
        return name_resolves[name]

    def resolve_valid_path(folder, name):
        if name is None or len(name) == 0:
            return None

        folder = '' if folder is None else folder

        if os.path.exists(os.path.join(folder, name)):
            return None

        start_index = 0
        end_index = -1
        while True:
            try:
                idx = name.rindex('_', start_index, end_index)
                end_index = idx - 1
            except ValueError:
                idx = -1

            if idx != -1:
                if name[idx + 1] == ' ': # Ignore
                    continue

                str2find = name[:idx]
                if os.path.exists(os.path.join(folder, str2find)):
                    #  print('Found: %s + %s' % (str2find, name[idx + 1:]))
                    return (str2find, name[idx + 1:])
            else:
                break
        return None

    parent = game_dir
    child = name
    result = None

    while True:
        result = resolve_valid_path(parent, child)
        if result is not None:
            if parent is None:
                parent = result[0]
            else:
                parent = os.path.join(parent, result[0])
            child = result[1]
        else:
            break

    def fixed_basename(name):
        try:
            basename = os.path.basename(name)
            basename.index('__')
            if not os.path.exists(name):
                basename = basename.replace('__', '_ ')
            if os.path.exists(os.path.join(os.path.dirname(name), basename)):
                name = os.path.join(os.path.dirname(name), basename)
        except ValueError:
            pass

        if not os.path.exists(name):
            basename = os.path.basename(name)
            for filename in os.listdir(os.path.dirname(name)):
                if filename.replace('_', ' ').lower() == basename.replace('_', ' ').lower():
                    name = os.path.join(os.path.dirname(name), filename)
                    break
        return name

    result = name

    if parent is None:
        result = child
    else:
        result = os.path.join(parent, child)

    if not os.path.exists(result):
        result = fixed_basename(result)

    name_resolves[name] = result
    return result

dump_output = None

def read_map(map_file, resolve_name=False, game_dir=b'', terrain_only=False, dump=False):

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

        def dump2(content, end=os.linesep):
            global dump_output
            if dump:
                if dump_output is None:
                    dump_output = ''
                dump_output += "%s%c" % (content, end)
            else:
                print(content, end=end)

        if dump:
            # print header.
            dump2('Path', end='\t')
            dump2('Valid', end='\t')
            dump2('x', end='\t')
            dump2('y', end='\t')
            dump2('z', end='\t')
            dump2('m00', end='\t')
            dump2('m01', end='\t')
            dump2('m02', end='\t')
            dump2('m10', end='\t')
            dump2('m11', end='\t')
            dump2('m12', end='\t')
            dump2('m20', end='\t')
            dump2('m21', end='\t')
            dump2('m22', end='\t')
            dump2('unk')

        geo_lists = []

        for i in range(geo_count):
            name_len = unpack(mf, '<h')
            geo_name, x, y, z = unpack(mf, '<%ds3f' % name_len)
            #  logging.debug('Geometry Name: %s' % geo_name.decode())
            #  logging.debug('Geometry Local Axis: %.4f, %.4f, %.4f' % (x, y, z))
            m00, m01, m02, \
            m10, m11, m12, \
            m20, m21, m22 = unpack(mf, '<9f')
            unk, = unpack(mf, '<f') # unknown

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

            if terrain_only and not geo_name.startswith(b'terrain_models\\'):
                continue

            geo_lists.append((geo_name, x, y, z, m00, m01, m02, m10, m11, m12, m20, m21, m22))

            name = geo_name
            if resolve_name:
                if geo_name.lower().startswith(b'terrain_models\\') or \
                        geo_name.lower().endswith(b'.bin'):
                    continue

                name = parse_geoname(geo_name, game_dir)
                try:
                    name = name.decode()
                except:
                    pass

            if len(game_dir) and name.startswith(game_dir):
                name = os.path.relpath(name, game_dir)
                name = name[0].upper() + name[1:]

            if dump:
                dump2(name, end='\t')
                dump2(os.path.exists(os.path.join(game_dir, name)), end='\t')
                dump2(x, end='\t')
                dump2(y, end='\t')
                dump2(z, end='\t')
                dump2(m00, end='\t')
                dump2(m01, end='\t')
                dump2(m02, end='\t')
                dump2(m10, end='\t')
                dump2(m11, end='\t')
                dump2(m12, end='\t')
                dump2(m20, end='\t')
                dump2(m21, end='\t')
                dump2(m22, end='\t')
                dump2(unk)

        if dump_output is not None:
            with open(os.path.basename(os.path.splitext(map_file)[0]) + '.csv', 'w') as csv_file:
                csv_file.write(dump_output)

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

def load_map(map_file_path, models_dir=None, terrain_only=False):
    if not os.path.exists(map_file_path) or not os.path.isfile(map_file_path):
        print(sys.stderr, 'Non exists map file ...')
        return

    geo_list = read_map(map_file_path, terrain_only=terrain_only)
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
                ob.rotation_euler = mat.to_euler()
                # bpy.context.scene.collection.objects.link(ob)
                if bpy.data.collections.find('geo_collection_%d' % layer_idx) == -1:
                    bpy.data.collections.new('geo_collection_%d' % layer_idx)
                bpy.data.collections['geo_collection_%d' % layer_idx].objects.link(ob)
                # ob.layers[layer_idx] = True
                # ob.layers[0] = False
        else:
            logging.warning('Non exists geometry: %s' % geo_path)

    for i in range(len(name_groups)):
        bpy.context.scene.collection.children.link(bpy.data.collections['geo_collection_%d' % i])
    # bpy.context.scene.update()

    # for k in bpy.data.screens.keys():
    #     bpy.data.screens[k].

def clear_all_data():
    for k in bpy.data.objects.values():
        bpy.data.objects.remove(k)

    for k in bpy.data.meshes.values():
        bpy.data.meshes.remove(k)

    for k in bpy.data.collections.values():
        bpy.data.collections.remove(k)

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

    parser.add_option('--game-dir', action='store', type='string', default='',
            dest='game_dir', help='Specified the game working directory, usage for searching files.')

    parser.add_option('--resolve-name', action='store_true', default=True,
            dest='resolve_name', help='Specified to resolve the asset path by geoname.')

    parser.add_option('--terrain-only', action='store_true', default=False,
            dest='terrain_only', help='Specified to resolve the terrain data only.')

    parser.add_option('--csv', action='store_true', default=False)

    parser.add_option('-d', '--geometry-dir',
            action='store', type='string', dest='geometry_dir',
            help='Specified the geometry searching directory.')

    keywords, positional = parser.parse_args(argv)

    if len(positional) == 0:
        parser.print_help()
        return

    if keywords.verbose:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.ERROR)

    logging.debug('Geometry Dir: %s' % keywords.geometry_dir)
    logging.debug('Map file: %s' % positional[0])

    return (keywords, positional)

def run_in_blender(argv=None, clean=False):
    if not argv:
        try:
            idx = sys.argv.index('--')
        except:
            idx = -1
        if idx > -1:
            argv = sys.argv[idx+1:]
    else:
        argv = []

    keywords, positional = parse_arguments(argv)

    if clean:
        clear_all_data()

    load_map(positional[0], keywords.geometry_dir, keywords.terrain_only)

def run(argv=None):
    keywords, positional = parse_arguments(argv)

    logging.debug('Run script for processing now on ...')

    for i, input_file in enumerate(positional):
        if not os.path.exists(os.path.abspath(input_file)):
            logging.warning("Non exist input file: %s" % input_file)
            continue

        read_map(os.path.abspath(input_file), keywords.resolve_name, keywords.game_dir, keywords.terrain_only, keywords.csv)

    logging.debug('Done!')

if __name__ == '__main__':
    if bpy_in:
        run_in_blender(clean=True)
    else:
        run()

