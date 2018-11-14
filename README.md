# io\_scene\_cgf\_extras
Some extra python scripts for converting CGF file format to other file format, such as fbx, obj, etc.

### cgf2fbx.py

Converting CGF file format to fbx, including the Meshes, Armatures, Animations, Materials, etc.

Run the 'cgf2fbx.py' script via Blender executable as the python runtime.

```
blender -b --python cgf2fbx.py -- [CGF file]
```

use '--' seperate with command line argument, usage shows above.

```
blender -b --python cgf2fbx.py -- [-a|--anim] [CGF file]
```

Resolves the animations data and export to fbx, so the final fbx including the meshes, materials, animations, etc.

```
blender -b --python cgf2fbx.py -- --anim_only [CGF file]
```

Resolves the animations data and export to fbx, but doesn't export the meshes, just the animation data only.

### dds2png.py

Converting DDS file format to PNG.

'dds2png.py' require module PIL, use `pip install image`

Usage

```
dds2png.py [DDS files...]
```

Go on continue ...
