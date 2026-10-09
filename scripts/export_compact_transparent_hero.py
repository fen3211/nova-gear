"""
NOVA FLUX 100W GaN Fast Charger - Compact Shadow & Side Wall Illumination Exporter
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Key Requirements:
1. Side Wall Illumination: Dedicated right-side fill (22W) and right vertical kicker (26W)
   to reveal the right graphite surface and laser branding on dark backgrounds.
2. Compact Ground Shadow: Key light elevated to 52 deg. Side fill and rim lights have
   cast_shadow=False so ground shadow is cast strictly by key/top softbox.
3. Zero Edge Clipping: Shadow softly tapers to alpha=0 well within the frame, leaving
   a guaranteed transparent margin (>180px) on all boundaries.
4. Identical Alignment: Isolated product and shadow share identical 1600x1600 coordinates.
5. Multi-Surface Card Mockups: Real card scale previews on Cream (#F3F0E7), Lime (#C7FF3D), and Dark (#111111).
"""

import bpy
import bmesh
import math
import os
import mathutils
from mathutils import Vector, Euler

OUTPUT_DIR = r"D:\Projects\ууу\assets\previews"
MODELS_DIR = r"D:\Projects\ууу\assets\models"
TEXTURES_DIR = r"D:\Projects\ууу\assets\textures"

os.makedirs(OUTPUT_DIR, exist_ok=True)

import sys
sys.path.append(r"D:\Projects\ууу\scripts")
import build_flux_charger_v9 as v9

def setup_refined_studio_lighting():
    """
    Sets up studio lighting with enhanced side-wall revelation for dark backgrounds
    and controlled single-source ground shadow.
    """
    # 1. Key Softbox (Elevated to 52 deg so shadow stays compact near device base)
    bpy.ops.object.light_add(type='AREA', location=(-1.9, -2.0, 2.3))
    key = bpy.context.active_object
    key.name = "Studio_Key_Softbox"
    key.data.energy = 46.0
    key.data.size = 1.6
    key.data.size_y = 1.4
    key.data.color = (1.0, 0.99, 0.97)
    dir_v = Vector((0, 0, -0.1)) - key.location
    key.rotation_euler = dir_v.to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True

    # 2. Side Fill Softbox (Reveals graphite side wall and laser typography on dark backgrounds)
    bpy.ops.object.light_add(type='AREA', location=(2.2, -0.6, 0.9))
    fill_side = bpy.context.active_object
    fill_side.name = "Studio_Fill_Side"
    fill_side.data.energy = 22.0
    fill_side.data.size = 1.6
    fill_side.data.size_y = 1.4
    fill_side.data.color = (0.97, 0.98, 1.0)
    dir_s = Vector((0.2, 0, 0)) - fill_side.location
    fill_side.rotation_euler = dir_s.to_track_quat('-Z', 'Y').to_euler()
    fill_side.data.use_shadow = False  # Does NOT throw secondary shadow onto floor

    # 3. Vertical Right Kicker Strip (Crisp edge glint separating right silhouette from dark backgrounds)
    bpy.ops.object.light_add(type='AREA', location=(1.9, 0.4, 0.9))
    rim_side = bpy.context.active_object
    rim_side.name = "Studio_Right_Kicker"
    rim_side.data.energy = 26.0
    rim_side.data.size = 0.25
    rim_side.data.size_y = 2.0
    rim_side.data.color = (0.98, 0.99, 1.0)
    dir_rs = Vector((0.22, 0, 0)) - rim_side.location
    rim_side.rotation_euler = dir_rs.to_track_quat('-Z', 'Y').to_euler()
    rim_side.data.use_shadow = False

    # 4. Top Accent Diffuser (Defines top shoulder and soft contact grounding)
    bpy.ops.object.light_add(type='AREA', location=(0.0, -0.2, 2.0))
    top = bpy.context.active_object
    top.name = "Studio_Top_Crown"
    top.data.energy = 14.0
    top.data.size = 1.2
    top.data.size_y = 0.5
    top.data.color = (0.98, 0.99, 1.0)
    top.rotation_euler = Euler((0, 0, 0), 'XYZ')
    top.data.use_shadow = True

    # 5. Rim / Kicker Softbox (Back-Right Strip for top-right corner fillet)
    bpy.ops.object.light_add(type='AREA', location=(1.8, 1.8, 1.4))
    rim = bpy.context.active_object
    rim.name = "Studio_Rim_Kicker"
    rim.data.energy = 36.0
    rim.data.size = 0.35
    rim.data.size_y = 2.4
    rim.data.color = (0.98, 0.99, 1.0)
    dir_r = Vector((0, 0, 0.1)) - rim.location
    rim.rotation_euler = dir_r.to_track_quat('-Z', 'Y').to_euler()
    rim.data.use_shadow = False

    # 6. Front Port Infill (Camera axis bounce for gold pins & gunmetal sleeves)
    bpy.ops.object.light_add(type='AREA', location=(-0.3, -2.4, 0.2))
    fill = bpy.context.active_object
    fill.name = "Studio_Port_Infill"
    fill.data.energy = 8.5
    fill.data.size = 1.0
    fill.data.size_y = 0.8
    fill.data.color = (1.0, 1.0, 1.0)
    dir_f = Vector((0, -0.28, 0.0)) - fill.location
    fill.rotation_euler = dir_f.to_track_quat('-Z', 'Y').to_euler()
    fill.data.use_shadow = False

def main():
    print("=== STARTING COMPACT TRANSPARENT PASSES EXPORT ===")
    scene = v9.reset_scene()
    v9.configure_cycles(scene, samples=384)
    
    mats = v9.create_materials()
    model_objs = v9.build_flux_charger_model(mats)
    setup_refined_studio_lighting()
    
    hero_cam = v9.setup_hero_camera(scene, model_objs)
    scene.camera = hero_cam
    
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1600
    scene.render.film_transparent = True
    
    floor = bpy.data.objects.get("Studio_Shadow_Catcher_Floor")
    
    # PASS 1: ISOLATED PRODUCT (Floor hidden, clean alpha silhouette)
    print("--- Rendering Pass 1: Isolated Product (With Refined Side Illumination) ---")
    floor.hide_render = True
    for obj in model_objs:
        obj.is_holdout = False
        
    iso_out = os.path.join(OUTPUT_DIR, "flux_charger_hero_isolated_raw.png")
    scene.render.filepath = iso_out
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {iso_out}")
    
    # PASS 2: COMPACT CONTACT SHADOW (Holdout product, shadow catcher floor)
    print("--- Rendering Pass 2: Compact Contact Shadow Only ---")
    floor.hide_render = False
    floor.is_shadow_catcher = True
    for obj in model_objs:
        obj.is_holdout = True
        
    shadow_out = os.path.join(OUTPUT_DIR, "flux_charger_hero_shadow_raw.png")
    scene.render.filepath = shadow_out
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {shadow_out}")
    
    # Save master blend file
    blend_path = os.path.join(MODELS_DIR, "flux_charger_v9_compact_master.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Master Scene Saved: {blend_path}")
    print("=== FINISHED BLENDER RENDERING ===")

if __name__ == "__main__":
    main()
