#!/bin/bash

$BATCH_SCRIPT -b $BLENDER -d $GAME_ASSET_DIR -k -j$JOIN -o $OUTPUT_DIR --skeleton=$GAME_ASSET_DIR/Objects/pc/lf/mesh/lf.cgf $OUTPUT_DIR/lf_animations_mini.lst
$BATCH_SCRIPT -b $BLENDER -d $GAME_ASSET_DIR -k -j$JOIN -o $OUTPUT_DIR --skeleton=$GAME_ASSET_DIR/Objects/pc/lm/mesh/lm.cgf $OUTPUT_DIR/lm_animations_mini.lst
$BATCH_SCRIPT -b $BLENDER -d $GAME_ASSET_DIR -k -j$JOIN -o $OUTPUT_DIR --skeleton=$GAME_ASSET_DIR/Objects/pc/df/mesh/df.cgf $OUTPUT_DIR/df_animations_mini.lst
$BATCH_SCRIPT -b $BLENDER -d $GAME_ASSET_DIR -k -j$JOIN -o $OUTPUT_DIR --skeleton=$GAME_ASSET_DIR/Objects/pc/dm/mesh/dm.cgf $OUTPUT_DIR/dm_animations_mini.lst

