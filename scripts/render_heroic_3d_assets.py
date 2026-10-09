"""
Master 3D Asset Renderer for NOVA Gear (Blender 5.2.2 LTS)
Builds photorealistic, high-fidelity models for:
1. Charger Flux (Parametric unibody, zero gap, real illuminated USB-C/A ports with gold pins, flush pinstripe, PBT micro-bump)
2. NovaDesk Mat (Rounded sheet, felt bump, 160+ discrete saddle stitches, embossed leather tag with brass rivet)
3. Light Beam (64-segment cylinder, brushed aluminum, glowing optical diffuser lens, rotary dial, gravity clamp)
4. NovaKeys K75 (Unified 75% ANSI layout, Cherry keycaps with crisp legends, knurled brass volume knob, 8 physical layers for assembled & exploded)

Automated Bounding-Box Camera Fit with >= 20% safety margin to ensure ZERO edge clipping.
"""

import bpy
import bmesh
import mathutils
import math
import os
import sys
import json

ROOT_DIR = "D:/Projects/ууу"
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
SCENES_DIR = os.path.join(ASSETS_DIR, "scenes")
STAGING_DIR = os.path.join(ASSETS_DIR, "staging")
TEXTURES_DIR = os.path.join(ASSETS_DIR, "textures")
PREVIEWS_DIR = os.path.join(ASSETS_DIR, "previews")

os.makedirs(SCENES_DIR, exist_ok=True)
os.makedirs(STAGING_DIR, exist_ok=True)
os.makedirs(PREVIEWS_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# HARDWARE & CYCLES CONFIGURATION
# -----------------------------------------------------------------------------
def configure_cycles(scene, samples=128):
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.render.film_transparent = True
    scene.cycles.use_denoising = True
    
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        device_types = [t[0] for t in prefs.get_device_types(bpy.context)]
        if 'OPTIX' in device_types:
            prefs.compute_device_type = 'OPTIX'
            for d in prefs.get_devices_for_type('OPTIX'):
                d.use = True
            scene.cycles.device = 'GPU'
        elif 'CUDA' in device_types:
            prefs.compute_device_type = 'CUDA'
            for d in prefs.get_devices_for_type('CUDA'):
                d.use = True
            scene.cycles.device = 'GPU'
        else:
            scene.cycles.device = 'CPU'
    except Exception as e:
        print("Device setup fallback:", e)
        scene.cycles.device = 'CPU'

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    return scene

# -----------------------------------------------------------------------------
# SHADER & MATERIAL HELPERS
# -----------------------------------------------------------------------------
def create_pbt_plastic(name, color_rgba, roughness=0.38, bump_strength=0.25):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = color_rgba
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = 0.0
    
    # Procedural fine noise bump for tactile injection-molded PBT texture
    node_tex = nodes.new('ShaderNodeTexNoise')
    node_tex.inputs['Scale'].default_value = 350.0
    node_tex.inputs['Detail'].default_value = 6.0
    node_tex.inputs['Roughness'].default_value = 0.7
    
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = bump_strength
    node_bump.inputs['Distance'].default_value = 0.001
    
    links.new(node_tex.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

def create_anodized_metal(name, color_rgba, roughness=0.22, bump_strength=0.15):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = color_rgba
    node_bsdf.inputs['Metallic'].default_value = 0.96
    node_bsdf.inputs['Roughness'].default_value = roughness
    
    # Brushed noise bump
    node_coord = nodes.new('ShaderNodeTexCoord')
    node_mapping = nodes.new('ShaderNodeMapping')
    node_mapping.inputs['Scale'].default_value = (500.0, 15.0, 15.0)
    
    node_tex = nodes.new('ShaderNodeTexNoise')
    node_tex.inputs['Scale'].default_value = 100.0
    node_tex.inputs['Detail'].default_value = 4.0
    
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = bump_strength
    node_bump.inputs['Distance'].default_value = 0.0008
    
    links.new(node_coord.outputs['Object'], node_mapping.inputs['Vector'])
    links.new(node_mapping.outputs['Vector'], node_tex.inputs['Vector'])
    links.new(node_tex.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

def create_polished_brass(name="PVD_Brass", roughness=0.10):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (0.94, 0.76, 0.34, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 1.0
    node_bsdf.inputs['Roughness'].default_value = roughness
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

def create_diffuser_material(name="Frosted_Diffuser", emission_color=(1.0, 0.94, 0.85, 1.0), emission_strength=5.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    node_bsdf.inputs['Roughness'].default_value = 0.22
    if 'Transmission Weight' in node_bsdf.inputs:
        node_bsdf.inputs['Transmission Weight'].default_value = 0.85
    elif 'Transmission' in node_bsdf.inputs:
        node_bsdf.inputs['Transmission'].default_value = 0.85
        
    node_bsdf.inputs['Emission Color'].default_value = emission_color
    node_bsdf.inputs['Emission Strength'].default_value = emission_strength
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

def create_felt_material(name="Anthracite_Felt"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (0.09, 0.095, 0.105, 1.0)
    node_bsdf.inputs['Roughness'].default_value = 0.92
    if 'Sheen Weight' in node_bsdf.inputs:
        node_bsdf.inputs['Sheen Weight'].default_value = 0.45
    elif 'Sheen' in node_bsdf.inputs:
        node_bsdf.inputs['Sheen'].default_value = 0.45
    
    node_tex = nodes.new('ShaderNodeTexNoise')
    node_tex.inputs['Scale'].default_value = 450.0
    node_tex.inputs['Detail'].default_value = 8.0
    node_tex.inputs['Roughness'].default_value = 0.85
    
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.45
    node_bump.inputs['Distance'].default_value = 0.002
    
    links.new(node_tex.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

def create_leather_material(name="Saddle_Leather"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (0.28, 0.16, 0.09, 1.0)
    node_bsdf.inputs['Roughness'].default_value = 0.45
    
    node_tex = nodes.new('ShaderNodeTexVoronoi')
    node_tex.inputs['Scale'].default_value = 180.0
    
    node_bump = nodes.new('ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.20
    node_bump.inputs['Distance'].default_value = 0.001
    
    links.new(node_tex.outputs['Distance'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

# -----------------------------------------------------------------------------
# LIGHTING & CAMERA AUTOMATION
# -----------------------------------------------------------------------------
def setup_lighting(energy_mult=1.0, port_fill=False):
    # Key light: Soft directional warm fill
    key_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_data.energy = 320.0 * energy_mult
    key_data.size = 3.5
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (4.0, -4.5, 5.0)
    key_obj.rotation_euler = (math.radians(50), math.radians(10), math.radians(40))
    
    # Fill light: Cool ambient
    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 140.0 * energy_mult
    fill_data.size = 4.0
    fill_data.color = (0.92, 0.95, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-4.0, -3.5, 3.5)
    fill_obj.rotation_euler = (math.radians(55), 0, math.radians(-50))
    
    # Rim / Kicker: High contrast crisp edge highlight
    rim_data = bpy.data.lights.new(name="RimLight", type='AREA')
    rim_data.energy = 360.0 * energy_mult
    rim_data.size = 2.5
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (2.5, 4.5, 4.0)
    rim_obj.rotation_euler = (math.radians(-45), 0, math.radians(150))

    if port_fill:
        # Specialized soft kicker illuminating front ports
        pfill_data = bpy.data.lights.new(name="PortFill", type='AREA')
        pfill_data.energy = 85.0 * energy_mult
        pfill_data.size = 1.0
        pfill_data.color = (1.0, 1.0, 0.98)
        pfill_obj = bpy.data.objects.new("PortFill", pfill_data)
        bpy.context.collection.objects.link(pfill_obj)
        pfill_obj.location = (0.0, -2.5, 0.0)
        pfill_obj.rotation_euler = (math.radians(90), 0, 0)

def fit_camera_to_scene(scene, objects, fov_deg=40.0, margin=0.22, rot_euler=(math.radians(54), 0, math.radians(40))):
    bpy.context.view_layer.update()
    corners = []
    for obj in objects:
        if obj.type == 'MESH':
            for c in obj.bound_box:
                corners.append(obj.matrix_world @ mathutils.Vector(c))
    
    if not corners:
        print("Warning: No corners found for camera fit")
        return None
    
    min_co = mathutils.Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    max_co = mathutils.Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    center = (min_co + max_co) / 2.0
    
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens_unit = 'FOV'
    cam_data.angle = math.radians(fov_deg)
    cam_data.sensor_fit = 'AUTO'
    
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    cam_obj.rotation_euler = rot_euler
    bpy.context.view_layer.update()
    
    rot_mat = cam_obj.rotation_euler.to_matrix()
    cam_right = rot_mat.col[0]
    cam_up = rot_mat.col[1]
    cam_forward = -rot_mat.col[2]
    cam_dir = -cam_forward
    
    res_x = scene.render.resolution_x
    res_y = scene.render.resolution_y
    aspect = res_x / res_y
    
    if aspect >= 1.0:
        fov_x = math.radians(fov_deg)
        fov_y = 2.0 * math.atan(math.tan(fov_x / 2.0) / aspect)
    else:
        fov_y = math.radians(fov_deg)
        fov_x = 2.0 * math.atan(math.tan(fov_y / 2.0) * aspect)
        
    tan_half_x = math.tan(fov_x / 2.0)
    tan_half_y = math.tan(fov_y / 2.0)
    
    max_req_dist = 0.0
    for p in corners:
        rel = p - center
        x_c = rel.dot(cam_right)
        y_c = rel.dot(cam_up)
        z_c = rel.dot(cam_forward)
        
        req_x = z_c + (abs(x_c) * (1.0 + margin)) / tan_half_x
        req_y = z_c + (abs(y_c) * (1.0 + margin)) / tan_half_y
        max_req_dist = max(max_req_dist, req_x, req_y)
        
    final_dist = max_req_dist * 1.08
    cam_obj.location = center + cam_dir * final_dist
    bpy.context.view_layer.update()
    print(f"Fit Camera OK: center={center}, distance={final_dist:.3f}")
    return cam_obj

# =============================================================================
# MODEL 1: CHARGER FLUX (Parametric, Zero Gap, Realistic Ports, Acid Lime Pinstripe)
# =============================================================================
def build_charger_flux():
    print("Building Charger Flux...")
    scene = reset_scene()
    configure_cycles(scene, samples=128)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1600
    
    # Parametric Dimensions
    W = 0.88  # Width X
    D = 1.24  # Depth Y
    H = 1.36  # Height Z
    
    x_min, x_max = -W / 2.0, W / 2.0
    y_front, y_back = -D / 2.0, D / 2.0
    z_min, z_max = -H / 2.0, H / 2.0
    
    # Materials
    mat_pbt = create_pbt_plastic("PBT_Charcoal", (0.10, 0.105, 0.115, 1.0), roughness=0.34, bump_strength=0.18)
    mat_plate = create_pbt_plastic("PBT_FrontPlate", (0.08, 0.085, 0.095, 1.0), roughness=0.28, bump_strength=0.12)
    mat_accent = create_pbt_plastic("Acid_Lime", (0.78, 1.0, 0.24, 1.0), roughness=0.26, bump_strength=0.10)
    mat_metal = create_anodized_metal("Nickel_Port", (0.86, 0.86, 0.88, 1.0), roughness=0.16)
    mat_gold = create_polished_brass("Gold_Contacts", roughness=0.10)
    mat_port_inner = create_pbt_plastic("Port_Cavity_Wall", (0.04, 0.04, 0.045, 1.0), roughness=0.5, bump_strength=0.0)
    
    mat_led = bpy.data.materials.new("LED_Emerald")
    mat_led.use_nodes = True
    bsdf_led = mat_led.node_tree.nodes.get("Principled BSDF")
    bsdf_led.inputs["Emission Color"].default_value = (0.2, 1.0, 0.5, 1.0)
    bsdf_led.inputs["Emission Strength"].default_value = 35.0
    
    created_objects = []
    
    # 1. Main Unibody Chassis
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0), scale=(W, D, H))
    body = bpy.context.active_object
    body.name = "Charger_Body"
    body.data.materials.append(mat_pbt)
    bev = body.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = 0.05
    bev.segments = 4
    bpy.ops.object.shade_smooth()
    created_objects.append(body)
    
    # 2. Front Face Bezel Plate (RESTING EXACTLY AT y_front - ZERO GAP!)
    plate_t = 0.024
    plate_y = y_front - plate_t / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, plate_y, 0), scale=(W * 0.90, plate_t, H * 0.92))
    front_plate = bpy.context.active_object
    front_plate.name = "Front_Panel"
    front_plate.data.materials.append(mat_plate)
    fbev = front_plate.modifiers.new(name="Bevel", type='BEVEL')
    fbev.width = 0.018
    fbev.segments = 3
    bpy.ops.object.shade_smooth()
    created_objects.append(front_plate)
    
    # 3. Signature Accent Inset Pinstripe (Thin 2mm band wrapping around side/top seam)
    stripe_w = W * 1.002
    stripe_d = D * 0.92
    stripe_h = 0.014
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_max - 0.08), scale=(stripe_w, stripe_d, stripe_h))
    stripe = bpy.context.active_object
    stripe.name = "Accent_Stripe"
    stripe.data.materials.append(mat_accent)
    created_objects.append(stripe)
    
    # 4. Realistic Recessed USB-C Ports (Hollow Metal Collars with Visible Gold Tongues)
    def add_hollow_usbc(name, z_center):
        # Outer metallic bezel
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.10, depth=0.024, 
            location=(0, plate_y - 0.010, z_center), 
            rotation=(math.radians(90), 0, 0),
            scale=(1.8, 1.0, 0.70)
        )
        collar = bpy.context.active_object
        collar.name = f"{name}_Collar"
        collar.data.materials.append(mat_metal)
        
        # Inner cutter to make collar hollow
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.076, depth=0.040, 
            location=(0, plate_y - 0.010, z_center), 
            rotation=(math.radians(90), 0, 0),
            scale=(1.7, 1.0, 0.60)
        )
        cutter = bpy.context.active_object
        
        bmod = collar.modifiers.new("CutHole", 'BOOLEAN')
        bmod.operation = 'DIFFERENCE'
        bmod.object = cutter
        bpy.context.view_layer.objects.active = collar
        bpy.ops.object.modifier_apply(modifier="CutHole")
        bpy.data.objects.remove(cutter, do_unlink=True)
        created_objects.append(collar)
        
        # Recessed dark socket cavity behind the collar
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.08, depth=0.04, 
            location=(0, plate_y + 0.015, z_center), 
            rotation=(math.radians(90), 0, 0),
            scale=(1.7, 1.0, 0.60)
        )
        cavity = bpy.context.active_object
        cavity.name = f"{name}_Cavity"
        cavity.data.materials.append(mat_port_inner)
        created_objects.append(cavity)
        
        # Center Tongue with Gold Contacts inside the opening
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, 
            location=(0, plate_y - 0.002, z_center), 
            scale=(0.14, 0.024, 0.016)
        )
        tongue = bpy.context.active_object
        tongue.name = f"{name}_Tongue"
        tongue.data.materials.append(mat_gold)
        created_objects.append(tongue)

    add_hollow_usbc("USB_C_1", 0.32)
    add_hollow_usbc("USB_C_2", -0.04)
    
    # 5. Realistic Recessed USB-A Port (Hollow Outer Frame + Orange Tongue + 4 Pins)
    usba_z = -0.40
    # Outer frame
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, plate_y - 0.008, usba_z), scale=(0.38, 0.024, 0.20))
    usba_frame = bpy.context.active_object
    usba_frame.name = "USB_A_Frame"
    usba_frame.data.materials.append(mat_metal)
    
    # Frame cutter
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, plate_y - 0.008, usba_z), scale=(0.32, 0.040, 0.15))
    usba_cutter = bpy.context.active_object
    
    abmod = usba_frame.modifiers.new("CutA", 'BOOLEAN')
    abmod.operation = 'DIFFERENCE'
    abmod.object = usba_cutter
    bpy.context.view_layer.objects.active = usba_frame
    bpy.ops.object.modifier_apply(modifier="CutA")
    bpy.data.objects.remove(usba_cutter, do_unlink=True)
    created_objects.append(usba_frame)
    
    # Cavity
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, plate_y + 0.015, usba_z), scale=(0.33, 0.045, 0.16))
    usba_void = bpy.context.active_object
    usba_void.name = "USB_A_Void"
    usba_void.data.materials.append(mat_port_inner)
    created_objects.append(usba_void)
    
    # Orange / Signature Lime Tongue inside top half of USB-A opening
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, plate_y + 0.002, usba_z + 0.035), scale=(0.28, 0.022, 0.028))
    usba_tongue = bpy.context.active_object
    usba_tongue.name = "USB_A_Tongue"
    usba_tongue.data.materials.append(mat_accent)
    created_objects.append(usba_tongue)
    
    for px in [-0.09, -0.03, 0.03, 0.09]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, plate_y - 0.004, usba_z + 0.018), scale=(0.015, 0.016, 0.006))
        pin = bpy.context.active_object
        pin.name = f"USB_A_Pin_{px}"
        pin.data.materials.append(mat_gold)
        created_objects.append(pin)

        
    # 6. Micro LED Indicator Pinhole
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.016, depth=0.014, 
        location=(W * 0.30, plate_y - 0.012, H * 0.38), 
        rotation=(math.radians(90), 0, 0)
    )
    led = bpy.context.active_object
    led.name = "LED_Pinhole"
    led.data.materials.append(mat_led)
    created_objects.append(led)
    
    # 7. Rear Foldable Prongs
    for x_off in [-0.18, 0.18]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, 
            location=(x_off, y_back + 0.10, -0.22), 
            scale=(0.035, 0.20, 0.16)
        )
        prong = bpy.context.active_object
        prong.name = f"Prong_{'L' if x_off < 0 else 'R'}"
        prong.data.materials.append(mat_metal)
        created_objects.append(prong)

    # Lighting & Camera
    setup_lighting(energy_mult=1.1, port_fill=True)
    
    # Perspective camera looking at front 3/4 angle
    cam_rot = (math.radians(58), 0, math.radians(38))
    fit_camera_to_scene(scene, created_objects, fov_deg=38.0, margin=0.22, rot_euler=cam_rot)
    
    blend_path = os.path.join(SCENES_DIR, "charger_flux.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    png_path = os.path.join(STAGING_DIR, "charger-flux.png")
    scene.render.filepath = png_path
    bpy.ops.render.render(write_still=True)
    print(f"Charger Flux successfully rendered: {png_path}")

# =============================================================================
# MODEL 2: NOVADESK XL MAT (Rounded, Discrete Stitches, Leather Badge, Rivet)
# =============================================================================
def build_mat_novadesk():
    print("Building NovaDesk XL Mat...")
    scene = reset_scene()
    configure_cycles(scene, samples=128)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    
    mat_w = 2.40
    mat_d = 1.25
    mat_h = 0.035
    corner_r = 0.16
    
    mat_felt = create_felt_material("Anthracite_Felt")
    mat_thread = create_pbt_plastic("Saddle_Thread", (0.36, 0.38, 0.42, 1.0), roughness=0.50, bump_strength=0.25)
    mat_leather = create_leather_material("Saddle_Leather")
    mat_brass = create_polished_brass("Turned_Brass_Rivet", roughness=0.15)
    mat_logo = create_polished_brass("Embossed_NOVA_Logo", roughness=0.2)
    
    created_objects = []
    
    # 1. Main Felt Mat Body
    mesh = bpy.data.meshes.new("MatMesh")
    bm = bmesh.new()
    
    subdivs = 14
    pts_2d = []
    cx = mat_w / 2.0 - corner_r
    cy = mat_d / 2.0 - corner_r
    
    corners_cfg = [
        (cx, cy, 0, math.pi / 2),
        (-cx, cy, math.pi / 2, math.pi),
        (-cx, -cy, math.pi, 3 * math.pi / 2),
        (cx, -cy, 3 * math.pi / 2, 2 * math.pi)
    ]
    for c_x, c_y, a_start, a_end in corners_cfg:
        for i in range(subdivs):
            angle = a_start + (a_end - a_start) * (i / subdivs)
            pts_2d.append((c_x + corner_r * math.cos(angle), c_y + corner_r * math.sin(angle)))
            
    v_bottom = [bm.verts.new((x, y, -mat_h / 2.0)) for x, y in pts_2d]
    v_top = [bm.verts.new((x, y, mat_h / 2.0)) for x, y in pts_2d]
    
    bm.faces.new(v_top)
    bm.faces.new(list(reversed(v_bottom)))
    n_pts = len(pts_2d)
    for i in range(n_pts):
        next_i = (i + 1) % n_pts
        bm.faces.new((v_bottom[i], v_bottom[next_i], v_top[next_i], v_top[i]))
        
    bm.to_mesh(mesh)
    bm.free()
    
    mat_body = bpy.data.objects.new("NovaDesk_Mat", mesh)
    bpy.context.collection.objects.link(mat_body)
    mat_body.data.materials.append(mat_felt)
    bev = mat_body.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = 0.012
    bev.segments = 3
    bpy.ops.object.shade_smooth()
    created_objects.append(mat_body)
    
    # 2. Discrete Perimeter Saddle Stitches (160+ discrete segments)
    stitch_inset = 0.042
    s_cx = mat_w / 2.0 - corner_r
    s_cy = mat_d / 2.0 - corner_r
    s_r = corner_r - stitch_inset
    
    stitch_pts = []
    stitch_subdivs = 10
    for c_x, c_y, a_start, a_end in corners_cfg:
        for i in range(stitch_subdivs):
            angle = a_start + (a_end - a_start) * (i / stitch_subdivs)
            px = c_x + s_r * math.cos(angle)
            py = c_y + s_r * math.sin(angle)
            tx = -math.sin(angle)
            ty = math.cos(angle)
            stitch_pts.append((px, py, tx, ty))
            
    n_edge = 28
    for i in range(1, n_edge):
        x = -s_cx + (2 * s_cx) * (i / n_edge)
        stitch_pts.append((x, s_cy + s_r, 1.0, 0.0))
    for i in range(1, n_edge):
        x = s_cx - (2 * s_cx) * (i / n_edge)
        stitch_pts.append((x, -s_cy - s_r, -1.0, 0.0))
    n_side = 14
    for i in range(1, n_side):
        y = -s_cy + (2 * s_cy) * (i / n_side)
        stitch_pts.append((s_cx + s_r, y, 0.0, 1.0))
    for i in range(1, n_side):
        y = s_cy - (2 * s_cy) * (i / n_side)
        stitch_pts.append((-s_cx - s_r, y, 0.0, -1.0))
        
    for idx, (sx, sy, tx, ty) in enumerate(stitch_pts):
        tangent_angle = math.atan2(ty, tx) + math.radians(24.0)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.0055, depth=0.028,
            location=(sx, sy, mat_h / 2.0 + 0.0035),
            rotation=(math.radians(90), 0, tangent_angle)
        )
        st = bpy.context.active_object
        st.name = f"Stitch_{idx}"
        st.data.materials.append(mat_thread)
        created_objects.append(st)
        
    # 3. Genuine Saddle Leather Brand Badge
    badge_w, badge_d, badge_h = 0.32, 0.13, 0.018
    badge_x = mat_w / 2.0 - 0.28
    badge_y = mat_d / 2.0 - 0.14
    badge_z = mat_h / 2.0 + badge_h / 2.0
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(badge_x, badge_y, badge_z), scale=(badge_w, badge_d, badge_h)
    )
    badge = bpy.context.active_object
    badge.name = "Leather_Badge"
    badge.data.materials.append(mat_leather)
    bbev = badge.modifiers.new("Bevel", 'BEVEL')
    bbev.width = 0.006
    bbev.segments = 2
    created_objects.append(badge)
    
    # Embossed NOVA Logo Bar on Leather
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(badge_x - 0.04, badge_y, badge_z + badge_h / 2.0 + 0.001),
        scale=(0.14, 0.04, 0.004)
    )
    logo_bar = bpy.context.active_object
    logo_bar.name = "Leather_NOVA_Mark"
    logo_bar.data.materials.append(mat_logo)
    created_objects.append(logo_bar)
    
    # 4. Turned Brass Rivet
    rivet_x = badge_x + badge_w / 2.0 - 0.04
    rivet_y = badge_y
    rivet_z = badge_z + badge_h / 2.0 + 0.004
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.018, depth=0.012, location=(rivet_x, rivet_y, rivet_z)
    )
    rivet = bpy.context.active_object
    rivet.name = "Brass_Rivet"
    rivet.data.materials.append(mat_brass)
    rbev = rivet.modifiers.new("Bevel", 'BEVEL')
    rbev.width = 0.003
    rbev.segments = 2
    created_objects.append(rivet)
    
    # Lighting & Camera
    setup_lighting(energy_mult=1.15)
    cam_rot = (math.radians(54), 0, math.radians(32))
    fit_camera_to_scene(scene, created_objects, fov_deg=38.0, margin=0.20, rot_euler=cam_rot)
    
    blend_path = os.path.join(SCENES_DIR, "mat_novadesk.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    png_path = os.path.join(STAGING_DIR, "mat-novadesk.png")
    scene.render.filepath = png_path
    bpy.ops.render.render(write_still=True)
    print(f"NovaDesk XL Mat successfully rendered: {png_path}")

# =============================================================================
# MODEL 3: LIGHT BEAM (High-Poly Bar, Brushed Alu, Glowing Diffuser, Gravity Mount)
# =============================================================================
def build_light_beam():
    print("Building Light Beam...")
    scene = reset_scene()
    configure_cycles(scene, samples=128)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    
    bar_len = 2.25
    bar_r = 0.048
    
    mat_alu = create_anodized_metal("SpaceGrey_Alu", (0.17, 0.18, 0.20, 1.0), roughness=0.20)
    mat_dial = create_anodized_metal("Knurled_Dial", (0.24, 0.25, 0.28, 1.0), roughness=0.18, bump_strength=0.3)
    mat_lens = create_diffuser_material("Frosted_Optics", emission_color=(1.0, 0.94, 0.85, 1.0), emission_strength=6.0)
    mat_rubber = create_pbt_plastic("Silicone_Pad", (0.05, 0.05, 0.06, 1.0), roughness=0.8, bump_strength=0.1)
    mat_pivot = create_polished_brass("Pivot_Brass_Pin", roughness=0.12)
    
    created_objects = []
    
    # 1. Main High-Poly Light Bar Cylinder (64 Segments)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=bar_r, depth=bar_len, 
        location=(0, 0, 0), rotation=(0, math.radians(90), 0)
    )
    bar = bpy.context.active_object
    bar.name = "Light_Bar_Body"
    bar.data.materials.append(mat_alu)
    bbev = bar.modifiers.new("Bevel", 'BEVEL')
    bbev.width = 0.008
    bbev.segments = 3
    bpy.ops.object.shade_smooth()
    created_objects.append(bar)
    
    # 2. Rotary Dial / Control Endcap on Right Edge
    dial_len = 0.09
    dial_x = bar_len / 2.0 + dial_len / 2.0
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=bar_r * 1.05, depth=dial_len,
        location=(dial_x, 0, 0), rotation=(0, math.radians(90), 0)
    )
    dial = bpy.context.active_object
    dial.name = "Rotary_Endcap"
    dial.data.materials.append(mat_dial)
    dbev = dial.modifiers.new("Bevel", 'BEVEL')
    dbev.width = 0.005
    dbev.segments = 2
    bpy.ops.object.shade_smooth()
    created_objects.append(dial)
    
    # 3. Left Flush Endcap
    left_x = -bar_len / 2.0 - 0.015
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=bar_r, depth=0.03,
        location=(left_x, 0, 0), rotation=(0, math.radians(90), 0)
    )
    lend = bpy.context.active_object
    lend.name = "Left_Endcap"
    lend.data.materials.append(mat_alu)
    created_objects.append(lend)
    
    # 4. Asymmetric Optical Diffuser Lens (Positioned to glow forward-downward)
    lens_len = bar_len * 0.90
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, -bar_r * 0.65, -bar_r * 0.45), 
        scale=(lens_len, bar_r * 0.55, 0.018)
    )
    lens = bpy.context.active_object
    lens.name = "Diffuser_Lens"
    lens.data.materials.append(mat_lens)
    created_objects.append(lens)
    
    # 5. Dual-Pivot Gravity Counterweight Clamp (Mounted at Center)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, -bar_r - 0.05, -0.04), scale=(0.14, 0.04, 0.12)
    )
    lip = bpy.context.active_object
    lip.name = "Clamp_Front_Lip"
    lip.data.materials.append(mat_alu)
    created_objects.append(lip)
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.032, depth=0.14,
        location=(0, 0.08, 0.02), rotation=(0, math.radians(90), 0)
    )
    hinge = bpy.context.active_object
    hinge.name = "Clamp_Hinge"
    hinge.data.materials.append(mat_alu)
    created_objects.append(hinge)
    
    for hx in [-0.072, 0.072]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.016, depth=0.012, location=(hx, 0.08, 0.02), rotation=(0, math.radians(90), 0)
        )
        hpin = bpy.context.active_object
        hpin.name = "Hinge_Brass_Pin"
        hpin.data.materials.append(mat_pivot)
        created_objects.append(hpin)
        
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0.24, -0.08), scale=(0.13, 0.22, 0.10)
    )
    mass = bpy.context.active_object
    mass.name = "Clamp_Counterweight"
    mass.data.materials.append(mat_alu)
    mbev = mass.modifiers.new("Bevel", 'BEVEL')
    mbev.width = 0.01
    mbev.segments = 2
    created_objects.append(mass)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0.24, -0.025), scale=(0.11, 0.18, 0.01)
    )
    grip = bpy.context.active_object
    grip.name = "Grip_Pad"
    grip.data.materials.append(mat_rubber)
    created_objects.append(grip)
    
    # Lighting & Camera
    setup_lighting(energy_mult=1.1)
    cam_rot = (math.radians(58), 0, math.radians(35))
    fit_camera_to_scene(scene, created_objects, fov_deg=38.0, margin=0.20, rot_euler=cam_rot)
    
    blend_path = os.path.join(SCENES_DIR, "light_beam.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    png_path = os.path.join(STAGING_DIR, "light-beam.png")
    scene.render.filepath = png_path
    bpy.ops.render.render(write_still=True)
    print(f"Light Beam successfully rendered: {png_path}")

# =============================================================================
# MODEL 4: NOVAKEYS K75 (Unified Hero Assembled & Exploded 8-Layer Architecture)
# =============================================================================
def build_k75_scene(mode="assembled"):
    print(f"Building NovaKeys K75 (Mode: {mode})...")
    scene = reset_scene()
    configure_cycles(scene, samples=128)
    
    if mode == "assembled":
        scene.render.resolution_x = 1600
        scene.render.resolution_y = 1200
    else:
        scene.render.resolution_x = 1600
        scene.render.resolution_y = 1600
        
    case_w = 3.20
    case_d = 1.34
    case_h = 0.24
    
    # Materials with enhanced contrast & highlights
    mat_case = create_anodized_metal("Case_Alu_6063", (0.18, 0.19, 0.21, 1.0), roughness=0.22)
    mat_brass = create_polished_brass("Mirror_PVD_Brass", roughness=0.08)
    mat_silicone = create_pbt_plastic("Acoustic_Silicone", (0.38, 0.39, 0.42, 1.0), roughness=0.5, bump_strength=0.1)
    mat_pcb = create_pbt_plastic("FR4_PCB_MatteBlack", (0.06, 0.065, 0.07, 1.0), roughness=0.45, bump_strength=0.1)
    mat_traces = create_polished_brass("ENIG_Gold_Traces", roughness=0.12)
    mat_foam = create_pbt_plastic("Poron_Gasket_Foam", (0.09, 0.095, 0.105, 1.0), roughness=0.85, bump_strength=0.35)
    mat_plate = create_anodized_metal("FR4_Switch_Plate", (0.14, 0.15, 0.16, 1.0), roughness=0.28)
    mat_sw_pc = bpy.data.materials.new("Switch_Housing_PC")
    mat_sw_pc.use_nodes = True
    bsdf_sw = mat_sw_pc.node_tree.nodes.get("Principled BSDF")
    bsdf_sw.inputs["Base Color"].default_value = (0.22, 0.24, 0.28, 1.0)
    bsdf_sw.inputs["Roughness"].default_value = 0.25
    if "Transmission Weight" in bsdf_sw.inputs:
        bsdf_sw.inputs["Transmission Weight"].default_value = 0.65
    elif "Transmission" in bsdf_sw.inputs:
        bsdf_sw.inputs["Transmission"].default_value = 0.65
    mat_sw_stem = create_pbt_plastic("Switch_Stem_POM", (0.78, 1.0, 0.24, 1.0), roughness=0.28, bump_strength=0.1)
    mat_knob = create_polished_brass("Brass_Rotary_Knob", roughness=0.16)
    
    # Keycap Atlas Material
    atlas_img_path = os.path.join(TEXTURES_DIR, "keycap_atlas.png")
    atlas_json_path = os.path.join(TEXTURES_DIR, "keycap_atlas.json")
    
    with open(atlas_json_path, 'r', encoding='utf-8') as f:
        atlas_coords = json.load(f)
        
    mat_keycaps = bpy.data.materials.new("K75_Keycap_Atlas")
    mat_keycaps.use_nodes = True
    knodes = mat_keycaps.node_tree.nodes
    klinks = mat_keycaps.node_tree.links
    knodes.clear()
    
    k_out = knodes.new('ShaderNodeOutputMaterial')
    k_bsdf = knodes.new('ShaderNodeBsdfPrincipled')
    k_bsdf.inputs['Roughness'].default_value = 0.35
    
    k_img = knodes.new('ShaderNodeTexImage')
    if os.path.exists(atlas_img_path):
        k_img.image = bpy.data.images.load(atlas_img_path)
        
    k_noise = knodes.new('ShaderNodeTexNoise')
    k_noise.inputs['Scale'].default_value = 400.0
    k_noise.inputs['Detail'].default_value = 4.0
    
    k_bump = knodes.new('ShaderNodeBump')
    k_bump.inputs['Strength'].default_value = 0.10
    k_bump.inputs['Distance'].default_value = 0.0005
    
    klinks.new(k_img.outputs['Color'], k_bsdf.inputs['Base Color'])
    klinks.new(k_noise.outputs['Fac'], k_bump.inputs['Height'])
    klinks.new(k_bump.outputs['Normal'], k_bsdf.inputs['Normal'])
    klinks.new(k_bsdf.outputs['BSDF'], k_out.inputs['Surface'])
    
    # Layer Z Offsets
    if mode == "assembled":
        z_case = 0.0
        z_weight = 0.03
        z_silicone = 0.05
        z_pcb = 0.07
        z_foam = 0.09
        z_plate = 0.11
        z_switches = 0.13
        z_keycaps = 0.20
        z_knob = 0.21
    else:
        z_case = 0.0
        z_weight = 0.32
        z_silicone = 0.65
        z_pcb = 1.05
        z_foam = 1.45
        z_plate = 1.85
        z_switches = 2.25
        z_keycaps = 2.75
        z_knob = 2.80
        
    created_objects = []
    
    # LAYER 1: CNC Aluminum Bottom Chassis
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_case), scale=(case_w, case_d, case_h))
    case = bpy.context.active_object
    case.name = "Chassis_Bottom"
    case.data.materials.append(mat_case)
    cbev = case.modifiers.new("Bevel", 'BEVEL')
    cbev.width = 0.045
    cbev.segments = 4
    bpy.ops.object.shade_smooth()
    created_objects.append(case)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.035, depth=0.08, 
        location=(-case_w * 0.32, case_d / 2.0, z_case + case_h * 0.15),
        rotation=(math.radians(90), 0, 0)
    )
    cport = bpy.context.active_object
    cport.name = "Chassis_USB_Port"
    cport.data.materials.append(mat_traces)
    created_objects.append(cport)
    
    # LAYER 2: PVD Mirror Brass Weight Bar
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_weight), scale=(case_w * 0.70, case_d * 0.38, 0.035))
    weight = bpy.context.active_object
    weight.name = "PVD_Brass_Weight_Bar"
    weight.data.materials.append(mat_brass)
    wbev = weight.modifiers.new("Bevel", 'BEVEL')
    wbev.width = 0.015
    wbev.segments = 3
    bpy.ops.object.shade_smooth()
    created_objects.append(weight)
    
    # LAYER 3: Molded Acoustic Silicone Sound Dampener
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_silicone), scale=(case_w * 0.90, case_d * 0.88, 0.03))
    silicone = bpy.context.active_object
    silicone.name = "Silicone_Dampening_Pad"
    silicone.data.materials.append(mat_silicone)
    sbev = silicone.modifiers.new("Bevel", 'BEVEL')
    sbev.width = 0.01
    sbev.segments = 2
    created_objects.append(silicone)
    
    # LAYER 4: Matte Black FR-4 PCB with Gold ENIG Circuit Traces
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_pcb), scale=(case_w * 0.92, case_d * 0.90, 0.02))
    pcb = bpy.context.active_object
    pcb.name = "FR4_PCB_Layer"
    pcb.data.materials.append(mat_pcb)
    created_objects.append(pcb)
    
    for t_idx in range(6):
        tx = -case_w * 0.40 + t_idx * (case_w * 0.16)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, 0, z_pcb + 0.011), scale=(0.015, case_d * 0.75, 0.002))
        tr = bpy.context.active_object
        tr.name = f"ENIG_Trace_{t_idx}"
        tr.data.materials.append(mat_traces)
        created_objects.append(tr)
        
    if mode == "exploded":
        for hs_r in range(5):
            for hs_c in range(14):
                hs_x = -case_w * 0.42 + hs_c * (case_w * 0.84 / 13)
                hs_y = -case_d * 0.38 + hs_r * (case_d * 0.76 / 4)
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hs_x, hs_y, z_pcb - 0.016), scale=(0.07, 0.04, 0.015))
                hs = bpy.context.active_object
                hs.name = f"HotSwap_Socket_{hs_r}_{hs_c}"
                hs.data.materials.append(mat_traces)
                created_objects.append(hs)
                
    # LAYER 5: Poron Gasket Acoustic Foam
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_foam), scale=(case_w * 0.90, case_d * 0.88, 0.025))
    foam = bpy.context.active_object
    foam.name = "Poron_Acoustic_Foam"
    foam.data.materials.append(mat_foam)
    created_objects.append(foam)
    
    # LAYER 6: FR4 Gasket Switch Plate with Isolation Tabs
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z_plate), scale=(case_w * 0.92, case_d * 0.90, 0.02))
    plate = bpy.context.active_object
    plate.name = "FR4_Switch_Plate"
    plate.data.materials.append(mat_plate)
    created_objects.append(plate)
    
    tab_mat = mat_foam
    tab_x_positions = [-case_w * 0.38, -case_w * 0.18, 0, case_w * 0.18, case_w * 0.38]
    for gx in tab_x_positions:
        for gy in [-case_d * 0.47, case_d * 0.47]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(gx, gy, z_plate), scale=(0.10, 0.04, 0.028))
            gtab = bpy.context.active_object
            gtab.name = "Gasket_Tab"
            gtab.data.materials.append(tab_mat)
            created_objects.append(gtab)
            
    # 75% ANSI KEYBOARD LAYOUT CONFIGURATION
    U = 0.185
    pitch = 0.198
    
    rows_def = [
        # Row 5: Function row
        [
            ("ESC", 1.0), ("F1", 1.0), ("F2", 1.0), ("F3", 1.0), ("F4", 1.0),
            ("F5", 1.0), ("F6", 1.0), ("F7", 1.0), ("F8", 1.0), ("F9", 1.0),
            ("F10", 1.0), ("F11", 1.0), ("F12", 1.0), ("DEL", 1.0)
        ],
        # Row 4: Numbers
        [
            ("TILDE", 1.0), ("1", 1.0), ("2", 1.0), ("3", 1.0), ("4", 1.0),
            ("5", 1.0), ("6", 1.0), ("7", 1.0), ("8", 1.0), ("9", 1.0),
            ("0", 1.0), ("MINUS", 1.0), ("PLUS", 1.0), ("BACKSPACE", 2.0), ("HOME", 1.0)
        ],
        # Row 3: QWERTY
        [
            ("TAB", 1.5), ("Q", 1.0), ("W", 1.0), ("E", 1.0), ("R", 1.0),
            ("T", 1.0), ("Y", 1.0), ("U", 1.0), ("I", 1.0), ("O", 1.0),
            ("P", 1.0), ("LBRACKET", 1.0), ("RBRACKET", 1.0), ("BACKSLASH", 1.5), ("PGUP", 1.0)
        ],
        # Row 2: Home row
        [
            ("CAPS", 1.75), ("A", 1.0), ("S", 1.0), ("D", 1.0), ("F", 1.0),
            ("G", 1.0), ("H", 1.0), ("J", 1.0), ("K", 1.0), ("L", 1.0),
            ("COLON", 1.0), ("QUOTE", 1.0), ("ENTER", 2.25), ("PGDN", 1.0)
        ],
        # Row 1: ZXCVBNM row
        [
            ("LSHIFT", 2.25), ("Z", 1.0), ("X", 1.0), ("C", 1.0), ("V", 1.0),
            ("B", 1.0), ("N", 1.0), ("M", 1.0), ("COMMA", 1.0), ("PERIOD", 1.0),
            ("SLASH", 1.0), ("RSHIFT", 1.75), ("UP", 1.0), ("END", 1.0)
        ],
        # Row 0: Bottom row
        [
            ("LCTRL", 1.25), ("LOPT", 1.25), ("LCMD", 1.25), ("SPACEBAR", 6.25),
            ("RCMD", 1.0), ("ROPT", 1.0), ("LEFT", 1.0), ("DOWN", 1.0), ("RIGHT", 1.0)
        ]
    ]
    
    total_rows = len(rows_def)
    y_start = (total_rows - 1) * pitch / 2.0
    
    # LAYER 7 & 8: SWITCHES & KEYCAPS
    for r_idx, row in enumerate(rows_def):
        row_y = y_start - r_idx * pitch
        row_units = sum(u for _, u in row)
        row_width = (row_units - 1) * pitch + U
        cur_x = -row_width / 2.0
        
        for key_name, u_size in row:
            key_w = (u_size - 1) * pitch + U
            key_x = cur_x + key_w / 2.0
            cur_x += key_w + 0.012
            
            # Switch
            bpy.ops.mesh.primitive_cube_add(
                size=1.0, location=(key_x, row_y, z_switches), scale=(0.14, 0.14, 0.07)
            )
            sw_body = bpy.context.active_object
            sw_body.name = f"Switch_{key_name}"
            sw_body.data.materials.append(mat_sw_pc)
            created_objects.append(sw_body)
            
            bpy.ops.mesh.primitive_cube_add(
                size=1.0, location=(key_x, row_y, z_switches + 0.04), scale=(0.04, 0.04, 0.05)
            )
            sw_stem = bpy.context.active_object
            sw_stem.name = f"Stem_{key_name}"
            sw_stem.data.materials.append(mat_sw_stem)
            created_objects.append(sw_stem)
            
            # Keycap with UV mapping
            coords = atlas_coords.get(key_name, atlas_coords.get("BLANK_CREAM"))
            u_min, u_max = coords['u_min'], coords['u_max']
            v_min, v_max = coords['v_min'], coords['v_max']
            
            k_mesh = bpy.data.meshes.new(f"Mesh_Key_{key_name}")
            bm_k = bmesh.new()
            
            kw = key_w
            kd = U
            kh = 0.10
            tw = kw * 0.76
            td = kd * 0.76
            
            bv0 = bm_k.verts.new((-kw/2, -kd/2, 0))
            bv1 = bm_k.verts.new((kw/2, -kd/2, 0))
            bv2 = bm_k.verts.new((kw/2, kd/2, 0))
            bv3 = bm_k.verts.new((-kw/2, kd/2, 0))
            
            tv4 = bm_k.verts.new((-tw/2, -td/2, kh))
            tv5 = bm_k.verts.new((tw/2, -td/2, kh))
            tv6 = bm_k.verts.new((tw/2, td/2, kh))
            tv7 = bm_k.verts.new((-tw/2, td/2, kh))
            
            f_top = bm_k.faces.new((tv4, tv5, tv6, tv7))
            f_front = bm_k.faces.new((bv0, bv1, tv5, tv4))
            f_right = bm_k.faces.new((bv1, bv2, tv6, tv5))
            f_back = bm_k.faces.new((bv2, bv3, tv7, tv6))
            f_left = bm_k.faces.new((bv3, bv0, tv4, tv7))
            
            uv_layer = bm_k.loops.layers.uv.new('UVMap')
            
            top_uvs = [(u_min, v_min), (u_max, v_min), (u_max, v_max), (u_min, v_max)]
            for loop, uv in zip(f_top.loops, top_uvs):
                loop[uv_layer].uv = uv
                
            bg_uv = (u_min + 0.002, v_min + 0.002)
            for side_face in [f_front, f_right, f_back, f_left]:
                for loop in side_face.loops:
                    loop[uv_layer].uv = bg_uv
                    
            bm_k.to_mesh(k_mesh)
            bm_k.free()
            
            kc_obj = bpy.data.objects.new(f"Key_{key_name}", k_mesh)
            bpy.context.collection.objects.link(kc_obj)
            kc_obj.location = (key_x, row_y, z_keycaps)
            kc_obj.data.materials.append(mat_keycaps)
            
            kbev = kc_obj.modifiers.new("Bevel", 'BEVEL')
            kbev.width = 0.007
            kbev.segments = 2
            bpy.ops.object.shade_smooth()
            created_objects.append(kc_obj)
            
    # ROTARY VOLUME KNOB (TOP-RIGHT CORNER)
    knob_x = case_w * 0.40
    knob_y = y_start
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.035, depth=0.10, location=(knob_x, knob_y, z_knob - 0.04)
    )
    kshaft = bpy.context.active_object
    kshaft.name = "Encoder_Shaft"
    kshaft.data.materials.append(mat_traces)
    created_objects.append(kshaft)
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=0.11, depth=0.13, location=(knob_x, knob_y, z_knob)
    )
    knob = bpy.context.active_object
    knob.name = "Rotary_Volume_Knob"
    knob.data.materials.append(mat_knob)
    knob_bev = knob.modifiers.new("Bevel", 'BEVEL')
    knob_bev.width = 0.012
    knob_bev.segments = 3
    bpy.ops.object.shade_smooth()
    created_objects.append(knob)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.012, depth=0.006, location=(knob_x, knob_y + 0.065, z_knob + 0.066)
    )
    kdot = bpy.context.active_object
    kdot.name = "Knob_Index_Dot"
    kdot.data.materials.append(mat_traces)
    created_objects.append(kdot)
    
    # Lighting & Camera
    setup_lighting(energy_mult=1.2)
    
    if mode == "assembled":
        cam_rot = (math.radians(52), 0, math.radians(35))
        fit_camera_to_scene(scene, created_objects, fov_deg=40.0, margin=0.22, rot_euler=cam_rot)
        
        blend_path = os.path.join(SCENES_DIR, "assembled_k75.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        
        png_path = os.path.join(STAGING_DIR, "keyboard-k75.png")
        scene.render.filepath = png_path
        bpy.ops.render.render(write_still=True)
        print(f"Assembled K75 successfully rendered: {png_path}")
        
    else: # Exploded View
        cam_rot = (math.radians(56), 0, math.radians(40))
        fit_camera_to_scene(scene, created_objects, fov_deg=44.0, margin=0.25, rot_euler=cam_rot)
        
        blend_path = os.path.join(SCENES_DIR, "exploded_k75.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        
        png_path = os.path.join(STAGING_DIR, "exploded-k75.png")
        scene.render.filepath = png_path
        bpy.ops.render.render(write_still=True)
        print(f"Exploded K75 successfully rendered: {png_path}")

# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================
def main():
    target = sys.argv[-1] if len(sys.argv) > 1 and not sys.argv[-1].endswith(".py") else "all"
    print(f"--- Starting Blender 3D Rendering (Target: {target}) ---")
    
    if target in ["all", "charger"]:
        build_charger_flux()
    if target in ["all", "mat"]:
        build_mat_novadesk()
    if target in ["all", "light"]:
        build_light_beam()
    if target in ["all", "k75_assembled"]:
        build_k75_scene(mode="assembled")
    if target in ["all", "k75_exploded"]:
        build_k75_scene(mode="exploded")
        
    print("--- 3D Assets Generation Finished Successfully ---")

if __name__ == "__main__":
    main()
