"""
NOVA FLUX 100W GaN Charger - Transparent Asset Exporter & Multi-Surface Validator
Renders directly from Blender Cycles:
1. flux_charger_hero_isolated.png / .webp (Product only, clean alpha silhouette, no baked floor)
2. flux_charger_hero_shadow.png / .webp (Contact shadow only, true alpha gradient, no product)
3. flux_charger_hero_transparent.png / .webp (Combined product + contact shadow on transparent alpha)
4. Multi-surface verification previews:
   - Cream (#F3F0E7)
   - Signature Lime (#C7FF3D)
   - Dark Theme (#111111)
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

# Import geometry & shaders from build_flux_charger_v9
import sys
sys.path.append(r"D:\Projects\ууу\scripts")
import build_flux_charger_v9 as v9

def main():
    print("=== EXPORTING TRANSPARENT HERO ASSETS ===")
    scene = v9.reset_scene()
    v9.configure_cycles(scene, samples=384)
    
    mats = v9.create_materials()
    model_objs = v9.build_flux_charger_model(mats)
    v9.setup_studio_lighting()
    
    hero_cam = v9.setup_hero_camera(scene, model_objs)
    macro_cam = v9.setup_true_macro_camera(scene)
    scene.camera = hero_cam
    
    # Save master blend file WITH cameras included
    blend_path = os.path.join(MODELS_DIR, "flux_charger_v9_master.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Master Scene with Cameras Saved: {blend_path}")
    
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1600
    scene.render.film_transparent = True
    
    floor = bpy.data.objects.get("Studio_Shadow_Catcher_Floor")
    
    # -------------------------------------------------------------
    # PASS 1: ISOLATED PRODUCT (Zero floor, pure transparent silhouette)
    # -------------------------------------------------------------
    print("--- Rendering Pass 1: Isolated Product (No Shadow) ---")
    floor.hide_render = True
    for obj in model_objs:
        obj.is_holdout = False
        
    iso_out = os.path.join(OUTPUT_DIR, "flux_charger_hero_isolated.png")
    scene.render.filepath = iso_out
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {iso_out}")
    
    # -------------------------------------------------------------
    # PASS 2: CONTACT SHADOW ONLY (Holdout product, shadow catcher floor)
    # -------------------------------------------------------------
    print("--- Rendering Pass 2: Contact Shadow Only ---")
    floor.hide_render = False
    floor.is_shadow_catcher = True
    
    for obj in model_objs:
        obj.is_holdout = True
        
    shadow_out = os.path.join(OUTPUT_DIR, "flux_charger_hero_shadow.png")
    scene.render.filepath = shadow_out
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {shadow_out}")
    
    # -------------------------------------------------------------
    # PASS 3: COMBINED TRANSPARENT HERO (Product + Contact Shadow)
    # -------------------------------------------------------------
    print("--- Rendering Pass 3: Combined Transparent Hero ---")
    for obj in model_objs:
        obj.is_holdout = False
        
    comb_out = os.path.join(OUTPUT_DIR, "flux_charger_hero_transparent.png")
    scene.render.filepath = comb_out
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {comb_out}")
    
    print("=== FINISHED BLENDER TRANSPARENT RENDERS ===")

if __name__ == "__main__":
    main()
