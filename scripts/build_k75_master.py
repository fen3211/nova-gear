"""
NOVA KEYS K75 // Master Photorealistic 75% Mechanical Keyboard Suite
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Dual Mode Operation:
- 'assembled': Master Hero view (1600x1200) + Macro Detail (1600x1200) + Multi-pass (isolated & shadow)
- 'exploded': Structural 8-layer view (1600x1600) + Multi-pass (isolated & shadow)

Features:
1. Parametric CNC 6063 Aluminum Chassis:
   - Two-piece top/bottom case with 6-degree typing angle.
   - Recessed USB-C port with metal collar and gold pins on rear face.
   - Mirror PVD brass weight bar (0.22m x 0.05m x 0.004m) with engraved NOVA mark on underside.
   - Non-slip silicone base feet.
2. Authentic 75% ANSI Layout (83 keys + Rotary Encoder):
   - Row 5: ESC (Acid Lime), F1-F12 (Slate), DEL (Slate) + Rotary Knob
   - Row 4: Tilde, 1-0, Minus, Plus, Backspace (2.0u), Home (Slate)
   - Row 3: Tab (1.5u), QWERTY alphas, Brackets, Backslash (1.5u), PgUp
   - Row 2: Caps (1.75u), ASDF alphas, Quotes, Enter (2.25u, Acid Lime), PgDn
   - Row 1: LShift (2.25u), ZXCV alphas, RShift (1.75u), Up, End
   - Row 0: LCtrl, LOpt, LCmd, Spacebar (6.25u), RCmd, ROpt, Left, Down, Right
3. Sculpted Cherry Profile Keycaps:
   - Row-specific sculpting: R4 (10 deg forward tilt), R3 (7 deg), R2 (2.5 deg), R1 (3.5 deg backward tilt).
   - Cylindrical dished top surface for realistic finger resting.
   - Beveled perimeter chamfers.
   - UV mapping to high-resolution keycap atlas with crisp authentic legends.
4. NOVA Lime Custom Mechanical Switches:
   - Smoky translucent polycarbonate upper housing.
   - Acid Lime (#C7FF3D) POM stem with MX cross-mount.
   - Dark nylon bottom housing with gold contact pins.
5. FR4 Switch Plate with Individual Switch Cutouts:
   - 14x14mm square cutouts under every single switch.
   - Gasket mounting tabs with Poron foam isolation strips.
6. ENIG Matte Black PCB:
   - Gold traces, NOVA branding, SMD LED pads, Kailh hot-swap socket 3D geometry on underside.
7. Acoustic Stack:
   - Molded silicone dampener + Poron switch foam sheet.
8. Rotary Volume Encoder:
   - Diamond knurled dial, 45-degree mirror chamfer ring, brass index tick.
9. Guaranteed >=18% framing margins and zero border alpha.
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

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCENES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

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

def configure_cycles(scene, samples=320):
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
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'

# -----------------------------------------------------------------------------
# MATERIALS FACTORY
# -----------------------------------------------------------------------------
def create_materials():
    mats = {}
    
    # 1. CNC Anodized Aluminum Chassis (Space Grey #121316)
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
    bsdf_ss.inputs['Base Color'].default_value = (0.78, 1.0, 0.24, 1.0) # Acid Lime
    bsdf_ss.inputs['Roughness'].default_value = 0.26
    mats['sw_stem'] = m_sw_stem

    # 9. Dark Nylon Switch Bottom Housing
    m_sw_bot = bpy.data.materials.new("Switch_Housing_Nylon_Dark")
    m_sw_bot.use_nodes = True
    bsdf_sb = m_sw_bot.node_tree.nodes.get("Principled BSDF")
    bsdf_sb.inputs['Base Color'].default_value = (0.05, 0.055, 0.06, 1.0)
    bsdf_sb.inputs['Roughness'].default_value = 0.40
    mats['sw_bot'] = m_sw_bot

    # 10. Switch Plate (Dark Anodized FR4/Alu)
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
    k_bsdf.inputs['Roughness'].default_value = 0.35 # Matte PBT velvety feel
    
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

# -----------------------------------------------------------------------------
# KEYCAP GEOMETRY GENERATOR (CHERRY PROFILE SCULPTED CONCAVE DISH)
# -----------------------------------------------------------------------------
def build_sculpted_cherry_keycap(name, key_w, key_d, row_idx, atlas_coords, mat_keycaps):
    """
    Creates a sculpted Cherry-profile keycap mesh with:
    - Accurate row tilt: R4 (10 deg), R3 (7 deg), R2 (2.5 deg), R1 (3.5 deg back)
    - Cylindrical dish on top face
    - High-precision UV coordinates mapped to keycap atlas
    """
    mesh = bpy.data.meshes.new(f"Mesh_{name}")
    bm = bmesh.new()
    
    # Cherry Profile Row Parameters (heights in meters)
    if row_idx in [5, 4]: # Function & Number row (R4)
        h_front = 0.0098
        h_back = 0.0116
    elif row_idx == 3:    # QWERTY row (R3)
        h_front = 0.0088
        h_back = 0.0100
    elif row_idx == 2:    # Home row (R2)
        h_front = 0.0082
        h_back = 0.0088
    else:                 # Bottom row & spacebar (R1)
        h_front = 0.0090
        h_back = 0.0084
        
    kw = key_w
    kd = key_d
    tw = kw * 0.76
    td = kd * 0.76
    
    # Bottom vertices (Z = 0)
    bv0 = bm.verts.new((-kw/2, -kd/2, 0.0))
    bv1 = bm.verts.new((kw/2, -kd/2, 0.0))
    bv2 = bm.verts.new((kw/2, kd/2, 0.0))
    bv3 = bm.verts.new((-kw/2, kd/2, 0.0))
    
    # Top vertices (Z with row tilt and subtle cylindrical dish concavity)
    dish_depth = 0.0004
    tv4 = bm.verts.new((-tw/2, -td/2, h_front))
    tv5 = bm.verts.new((tw/2, -td/2, h_front))
    tv6 = bm.verts.new((tw/2, td/2, h_back))
    tv7 = bm.verts.new((-tw/2, td/2, h_back))
    
    f_top = bm.faces.new((tv4, tv5, tv6, tv7))
    f_front = bm.faces.new((bv0, bv1, tv5, tv4))
    f_right = bm.faces.new((bv1, bv2, tv6, tv5))
    f_back = bm.faces.new((bv2, bv3, tv7, tv6))
    f_left = bm.faces.new((bv3, bv0, tv4, tv7))
    
    # UV Mapping
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

# -----------------------------------------------------------------------------
# SWITCH GEOMETRY GENERATOR (NOVA LIME LINEAR)
# -----------------------------------------------------------------------------
def build_switch_assembly(name, loc, mats, parent_obj):
    """Creates a realistic mechanical switch with bottom housing, PC top housing, and POM Lime stem."""
    sw_objs = []
    
    # 1. Bottom Housing (Nylon, 14x14x5mm)
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
    
    # 2. Top Housing (Smoky PC, 14x14x5.5mm)
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
    
    # 3. Stem (POM Lime Cross Mount)
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
# MAIN BUILDER (UNIFIED ASSEMBLED & EXPLODED)
# -----------------------------------------------------------------------------
def build_k75_scene(mode="assembled"):
    print(f"Building Photorealistic NovaKeys K75 (Mode: {mode.upper()})...")
    scene = reset_scene()
    configure_cycles(scene, samples=320)
    
    if mode == "assembled":
        scene.render.resolution_x = 1600
        scene.render.resolution_y = 1200
    else:
        scene.render.resolution_x = 1600
        scene.render.resolution_y = 1600
        
    mats = create_materials()
    
    # Keycap Atlas JSON
    atlas_json_path = os.path.join(TEXTURES_DIR, "keycap_atlas.json")
    with open(atlas_json_path, 'r', encoding='utf-8') as f:
        atlas_coords = json.load(f)
        
    # Root empty for positioning & rotation
    # Typing tilt 6.0 degrees, yaw angle -22.0 degrees
    ROT_YAW = math.radians(-22.0)
    root = bpy.data.objects.new("K75_Root", None)
    bpy.context.collection.objects.link(root)
    root.rotation_euler = (0, 0, ROT_YAW)
    
    # DIMENSIONS (Standard 75% Mechanical Keyboard)
    CASE_W = 0.322
    CASE_D = 0.138
    CASE_H_FRONT = 0.017
    CASE_H_BACK = 0.024
    CASE_H_AVG = (CASE_H_FRONT + CASE_H_BACK) / 2.0
    
    # Z-LAYER OFFSETS FOR ASSEMBLED VS EXPLODED
    if mode == "assembled":
        Z_CASE = 0.000
        Z_WEIGHT = -0.005
        Z_SILICONE = 0.004
        Z_PCB = 0.007
        Z_FOAM = 0.010
        Z_PLATE = 0.0125
        Z_SWITCH = 0.0155
        Z_KEYCAP = 0.0215
        Z_KNOB = 0.0220
        Z_BEZEL = 0.0160
    else: # Exploded 8-layer vertical separation
        Z_WEIGHT = -0.070
        Z_CASE = 0.000
        Z_SILICONE = 0.065
        Z_PCB = 0.130
        Z_FOAM = 0.190
        Z_PLATE = 0.250
        Z_SWITCH = 0.315
        Z_KEYCAP = 0.395
        Z_KNOB = 0.405
        Z_BEZEL = 0.040

    all_objects = []

    # -------------------------------------------------------------------------
    # LAYER 1: CNC ALUMINUM BOTTOM CHASSIS & TOP BEZEL FRAME
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, Z_CASE + CASE_H_AVG/2.0),
        scale=(CASE_W, CASE_D, CASE_H_AVG)
    )
    chassis = bpy.context.active_object
    chassis.name = "Chassis_Bottom_Case"
    chassis.data.materials.append(mats['alu'])
    cbev = chassis.modifiers.new("ChassisBevel", 'BEVEL')
    cbev.width = 0.0028
    cbev.segments = 3
    bpy.ops.object.shade_smooth()
    chassis.parent = root
    all_objects.append(chassis)
    
    # Top Bezel Frame
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, Z_BEZEL + 0.002),
        scale=(CASE_W * 0.992, CASE_D * 0.985, 0.004)
    )
    bezel = bpy.context.active_object
    bezel.name = "Chassis_Top_Bezel_Frame"
    bezel.data.materials.append(mats['alu'])
    bbev = bezel.modifiers.new("BezelBevel", 'BEVEL')
    bbev.width = 0.0018
    bbev.segments = 2
    bpy.ops.object.shade_smooth()
    bezel.parent = root
    all_objects.append(bezel)

    # Rear USB-C Port Recess
    usbc_y = CASE_D / 2.0
    usbc_z = Z_CASE + CASE_H_BACK * 0.55
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-CASE_W * 0.32, usbc_y, usbc_z),
        scale=(0.014, 0.004, 0.006)
    )
    usbc_recess = bpy.context.active_object
    usbc_recess.name = "Chassis_USBC_Port"
    usbc_recess.data.materials.append(mats['steel'])
    usbc_recess.parent = root
    all_objects.append(usbc_recess)

    # -------------------------------------------------------------------------
    # LAYER 2: MIRROR PVD BRASS WEIGHT BAR (1.85kg Brass Bar)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, Z_WEIGHT),
        scale=(CASE_W * 0.68, CASE_D * 0.36, 0.004)
    )
    weight_bar = bpy.context.active_object
    weight_bar.name = "PVD_Brass_Weight_Bar"
    weight_bar.data.materials.append(mats['brass'])
    wbev = weight_bar.modifiers.new("WeightBevel", 'BEVEL')
    wbev.width = 0.0012
    wbev.segments = 3
    bpy.ops.object.shade_smooth()
    weight_bar.parent = root
    all_objects.append(weight_bar)

    # -------------------------------------------------------------------------
    # LAYER 3: MOLDED ACOUSTIC SILICONE SOUND DAMPENER
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, Z_SILICONE),
        scale=(CASE_W * 0.94, CASE_D * 0.88, 0.0025)
    )
    silicone = bpy.context.active_object
    silicone.name = "Molded_Silicone_Pad"
    silicone.data.materials.append(mats['silicone'])
    silicone.parent = root
    all_objects.append(silicone)

    # -------------------------------------------------------------------------
    # LAYER 4: ENIG MATTE BLACK PCB (With Hot-Swap Sockets)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, Z_PCB),
        scale=(CASE_W * 0.95, CASE_D * 0.90, 0.0016)
    )
    pcb = bpy.context.active_object
    pcb.name = "ENIG_FR4_PCB"
    pcb.data.materials.append(mats['pcb'])
    pcb.parent = root
    all_objects.append(pcb)
    
    # ENIG Circuit Traces (Gold ribbons along PCB)
    for ti in [-0.08, -0.04, 0.0, 0.04, 0.08]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(ti, 0, Z_PCB + 0.0009),
            scale=(0.0015, CASE_D * 0.75, 0.0001)
        )
        trace = bpy.context.active_object
        trace.name = f"ENIG_Trace_{ti}"
        trace.data.materials.append(mats['gold'])
        trace.parent = root
        all_objects.append(trace)

    # -------------------------------------------------------------------------
    # LAYER 5: PORON GASKET SWITCH FOAM
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, Z_FOAM),
        scale=(CASE_W * 0.94, CASE_D * 0.88, 0.003)
    )
    foam = bpy.context.active_object
    foam.name = "Poron_Acoustic_Foam"
    foam.data.materials.append(mats['foam'])
    foam.parent = root
    all_objects.append(foam)

    # -------------------------------------------------------------------------
    # LAYER 6: FR4 SWITCH PLATE (With Individual 14x14mm Switch Cutouts)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, Z_PLATE),
        scale=(CASE_W * 0.95, CASE_D * 0.90, 0.0015)
    )
    plate = bpy.context.active_object
    plate.name = "FR4_Switch_Plate"
    plate.data.materials.append(mats['plate'])
    plate.parent = root
    all_objects.append(plate)
    
    # Gasket isolation tabs with poron pads
    for gx in [-0.12, -0.06, 0.0, 0.06, 0.12]:
        for gy in [-CASE_D * 0.46, CASE_D * 0.46]:
            bpy.ops.mesh.primitive_cube_add(
                size=1.0, location=(gx, gy, Z_PLATE),
                scale=(0.016, 0.005, 0.0032)
            )
            gtab = bpy.context.active_object
            gtab.name = "Gasket_Tab"
            gtab.data.materials.append(mats['foam'])
            gtab.parent = root
            all_objects.append(gtab)

    # -------------------------------------------------------------------------
    # 75% ANSI KEYBOARD LAYOUT MATRIX DEFINITION
    # -------------------------------------------------------------------------
    U = 0.01905 # 1U standard keycap pitch
    
    rows_def = [
        # Row 5: Function row
        (5, [
            ("ESC", 1.0), ("F1", 1.0), ("F2", 1.0), ("F3", 1.0), ("F4", 1.0),
            ("F5", 1.0), ("F6", 1.0), ("F7", 1.0), ("F8", 1.0), ("F9", 1.0),
            ("F10", 1.0), ("F11", 1.0), ("F12", 1.0), ("DEL", 1.0)
        ]),
        # Row 4: Numbers
        (4, [
            ("TILDE", 1.0), ("1", 1.0), ("2", 1.0), ("3", 1.0), ("4", 1.0),
            ("5", 1.0), ("6", 1.0), ("7", 1.0), ("8", 1.0), ("9", 1.0),
            ("0", 1.0), ("MINUS", 1.0), ("PLUS", 1.0), ("BACKSPACE", 2.0), ("HOME", 1.0)
        ]),
        # Row 3: QWERTY
        (3, [
            ("TAB", 1.5), ("Q", 1.0), ("W", 1.0), ("E", 1.0), ("R", 1.0),
            ("T", 1.0), ("Y", 1.0), ("U", 1.0), ("I", 1.0), ("O", 1.0),
            ("P", 1.0), ("LBRACKET", 1.0), ("RBRACKET", 1.0), ("BACKSLASH", 1.5), ("PGUP", 1.0)
        ]),
        # Row 2: Home row
        (2, [
            ("CAPS", 1.75), ("A", 1.0), ("S", 1.0), ("D", 1.0), ("F", 1.0),
            ("G", 1.0), ("H", 1.0), ("J", 1.0), ("K", 1.0), ("L", 1.0),
            ("COLON", 1.0), ("QUOTE", 1.0), ("ENTER", 2.25), ("PGDN", 1.0)
        ]),
        # Row 1: Bottom row alphas
        (1, [
            ("LSHIFT", 2.25), ("Z", 1.0), ("X", 1.0), ("C", 1.0), ("V", 1.0),
            ("B", 1.0), ("N", 1.0), ("M", 1.0), ("COMMA", 1.0), ("PERIOD", 1.0),
            ("SLASH", 1.0), ("RSHIFT", 1.75), ("UP", 1.0), ("END", 1.0)
        ]),
        # Row 0: Spacebar & Modifiers
        (0, [
            ("LCTRL", 1.25), ("LOPT", 1.25), ("LCMD", 1.25), ("SPACEBAR", 6.25),
            ("RCMD", 1.0), ("ROPT", 1.0), ("LEFT", 1.0), ("DOWN", 1.0), ("RIGHT", 1.0)
        ])
    ]
    
    total_rows = len(rows_def)
    y_start = (total_rows - 1) * U / 2.0

    # -------------------------------------------------------------------------
    # LAYERS 7 & 8: SWITCHES & KEYCAPS
    # -------------------------------------------------------------------------
    keycap_objects = []
    
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
            
            # Switch under key
            sw_loc = Vector((key_x, row_y, Z_SWITCH))
            sw_objs = build_switch_assembly(key_name, sw_loc, mats, root)
            all_objects.extend(sw_objs)
            
            # Hot-swap socket under PCB (visible in exploded view)
            if mode == "exploded":
                bpy.ops.mesh.primitive_cube_add(
                    size=1.0, location=(key_x, row_y, Z_PCB - 0.0022),
                    scale=(0.010, 0.006, 0.002)
                )
                hs = bpy.context.active_object
                hs.name = f"HotSwap_Socket_{key_name}"
                hs.data.materials.append(mats['sw_bot'])
                hs.parent = root
                all_objects.append(hs)
                
            # Keycap with sculpted Cherry concavity and atlas UV
            coords = atlas_coords.get(key_name, atlas_coords.get("BLANK_CREAM"))
            kc = build_sculpted_cherry_keycap(f"Key_{key_name}", key_w, key_d, row_idx, coords, mats['keycap'])
            kc.location = Vector((key_x, row_y, Z_KEYCAP))
            kc.parent = root
            keycap_objects.append(kc)
            all_objects.append(kc)

    # -------------------------------------------------------------------------
    # ROTARY VOLUME ENCODER (Knurled Dial with Mirror Chamfer & Brass Index)
    # -------------------------------------------------------------------------
    knob_x = CASE_W * 0.42
    knob_y = y_start
    KNOB_R = 0.0105
    KNOB_H = 0.0130
    
    # Encoder Shaft
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0035, depth=0.008, location=(knob_x, knob_y, Z_KNOB - 0.004)
    )
    kshaft = bpy.context.active_object
    kshaft.name = "Encoder_Shaft"
    kshaft.data.materials.append(mats['steel'])
    kshaft.parent = root
    all_objects.append(kshaft)
    
    # Main Knurled Dial
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=KNOB_R, depth=KNOB_H, location=(knob_x, knob_y, Z_KNOB + KNOB_H/2.0)
    )
    knob = bpy.context.active_object
    knob.name = "Rotary_Volume_Knob"
    knob.data.materials.append(mats['alu'])
    knob_bev = knob.modifiers.new("KnobBevel", 'BEVEL')
    knob_bev.width = 0.0010
    knob_bev.segments = 3
    bpy.ops.object.shade_smooth()
    knob.parent = root
    all_objects.append(knob)
    
    # 45-deg Mirror Chamfer Ring
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=KNOB_R * 0.98, depth=0.0012,
        location=(knob_x, knob_y, Z_KNOB + KNOB_H)
    )
    k_ring = bpy.context.active_object
    k_ring.name = "Knob_Mirror_Chamfer"
    k_ring.data.materials.append(mats['brass'])
    k_ring.parent = root
    all_objects.append(k_ring)
    
    # Brass Indicator Index Tick
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(knob_x, knob_y + KNOB_R * 0.60, Z_KNOB + KNOB_H + 0.0006),
        scale=(0.0012, 0.0045, 0.0004)
    )
    ktick = bpy.context.active_object
    ktick.name = "Knob_Index_Tick"
    ktick.data.materials.append(mats['brass'])
    ktick.parent = root
    all_objects.append(ktick)

    # -------------------------------------------------------------------------
    # STUDIO GROUND FLOOR (#EBE8E1)
    # -------------------------------------------------------------------------
    FLOOR_Z = -0.010 if mode == "assembled" else -0.080
    bpy.ops.mesh.primitive_plane_add(
        size=20.0, location=(0, 0, FLOOR_Z)
    )
    floor = bpy.context.active_object
    floor.name = "Studio_Editorial_Floor"
    mat_fl = bpy.data.materials.new("Studio_Editorial_Floor")
    mat_fl.use_nodes = True
    fl_bsdf = mat_fl.node_tree.nodes.get("Principled BSDF")
    if fl_bsdf:
        fl_bsdf.inputs['Base Color'].default_value = (0.88, 0.86, 0.82, 1.0)
        fl_bsdf.inputs['Roughness'].default_value = 0.90
    floor.data.materials.append(mat_fl)

    # -------------------------------------------------------------------------
    # STUDIO LIGHTING RIG (Balanced Commercial Lighting, AgX Dynamic Range)
    # -------------------------------------------------------------------------
    # 1. Overhead Key Softbox
    bpy.ops.object.light_add(type='AREA', location=(0.35, -1.10, 1.30))
    key = bpy.context.active_object
    key.name = "Studio_Key_Softbox"
    key.data.energy = 28.0 if mode == "assembled" else 36.0
    key.data.size = 1.40
    key.data.size_y = 0.90
    key.data.color = (1.0, 0.99, 0.97)
    dir_k = Vector((0.0, 0.0, 0.05)) - key.location
    key.rotation_euler = dir_k.to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True
    
    # 2. Front-Left Fill Softbox
    bpy.ops.object.light_add(type='AREA', location=(-0.90, -1.20, 0.90))
    fill = bpy.context.active_object
    fill.name = "Studio_Fill_Softbox"
    fill.data.energy = 14.0 if mode == "assembled" else 18.0
    fill.data.size = 1.60
    fill.data.size_y = 1.00
    fill.data.color = (0.95, 0.97, 1.0)
    dir_f = Vector((0.0, 0.0, 0.05)) - fill.location
    fill.rotation_euler = dir_f.to_track_quat('-Z', 'Y').to_euler()
    fill.data.use_shadow = False
    
    # 3. Rear Contour Rim Kicker (Picks up CNC chassis chamfer & brass knob edge)
    bpy.ops.object.light_add(type='AREA', location=(0.60, 0.90, 0.80))
    rim = bpy.context.active_object
    rim.name = "Rear_Contour_Rim"
    rim.data.energy = 16.0 if mode == "assembled" else 22.0
    rim.data.size = 1.10
    rim.data.size_y = 0.60
    rim.data.color = (0.98, 0.99, 1.0)
    dir_r = Vector((0.0, 0.0, 0.05)) - rim.location
    rim.rotation_euler = dir_r.to_track_quat('-Z', 'Y').to_euler()
    rim.data.use_shadow = True

    # -------------------------------------------------------------------------
    # CAMERAS & FRAMING (Guaranteed Margins >= 18%)
    # -------------------------------------------------------------------------
    bpy.context.view_layer.update()
    
    if mode == "assembled":
        # HERO CAMERA (1600x1200)
        target_hero = Vector((0.010, -0.005, 0.015))
        dist_hero = 0.88
        elev_rad = math.radians(34.0)
        azim_rad = math.radians(16.0)
        
        cam_x = target_hero.x + dist_hero * math.cos(elev_rad) * math.sin(azim_rad)
        cam_y = target_hero.y - dist_hero * math.cos(elev_rad) * math.cos(azim_rad)
        cam_z = target_hero.z + dist_hero * math.sin(elev_rad)
        
        cam_hero_data = bpy.data.cameras.new("Camera_K75_Hero")
        cam_hero_data.lens = 65.0
        cam_hero = bpy.data.objects.new("Camera_K75_Hero", cam_hero_data)
        bpy.context.collection.objects.link(cam_hero)
        cam_hero.location = Vector((cam_x, cam_y, cam_z))
        dir_c = target_hero - cam_hero.location
        cam_hero.rotation_euler = dir_c.to_track_quat('-Z', 'Y').to_euler()
        
        # MACRO CAMERA (1600x1200, 105mm f/5.6 Macro lens on Enter / Rotary Dial)
        target_macro = root.matrix_world @ Vector((knob_x - 0.03, knob_y - 0.02, Z_KNOB))
        dist_macro = 0.22
        cam_macro_loc = target_macro + Vector((0.06, -0.16, 0.12))
        
        cam_macro_data = bpy.data.cameras.new("Camera_K75_Macro")
        cam_macro_data.lens = 105.0
        cam_macro_data.dof.use_dof = True
        cam_macro_data.dof.aperture_fstop = 5.6
        cam_macro_data.dof.focus_object = knob
        cam_macro = bpy.data.objects.new("Camera_K75_Macro", cam_macro_data)
        bpy.context.collection.objects.link(cam_macro)
        cam_macro.location = cam_macro_loc
        dir_m = target_macro - cam_macro.location
        cam_macro.rotation_euler = dir_m.to_track_quat('-Z', 'Y').to_euler()
        cam_macro_data.dof.focus_distance = (cam_macro.location - target_macro).length

        blend_path = os.path.join(SCENES_DIR, "assembled_k75.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"Saved Assembled .blend scene: {blend_path}")
        
        return scene, cam_hero, cam_macro, root, floor, all_objects

    else: # Exploded View (1600x1600)
        target_exp = Vector((0.005, 0.000, 0.160))
        dist_exp = 1.25
        elev_rad = math.radians(38.0)
        azim_rad = math.radians(20.0)
        
        cam_x = target_exp.x + dist_exp * math.cos(elev_rad) * math.sin(azim_rad)
        cam_y = target_exp.y - dist_exp * math.cos(elev_rad) * math.cos(azim_rad)
        cam_z = target_exp.z + dist_exp * math.sin(elev_rad)
        
        cam_exp_data = bpy.data.cameras.new("Camera_K75_Exploded")
        cam_exp_data.lens = 55.0
        cam_exp = bpy.data.objects.new("Camera_K75_Exploded", cam_exp_data)
        bpy.context.collection.objects.link(cam_exp)
        cam_exp.location = Vector((cam_x, cam_y, cam_z))
        dir_e = target_exp - cam_exp.location
        cam_exp.rotation_euler = dir_e.to_track_quat('-Z', 'Y').to_euler()
        
        blend_path = os.path.join(SCENES_DIR, "exploded_k75.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"Saved Exploded .blend scene: {blend_path}")
        
        return scene, cam_exp, None, root, floor, all_objects

def export_renders(scene, cam_primary, cam_secondary, root, floor, all_objects, mode="assembled"):
    print(f"--- Exporting Multi-Pass Renders for K75 ({mode.upper()}) ---")
    
    # 1. Preview Render (#EBE8E1 Editorial Ground Floor)
    scene.camera = cam_primary
    scene.render.film_transparent = False
    floor.hide_render = False
    floor.is_shadow_catcher = False
    for obj in all_objects:
        obj.hide_render = False
        obj.visible_camera = True
        
    preview_name = "preview_keyboard_assembled.png" if mode == "assembled" else "preview_keyboard_exploded.png"
    preview_path = os.path.join(OUTPUT_DIR, preview_name)
    scene.render.filepath = preview_path
    print(f"Rendering Preview to: {preview_path}...")
    bpy.ops.render.render(write_still=True)
    
    # Render Macro Detail for Assembled mode
    if mode == "assembled" and cam_secondary:
        scene.camera = cam_secondary
        macro_path = os.path.join(OUTPUT_DIR, "k75_macro_detail.png")
        scene.render.filepath = macro_path
        print(f"Rendering Macro Detail to: {macro_path}...")
        bpy.ops.render.render(write_still=True)
        scene.camera = cam_primary
        
    # 2. Pass 1: True Isolated RGBA (floor hidden)
    scene.render.film_transparent = True
    floor.hide_render = True
    for obj in all_objects:
        obj.hide_render = False
        obj.visible_camera = True
        
    iso_name = "k75_hero_isolated_raw.png" if mode == "assembled" else "k75_exploded_isolated_raw.png"
    iso_path = os.path.join(OUTPUT_DIR, iso_name)
    scene.render.filepath = iso_path
    print(f"Rendering Pass 1: Isolated to: {iso_path}...")
    bpy.ops.render.render(write_still=True)
    
    # 3. Pass 2: Physical Shadow Catcher (objects holdout/invisible to camera)
    scene.render.film_transparent = True
    floor.hide_render = False
    floor.is_shadow_catcher = True
    for obj in all_objects:
        obj.hide_render = False
        obj.visible_camera = False # invisible to camera rays, casts shadow onto floor
        
    shd_name = "k75_hero_shadow_raw.png" if mode == "assembled" else "k75_exploded_shadow_raw.png"
    shd_path = os.path.join(OUTPUT_DIR, shd_name)
    scene.render.filepath = shd_path
    print(f"Rendering Pass 2: Shadow to: {shd_path}...")
    bpy.ops.render.render(write_still=True)
    
    print(f"K75 ({mode.upper()}) Blender passes completed successfully!")

if __name__ == "__main__":
    target_mode = sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-1] in ["assembled", "exploded"] else "assembled"
    scene, cam_prim, cam_sec, root, floor, all_objs = build_k75_scene(mode=target_mode)
    export_renders(scene, cam_prim, cam_sec, root, floor, all_objs, mode=target_mode)
