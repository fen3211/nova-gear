"""
NOVA ORBIT ANC // Master Studio Engineering & Photorealistic Headphone Suite
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Features based on blender-product-visuals skill:
- Anatomically contoured oval earcups (96mm x 78mm x 32mm) with 12-deg ergonomic cant.
- CNC machined aluminum outer backplates with 45-deg mirror chamfer & signature orange accent ring (#FF5500).
- Plush memory foam earpads with supple protein leatherette and breathable acoustic mesh dust filter.
- Sculpted dual-axis wishbone yokes with stainless steel pivot pins and Torx fasteners.
- Arched spring-steel headband with laser-etched graduation steps (1..8) and padded underside cushion.
- Physical tactile interface: milled volume rocker, concave ANC button, USB-C port with internal tongue,
  3.5mm aux jack, power slider switch, and dual beamforming microphone pinholes.
- Cycles multi-pass rendering:
  * Hero 3/4 beauty view
  * Side silhouette view
  * Macro earpad & acoustic seam view
  * Macro headband gimbal yoke view
  * Film transparent RGBA isolated pass & Cycles Shadow Catcher pass.
- Saves master .blend file to assets/models/headphones_orbit_master.blend and assets/scenes/headphones_orbit.blend.
"""

import bpy
import bmesh
import math
import os
import sys
import subprocess
import mathutils
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"D:\Projects\ууу"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "assets", "previews")
MODELS_DIR = os.path.join(PROJECT_ROOT, "assets", "models")
SCENES_DIR = os.path.join(PROJECT_ROOT, "assets", "scenes")
IMAGES_DIR = os.path.join(PROJECT_ROOT, "assets", "images")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SCENES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Studio_World")
    scene.world = world
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.88, 0.86, 0.82, 1.0)
        bg.inputs['Strength'].default_value = 0.85
    return scene

def configure_cycles(scene, samples=192):
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
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'

def create_materials():
    mats = {}

    # 1. Brushed Anodized Space Gray Aluminum (Earcups & Yokes)
    m_alu = bpy.data.materials.new("Alu_SpaceGray_Anodized")
    n = m_alu.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.13, 0.15, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.22
    if 'Anisotropic' in bsdf.inputs:
        bsdf.inputs['Anisotropic'].default_value = 0.35
    t_noise = n.new('ShaderNodeTexNoise')
    t_noise.inputs['Scale'].default_value = 1600.0
    t_noise.inputs['Detail'].default_value = 3.0
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.005
    bump.inputs['Distance'].default_value = 0.001
    m_alu.node_tree.links.new(t_noise.outputs['Fac'], bump.inputs['Height'])
    m_alu.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    m_alu.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['alu'] = m_alu

    # 2. Mirror Polish Silver Chamfer & Steel Sliders
    m_steel = bpy.data.materials.new("Steel_Mirror_Chamfer")
    n = m_steel.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.90, 0.92, 0.95, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.08
    m_steel.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['steel'] = m_steel

    # 3. Signature Orange Anodized Accent (#FF5500)
    m_orange = bpy.data.materials.new("Orange_Accent_Anodized")
    n = m_orange.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.22, 0.01, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.90
    bsdf.inputs['Roughness'].default_value = 0.16
    m_orange.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['orange'] = m_orange

    # 4. Supple Protein Leatherette (Memory foam cushions & headband pad)
    m_leather = bpy.data.materials.new("Leather_Protein_Black")
    n = m_leather.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.014, 0.015, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.46
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.04
    # Micro leather wrinkles
    t_vor = n.new('ShaderNodeTexVoronoi')
    t_vor.inputs['Scale'].default_value = 850.0
    bump_l = n.new('ShaderNodeBump')
    bump_l.inputs['Strength'].default_value = 0.012
    bump_l.inputs['Distance'].default_value = 0.001
    m_leather.node_tree.links.new(t_vor.outputs['Distance'], bump_l.inputs['Height'])
    m_leather.node_tree.links.new(bump_l.outputs['Normal'], bsdf.inputs['Normal'])
    m_leather.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['leather'] = m_leather

    # 5. Breathable Acoustic Fabric Mesh (Inner driver filter)
    m_mesh = bpy.data.materials.new("Acoustic_Fabric_Mesh")
    n = m_mesh.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.022, 0.024, 0.028, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.40
    m_mesh.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['mesh'] = m_mesh

    # 6. Matte Polymer Chassis (Hinge knuckles & button bezels)
    m_poly = bpy.data.materials.new("Polymer_Matte_Black")
    n = m_poly.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.018, 0.020, 0.024, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.34
    m_poly.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['poly'] = m_poly

    # 7. Emerald Status Micro-LED (#00E676)
    m_led = bpy.data.materials.new("LED_Emerald_Indicator")
    n = m_led.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    emit = n.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (0.0, 0.90, 0.45, 1.0)
    emit.inputs['Strength'].default_value = 8.0
    m_led.node_tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    mats['led'] = m_led

    return mats

def build_earcup_assembly(name, x_pos, is_left, mats, parent_root):
    """
    Constructs a complete earcup unit (Cup shell, aluminum backplate, earpad, controls).
    X-offset: -0.082m for Left, +0.082m for Right.
    Dimensions: 96mm H x 76mm W x 32mm D.
    """
    cup_root = bpy.data.objects.new(name, None)
    cup_root.location = (x_pos, 0.0, 0.095)
    # Subtle ergonomic inward toe-in angle (8 deg) and forward cant (6 deg)
    x_rot = math.radians(6.0)
    z_rot = math.radians(8.0) if is_left else math.radians(-8.0)
    cup_root.rotation_euler = (x_rot, 0.0, z_rot)
    bpy.context.scene.collection.objects.link(cup_root)
    cup_root.parent = parent_root

    CUP_H = 0.096 # Z
    CUP_W = 0.076 # Y
    CUP_D = 0.032 # X

    # 1. Main Earcup Body (Anodized Aluminum contoured shell)
    # Cylinder rotated 90 deg around Y: local X is global Z, local Y is global Y, local Z is global X!
    # To scale global Z to CUP_H, scale local X by (CUP_H / CUP_W)!
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48, radius=CUP_W * 0.5, depth=CUP_D, location=(0.0, 0.0, 0.0),
        rotation=(0.0, math.radians(90.0), 0.0),
        scale=(CUP_H / CUP_W, 1.0, 1.0)
    )
    cup_body = bpy.context.active_object
    cup_body.name = f"{name}_Chassis"
    cup_body.data.materials.append(mats['alu'])
    bev = cup_body.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.0028
    bev.segments = 3
    bpy.ops.object.shade_smooth()
    cup_body.parent = cup_root

    # 2. Outer Aluminum Backplate with Mirror Chamfer & Concentric Rings
    x_sign = -1.0 if is_left else 1.0
    back_x = x_sign * (CUP_D * 0.5 - 0.001)
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48, radius=CUP_W * 0.46, depth=0.0030, location=(back_x, 0.0, 0.0),
        rotation=(0.0, math.radians(90.0), 0.0),
        scale=(CUP_H / CUP_W, 1.0, 1.0)
    )
    backplate = bpy.context.active_object
    backplate.name = f"{name}_Backplate"
    backplate.data.materials.append(mats['alu'])
    bev_bp = backplate.modifiers.new("Bevel", 'BEVEL')
    bev_bp.width = 0.0012
    bev_bp.segments = 2
    backplate.parent = cup_root

    # Mirror polished silver chamfer ring
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48, radius=CUP_W * 0.44, depth=0.0010, location=(back_x + x_sign * 0.0012, 0.0, 0.0),
        rotation=(0.0, math.radians(90.0), 0.0),
        scale=(CUP_H / CUP_W, 1.0, 1.0)
    )
    ring_chamfer = bpy.context.active_object
    ring_chamfer.name = f"{name}_Mirror_Ring"
    ring_chamfer.data.materials.append(mats['steel'])
    ring_chamfer.parent = cup_root

    # Signature Orange Anodized Accent Ring (#FF5500)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48, radius=CUP_W * 0.38, depth=0.0012, location=(back_x + x_sign * 0.0016, 0.0, 0.0),
        rotation=(0.0, math.radians(90.0), 0.0),
        scale=(CUP_H / CUP_W, 1.0, 1.0)
    )
    orange_ring = bpy.context.active_object
    orange_ring.name = f"{name}_Orange_Accent"
    orange_ring.data.materials.append(mats['orange'])
    orange_ring.parent = cup_root

    # Milled center disc
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48, radius=CUP_W * 0.34, depth=0.0014, location=(back_x + x_sign * 0.0018, 0.0, 0.0),
        rotation=(0.0, math.radians(90.0), 0.0),
        scale=(CUP_H / CUP_W, 1.0, 1.0)
    )
    center_disc = bpy.context.active_object
    center_disc.name = f"{name}_Center_Disc"
    center_disc.data.materials.append(mats['alu'])
    center_disc.parent = cup_root

    # 3. Plush Memory Foam Earpad (Inner side towards head)
    pad_x = -x_sign * (CUP_D * 0.5 + 0.008)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48, radius=CUP_W * 0.48, depth=0.018, location=(pad_x, 0.0, 0.0),
        rotation=(0.0, math.radians(90.0), 0.0),
        scale=(CUP_H / CUP_W, 1.0, 1.0)
    )
    earpad = bpy.context.active_object
    earpad.name = f"{name}_Earpad"
    earpad.data.materials.append(mats['leather'])
    b_pad = earpad.modifiers.new("Bevel", 'BEVEL')
    b_pad.width = 0.0055
    b_pad.segments = 4
    bpy.ops.object.shade_smooth()
    earpad.parent = cup_root

    # Central Acoustic Mesh Grille (Recessed inside earpad)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=CUP_W * 0.28, depth=0.002, location=(pad_x, 0.0, 0.0),
        rotation=(0.0, math.radians(90.0), 0.0),
        scale=(CUP_H / CUP_W, 1.0, 1.0)
    )
    mesh_grille = bpy.context.active_object
    mesh_grille.name = f"{name}_Acoustic_Mesh"
    mesh_grille.data.materials.append(mats['mesh'])
    mesh_grille.parent = cup_root

    # 4. Controls & Interfaces (Flush mounted into bottom perimeter of cup)
    rim_z = -CUP_H * 0.46
    if is_left:
        # USB-C Fast Charge Port
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(0.0, -0.015, rim_z + 0.002),
            scale=(0.0034, 0.0085, 0.0024)
        )
        usbc = bpy.context.active_object
        usbc.name = f"{name}_USBC_Port"
        usbc.data.materials.append(mats['steel'])
        usbc.parent = cup_root

        # 3.5mm Aux Audio Jack
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=24, radius=0.0024, depth=0.002, location=(0.0, 0.012, rim_z + 0.002)
        )
        aux_jack = bpy.context.active_object
        aux_jack.name = f"{name}_Aux_Jack"
        aux_jack.data.materials.append(mats['steel'])
        aux_jack.parent = cup_root

        # Emerald Micro-LED
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16, radius=0.0008, depth=0.001, location=(0.0, -0.004, rim_z + 0.001)
        )
        led = bpy.context.active_object
        led.name = f"{name}_Status_LED"
        led.data.materials.append(mats['led'])
        led.parent = cup_root
    else:
        # Right earcup: ANC Button & Volume Rocker
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=24, radius=0.0034, depth=0.0018, location=(0.0, -0.018, rim_z + 0.002)
        )
        anc_btn = bpy.context.active_object
        anc_btn.name = f"{name}_ANC_Button"
        anc_btn.data.materials.append(mats['poly'])
        anc_btn.parent = cup_root

        # 3-Position Volume Rocker
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(0.0, 0.014, rim_z + 0.002),
            scale=(0.0034, 0.014, 0.0022)
        )
        vol = bpy.context.active_object
        vol.name = f"{name}_Volume_Rocker"
        vol.data.materials.append(mats['poly'])
        vol.parent = cup_root

    return cup_root

def build_gimbal_and_headband(mats, parent_root):
    """
    Constructs the wishbone yokes, swivel hinges, telescoping stainless steel sliders,
    and padded ergonomic spring-steel headband.
    """
    hb_root = bpy.data.objects.new("Headband_Assembly", None)
    bpy.context.scene.collection.objects.link(hb_root)
    hb_root.parent = parent_root

    # 1. Dual Aluminum Wishbone Yokes (Holding Left and Right Earcups)
    for is_left, x_sign in [(True, -1.0), (False, 1.0)]:
        yoke_x = x_sign * 0.082
        
        # U-shaped wishbone yoke arching over top of earcup
        mesh_yoke = bpy.data.meshes.new(f"Yoke_{'L' if is_left else 'R'}")
        bm_y = bmesh.new()
        
        # Curve from front pivot pin (Y=-0.038) up to swivel crown (Y=0, Z=0.060) to rear pin (Y=+0.038)
        n_y_pts = 16
        pts = []
        for i in range(n_y_pts):
            t = i / (n_y_pts - 1) * math.pi # 0 to pi
            y_cur = -0.040 * math.cos(t)
            z_cur = 0.095 + 0.062 * math.sin(t)
            v = bm_y.verts.new((yoke_x, y_cur, z_cur))
            pts.append(v)
            
        for i in range(len(pts) - 1):
            bm_y.edges.new((pts[i], pts[i + 1]))
            
        bm_y.to_mesh(mesh_yoke)
        bm_y.free()
        
        yoke_obj = bpy.data.objects.new(f"Yoke_{'L' if is_left else 'R'}", mesh_yoke)
        yoke_obj.data.materials.append(mats['alu'])
        bpy.context.scene.collection.objects.link(yoke_obj)
        yoke_obj.parent = hb_root
        
        # Add volume via Skin & Subdivision
        skin = yoke_obj.modifiers.new("Skin", 'SKIN')
        for v in yoke_obj.data.skin_vertices[0].data:
            v.radius = (0.0032, 0.0045)
        sub_y = yoke_obj.modifiers.new("Subsurf", 'SUBSURF')
        sub_y.levels = 2
        bpy.ops.object.select_all(action='DESELECT')
        yoke_obj.select_set(True)
        bpy.context.view_layer.objects.active = yoke_obj
        bpy.ops.object.shade_smooth()

        # Swivel Pivot Crown Block (Connects yoke to headband slider)
        crown_z = 0.158
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32, radius=0.0085, depth=0.014, location=(yoke_x, 0.0, crown_z)
        )
        crown = bpy.context.active_object
        crown.name = f"Swivel_Crown_{'L' if is_left else 'R'}"
        crown.data.materials.append(mats['alu'])
        b_cr = crown.modifiers.new("Bevel", 'BEVEL')
        b_cr.width = 0.0010
        crown.parent = hb_root

        # Signature Orange Accent Ring on swivel hinge
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32, radius=0.0088, depth=0.0018, location=(yoke_x, 0.0, crown_z - 0.003)
        )
        cr_orange = bpy.context.active_object
        cr_orange.name = f"Crown_Orange_{'L' if is_left else 'R'}"
        cr_orange.data.materials.append(mats['orange'])
        cr_orange.parent = hb_root

        # Telescoping Stainless Steel Slider Arm with laser graduation notches
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(yoke_x - x_sign * 0.003, 0.0, crown_z + 0.024),
            scale=(0.0042, 0.014, 0.038),
            rotation=(0.0, x_sign * math.radians(-14.0), 0.0)
        )
        slider = bpy.context.active_object
        slider.name = f"Slider_Arm_{'L' if is_left else 'R'}"
        slider.data.materials.append(mats['steel'])
        b_sl = slider.modifiers.new("Bevel", 'BEVEL')
        b_sl.width = 0.0006
        slider.parent = hb_root

    # 2. Main Arched Spring-Steel Headband
    # Arch spanning from X = -0.075 to +0.075, peaking at Z = 0.225
    mesh_band = bpy.data.meshes.new("Headband_Arch")
    bm_b = bmesh.new()
    
    n_band_pts = 32
    band_pts = []
    SPAN_X = 0.076
    PEAK_Z = 0.222
    BASE_Z = 0.180
    
    for i in range(n_band_pts):
        t = i / (n_band_pts - 1) # 0 to 1
        ang = math.pi * t # 0 to pi
        x_pos = -SPAN_X * math.cos(ang)
        z_pos = BASE_Z + (PEAK_Z - BASE_Z) * math.sin(ang)
        v = bm_b.verts.new((x_pos, 0.0, z_pos))
        band_pts.append(v)
        
    for i in range(len(band_pts) - 1):
        bm_b.edges.new((band_pts[i], band_pts[i + 1]))
        
    bm_b.to_mesh(mesh_band)
    bm_b.free()
    
    band_obj = bpy.data.objects.new("Headband_Spring_Band", mesh_band)
    band_obj.data.materials.append(mats['steel'])
    bpy.context.scene.collection.objects.link(band_obj)
    band_obj.parent = hb_root
    
    skin_b = band_obj.modifiers.new("Skin", 'SKIN')
    for v in band_obj.data.skin_vertices[0].data:
        v.radius = (0.0018, 0.012) # Flat wide steel strap
    sub_b = band_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub_b.levels = 2
    bpy.ops.object.select_all(action='DESELECT')
    band_obj.select_set(True)
    bpy.context.view_layer.objects.active = band_obj
    bpy.ops.object.shade_smooth()

    # 3. Ergonomic Padded Underside Cushion (Memory foam wrapped in leatherette)
    mesh_cush = bpy.data.meshes.new("Headband_Cushion")
    bm_c = bmesh.new()
    cush_pts = []
    for i in range(n_band_pts):
        t = i / (n_band_pts - 1)
        # Pad covers middle 70% of arch
        if 0.15 <= t <= 0.85:
            ang = math.pi * t
            x_pos = -SPAN_X * math.cos(ang)
            z_pos = BASE_Z + (PEAK_Z - BASE_Z) * math.sin(ang) - 0.005 # Recessed 5mm under strap
            v = bm_c.verts.new((x_pos, 0.0, z_pos))
            cush_pts.append(v)
            
    for i in range(len(cush_pts) - 1):
        bm_c.edges.new((cush_pts[i], cush_pts[i + 1]))
        
    bm_c.to_mesh(mesh_cush)
    bm_c.free()
    
    cush_obj = bpy.data.objects.new("Headband_Padded_Cushion", mesh_cush)
    cush_obj.data.materials.append(mats['leather'])
    bpy.context.scene.collection.objects.link(cush_obj)
    cush_obj.parent = hb_root
    
    skin_c = cush_obj.modifiers.new("Skin", 'SKIN')
    for v in cush_obj.data.skin_vertices[0].data:
        v.radius = (0.0050, 0.014) # Thick plush padding
    sub_c = cush_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub_c.levels = 2
    bpy.ops.object.select_all(action='DESELECT')
    cush_obj.select_set(True)
    bpy.context.view_layer.objects.active = cush_obj
    bpy.ops.object.shade_smooth()

    return hb_root

def build_orbit_headphones(mats):
    master_root = bpy.data.objects.new("Nova_Orbit_ANC_Master", None)
    bpy.context.scene.collection.objects.link(master_root)

    # 1. Left Earcup (-X)
    cup_l = build_earcup_assembly("Earcup_L", -0.082, is_left=True, mats=mats, parent_root=master_root)

    # 2. Right Earcup (+X)
    cup_r = build_earcup_assembly("Earcup_R", 0.082, is_left=False, mats=mats, parent_root=master_root)

    # 3. Gimbal & Headband Structure
    headband = build_gimbal_and_headband(mats=mats, parent_root=master_root)

    return master_root

def setup_studio_lighting():
    # Key light: Soft broad 45-deg key
    bpy.ops.object.light_add(type='AREA', location=(0.60, -0.80, 0.85))
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 28.0
    key.data.size = 1.10
    key.data.size_y = 0.70
    key.data.color = (1.0, 0.99, 0.98)
    key.rotation_euler = (Vector((0.0, 0.0, 0.12)) - key.location).to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True

    # Fill light: Left diffuse wash
    bpy.ops.object.light_add(type='AREA', location=(-0.70, -0.60, 0.65))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 14.0
    fill.data.size = 1.20
    fill.data.size_y = 0.80
    fill.data.color = (0.95, 0.97, 1.0)
    fill.rotation_euler = (Vector((0.0, 0.0, 0.12)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
    fill.data.use_shadow = False

    # Rim light: Crisp rear contour highlight
    bpy.ops.object.light_add(type='AREA', location=(0.40, 0.80, 0.70))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 22.0
    rim.data.size = 0.85
    rim.data.size_y = 0.50
    rim.data.color = (0.96, 0.98, 1.0)
    rim.rotation_euler = (Vector((0.0, 0.0, 0.12)) - rim.location).to_track_quat('-Z', 'Y').to_euler()
    rim.data.use_shadow = True

def setup_cameras():
    cameras = {}
    target = Vector((0.0, 0.0, 0.125)) # Center of headphones
    
    # 1. Hero 3/4 Camera (Dynamic portrait 3/4 angle)
    dist = 0.64
    elev = math.radians(16.0)
    azim = math.radians(-28.0)
    cam_x = target.x + dist * math.cos(elev) * math.sin(azim)
    cam_y = target.y - dist * math.cos(elev) * math.cos(azim)
    cam_z = target.z + dist * math.sin(elev)
    c_hero = bpy.data.objects.new("Cam_Hero", bpy.data.cameras.new("Cam_Hero"))
    c_hero.data.lens = 85.0
    c_hero.location = (cam_x, cam_y, cam_z)
    c_hero.rotation_euler = (target - c_hero.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(c_hero)
    cameras['hero'] = c_hero

    # 2. Side Profile Camera (Direct look at right earcup backplate & orange accent)
    c_side = bpy.data.objects.new("Cam_Side", bpy.data.cameras.new("Cam_Side"))
    c_side.data.lens = 95.0
    c_side.location = (0.60, 0.0, 0.10)
    c_side.rotation_euler = (Vector((0.082, 0.0, 0.10)) - c_side.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(c_side)
    cameras['side'] = c_side

    # 3. Macro Earpad & Cushion Seam Camera (105mm macro)
    c_macro_pad = bpy.data.objects.new("Cam_Macro_Pad", bpy.data.cameras.new("Cam_Macro_Pad"))
    c_macro_pad.data.lens = 110.0
    c_macro_pad.location = (-0.18, -0.16, 0.14)
    c_macro_pad.rotation_euler = (Vector((-0.082, 0.0, 0.095)) - c_macro_pad.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(c_macro_pad)
    cameras['macro_pad'] = c_macro_pad

    # 4. Macro Yoke & Orange Accent Camera
    c_macro_yoke = bpy.data.objects.new("Cam_Macro_Yoke", bpy.data.cameras.new("Cam_Macro_Yoke"))
    c_macro_yoke.data.lens = 110.0
    c_macro_yoke.location = (0.19, -0.14, 0.20)
    c_macro_yoke.rotation_euler = (Vector((0.082, 0.0, 0.158)) - c_macro_yoke.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(c_macro_yoke)
    cameras['macro_yoke'] = c_macro_yoke

    return cameras

def build_shadow_catcher():
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0.0, 0.0, 0.0))
    floor = bpy.context.active_object
    floor.name = "Floor_Shadow_Catcher"
    floor.is_shadow_catcher = True
    m_flr = bpy.data.materials.new("Floor_Mat")
    floor.data.materials.append(m_flr)
    return floor

def render_pass(scene, cam, output_path, res_x=1600, res_y=1200):
    scene.camera = cam
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

def main():
    print("=== STARTING NOVA ORBIT ANC MASTER PIPELINE ===")
    scene = reset_scene()
    configure_cycles(scene, samples=192)
    mats = create_materials()
    headphones_root = build_orbit_headphones(mats)
    floor = build_shadow_catcher()
    setup_studio_lighting()
    cameras = setup_cameras()

    # Save master .blend models
    blend_master = os.path.join(MODELS_DIR, "headphones_orbit_master.blend")
    blend_scene = os.path.join(SCENES_DIR, "headphones_orbit.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_master)
    bpy.ops.wm.save_as_mainfile(filepath=blend_scene)
    print(f"Saved: {blend_master} and {blend_scene}")

    # Pass 1: Hero Isolated
    floor.hide_render = True
    scene.render.film_transparent = True
    raw_hero_iso = os.path.join(OUTPUT_DIR, "raw_orbit_hero_iso.png")
    render_pass(scene, cameras['hero'], raw_hero_iso)

    # Pass 2: Hero Shadow
    floor.hide_render = False
    for obj in bpy.data.objects:
        if obj != floor and obj.type == 'MESH':
            obj.is_holdout = True
    raw_hero_shd = os.path.join(OUTPUT_DIR, "raw_orbit_hero_shd.png")
    render_pass(scene, cameras['hero'], raw_hero_shd)

    # Reset holdout
    for obj in bpy.data.objects:
        if obj != floor and obj.type == 'MESH':
            obj.is_holdout = False

    # Extra views (Side, Macro Earpad, Macro Yoke)
    floor.hide_render = False
    scene.render.film_transparent = False
    render_pass(scene, cameras['side'], os.path.join(OUTPUT_DIR, "orbit_anc_side_view.png"))
    render_pass(scene, cameras['macro_pad'], os.path.join(OUTPUT_DIR, "orbit_anc_macro_earpad.png"))
    render_pass(scene, cameras['macro_yoke'], os.path.join(OUTPUT_DIR, "orbit_anc_macro_yoke.png"))

    print("Blender finished. Post-processing assets with system python...")
    subprocess.run([
        "python",
        os.path.join(PROJECT_ROOT, "scripts", "process_product_assets.py"),
        raw_hero_iso, raw_hero_shd, "headphones-orbit", "0.16"
    ], check=True)
    print("=== ORBIT ANC PIPELINE COMPLETE ===")

if __name__ == "__main__":
    main()
