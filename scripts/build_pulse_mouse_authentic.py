"""
PULSE PRO WIRELESS MOUSE // Authentic 3D Master Model & Renders
100% faithful recreation of original design (media_1791575583430_5b6e195d.jpg)
- Wide ergonomic thumb rest shelf on the lower left
- High arched palm shell sloping down to the right
- Split left/right clicks with ergonomic finger grooves
- Diamond-knurled metal/rubber wheel with illuminated cyan/blue LED neon ring
- 'PULSE PRO' branding pad-print on the top shell
- Dual side buttons (G1, G2) + lower thumb paddle button
- Recessed front USB-C port
- Cycles GPU / OptiX photorealistic studio rendering
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"D:\Projects\ууу"
MODELS_DIR = os.path.join(PROJECT_ROOT, "assets", "models")
SCENES_DIR = os.path.join(PROJECT_ROOT, "assets", "scenes")
PREVIEWS_DIR = os.path.join(PROJECT_ROOT, "assets", "previews")
IMAGES_DIR = os.path.join(PROJECT_ROOT, "assets", "images")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SCENES_DIR, exist_ok=True)
os.makedirs(PREVIEWS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Studio_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        # Warm neutral background matching reference photo (#F5EFEB)
        bg.inputs['Color'].default_value = (0.91, 0.89, 0.84, 1.0)
        bg.inputs['Strength'].default_value = 0.95
    return scene

def configure_cycles(scene, samples=64):
    scene.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = (dev.type == 'OPTIX')
    scene.cycles.device = 'GPU'
    scene.cycles.samples = samples
    scene.cycles.preview_samples = 16
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'

def create_materials():
    mats = {}

    # 1. Premium Matte Black Shell (#1C1D21) with fine micro-grain
    m_body = bpy.data.materials.new("Mouse_Body_MatteBlack")
    m_body.use_nodes = True
    nodes = m_body.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.024, 0.025, 0.028, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.38
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['IOR'].default_value = 1.48
    
    # Micro noise bump
    t_noise = nodes.new('ShaderNodeTexNoise')
    t_noise.inputs['Scale'].default_value = 850.0
    t_noise.inputs['Detail'].default_value = 4.0
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.015
    bump.inputs['Distance'].default_value = 0.001
    m_body.node_tree.links.new(t_noise.outputs['Fac'], bump.inputs['Height'])
    m_body.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    m_body.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['body'] = m_body

    # 2. Side Grip Satin Polymer (#18191C)
    m_grip = bpy.data.materials.new("Mouse_Grip_Satin")
    m_grip.use_nodes = True
    g_nodes = m_grip.node_tree.nodes
    g_nodes.clear()
    g_out = g_nodes.new('ShaderNodeOutputMaterial')
    g_bsdf = g_nodes.new('ShaderNodeBsdfPrincipled')
    g_bsdf.inputs['Base Color'].default_value = (0.018, 0.019, 0.021, 1.0)
    g_bsdf.inputs['Roughness'].default_value = 0.45
    g_bsdf.inputs['Metallic'].default_value = 0.0
    g_nodes.new('ShaderNodeBump')
    g_noise = g_nodes.new('ShaderNodeTexNoise')
    g_noise.inputs['Scale'].default_value = 1200.0
    g_bump = g_nodes.get('Bump')
    g_bump.inputs['Strength'].default_value = 0.025
    g_grip_links = m_grip.node_tree.links
    g_grip_links.new(g_noise.outputs['Fac'], g_bump.inputs['Height'])
    g_grip_links.new(g_bump.outputs['Normal'], g_bsdf.inputs['Normal'])
    g_grip_links.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])
    mats['grip'] = m_grip

    # 3. Knurled Metal Wheel Tire (Gunmetal Titanium)
    m_knurl = bpy.data.materials.new("Wheel_Knurled_Metal")
    m_knurl.use_nodes = True
    k_nodes = m_knurl.node_tree.nodes
    k_nodes.clear()
    k_out = k_nodes.new('ShaderNodeOutputMaterial')
    k_bsdf = k_nodes.new('ShaderNodeBsdfPrincipled')
    k_bsdf.inputs['Base Color'].default_value = (0.05, 0.055, 0.06, 1.0)
    k_bsdf.inputs['Metallic'].default_value = 0.95
    k_bsdf.inputs['Roughness'].default_value = 0.32
    # Procedural knurling texture
    k_voronoi = k_nodes.new('ShaderNodeTexVoronoi')
    k_voronoi.feature = 'F1'
    k_voronoi.distance = 'MANHATTAN'
    k_voronoi.inputs['Scale'].default_value = 240.0
    k_bump = k_nodes.new('ShaderNodeBump')
    k_bump.inputs['Strength'].default_value = 0.12
    k_bump.inputs['Distance'].default_value = 0.002
    m_knurl.node_tree.links.new(k_voronoi.outputs['Distance'], k_bump.inputs['Height'])
    m_knurl.node_tree.links.new(k_bump.outputs['Normal'], k_bsdf.inputs['Normal'])
    m_knurl.node_tree.links.new(k_bsdf.outputs['BSDF'], k_out.inputs['Surface'])
    mats['wheel_knurl'] = m_knurl

    # 4. Cyan Neon Glowing LED Ring (#00E5FF)
    m_cyan = bpy.data.materials.new("LED_Cyan_Neon")
    m_cyan.use_nodes = True
    c_nodes = m_cyan.node_tree.nodes
    c_nodes.clear()
    c_out = c_nodes.new('ShaderNodeOutputMaterial')
    c_emit = c_nodes.new('ShaderNodeEmission')
    c_emit.inputs['Color'].default_value = (0.0, 0.85, 1.0, 1.0)
    c_emit.inputs['Strength'].default_value = 10.0
    m_cyan.node_tree.links.new(c_emit.outputs['Emission'], c_out.inputs['Surface'])
    mats['cyan_led'] = m_cyan

    # 5. Silver Pad-Print Branding ('PULSE PRO', G1, G2)
    m_print = bpy.data.materials.new("Print_Silver")
    m_print.use_nodes = True
    p_nodes = m_print.node_tree.nodes
    p_nodes.clear()
    p_out = p_nodes.new('ShaderNodeOutputMaterial')
    p_bsdf = p_nodes.new('ShaderNodeBsdfPrincipled')
    p_bsdf.inputs['Base Color'].default_value = (0.75, 0.78, 0.82, 1.0)
    p_bsdf.inputs['Metallic'].default_value = 0.5
    p_bsdf.inputs['Roughness'].default_value = 0.3
    m_print.node_tree.links.new(p_bsdf.outputs['BSDF'], p_out.inputs['Surface'])
    mats['print'] = m_print

    # 6. Smooth Gloss Accent Plastic (Interior well & seams)
    m_gloss = bpy.data.materials.new("Mouse_Interior_Gloss")
    m_gloss.use_nodes = True
    gl_nodes = m_gloss.node_tree.nodes
    gl_nodes.clear()
    gl_out = gl_nodes.new('ShaderNodeOutputMaterial')
    gl_bsdf = gl_nodes.new('ShaderNodeBsdfPrincipled')
    gl_bsdf.inputs['Base Color'].default_value = (0.015, 0.016, 0.018, 1.0)
    gl_bsdf.inputs['Roughness'].default_value = 0.15
    m_gloss.node_tree.links.new(gl_bsdf.outputs['BSDF'], gl_out.inputs['Surface'])
    mats['interior_gloss'] = m_gloss

    # 7. Warm Studio Floor
    m_floor = bpy.data.materials.new("Studio_Floor_Beige")
    m_floor.use_nodes = True
    fl_nodes = m_floor.node_tree.nodes
    fl_nodes.clear()
    fl_out = fl_nodes.new('ShaderNodeOutputMaterial')
    fl_bsdf = fl_nodes.new('ShaderNodeBsdfPrincipled')
    fl_bsdf.inputs['Base Color'].default_value = (0.88, 0.85, 0.80, 1.0)
    fl_bsdf.inputs['Roughness'].default_value = 0.65
    m_floor.node_tree.links.new(fl_bsdf.outputs['BSDF'], fl_out.inputs['Surface'])
    mats['floor'] = m_floor

    return mats

def build_pulse_mouse(mats):
    root = bpy.data.objects.new("Pulse_Pro_Master", None)
    bpy.context.collection.objects.link(root)

    # -------------------------------------------------------------------------
    # 1. MAIN ASYMMETRIC ERGONOMIC PALM SHELL WITH THUMB REST WING
    # -------------------------------------------------------------------------
    bm = bmesh.new()

    # We construct a high-precision quad-mesh cage for subdivision surface:
    # Length: Y from -0.064m (rear tail) to +0.060m (front nose) -> 124mm
    # Width: X from -0.046m (thumb wing tip) to +0.034m (right side) -> 80mm
    # Height: Z from 0.000m (skates base) to +0.043m (palm apex) -> 43mm

    u_steps = 14
    v_steps = 20
    verts_grid = []

    for v_i in range(v_steps):
        v_ratio = v_i / float(v_steps - 1) # 0 (front) to 1 (rear)
        y = 0.060 - v_ratio * 0.124

        row_verts = []
        for u_i in range(u_steps):
            u_ratio = u_i / float(u_steps - 1) # 0 (left / thumb side) to 1 (right)

            # Profile width variations
            # Front nose narrows:
            front_taper = 0.55 + 0.45 * math.sin(v_ratio * math.pi)
            if v_ratio < 0.25:
                front_taper = 0.55 + 0.45 * (v_ratio / 0.25)
            elif v_ratio > 0.75:
                front_taper = 0.55 + 0.45 * ((1.0 - v_ratio) / 0.25)

            # Left wing extends prominently between v_ratio = 0.35 and 0.80 (thumb rest area):
            wing_factor = 0.0
            if 0.25 <= v_ratio <= 0.85:
                wing_norm = (v_ratio - 0.25) / 0.60
                wing_factor = math.sin(wing_norm * math.pi) ** 1.5

            left_x = -0.032 - (wing_factor * 0.016) # flares to -0.048m
            right_x = 0.034 * front_taper

            x = left_x + u_ratio * (right_x - left_x)

            # Height Z distribution:
            # Palm crest peaks at v_ratio = 0.55, biased towards left (thumb side at u_ratio ~ 0.38)
            y_arch = math.sin(v_ratio * math.pi * 0.88 + 0.12)
            if v_ratio < 0.20:
                y_arch = 0.30 + 0.70 * (v_ratio / 0.20)

            # Ergonomic tilt: left side (u ~ 0.35) is higher than right side (u ~ 1.0)
            lateral_arch = math.sin(u_ratio * math.pi)
            # Add ergonomic slant (drops ~5mm towards right):
            tilt_drop = (u_ratio - 0.35) * 0.007 if u_ratio > 0.35 else 0.0

            # Thumb wing remains close to floor (Z ~ 2mm .. 7mm) on the outer edge (u_ratio < 0.15)
            if u_ratio < 0.18 and wing_factor > 0.1:
                z = 0.002 + (u_ratio / 0.18) * 0.010 * wing_factor
            else:
                z = max(0.001, (y_arch * 0.042 * lateral_arch) - tilt_drop)
                # Front click ramp slopes down to 14mm at the nose
                if v_ratio < 0.20:
                    z *= (0.35 + 0.65 * (v_ratio / 0.20))

            vert = bm.verts.new((x, y, z))
            row_verts.append(vert)
        verts_grid.append(row_verts)

    # Create quad faces
    for v_i in range(v_steps - 1):
        for u_i in range(u_steps - 1):
            v0 = verts_grid[v_i][u_i]
            v1 = verts_grid[v_i][u_i + 1]
            v2 = verts_grid[v_i + 1][u_i + 1]
            v3 = verts_grid[v_i + 1][u_i]
            bm.faces.new((v0, v1, v2, v3))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("Pulse_Pro_Shell_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    shell_obj = bpy.data.objects.new("Pulse_Pro_Body", mesh)
    bpy.context.collection.objects.link(shell_obj)
    shell_obj.parent = root

    # Subdivision surface modifier for silky smooth organic curves
    subsurf = shell_obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    shell_obj.data.materials.append(mats['body'])

    # -------------------------------------------------------------------------
    # 2. SEPARATE LEFT AND RIGHT CLICK PANELS (SPLIT BUTTONS)
    # -------------------------------------------------------------------------
    # Left Click Button (with finger concave scoop)
    bm_l = bmesh.new()
    bmesh.ops.create_cube(bm_l, size=1.0)
    # Scale and contour to left front
    for v in bm_l.verts:
        v.co.x = -0.017 + v.co.x * 0.014
        v.co.y = 0.034 + v.co.y * 0.026
        v.co.z = 0.021 + v.co.z * 0.007
        # Finger scoop: concave dip along center
        if abs(v.co.x - (-0.017)) < 0.008:
            v.co.z -= 0.0015
    mesh_l = bpy.data.meshes.new("Left_Click_Mesh")
    bm_l.to_mesh(mesh_l)
    bm_l.free()
    l_click = bpy.data.objects.new("Left_Click_Panel", mesh_l)
    bpy.context.collection.objects.link(l_click)
    l_click.parent = root
    sub_l = l_click.modifiers.new("Subsurf", 'SUBSURF')
    sub_l.levels = 2
    l_click.data.materials.append(mats['body'])

    # Right Click Button (sloping to right)
    bm_r = bmesh.new()
    bmesh.ops.create_cube(bm_r, size=1.0)
    for v in bm_r.verts:
        v.co.x = 0.017 + v.co.x * 0.014
        v.co.y = 0.034 + v.co.y * 0.026
        v.co.z = 0.018 + v.co.z * 0.007
        # Slanted ergonomic drop
        v.co.z -= (v.co.x - 0.005) * 0.12
    mesh_r = bpy.data.meshes.new("Right_Click_Mesh")
    bm_r.to_mesh(mesh_r)
    bm_r.free()
    r_click = bpy.data.objects.new("Right_Click_Panel", mesh_r)
    bpy.context.collection.objects.link(r_click)
    r_click.parent = root
    sub_r = r_click.modifiers.new("Subsurf", 'SUBSURF')
    sub_r.levels = 2
    r_click.data.materials.append(mats['body'])

    # -------------------------------------------------------------------------
    # 3. SCROLL WHEEL CAVITY & RECESSED WELL
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.032, 0.020))
    well = bpy.context.active_object
    well.name = "Wheel_Cavity"
    well.scale = (0.013, 0.030, 0.016)
    well.parent = root
    well.data.materials.append(mats['interior_gloss'])

    # -------------------------------------------------------------------------
    # 4. SCROLL WHEEL ASSEMBLY (KNURLED TIRE + DUAL CYAN NEON GLOW RINGS)
    # -------------------------------------------------------------------------
    # Wheel Center: knurled metal tire
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.0125, depth=0.0075,
        location=(0.0, 0.033, 0.024),
        rotation=(0, math.radians(90), 0)
    )
    wheel = bpy.context.active_object
    wheel.name = "Scroll_Wheel_Tire"
    wheel.parent = root
    bev_w = wheel.modifiers.new("Bevel", 'BEVEL')
    bev_w.width = 0.0008
    bev_w.segments = 3
    wheel.data.materials.append(mats['wheel_knurl'])

    # Cyan Neon LED Ring (Left side of wheel)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.0122, minor_radius=0.0007,
        major_segments=32, minor_segments=12,
        location=(-0.0042, 0.033, 0.024),
        rotation=(0, math.radians(90), 0)
    )
    ring_l = bpy.context.active_object
    ring_l.name = "Wheel_Neon_Ring_L"
    ring_l.parent = root
    ring_l.data.materials.append(mats['cyan_led'])

    # Cyan Neon LED Ring (Right side of wheel)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.0122, minor_radius=0.0007,
        major_segments=32, minor_segments=12,
        location=(0.0042, 0.033, 0.024),
        rotation=(0, math.radians(90), 0)
    )
    ring_r = bpy.context.active_object
    ring_r.name = "Wheel_Neon_Ring_R"
    ring_r.parent = root
    ring_r.data.materials.append(mats['cyan_led'])

    # Rear cyan indicator dash line behind wheel
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.0, 0.017, 0.027)
    )
    dash = bpy.context.active_object
    dash.name = "Wheel_LED_Dash"
    dash.scale = (0.0010, 0.0050, 0.0008)
    dash.parent = root
    dash.data.materials.append(mats['cyan_led'])

    # -------------------------------------------------------------------------
    # 5. SIDE THUMB BUTTONS (G1, G2) & LOWER THUMB PADDLE
    # -------------------------------------------------------------------------
    # G1 Button (Forward thumb button)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-0.028, 0.012, 0.024),
        rotation=(math.radians(12), math.radians(-24), math.radians(-14))
    )
    g1 = bpy.context.active_object
    g1.name = "Button_G1"
    g1.scale = (0.0035, 0.010, 0.0045)
    g1.parent = root
    b_g1 = g1.modifiers.new("Bevel", 'BEVEL')
    b_g1.width = 0.0008
    b_g1.segments = 3
    g1.data.materials.append(mats['body'])

    # G2 Button (Rear thumb button)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-0.033, -0.002, 0.024),
        rotation=(math.radians(8), math.radians(-26), math.radians(-18))
    )
    g2 = bpy.context.active_object
    g2.name = "Button_G2"
    g2.scale = (0.0035, 0.009, 0.0045)
    g2.parent = root
    b_g2 = g2.modifiers.new("Bevel", 'BEVEL')
    b_g2.width = 0.0008
    b_g2.segments = 3
    g2.data.materials.append(mats['body'])

    # Lower Thumb Paddle Button (on thumb wing shelf)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-0.036, -0.012, 0.011),
        rotation=(math.radians(-6), math.radians(-32), math.radians(-8))
    )
    g_paddle = bpy.context.active_object
    g_paddle.name = "Button_Thumb_Paddle"
    g_paddle.scale = (0.0030, 0.0080, 0.0065)
    g_paddle.parent = root
    b_pad = g_paddle.modifiers.new("Bevel", 'BEVEL')
    b_pad.width = 0.0010
    b_pad.segments = 3
    g_paddle.data.materials.append(mats['body'])

    # -------------------------------------------------------------------------
    # 6. 'PULSE PRO' PAD-PRINT BRANDING TEXT (3D EMBOSSED PLATE)
    # -------------------------------------------------------------------------
    # Text curve converted to mesh on the left ridge
    curve_data = bpy.data.curves.new(name="PulseProTextData", type='FONT')
    curve_data.body = "PULSE PRO"
    curve_data.size = 0.0042
    curve_data.extrude = 0.0003
    text_obj = bpy.data.objects.new("Brand_Pulse_Pro_Text", curve_data)
    bpy.context.collection.objects.link(text_obj)
    text_obj.parent = root
    # Position along left palm ramp matching photo
    text_obj.location = Vector((-0.019, 0.005, 0.0315))
    text_obj.rotation_euler = Euler((math.radians(32), math.radians(-18), math.radians(14)))
    text_obj.data.materials.append(mats['print'])

    # Small G1 and G2 button text labels
    g1_text_data = bpy.data.curves.new(name="G1TextData", type='FONT')
    g1_text_data.body = "G1"
    g1_text_data.size = 0.0018
    g1_text_data.extrude = 0.0002
    g1_text_obj = bpy.data.objects.new("Label_G1", g1_text_data)
    bpy.context.collection.objects.link(g1_text_obj)
    g1_text_obj.parent = root
    g1_text_obj.location = Vector((-0.030, 0.009, 0.024))
    g1_text_obj.rotation_euler = Euler((math.radians(12), math.radians(-24), math.radians(-14)))
    g1_text_obj.data.materials.append(mats['print'])

    g2_text_data = bpy.data.curves.new(name="G2TextData", type='FONT')
    g2_text_data.body = "G2"
    g2_text_data.size = 0.0018
    g2_text_data.extrude = 0.0002
    g2_text_obj = bpy.data.objects.new("Label_G2", g2_text_data)
    bpy.context.collection.objects.link(g2_text_obj)
    g2_text_obj.parent = root
    g2_text_obj.location = Vector((-0.035, -0.005, 0.024))
    g2_text_obj.rotation_euler = Euler((math.radians(8), math.radians(-26), math.radians(-18)))
    g2_text_obj.data.materials.append(mats['print'])

    # -------------------------------------------------------------------------
    # 7. FRONT USB-C RECESSED PORT & NOSE CUTOUT
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.0035, depth=0.008,
        location=(0.0, 0.059, 0.0065),
        rotation=(math.radians(90), 0, 0)
    )
    port = bpy.context.active_object
    port.name = "Front_USBC_Port"
    port.scale = (1.8, 1.0, 0.7)
    port.parent = root
    port.data.materials.append(mats['interior_gloss'])

    # -------------------------------------------------------------------------
    # 8. BOTTOM SKATES & PIXART PAW3395 SENSOR RING
    # -------------------------------------------------------------------------
    # Front curved PTFE skate
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.016, depth=0.0008,
        location=(0.0, 0.046, 0.0004)
    )
    skate_f = bpy.context.active_object
    skate_f.name = "PTFE_Skate_Front"
    skate_f.scale = (1.2, 0.6, 1.0)
    skate_f.parent = root
    skate_f.data.materials.append(mats['interior_gloss'])

    # Rear curved PTFE skate
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=0.020, depth=0.0008,
        location=(0.0, -0.046, 0.0004)
    )
    skate_r = bpy.context.active_object
    skate_r.name = "PTFE_Skate_Rear"
    skate_r.scale = (1.3, 0.7, 1.0)
    skate_r.parent = root
    skate_r.data.materials.append(mats['interior_gloss'])

    # Thumb wing PTFE skate
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.010, depth=0.0008,
        location=(-0.034, -0.006, 0.0004)
    )
    skate_w = bpy.context.active_object
    skate_w.name = "PTFE_Skate_Wing"
    skate_w.scale = (0.7, 1.4, 1.0)
    skate_w.parent = root
    skate_w.data.materials.append(mats['interior_gloss'])

    # Sensor ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.006, minor_radius=0.001,
        location=(0.0, 0.002, 0.0004)
    )
    sensor = bpy.context.active_object
    sensor.name = "Sensor_Aperture"
    sensor.parent = root
    sensor.data.materials.append(mats['interior_gloss'])

    return root

def setup_studio_lighting():
    # Studio lighting matching the warm neutral photo reference
    # Key light: Softbox top-left
    bpy.ops.object.light_add(type='AREA', location=(-0.35, -0.45, 0.55))
    key = bpy.context.active_object
    key.name = "Studio_Key_Light"
    key.data.energy = 28.0
    key.data.size = 0.65
    key.data.size_y = 0.45
    key.data.color = (1.0, 0.98, 0.95)
    dir_k = Vector((0.0, 0.0, 0.02)) - key.location
    key.rotation_euler = dir_k.to_track_quat('-Z', 'Y').to_euler()

    # Fill light: Right side fill
    bpy.ops.object.light_add(type='AREA', location=(0.45, -0.30, 0.40))
    fill = bpy.context.active_object
    fill.name = "Studio_Fill_Light"
    fill.data.energy = 14.0
    fill.data.size = 0.80
    fill.data.size_y = 0.60
    fill.data.color = (0.96, 0.97, 1.0)
    dir_f = Vector((0.0, 0.0, 0.02)) - fill.location
    fill.rotation_euler = dir_f.to_track_quat('-Z', 'Y').to_euler()

    # Rim light: Rear contour highlight
    bpy.ops.object.light_add(type='AREA', location=(-0.15, 0.45, 0.35))
    rim = bpy.context.active_object
    rim.name = "Studio_Rim_Light"
    rim.data.energy = 18.0
    rim.data.size = 0.50
    rim.data.size_y = 0.30
    rim.data.color = (0.98, 0.99, 1.0)
    dir_r = Vector((0.0, 0.0, 0.02)) - rim.location
    rim.rotation_euler = dir_r.to_track_quat('-Z', 'Y').to_euler()

    # Ground floor plane for matching shadow & environment
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Ground_Plane"
    floor.data.materials.append(bpy.data.materials.get("Studio_Floor_Beige"))
    return floor

def setup_hero_camera(scene):
    # Camera calibrated to match EXACT 3/4 perspective of media_1791575583430_5b6e195d.jpg
    target = Vector((-0.004, 0.005, 0.022))
    dist = 0.32
    elev_deg = 35.5
    azim_deg = 34.0

    elev_rad = math.radians(elev_deg)
    azim_rad = math.radians(azim_deg)

    cam_x = target.x - dist * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target.y - dist * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target.z + dist * math.sin(elev_rad)

    cam_data = bpy.data.cameras.new("Camera_Pulse_Hero")
    cam_data.lens = 85.0 # Telephoto compression matching photo
    cam_obj = bpy.data.objects.new("Camera_Pulse_Hero", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    direction = target - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam_obj
    return cam_obj

def run_build_and_render():
    print(">>> Initializing Pulse Pro Authentic Recreation Scene...")
    scene = reset_scene()
    configure_cycles(scene, samples=64)
    mats = create_materials()
    mouse = build_pulse_mouse(mats)
    floor = setup_studio_lighting()
    cam = setup_hero_camera(scene)

    # Save Master .blend models
    master_blend = os.path.join(MODELS_DIR, "mouse_pulse_master.blend")
    scene_blend = os.path.join(SCENES_DIR, "mouse_pulse.blend")
    bpy.ops.wm.save_as_mainfile(filepath=master_blend)
    bpy.ops.wm.save_as_mainfile(filepath=scene_blend)
    print(f"[OK] Master blend saved: {master_blend}")

    # 1. Render Hero with Floor (matching photo reference)
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.film_transparent = False
    hero_render_path = os.path.join(PREVIEWS_DIR, "pulse_pro_authentic_render.png")
    scene.render.filepath = hero_render_path
    print(f">>> Rendering Hero reference pass -> {hero_render_path}...")
    bpy.ops.render.render(write_still=True)

    # 2. Render Isolated Pass (transparent film)
    floor.hide_render = True
    scene.render.film_transparent = True
    iso_render_path = os.path.join(PREVIEWS_DIR, "pulse_pro_hero_isolated.png")
    scene.render.filepath = iso_render_path
    print(f">>> Rendering Isolated transparent pass -> {iso_render_path}...")
    bpy.ops.render.render(write_still=True)

    # 3. Render Shadow Catcher Pass
    floor.hide_render = False
    floor.is_shadow_catcher = True
    mouse.hide_render = True
    # Hide all children of mouse
    for child in mouse.children_recursive:
        child.hide_render = True
    shd_render_path = os.path.join(PREVIEWS_DIR, "pulse_pro_hero_shadow.png")
    scene.render.filepath = shd_render_path
    print(f">>> Rendering Shadow catcher pass -> {shd_render_path}...")
    bpy.ops.render.render(write_still=True)

    print(">>> Pulse Pro 3D Build and Renders Complete!")

if __name__ == "__main__":
    run_build_and_render()
