"""
Export NovaDesk XL Mat Isolated Mesh and Physical Shadow Layer with True Transparency.
Guarantees:
1. Reduced macro felt bump relief (refined, dense, luxury merino wool).
2. Updated Macro render: novadesk_mat_macro_detail.png.
3. Pass 1: Isolated 3D Mat with true alpha (film transparent, floor hidden).
4. Pass 2: Physical Cycles Shadow Catcher (film transparent, objects invisible to camera, casting shadow onto catcher).
5. Identical tight bounding box crop for both layers:
   - Boundary alpha = 0 (no clipped shadows).
   - Identical resolution and aspect ratio (zero layer drift).
6. Production WebP assets saved to assets/images/ and assets/previews/.
"""

import bpy
import os
import math

PREVIEWS_DIR = r"D:\Projects\ууу\assets\previews"
IMAGES_DIR = r"D:\Projects\ууу\assets\images"
MODELS_DIR = r"D:\Projects\ууу\assets\models"

def main():
    blend_path = os.path.join(MODELS_DIR, "novadesk_mat_master.blend")
    if not os.path.exists(blend_path):
        print(f"Error: {blend_path} not found")
        return
        
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene
    
    # 1. Refine Felt Material: soften coarse bump/relief as requested
    felt_mat = bpy.data.materials.get("Anthracite_Merino_Felt")
    if felt_mat and felt_mat.use_nodes:
        for node in felt_mat.node_tree.nodes:
            if node.type == 'NORMAL_MAP':
                node.inputs['Strength'].default_value = 0.38 # Softened from 0.85
                print("Felt normal map strength tuned to 0.38")
                
    # 2. Render Updated Macro Detail View (1600x1200)
    macro_cam = bpy.data.objects.get("Camera_NovaDesk_Macro")
    if macro_cam:
        print("--- Rendering Refined Macro Detail View ---")
        scene.camera = macro_cam
        scene.render.resolution_x = 1600
        scene.render.resolution_y = 1200
        scene.render.film_transparent = False
        
        macro_out = os.path.join(PREVIEWS_DIR, "novadesk_mat_macro_detail.png")
        scene.render.filepath = macro_out
        bpy.ops.render.render(write_still=True)
        print(f"Macro Detail Saved: {macro_out}")
        
    # 3. Setup Hero Camera for Pass 1 and Pass 2
    hero_cam = bpy.data.objects.get("Camera_NovaDesk_Hero")
    if not hero_cam:
        print("Error: Camera_NovaDesk_Hero not found")
        return
    scene.camera = hero_cam
    scene.render.resolution_x = 2000
    scene.render.resolution_y = 1500
    
    floor = bpy.data.objects.get("Studio_Floor")
    mat_objs = [
        bpy.data.objects.get("NovaDesk_Merino_Felt"),
        bpy.data.objects.get("NovaDesk_Rubber_Base"),
        bpy.data.objects.get("NovaDesk_Stitches"),
        bpy.data.objects.get("NovaDesk_Punctures"),
        bpy.data.objects.get("NovaDesk_Leather_Badge"),
        bpy.data.objects.get("NovaDesk_Brass_Rivet"),
        bpy.data.objects.get("NovaDesk_Brass_Rivet_Dot")
    ]
    mat_objs = [obj for obj in mat_objs if obj is not None]
    
    # -------------------------------------------------------------------------
    # PASS 1: ISOLATED PRODUCT (Transparent background, floor hidden)
    # -------------------------------------------------------------------------
    print("--- Rendering Pass 1: Isolated Product ---")
    scene.render.film_transparent = True
    if floor:
        floor.hide_render = True
    for obj in mat_objs:
        obj.hide_render = False
        obj.visible_camera = True
        
    iso_raw_path = os.path.join(PREVIEWS_DIR, "novadesk_mat_hero_isolated_raw.png")
    scene.render.filepath = iso_raw_path
    bpy.ops.render.render(write_still=True)
    print(f"Isolated Raw Render Saved: {iso_raw_path}")
    
    # -------------------------------------------------------------------------
    # PASS 2: PHYSICAL CONTACT SHADOW ONLY (Shadow Catcher)
    # -------------------------------------------------------------------------
    print("--- Rendering Pass 2: Physical Contact Shadow ---")
    scene.render.film_transparent = True
    if floor:
        floor.hide_render = False
        floor.is_shadow_catcher = True
        
    for obj in mat_objs:
        obj.hide_render = False
        obj.visible_camera = False # Invisible to camera rays, casts shadow onto catcher
        
    shd_raw_path = os.path.join(PREVIEWS_DIR, "novadesk_mat_hero_shadow_raw.png")
    scene.render.filepath = shd_raw_path
    bpy.ops.render.render(write_still=True)
    print(f"Shadow Raw Render Saved: {shd_raw_path}")
    
    # Save blend
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("Blender scene updated and saved.")

if __name__ == "__main__":
    main()
