"""
NOVA PULSE PRO V3 // Precision Industrial CAD-Quality Gaming Mouse
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)
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

    # 1. Dark Matte Polymer (Shell)
    m_shell = bpy.data.materials.new("Polymer_Chassis_Black")
    n = m_shell.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.016, 0.018, 0.022, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['IOR'].default_value = 1.54
    t_noise = n.new('ShaderNodeTexNoise')
    t_noise.inputs['Scale'].default_value = 1400.0
    t_noise.inputs['Detail'].default_value = 3.0
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.005
    bump.inputs['Distance'].default_value = 0.001
    m_shell.node_tree.links.new(t_noise.outputs['Fac'], bump.inputs['Height'])
    m_shell.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    m_shell.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['shell'] = m_shell

    # 2. Clicks Polymer (Subtle contrast)
    m_btn = bpy.data.materials.new("Polymer_Clicks_Mat")
    n = m_btn.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.013, 0.014, 0.017, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.28
    bsdf.inputs['IOR'].default_value = 1.54
    m_btn.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['btn'] = m_btn

    # 3. Rubber Wheel Tread
    m_rubber = bpy.data.materials.new("Rubber_Wheel_Tread")
    n = m_rubber.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.010, 0.011, 0.013, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.75
    m_rubber.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['rubber'] = m_rubber

    # 4. Metal Wheel Hub
    m_metal = bpy.data.materials.new("Metal_Magnesium_Hub")
    n = m_metal.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.24, 0.26, 0.30, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.20
    m_metal.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['metal'] = m_metal

    # 5. Virgin PTFE Skates
    m_ptfe = bpy.data.materials.new("PTFE_Glide_Skates")
    n = m_ptfe.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.93, 0.96, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.10
    bsdf.inputs['IOR'].default_value = 1.35
    m_ptfe.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['ptfe'] = m_ptfe

    # 6. Ice-Cyan Glow (#00E5FF)
    m_glow = bpy.data.materials.new("LED_Micro_Glow_Cyan")
    n = m_glow.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    emit = n.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (0.0, 0.898, 1.0, 1.0)
    emit.inputs['Strength'].default_value = 10.0
    m_glow.node_tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    mats['glow'] = m_glow

    # 7. Optical Sensor Lens
    m_lens = bpy.data.materials.new("Optical_Glass_Lens")
    n = m_lens.node_tree.nodes
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['Transmission Weight'].default_value = 0.95
    bsdf.inputs['IOR'].default_value = 1.52
    m_lens.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['lens'] = m_lens

    return mats

def build_pulse_mouse(mats):
    root = bpy.data.objects.new("Nova_Pulse_Pro_Master", None)
    bpy.context.scene.collection.objects.link(root)

    # -------------------------------------------------------------------------
    # 1. PROCEDURAL LOFTED SOLID ERGONOMIC BODY
    # -------------------------------------------------------------------------
    # 12 cross sections along Y from front (Y=-0.060) to back (Y=+0.062)
    # Each cross section is an 18-vertex ring from bottom-center to top-center to right to bottom
    sections_y = [
        -0.060, -0.052, -0.040, -0.026, -0.010,
         0.005,  0.020,  0.035,  0.048,  0.056,  0.062
    ]
    
    # Ergonomic parameters per section:
    # (width_left, width_right, height_peak, z_base)
    # Front is low and tapered, waist is gripped, rear hump peaks at Y=0.020
    sec_params = [
        (0.025, 0.024, 0.014, 0.002), # Front lip
        (0.027, 0.026, 0.018, 0.002),
        (0.029, 0.028, 0.024, 0.002),
        (0.030, 0.029, 0.030, 0.002), # Wheel front
        (0.031, 0.030, 0.035, 0.002), # Wheel rear
        (0.032, 0.030, 0.038, 0.002), # Waist
        (0.034, 0.031, 0.040, 0.002), # Peak hump
        (0.033, 0.030, 0.037, 0.002),
        (0.030, 0.028, 0.028, 0.002),
        (0.025, 0.024, 0.018, 0.002),
        (0.016, 0.016, 0.010, 0.002), # Tail tip
    ]

    mesh_body = bpy.data.meshes.new("Mouse_Chassis_Mesh")
    bm = bmesh.new()
    
    n_pts_ring = 24
    rings = []
    
    for idx, y_pos in enumerate(sections_y):
        wl, wr, hp, zb = sec_params[idx]
        ring_verts = []
        for p in range(n_pts_ring):
            # Angle 0 = bottom center, 90 deg = right flank, 180 deg = top crest, 270 deg = left flank
            ang = 2.0 * math.pi * p / n_pts_ring
            sin_a = math.sin(ang)
            cos_a = math.cos(ang)
            
            # Width radius depends on left (-X) vs right (+X)
            w_rad = wr if sin_a >= 0 else wl
            # Thumb rest shelf on left side (-X) near bottom
            if sin_a < -0.5 and cos_a < 0.2:
                w_rad += 0.0035 * (1.0 - abs(y_pos / 0.06))
                
            x = sin_a * w_rad
            
            # Vertical distribution: zb at bottom (cos_a=-1) to hp at top (cos_a=+1)
            # Flatten bottom (cos_a < -0.7) to flat floor
            t_z = (cos_a + 1.0) * 0.5 # 0 (bottom) to 1 (top)
            
            # Right-side ergonomic tilt: top crest leans slightly right
            tilt_x = 0.0018 * math.sin(t_z * math.pi)
            
            if t_z < 0.15:
                z = zb # Flat glide base
            else:
                z = zb + (hp - zb) * (t_z ** 1.15)
                
            v = bm.verts.new((x + tilt_x, y_pos, z))
            ring_verts.append(v)
        rings.append(ring_verts)

    # Bridge rings with quad faces
    for i in range(len(rings) - 1):
        for p in range(n_pts_ring):
            p_next = (p + 1) % n_pts_ring
            v1 = rings[i][p]
            v2 = rings[i][p_next]
            v3 = rings[i + 1][p_next]
            v4 = rings[i + 1][p]
            bm.faces.new((v1, v2, v3, v4))

    # Cap front and back poles
    v_front = bm.verts.new((0.0, sections_y[0] - 0.001, sec_params[0][3] + 0.005))
    for p in range(n_pts_ring):
        p_next = (p + 1) % n_pts_ring
        bm.faces.new((v_front, rings[0][p_next], rings[0][p]))

    v_back = bm.verts.new((0.0, sections_y[-1] + 0.001, sec_params[-1][3] + 0.004))
    for p in range(n_pts_ring):
        p_next = (p + 1) % n_pts_ring
        bm.faces.new((v_back, rings[-1][p], rings[-1][p_next]))

    bm.to_mesh(mesh_body)
    bm.free()

    obj_body = bpy.data.objects.new("Mouse_Body", mesh_body)
    obj_body.data.materials.append(mats['shell'])
    bpy.context.scene.collection.objects.link(obj_body)
    obj_body.parent = root

    bpy.ops.object.select_all(action='DESELECT')
    obj_body.select_set(True)
    bpy.context.view_layer.objects.active = obj_body
    bpy.ops.object.shade_smooth()

    sub = obj_body.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2

    # -------------------------------------------------------------------------
    # 2. BOOLEAN CUTTERS FOR REALISTIC SPLIT CLICKS & WHEEL WELL
    # -------------------------------------------------------------------------
    # Center separation trench cutter (1.6mm wide, cuts from front to mid-mouse)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.0, -0.035, 0.025),
        scale=(0.0016, 0.055, 0.035)
    )
    c_trench = bpy.context.active_object
    c_trench.name = "Cutter_Trench"
    c_trench.hide_render = True
    c_trench.hide_viewport = True

    # Wheel well cavity cutter (10mm wide, 24mm long)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.0, -0.026, 0.028),
        scale=(0.0102, 0.025, 0.022)
    )
    c_well = bpy.context.active_object
    c_well.name = "Cutter_Well"
    c_well.hide_render = True
    c_well.hide_viewport = True

    # Apply cutters to main body
    mod_tr = obj_body.modifiers.new("Cut_Trench", 'BOOLEAN')
    mod_tr.object = c_trench
    mod_tr.operation = 'DIFFERENCE'

    mod_wl = obj_body.modifiers.new("Cut_Well", 'BOOLEAN')
    mod_wl.object = c_well
    mod_wl.operation = 'DIFFERENCE'

    # -------------------------------------------------------------------------
    # 3. HIGH-END SCROLL WHEEL ASSEMBLY
    # -------------------------------------------------------------------------
    WHEEL_R = 0.0135
    WHEEL_W = 0.0066
    wheel_center = Vector((0.0, -0.026, 0.026))

    # Internal well lining box
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.0, -0.026, 0.022),
        scale=(0.0098, 0.024, 0.015)
    )
    well_liner = bpy.context.active_object
    well_liner.name = "Wheel_Well_Liner"
    well_liner.data.materials.append(mats['btn'])
    well_liner.parent = root

    # Steel Axle
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0018, depth=WHEEL_W * 1.8, location=wheel_center,
        rotation=(0.0, math.radians(90.0), 0.0)
    )
    axle = bpy.context.active_object
    axle.name = "Wheel_Axle"
    axle.data.materials.append(mats['metal'])
    axle.parent = root

    # Magnesium Skeletal Inner Hub
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48, radius=WHEEL_R * 0.82, depth=WHEEL_W * 0.88, location=wheel_center,
        rotation=(0.0, math.radians(90.0), 0.0)
    )
    hub = bpy.context.active_object
    hub.name = "Wheel_Hub"
    hub.data.materials.append(mats['metal'])
    bev_h = hub.modifiers.new("Bevel", 'BEVEL')
    bev_h.width = 0.0006
    hub.parent = root

    # Knurled Rubber Tire (64 vertices with micro-ribbing)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=WHEEL_R, depth=WHEEL_W, location=wheel_center,
        rotation=(0.0, math.radians(90.0), 0.0)
    )
    tire = bpy.context.active_object
    tire.name = "Wheel_Tire"
    tire.data.materials.append(mats['rubber'])
    bev_t = tire.modifiers.new("Bevel", 'BEVEL')
    bev_t.width = 0.0008
    bev_t.segments = 2
    tire.parent = root

    # Cyan Micro-Glow Halo
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=WHEEL_R * 0.68, depth=0.0010,
        location=(0.0, wheel_center.y, wheel_center.z - 0.002),
        rotation=(0.0, math.radians(90.0), 0.0)
    )
    halo = bpy.context.active_object
    halo.name = "Wheel_Cyan_Glow"
    halo.data.materials.append(mats['glow'])
    halo.parent = root

    # -------------------------------------------------------------------------
    # 4. DUAL SIDE BUTTONS (Forward & Back on left thumb flank)
    # -------------------------------------------------------------------------
    def add_side_btn(name, y_loc):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(-0.0305, y_loc, 0.022),
            scale=(0.0032, 0.0095, 0.0045),
            rotation=(0.0, math.radians(14.0), math.radians(-4.0))
        )
        sb = bpy.context.active_object
        sb.name = name
        sb.data.materials.append(mats['btn'])
        b = sb.modifiers.new("Bevel", 'BEVEL')
        b.width = 0.0008
        b.segments = 3
        bpy.ops.object.shade_smooth()
        sb.parent = root
        return sb

    add_side_btn("Mouse_Side_Forward", -0.006)
    add_side_btn("Mouse_Side_Back", 0.015)

    # -------------------------------------------------------------------------
    # 5. UNDERSIDE SENSOR & VIRGIN PTFE SKATES
    # -------------------------------------------------------------------------
    # Baseplate rim
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.028, depth=0.0016, location=(0.0, 0.0, 0.0010),
        scale=(1.0, 1.85, 1.0)
    )
    bp = bpy.context.active_object
    bp.name = "Underside_BasePlate"
    bp.data.materials.append(mats['btn'])
    bp.parent = root

    # Sensor Aperture & Lens
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.0075, depth=0.0018, location=(0.0, -0.002, 0.0006)
    )
    sensor_bz = bpy.context.active_object
    sensor_bz.name = "Sensor_Bezel"
    sensor_bz.data.materials.append(mats['shell'])
    sensor_bz.parent = root

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.0032, depth=0.0014, location=(0.0, -0.002, 0.0009)
    )
    sensor_ln = bpy.context.active_object
    sensor_ln.name = "Sensor_Lens"
    sensor_ln.data.materials.append(mats['lens'])
    sensor_ln.parent = root

    # PTFE Skate 1: Front Curve
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.016, depth=0.0008, location=(0.0, -0.044, 0.0004),
        scale=(1.25, 0.50, 1.0)
    )
    sk_f = bpy.context.active_object
    sk_f.name = "PTFE_Skate_Front"
    sk_f.data.materials.append(mats['ptfe'])
    b_skf = sk_f.modifiers.new("Bevel", 'BEVEL')
    b_skf.width = 0.0004
    sk_f.parent = root

    # PTFE Skate 2: Rear Horseshoe
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.020, depth=0.0008, location=(0.0, 0.040, 0.0004),
        scale=(1.15, 0.55, 1.0)
    )
    sk_r = bpy.context.active_object
    sk_r.name = "PTFE_Skate_Rear"
    sk_r.data.materials.append(mats['ptfe'])
    b_skr = sk_r.modifiers.new("Bevel", 'BEVEL')
    b_skr.width = 0.0004
    sk_r.parent = root

    # PTFE Skate 3: Sensor Ring
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.010, depth=0.0008, location=(0.0, -0.002, 0.0004)
    )
    sk_m = bpy.context.active_object
    sk_m.name = "PTFE_Skate_Sensor_Ring"
    sk_m.data.materials.append(mats['ptfe'])
    sk_m.parent = root

    # 3-Way Mode Switch & DPI Button
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-0.013, -0.015, 0.0008),
        scale=(0.0048, 0.0030, 0.0012)
    )
    sw_box = bpy.context.active_object
    sw_box.name = "Underside_Switch"
    sw_box.data.materials.append(mats['btn'])
    sw_box.parent = root

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.0026, depth=0.0012, location=(0.013, -0.015, 0.0008)
    )
    dpi_btn = bpy.context.active_object
    dpi_btn.name = "Underside_DPI"
    dpi_btn.data.materials.append(mats['btn'])
    dpi_btn.parent = root

    return root

def setup_studio_lighting():
    # Key light: Soft broad overhead softbox
    bpy.ops.object.light_add(type='AREA', location=(0.40, -0.60, 0.75))
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 26.0
    key.data.size = 0.90
    key.data.size_y = 0.60
    key.data.color = (1.0, 0.99, 0.98)
    key.rotation_euler = (Vector((0.0, 0.0, 0.02)) - key.location).to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True

    # Fill light: Left subtle wash
    bpy.ops.object.light_add(type='AREA', location=(-0.55, -0.40, 0.50))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 11.0
    fill.data.size = 0.95
    fill.data.size_y = 0.65
    fill.data.color = (0.95, 0.97, 1.0)
    fill.rotation_euler = (Vector((0.0, 0.0, 0.02)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
    fill.data.use_shadow = False

    # Rim light: Crisp rear edge contour
    bpy.ops.object.light_add(type='AREA', location=(0.30, 0.65, 0.45))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 18.0
    rim.data.size = 0.70
    rim.data.size_y = 0.35
    rim.data.color = (0.96, 0.98, 1.0)
    rim.rotation_euler = (Vector((0.0, 0.0, 0.02)) - rim.location).to_track_quat('-Z', 'Y').to_euler()
    rim.data.use_shadow = True

def setup_cameras():
    cameras = {}
    target = Vector((0.0, -0.005, 0.018))
    
    # Hero 3/4
    dist = 0.34
    elev = math.radians(32.0)
    azim = math.radians(-34.0)
    cam_x = target.x + dist * math.cos(elev) * math.sin(azim)
    cam_y = target.y - dist * math.cos(elev) * math.cos(azim)
    cam_z = target.z + dist * math.sin(elev)
    c_hero = bpy.data.objects.new("Cam_Hero", bpy.data.cameras.new("Cam_Hero"))
    c_hero.data.lens = 78.0
    c_hero.location = (cam_x, cam_y, cam_z)
    c_hero.rotation_euler = (target - c_hero.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(c_hero)
    cameras['hero'] = c_hero

    # Side Profile
    c_side = bpy.data.objects.new("Cam_Side", bpy.data.cameras.new("Cam_Side"))
    c_side.data.lens = 85.0
    c_side.location = (-0.38, 0.0, 0.022)
    c_side.rotation_euler = (Vector((0.0, 0.0, 0.020)) - c_side.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(c_side)
    cameras['side'] = c_side

    # Macro Wheel
    c_macro = bpy.data.objects.new("Cam_Macro", bpy.data.cameras.new("Cam_Macro"))
    c_macro.data.lens = 110.0
    c_macro.location = (0.09, -0.16, 0.075)
    c_macro.rotation_euler = (Vector((0.0, -0.026, 0.025)) - c_macro.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(c_macro)
    cameras['macro'] = c_macro

    # Bottom Engineering
    c_bot = bpy.data.objects.new("Cam_Bottom", bpy.data.cameras.new("Cam_Bottom"))
    c_bot.data.lens = 85.0
    c_bot.location = (0.0, 0.0, -0.38)
    c_bot.rotation_euler = (0.0, math.radians(180.0), math.radians(90.0))
    bpy.context.scene.collection.objects.link(c_bot)
    cameras['bottom'] = c_bot

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
    print("=== STARTING NOVA PULSE PRO V3 PIPELINE ===")
    scene = reset_scene()
    configure_cycles(scene, samples=192)
    mats = create_materials()
    mouse_root = build_pulse_mouse(mats)
    floor = build_shadow_catcher()
    setup_studio_lighting()
    cameras = setup_cameras()

    # Save master .blend files
    blend_master = os.path.join(MODELS_DIR, "mouse_pulse_master.blend")
    blend_scene = os.path.join(SCENES_DIR, "mouse_pulse.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_master)
    bpy.ops.wm.save_as_mainfile(filepath=blend_scene)
    print(f"Saved: {blend_master} and {blend_scene}")

    # Pass 1: Hero Isolated
    floor.hide_render = True
    scene.render.film_transparent = True
    raw_hero_iso = os.path.join(OUTPUT_DIR, "raw_pulse_hero_iso.png")
    render_pass(scene, cameras['hero'], raw_hero_iso)

    # Pass 2: Hero Shadow
    floor.hide_render = False
    for obj in bpy.data.objects:
        if obj != floor and obj.type == 'MESH':
            obj.is_holdout = True
    raw_hero_shd = os.path.join(OUTPUT_DIR, "raw_pulse_hero_shd.png")
    render_pass(scene, cameras['hero'], raw_hero_shd)

    # Reset holdout
    for obj in bpy.data.objects:
        if obj != floor and obj.type == 'MESH':
            obj.is_holdout = False

    # Extra views
    floor.hide_render = False
    scene.render.film_transparent = False
    render_pass(scene, cameras['side'], os.path.join(OUTPUT_DIR, "pulse_pro_side_view.png"))
    render_pass(scene, cameras['macro'], os.path.join(OUTPUT_DIR, "pulse_pro_macro_wheel.png"))

    floor.hide_render = True
    render_pass(scene, cameras['bottom'], os.path.join(OUTPUT_DIR, "pulse_pro_bottom_engineering.png"))

    print("Blender finished. Post-processing assets with system python...")
    subprocess.run([
        "python",
        os.path.join(PROJECT_ROOT, "scripts", "process_product_assets.py"),
        raw_hero_iso, raw_hero_shd, "mouse-pulse", "0.18"
    ], check=True)
    print("=== PULSE PRO V3 COMPLETE ===")

if __name__ == "__main__":
    main()
