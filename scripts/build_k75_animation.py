"""
NOVA KEYS K75 // Master Photorealistic Assembly / Disassembly Animation Suite
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Animation Architecture:
- 144 Frames @ 24 fps (Exact 6.00s seamless loop)
- Motion sequence:
  * Frames 1..12:   Hold exploded state (0.5s pause)
  * Frames 13..68:  Assembly from bottom to top with progressive overlap (2.3s)
                    - PVD brass weight inserts into bottom chassis
                    - Silicone dampener drops in
                    - ENIG PCB seats onto silicone
                    - Poron foam seats onto PCB
                    - FR4 switch plate seats onto gasket tabs
                    - Switches drop and click into plate
                    - Rotary knob drops onto encoder shaft
                    - Keycaps descend in an elegant row-by-row cascade wave (R5 -> R4 -> R3 -> R2 -> R1 -> R0)
  * Frames 69..92:  Hold fully assembled state (1.0s pause)
  * Frames 93..136: Disassembly back up in reverse cascade order (1.8s)
                    - Keycaps lift in reverse wave (R0 -> R1 -> ... -> R5)
                    - Switches & knob lift
                    - Plate, foam, PCB, silicone lift
                    - Brass weight lowers
  * Frames 137..144: Brief hold in exploded state (0.3s pause) matching Frame 1 perfectly!
- Smooth Bezier deceleration with zero rubbery bouncing or collision.
- Fixed camera framing entire exploded assembly with >=18% margins.
- Film transparent for native e-commerce alpha channel.
- Saves master .blend file to assets/scenes/k75_animation.blend.
"""

import bpy
import bmesh
import math
import os
import sys
import json
import mathutils
from mathutils import Vector, Euler, Matrix

OUTPUT_DIR = r"D:\Projects\ууу\assets\previews"
SCENES_DIR = r"D:\Projects\ууу\assets\scenes"
IMAGES_DIR = r"D:\Projects\ууу\assets\images"
TEXTURES_DIR = r"D:\Projects\ууу\assets\textures"
FRAMES_DIR = r"D:\Projects\ууу\assets\frames_k75"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCENES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Studio_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.88, 0.86, 0.82, 1.0)
        bg.inputs['Strength'].default_value = 0.85
    return scene

def configure_cycles(scene, samples=128):
    scene.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for dev in prefs.devices:
        if dev.type == 'OPTIX':
            dev.use = True
        else:
            dev.use = False
    scene.cycles.device = 'GPU'
    scene.cycles.samples = samples
    scene.cycles.preview_samples = 32
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    scene.cycles.max_bounces = 8
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 4
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'

def create_materials():
    mats = {}
    
    # 1. CNC Anodized Aluminum (Space Grey #121316)
    m_alu = bpy.data.materials.new("Chassis_Alu_6063")
    m_alu.use_nodes = True
    nodes = m_alu.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.09, 0.10, 0.11, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.22
    if 'Anisotropic' in bsdf.inputs:
        bsdf.inputs['Anisotropic'].default_value = 0.20
    t_noise = nodes.new('ShaderNodeTexNoise')
    t_noise.inputs['Scale'].default_value = 1400.0
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.005
    m_alu.node_tree.links.new(t_noise.outputs['Fac'], bump.inputs['Height'])
    m_alu.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    m_alu.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['alu'] = m_alu

    # 2. Mirror PVD Brass Weight Bar (#C5A059)
    m_brass = bpy.data.materials.new("PVD_Brass_Mirror")
    m_brass.use_nodes = True
    bsdf_b = m_brass.node_tree.nodes.get("Principled BSDF")
    bsdf_b.inputs['Base Color'].default_value = (0.92, 0.78, 0.42, 1.0)
    bsdf_b.inputs['Metallic'].default_value = 1.0
    bsdf_b.inputs['Roughness'].default_value = 0.08
    mats['brass'] = m_brass

    # 3. ENIG Gold Traces & Accents
    m_gold = bpy.data.materials.new("ENIG_Gold")
    m_gold.use_nodes = True
    bsdf_g = m_gold.node_tree.nodes.get("Principled BSDF")
    bsdf_g.inputs['Base Color'].default_value = (0.95, 0.82, 0.38, 1.0)
    bsdf_g.inputs['Metallic'].default_value = 1.0
    bsdf_g.inputs['Roughness'].default_value = 0.14
    mats['gold'] = m_gold

    # 4. Matte Black FR4 PCB
    m_pcb = bpy.data.materials.new("FR4_PCB_MatteBlack")
    m_pcb.use_nodes = True
    bsdf_p = m_pcb.node_tree.nodes.get("Principled BSDF")
    bsdf_p.inputs['Base Color'].default_value = (0.04, 0.045, 0.05, 1.0)
    bsdf_p.inputs['Roughness'].default_value = 0.45
    mats['pcb'] = m_pcb

    # 5. Acoustic Poron Foam
    m_foam = bpy.data.materials.new("Poron_Foam")
    m_foam.use_nodes = True
    bsdf_f = m_foam.node_tree.nodes.get("Principled BSDF")
    bsdf_f.inputs['Base Color'].default_value = (0.07, 0.075, 0.08, 1.0)
    bsdf_f.inputs['Roughness'].default_value = 0.85
    mats['foam'] = m_foam

    # 6. Molded Silicone Dampener
    m_silicone = bpy.data.materials.new("Molded_Silicone")
    m_silicone.use_nodes = True
    bsdf_s = m_silicone.node_tree.nodes.get("Principled BSDF")
    bsdf_s.inputs['Base Color'].default_value = (0.24, 0.25, 0.28, 1.0)
    bsdf_s.inputs['Roughness'].default_value = 0.55
    mats['silicone'] = m_silicone

    # 7. Smoky Polycarbonate Switch Top Housing
    m_sw_pc = bpy.data.materials.new("Switch_Housing_Smoky_PC")
    m_sw_pc.use_nodes = True
    bsdf_sp = m_sw_pc.node_tree.nodes.get("Principled BSDF")
    bsdf_sp.inputs['Base Color'].default_value = (0.18, 0.20, 0.22, 1.0)
    bsdf_sp.inputs['Roughness'].default_value = 0.22
    if 'Transmission Weight' in bsdf_sp.inputs:
        bsdf_sp.inputs['Transmission Weight'].default_value = 0.65
    elif 'Transmission' in bsdf_sp.inputs:
        bsdf_sp.inputs['Transmission'].default_value = 0.65
    mats['sw_pc'] = m_sw_pc

    # 8. Acid Lime Switch Stem (POM #C7FF3D)
    m_sw_stem = bpy.data.materials.new("Switch_Stem_POM_Lime")
    m_sw_stem.use_nodes = True
    bsdf_ss = m_sw_stem.node_tree.nodes.get("Principled BSDF")
    bsdf_ss.inputs['Base Color'].default_value = (0.78, 1.0, 0.24, 1.0)
    bsdf_ss.inputs['Roughness'].default_value = 0.26
    mats['sw_stem'] = m_sw_stem

    # 9. Dark Nylon Switch Bottom Housing
    m_sw_bot = bpy.data.materials.new("Switch_Housing_Nylon_Dark")
    m_sw_bot.use_nodes = True
    bsdf_sb = m_sw_bot.node_tree.nodes.get("Principled BSDF")
    bsdf_sb.inputs['Base Color'].default_value = (0.05, 0.055, 0.06, 1.0)
    bsdf_sb.inputs['Roughness'].default_value = 0.40
    mats['sw_bot'] = m_sw_bot

    # 10. Switch Plate
    m_plate = bpy.data.materials.new("Switch_Plate_FR4")
    m_plate.use_nodes = True
    bsdf_pl = m_plate.node_tree.nodes.get("Principled BSDF")
    bsdf_pl.inputs['Base Color'].default_value = (0.11, 0.12, 0.13, 1.0)
    bsdf_pl.inputs['Roughness'].default_value = 0.32
    mats['plate'] = m_plate

    # 11. Stainless Steel Hardware
    m_steel = bpy.data.materials.new("Stainless_Steel")
    m_steel.use_nodes = True
    bsdf_st = m_steel.node_tree.nodes.get("Principled BSDF")
    bsdf_st.inputs['Base Color'].default_value = (0.85, 0.86, 0.88, 1.0)
    bsdf_st.inputs['Metallic'].default_value = 1.0
    bsdf_st.inputs['Roughness'].default_value = 0.15
    mats['steel'] = m_steel

    # 12. Keycap Atlas Textured Material
    atlas_png = os.path.join(TEXTURES_DIR, "keycap_atlas.png")
    m_keycap = bpy.data.materials.new("Keycap_PBT_Atlas")
    m_keycap.use_nodes = True
    knodes = m_keycap.node_tree.nodes
    knodes.clear()
    k_out = knodes.new('ShaderNodeOutputMaterial')
    k_bsdf = knodes.new('ShaderNodeBsdfPrincipled')
    k_bsdf.inputs['Roughness'].default_value = 0.35
    
    k_img = knodes.new('ShaderNodeTexImage')
    if os.path.exists(atlas_png):
        k_img.image = bpy.data.images.load(atlas_png)
        
    k_noise = knodes.new('ShaderNodeTexNoise')
    k_noise.inputs['Scale'].default_value = 800.0
    k_bump = knodes.new('ShaderNodeBump')
    k_bump.inputs['Strength'].default_value = 0.008
    
    m_keycap.node_tree.links.new(k_img.outputs['Color'], k_bsdf.inputs['Base Color'])
    m_keycap.node_tree.links.new(k_noise.outputs['Fac'], k_bump.inputs['Height'])
    m_keycap.node_tree.links.new(k_bump.outputs['Normal'], k_bsdf.inputs['Normal'])
    m_keycap.node_tree.links.new(k_bsdf.outputs['BSDF'], k_out.inputs['Surface'])
    mats['keycap'] = m_keycap

    return mats

def build_sculpted_cherry_keycap(name, key_w, key_d, row_idx, atlas_coords, mat_keycaps):
    mesh = bpy.data.meshes.new(f"Mesh_{name}")
    bm = bmesh.new()
    
    if row_idx in [5, 4]:
        h_front = 0.0098
        h_back = 0.0116
    elif row_idx == 3:
        h_front = 0.0088
        h_back = 0.0100
    elif row_idx == 2:
        h_front = 0.0082
        h_back = 0.0088
    else:
        h_front = 0.0090
        h_back = 0.0084
        
    kw = key_w
    kd = key_d
    tw = kw * 0.76
    td = kd * 0.76
    
    bv0 = bm.verts.new((-kw/2, -kd/2, 0.0))
    bv1 = bm.verts.new((kw/2, -kd/2, 0.0))
    bv2 = bm.verts.new((kw/2, kd/2, 0.0))
    bv3 = bm.verts.new((-kw/2, kd/2, 0.0))
    
    tv4 = bm.verts.new((-tw/2, -td/2, h_front))
    tv5 = bm.verts.new((tw/2, -td/2, h_front))
    tv6 = bm.verts.new((tw/2, td/2, h_back))
    tv7 = bm.verts.new((-tw/2, td/2, h_back))
    
    f_top = bm.faces.new((tv4, tv5, tv6, tv7))
    f_front = bm.faces.new((bv0, bv1, tv5, tv4))
    f_right = bm.faces.new((bv1, bv2, tv6, tv5))
    f_back = bm.faces.new((bv2, bv3, tv7, tv6))
    f_left = bm.faces.new((bv3, bv0, tv4, tv7))
    
    uv_layer = bm.loops.layers.uv.new('UVMap')
    u_min, u_max = atlas_coords['u_min'], atlas_coords['u_max']
    v_min, v_max = atlas_coords['v_min'], atlas_coords['v_max']
    
    top_uvs = [(u_min, v_min), (u_max, v_min), (u_max, v_max), (u_min, v_max)]
    for loop, uv in zip(f_top.loops, top_uvs):
        loop[uv_layer].uv = uv
        
    bg_uv = (u_min + 0.003, v_min + 0.003)
    for side_face in [f_front, f_right, f_back, f_left]:
        for loop in side_face.loops:
            loop[uv_layer].uv = bg_uv
            
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat_keycaps)
    
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.0006
    bev.segments = 2
    bpy.ops.object.shade_smooth()
    return obj

def build_switch_assembly(name, loc, mats, parent_obj):
    sw_objs = []
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(loc.x, loc.y, loc.z - 0.0025),
        scale=(0.014, 0.014, 0.005)
    )
    bot = bpy.context.active_object
    bot.name = f"Sw_Bot_{name}"
    bot.data.materials.append(mats['sw_bot'])
    bot_bev = bot.modifiers.new("Bevel", 'BEVEL')
    bot_bev.width = 0.0004
    bot_bev.segments = 2
    bpy.ops.object.shade_smooth()
    sw_objs.append(bot)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(loc.x, loc.y, loc.z + 0.0025),
        scale=(0.0138, 0.0138, 0.0052)
    )
    top = bpy.context.active_object
    top.name = f"Sw_Top_{name}"
    top.data.materials.append(mats['sw_pc'])
    top_bev = top.modifiers.new("Bevel", 'BEVEL')
    top_bev.width = 0.0005
    top_bev.segments = 2
    bpy.ops.object.shade_smooth()
    sw_objs.append(top)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(loc.x, loc.y, loc.z + 0.0055),
        scale=(0.0042, 0.0042, 0.0040)
    )
    stem = bpy.context.active_object
    stem.name = f"Sw_Stem_{name}"
    stem.data.materials.append(mats['sw_stem'])
    sw_objs.append(stem)
    
    for obj in sw_objs:
        obj.parent = parent_obj
    return sw_objs

# -----------------------------------------------------------------------------
# ANIMATION KEYFRAME UTILITY
# -----------------------------------------------------------------------------
def set_z_keyframes(obj, z_exp, z_asm, f_start_down, f_end_down, f_start_up, f_end_up, total_frames=144):
    """
    Sets smooth Bezier keyframes on obj.location.z:
    - Frames 1 .. f_start_down: z_exp
    - Frame f_end_down .. f_start_up: z_asm
    - Frame f_end_up .. total_frames: z_exp
    """
    obj.animation_data_create()
    
    # Frame 1: Exploded
    obj.location.z = z_exp
    obj.keyframe_insert(data_path="location", index=2, frame=1)
    
    # Start assembly move
    obj.location.z = z_exp
    obj.keyframe_insert(data_path="location", index=2, frame=f_start_down)
    
    # Finish assembly (settled on assembled position)
    obj.location.z = z_asm
    obj.keyframe_insert(data_path="location", index=2, frame=f_end_down)
    
    # Start disassembly move
    obj.location.z = z_asm
    obj.keyframe_insert(data_path="location", index=2, frame=f_start_up)
    
    # Finish disassembly (settled back to exploded position)
    obj.location.z = z_exp
    obj.keyframe_insert(data_path="location", index=2, frame=f_end_up)
    
    # End frame: Exploded (identical to Frame 1 for seamless loop)
    obj.location.z = z_exp
    obj.keyframe_insert(data_path="location", index=2, frame=total_frames)
    
    # Set Bezier smoothing on the fcurve
    if obj.animation_data and obj.animation_data.action:
        act = obj.animation_data.action
        fcurves = getattr(act, 'fcurves', None)
        if fcurves is None and hasattr(act, 'curves'):
            fcurves = act.curves
        if fcurves:
            for fcurve in fcurves:
                for kp in getattr(fcurve, 'keyframe_points', []):
                    kp.interpolation = 'BEZIER'
                    kp.easing = 'EASE_IN_OUT'

def build_k75_animation_scene():
    print("Building Photorealistic NovaKeys K75 Animation Scene...")
    scene = reset_scene()
    configure_cycles(scene, samples=96)
    
    scene.frame_start = 1
    scene.frame_end = 144
    scene.render.fps = 24
    scene.render.resolution_x = 720
    scene.render.resolution_y = 720
    
    mats = create_materials()
    
    atlas_json_path = os.path.join(TEXTURES_DIR, "keycap_atlas.json")
    with open(atlas_json_path, 'r', encoding='utf-8') as f:
        atlas_coords = json.load(f)
        
    ROT_YAW = math.radians(-22.0)
    root = bpy.data.objects.new("K75_Root", None)
    bpy.context.collection.objects.link(root)
    root.rotation_euler = (0, 0, ROT_YAW)
    
    CASE_W = 0.322
    CASE_D = 0.138
    CASE_H_FRONT = 0.017
    CASE_H_BACK = 0.024
    CASE_H_AVG = (CASE_H_FRONT + CASE_H_BACK) / 2.0
    
    # -------------------------------------------------------------------------
    # PARENT EMPIES FOR EACH STRUCTURAL LAYER TO ANIMATE TOGETHER
    # -------------------------------------------------------------------------
    layer_roots = {}
    layer_names = [
        "chassis", "weight", "silicone", "pcb", "foam", "plate", "switches", "knob", "bezel"
    ]
    for l_name in layer_names:
        empty = bpy.data.objects.new(f"Root_Layer_{l_name}", None)
        bpy.context.collection.objects.link(empty)
        empty.parent = root
        layer_roots[l_name] = empty

    # Row-specific keycap parent empties for the cascade wave
    for r_idx in range(6):
        k_empty = bpy.data.objects.new(f"Root_Keycaps_Row_{r_idx}", None)
        bpy.context.collection.objects.link(k_empty)
        k_empty.parent = root
        layer_roots[f"keys_row_{r_idx}"] = k_empty

    # -------------------------------------------------------------------------
    # LAYER 1: CHASSIS & USB-C (Stays grounded)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, CASE_H_AVG/2.0),
        scale=(CASE_W, CASE_D, CASE_H_AVG)
    )
    chassis = bpy.context.active_object
    chassis.name = "Chassis_Bottom_Case"
    chassis.data.materials.append(mats['alu'])
    cbev = chassis.modifiers.new("ChassisBevel", 'BEVEL')
    cbev.width = 0.0028
    cbev.segments = 3
    bpy.ops.object.shade_smooth()
    chassis.parent = layer_roots['chassis']
    
    usbc_y = CASE_D / 2.0
    usbc_z = CASE_H_BACK * 0.55
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-CASE_W * 0.32, usbc_y, usbc_z),
        scale=(0.014, 0.004, 0.006)
    )
    usbc = bpy.context.active_object
    usbc.name = "Chassis_USBC_Port"
    usbc.data.materials.append(mats['steel'])
    usbc.parent = layer_roots['chassis']

    # Bezel Frame
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 0.002),
        scale=(CASE_W * 0.992, CASE_D * 0.985, 0.004)
    )
    bezel = bpy.context.active_object
    bezel.name = "Chassis_Top_Bezel_Frame"
    bezel.data.materials.append(mats['alu'])
    bbev = bezel.modifiers.new("BezelBevel", 'BEVEL')
    bbev.width = 0.0018
    bbev.segments = 2
    bpy.ops.object.shade_smooth()
    bezel.parent = layer_roots['bezel']

    # LAYER 2: PVD BRASS WEIGHT BAR
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 0.0),
        scale=(CASE_W * 0.68, CASE_D * 0.36, 0.004)
    )
    weight_bar = bpy.context.active_object
    weight_bar.name = "PVD_Brass_Weight_Bar"
    weight_bar.data.materials.append(mats['brass'])
    wbev = weight_bar.modifiers.new("WeightBevel", 'BEVEL')
    wbev.width = 0.0012
    wbev.segments = 3
    bpy.ops.object.shade_smooth()
    weight_bar.parent = layer_roots['weight']

    # LAYER 3: SILICONE DAMPENER
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 0.0),
        scale=(CASE_W * 0.94, CASE_D * 0.88, 0.0025)
    )
    silicone = bpy.context.active_object
    silicone.name = "Molded_Silicone_Pad"
    silicone.data.materials.append(mats['silicone'])
    silicone.parent = layer_roots['silicone']

    # LAYER 4: ENIG PCB
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 0.0),
        scale=(CASE_W * 0.95, CASE_D * 0.90, 0.0016)
    )
    pcb = bpy.context.active_object
    pcb.name = "ENIG_FR4_PCB"
    pcb.data.materials.append(mats['pcb'])
    pcb.parent = layer_roots['pcb']
    
    for ti in [-0.08, -0.04, 0.0, 0.04, 0.08]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(ti, 0, 0.0009),
            scale=(0.0015, CASE_D * 0.75, 0.0001)
        )
        trace = bpy.context.active_object
        trace.name = f"ENIG_Trace_{ti}"
        trace.data.materials.append(mats['gold'])
        trace.parent = layer_roots['pcb']

    # LAYER 5: PORON FOAM
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 0.0),
        scale=(CASE_W * 0.94, CASE_D * 0.88, 0.003)
    )
    foam = bpy.context.active_object
    foam.name = "Poron_Acoustic_Foam"
    foam.data.materials.append(mats['foam'])
    foam.parent = layer_roots['foam']

    # LAYER 6: FR4 SWITCH PLATE & GASKET TABS
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 0.0),
        scale=(CASE_W * 0.95, CASE_D * 0.90, 0.0015)
    )
    plate = bpy.context.active_object
    plate.name = "FR4_Switch_Plate"
    plate.data.materials.append(mats['plate'])
    plate.parent = layer_roots['plate']
    
    for gx in [-0.12, -0.06, 0.0, 0.06, 0.12]:
        for gy in [-CASE_D * 0.46, CASE_D * 0.46]:
            bpy.ops.mesh.primitive_cube_add(
                size=1.0, location=(gx, gy, 0.0),
                scale=(0.016, 0.005, 0.0032)
            )
            gtab = bpy.context.active_object
            gtab.name = "Gasket_Tab"
            gtab.data.materials.append(mats['foam'])
            gtab.parent = layer_roots['plate']

    # LAYERS 7 & 8: SWITCHES & KEYCAPS
    U = 0.01905
    rows_def = [
        (5, [
            ("ESC", 1.0), ("F1", 1.0), ("F2", 1.0), ("F3", 1.0), ("F4", 1.0),
            ("F5", 1.0), ("F6", 1.0), ("F7", 1.0), ("F8", 1.0), ("F9", 1.0),
            ("F10", 1.0), ("F11", 1.0), ("F12", 1.0), ("DEL", 1.0)
        ]),
        (4, [
            ("TILDE", 1.0), ("1", 1.0), ("2", 1.0), ("3", 1.0), ("4", 1.0),
            ("5", 1.0), ("6", 1.0), ("7", 1.0), ("8", 1.0), ("9", 1.0),
            ("0", 1.0), ("MINUS", 1.0), ("PLUS", 1.0), ("BACKSPACE", 2.0), ("HOME", 1.0)
        ]),
        (3, [
            ("TAB", 1.5), ("Q", 1.0), ("W", 1.0), ("E", 1.0), ("R", 1.0),
            ("T", 1.0), ("Y", 1.0), ("U", 1.0), ("I", 1.0), ("O", 1.0),
            ("P", 1.0), ("LBRACKET", 1.0), ("RBRACKET", 1.0), ("BACKSLASH", 1.5), ("PGUP", 1.0)
        ]),
        (2, [
            ("CAPS", 1.75), ("A", 1.0), ("S", 1.0), ("D", 1.0), ("F", 1.0),
            ("G", 1.0), ("H", 1.0), ("J", 1.0), ("K", 1.0), ("L", 1.0),
            ("COLON", 1.0), ("QUOTE", 1.0), ("ENTER", 2.25), ("PGDN", 1.0)
        ]),
        (1, [
            ("LSHIFT", 2.25), ("Z", 1.0), ("X", 1.0), ("C", 1.0), ("V", 1.0),
            ("B", 1.0), ("N", 1.0), ("M", 1.0), ("COMMA", 1.0), ("PERIOD", 1.0),
            ("SLASH", 1.0), ("RSHIFT", 1.75), ("UP", 1.0), ("END", 1.0)
        ]),
        (0, [
            ("LCTRL", 1.25), ("LOPT", 1.25), ("LCMD", 1.25), ("SPACEBAR", 6.25),
            ("RCMD", 1.0), ("ROPT", 1.0), ("LEFT", 1.0), ("DOWN", 1.0), ("RIGHT", 1.0)
        ])
    ]
    
    total_rows = len(rows_def)
    y_start = (total_rows - 1) * U / 2.0

    for r_seq, (row_idx, row_keys) in enumerate(rows_def):
        row_y = y_start - r_seq * U
        row_units = sum(u for _, u in row_keys)
        row_width = row_units * U
        cur_x = -row_width / 2.0
        
        for key_name, u_size in row_keys:
            key_w = u_size * U - 0.0008
            key_d = U - 0.0008
            key_x = cur_x + (u_size * U) / 2.0
            cur_x += u_size * U
            
            # Switch belongs to switches layer root
            sw_loc = Vector((key_x, row_y, 0.0))
            build_switch_assembly(key_name, sw_loc, mats, layer_roots['switches'])
            
            # Hot-swap socket on PCB
            bpy.ops.mesh.primitive_cube_add(
                size=1.0, location=(key_x, row_y, -0.0022),
                scale=(0.010, 0.006, 0.002)
            )
            hs = bpy.context.active_object
            hs.name = f"HotSwap_Socket_{key_name}"
            hs.data.materials.append(mats['sw_bot'])
            hs.parent = layer_roots['pcb']
            
            # Keycap belongs to its specific row root for wave animation
            coords = atlas_coords.get(key_name, atlas_coords.get("BLANK_CREAM"))
            kc = build_sculpted_cherry_keycap(f"Key_{key_name}", key_w, key_d, row_idx, coords, mats['keycap'])
            kc.location = Vector((key_x, row_y, 0.0))
            kc.parent = layer_roots[f"keys_row_{row_idx}"]

    # ROTARY VOLUME KNOB
    knob_x = CASE_W * 0.42
    knob_y = y_start
    KNOB_R = 0.0105
    KNOB_H = 0.0130
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0035, depth=0.008, location=(knob_x, knob_y, -0.004)
    )
    kshaft = bpy.context.active_object
    kshaft.name = "Encoder_Shaft"
    kshaft.data.materials.append(mats['steel'])
    kshaft.parent = layer_roots['knob']
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=KNOB_R, depth=KNOB_H, location=(knob_x, knob_y, KNOB_H/2.0)
    )
    knob = bpy.context.active_object
    knob.name = "Rotary_Volume_Knob"
    knob.data.materials.append(mats['alu'])
    knob_bev = knob.modifiers.new("KnobBevel", 'BEVEL')
    knob_bev.width = 0.0010
    knob_bev.segments = 3
    bpy.ops.object.shade_smooth()
    knob.parent = layer_roots['knob']
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=KNOB_R * 0.98, depth=0.0012,
        location=(knob_x, knob_y, KNOB_H)
    )
    k_ring = bpy.context.active_object
    k_ring.name = "Knob_Mirror_Chamfer"
    k_ring.data.materials.append(mats['brass'])
    k_ring.parent = layer_roots['knob']
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(knob_x, knob_y + KNOB_R * 0.60, KNOB_H + 0.0006),
        scale=(0.0012, 0.0045, 0.0004)
    )
    ktick = bpy.context.active_object
    ktick.name = "Knob_Index_Tick"
    ktick.data.materials.append(mats['brass'])
    ktick.parent = layer_roots['knob']

    # -------------------------------------------------------------------------
    # ANIMATE EACH LAYER WITH PRECISE OVERLAPPING TIMINGS
    # -------------------------------------------------------------------------
    # Frame sequence (24 fps, 144 frames total = 6.00s):
    # Assembly down: 13 .. 68
    # Hold assembled: 69 .. 92
    # Disassembly up: 93 .. 136
    # Hold exploded: 137 .. 144 (and 1 .. 12)
    
    # 1. PVD Brass Weight: z_exp = -0.070, z_asm = -0.005
    set_z_keyframes(layer_roots['weight'], -0.070, -0.005, 14, 34, 118, 136)
    
    # 2. Silicone Dampener: z_exp = 0.065, z_asm = 0.004
    set_z_keyframes(layer_roots['silicone'], 0.065, 0.004, 16, 38, 116, 134)
    
    # 3. ENIG PCB: z_exp = 0.130, z_asm = 0.007
    set_z_keyframes(layer_roots['pcb'], 0.130, 0.007, 20, 42, 112, 132)
    
    # 4. Top Bezel: z_exp = 0.040, z_asm = 0.016
    set_z_keyframes(layer_roots['bezel'], 0.040, 0.016, 22, 44, 110, 130)
    
    # 5. Poron Foam: z_exp = 0.190, z_asm = 0.010
    set_z_keyframes(layer_roots['foam'], 0.190, 0.010, 24, 46, 108, 128)
    
    # 6. FR4 Plate: z_exp = 0.250, z_asm = 0.0125
    set_z_keyframes(layer_roots['plate'], 0.250, 0.0125, 28, 50, 104, 124)
    
    # 7. Switches: z_exp = 0.315, z_asm = 0.0155
    set_z_keyframes(layer_roots['switches'], 0.315, 0.0155, 34, 54, 100, 120)
    
    # 8. Rotary Knob: z_exp = 0.405, z_asm = 0.022
    set_z_keyframes(layer_roots['knob'], 0.405, 0.022, 36, 56, 98, 118)
    
    # 9. Keycaps: Cascade Wave by rows (R5 -> R4 -> R3 -> R2 -> R1 -> R0)
    # Assembly down starts sequentially, disassembly lifts in reverse
    key_timings = [
        # row_idx: (f_down_start, f_down_end, f_up_start, f_up_end)
        (5, 38, 56, 104, 122), # Function row
        (4, 40, 58, 102, 120), # Number row
        (3, 42, 60, 100, 118), # QWERTY row
        (2, 44, 62, 98, 116),  # Home row
        (1, 46, 64, 96, 114),  # ZXCV row
        (0, 48, 66, 94, 112),  # Spacebar / Bottom row
    ]
    for r_idx, fds, fde, fus, fue in key_timings:
        set_z_keyframes(layer_roots[f"keys_row_{r_idx}"], 0.395, 0.0215, fds, fde, fus, fue)

    # -------------------------------------------------------------------------
    # LIGHTING RIG (Balanced Studio Lighting, Cycles AgX)
    # -------------------------------------------------------------------------
    bpy.ops.object.light_add(type='AREA', location=(0.35, -1.10, 1.30))
    key = bpy.context.active_object
    key.name = "Studio_Key_Softbox"
    key.data.energy = 32.0
    key.data.size = 1.40
    key.data.size_y = 0.90
    key.data.color = (1.0, 0.99, 0.97)
    dir_k = Vector((0.0, 0.0, 0.12)) - key.location
    key.rotation_euler = dir_k.to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True
    
    bpy.ops.object.light_add(type='AREA', location=(-0.90, -1.20, 0.90))
    fill = bpy.context.active_object
    fill.name = "Studio_Fill_Softbox"
    fill.data.energy = 16.0
    fill.data.size = 1.60
    fill.data.size_y = 1.00
    fill.data.color = (0.95, 0.97, 1.0)
    dir_f = Vector((0.0, 0.0, 0.12)) - fill.location
    fill.rotation_euler = dir_f.to_track_quat('-Z', 'Y').to_euler()
    fill.data.use_shadow = False
    
    bpy.ops.object.light_add(type='AREA', location=(0.60, 0.90, 0.80))
    rim = bpy.context.active_object
    rim.name = "Rear_Contour_Rim"
    rim.data.energy = 18.0
    rim.data.size = 1.10
    rim.data.size_y = 0.60
    rim.data.color = (0.98, 0.99, 1.0)
    dir_r = Vector((0.0, 0.0, 0.12)) - rim.location
    rim.rotation_euler = dir_r.to_track_quat('-Z', 'Y').to_euler()
    rim.data.use_shadow = True

    # -------------------------------------------------------------------------
    # FIXED CAMERA (Framing entire vertical travel Z=[-0.07m .. +0.41m])
    # -------------------------------------------------------------------------
    target_anim = Vector((0.005, 0.000, 0.155))
    dist_anim = 1.34
    elev_rad = math.radians(36.0)
    azim_rad = math.radians(18.0)
    
    cam_x = target_anim.x + dist_anim * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target_anim.y - dist_anim * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target_anim.z + dist_anim * math.sin(elev_rad)
    
    cam_data = bpy.data.cameras.new("Camera_K75_Animated")
    cam_data.lens = 54.0
    cam_obj = bpy.data.objects.new("Camera_K75_Animated", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    dir_a = target_anim - cam_obj.location
    cam_obj.rotation_euler = dir_a.to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam_obj

    # Save animated .blend scene
    blend_path = os.path.join(SCENES_DIR, "k75_animation.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved animated Master .blend scene: {blend_path}")

    return scene, cam_obj

def render_preview_or_full(scene, mode="preview"):
    print(f"--- Rendering Animation ({mode.upper()}) ---")
    if mode == "preview":
        # Render key checkpoint frames: 1 (exploded), 40 (mid-assembly), 75 (fully assembled), 110 (mid-disassembly)
        checkpoint_frames = [1, 35, 52, 75, 105, 125, 144]
        for f in checkpoint_frames:
            scene.frame_set(f)
            out_file = os.path.join(OUTPUT_DIR, f"k75_anim_check_f{f:03d}.png")
            scene.render.filepath = out_file
            print(f"Rendering check frame {f} -> {out_file}...")
            bpy.ops.render.render(write_still=True)
        print("Check frames successfully rendered!")
    else:
        # Full animation render to frames folder
        scene.render.filepath = os.path.join(FRAMES_DIR, "k75_frame_")
        print(f"Rendering all 144 frames to {FRAMES_DIR}...")
        bpy.ops.render.render(animation=True)
        print("Full 144-frame animation render completed!")

if __name__ == "__main__":
    target_mode = sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-1] in ["preview", "full"] else "preview"
    scene, cam = build_k75_animation_scene()
    render_preview_or_full(scene, mode=target_mode)
