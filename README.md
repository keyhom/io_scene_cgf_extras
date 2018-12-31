io\_scene\_cgf\_extras
===

## Intro

Some extra python scripts for converting CGF file format to other file format, such as fbx, obj, etc. The scripts is working in `AION`.

## Prerequisite

Particular scripts requires executing in the runtime environment on `Blender`.
Such as `cgf2fbx.py`, convert a __cgf/caf__ to __fbx__, `load_geomap.py` etc.

> Due to the python API on Blender 2.8, unsupported for now.

The kind of scripts was working on `Blender 2.79`, so should get work correctly on `Blender 2.6` too.

Execute as a command line in terminal, replace the default `python` runtime by the `Blender` binary executable.

Run in **Background** mode.

```bash
{blender_executable} -b --python {script} -- {script_arguments}
```

Or run the `script` in `Blender` 's `Console` directly, e.g.

```
# Blender 2.79b Python Console.

# defines the filename in the locals()
filename = {script_filename}
# Run the given script by exec mode.
exec(compile(open(filename).read(), filename, 'exec'))
```

Particular scripts has arguments required, so passing the *arguments* as the `variables` in the `locals` context, just define the the argument as the local variable will be work fine.

```
# Blender 2.79b Python Console.

# defines the arguments
cgf_file='/Volumes/assets/Objects/monster/mosbear/mosbear.cgf'
# defines the filename in the locals()
filename = ~/Projects/io_scene_cgf_extras/cgf2fbx.py
# Run the given script by exec mode.
exec(compile(open(filename).read(), filename, 'exec'))
```

More information about how to execute with `Blender`, see [Tips and Tricks in blender.org](https://docs.blender.org/api/current/info_tips_and_tricks.html#executing-external-scripts)
## Scripts

### cgf2fbx.py

Convert ___CGF/CAF___ file format to ___fbx___, including the **Meshes**, **Armatures**, **Animations**, **Materials**, etc.

#### Prerequisite

`blender` executable runtime enviroment required.

#### Usage

A simple commond for converting a given `cgf` file into `fbx`, no animation data exporting, just includes the `meshes` and the `materials`:

```
blender -b --python cgf2fbx.py -- [CGF file]
```

Resolves the animations data and export to fbx, so the final fbx including the meshes, materials, animations, etc.

```
blender -b --python cgf2fbx.py -- [-a|--anim] [CGF file]
```

Resolves the animations data and export to fbx, but doesn't export the meshes, just the animation data only.

```
blender -b --python cgf2fbx.py -- --anim_only [CGF file]
```

### dds2png.py

Convert file format `DDS` to `PNG`.

#### Prerequisite

`dds2png.py` require module `PIL`.

Install the `PIL` module via `pip`, following below:

On `python 2.x`:

```
pip install image
```

On `python 3.x`, choose `pillow` instead of `image`:

```
pip install pillow
```

#### Usage

```
dds2png.py [DDS files...]
```

The output files will generating at the same directory as input files.

### combine_tile.py

Combines `x` * `y` tiles image to a single image.

#### Prerequisite

The same as `dds2png.py`, this required `PIL` module as well. See [dds2png.py](#dds2png.py).

#### Usage

A simple example run in command-line combining *ZoneMap* from radar display:

```
combine_tile.py -x 256x256 -p radar_df1_%03d.dds -d /Volumes/assets/Textures/ui/zonemap/df1 -o DF1.png
```

### load_geomap.py

Load `terrain` data from `GEO` data into `Blender`.

#### Prerequisite

the `load_geomap.py` requires `blender` as the executable runtime, see [cgf2fbx.py](#cgf2fbx.py)

#### Usage

There're a example command-line for importing `GEO` mapdata into `blender`:

```
blender --python load_geomap.py -- -d /Volumes/Untitled/Resources/geo_data/models /Volumes/Untitled/Resources/geo_data/220010000.bin
```

When finished executing the `load_geomap.py`, will showing the `terrain` in the blender application.

### h322r16.py

A tool for converting `.h32` file format into `.r16` or `.raw`, make working correctly in `Unity`, `UE4`, `WorldMachine`, etc. The type of heightmap converted is setting to __unsigned 16bit little endian__.

#### Prerequisite

The same as `dds2png.py`, requires `PIL` module as well. see [dds2png.py](#dds2png.py)

#### Usage

A simple usage show at command-line mode:

```
h322r16.py [H32 files ...]
```

Specified `-o` to the `output` destination.

