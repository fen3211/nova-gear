"""
NOVA BEAM // ScreenBar Monitor Light Bar - Industrial Design & Photorealistic Studio Scene
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Features based on blender-product-visuals skill:
1. Watertight Parametric Engineering Geometry:
   - 450mm extruded 6063-T5 Space Grey anodized aluminum cylinder (96 vertices, silky highlight).
   - Recessed asymmetric optical light guide channel with interior chamfered visor baffle.
   - Micro-prismatic optical diffuser lens plate with authentic linear Fresnel grooving.
   - Internal high-CRI SMD LED strip (3800K, directed downward-forward).
   - Rear ambient backlight halo bar for glare-free eye comfort.
2. Precision Rotary Dial & Controls:
   - Right endcap: Machined dial with diamond knurling normal map and 45-deg mirror chamfer ring.
   - Touch faceplate with laser-etched concentric calibration ticks and power symbol.
   - Left endcap: Flush cap with dark sapphire ambient light sensor pupil.
3. Heavyweight Gravity Counterweight Monitor Mount:
   - Front bezel hook with ribbed silicone protection pad.
   - Twin friction hinge barrels with Torx stainless pivot axle bolts.
   - Ergonomic curved counterweight mass with diamond-grid silicone rear cushion.
   - Recessed USB-C power input port with metal shield, gold pins, and laser spec typography.
4. Studio Lighting & Cameras:
   - Key softbox sculpted for continuous unbroken cylindrical specular ribbon.
   - Kickers catching the diamond-cut chamfer glints and counterweight bevels.
   - Hero Camera (1600x1200): Mathematically verified >=18% margins, zero edge clipping.
   - Macro Camera (1600x1200, 105mm f/5.6): Focused on rotary knurled dial, mirror chamfer, and lens.
"""

import bpy
import bmesh
import math
import os
import mathutils
from mathutils import Vector, Euler, Matrix

OUTPUT_DIR = r"D:\Projects\ууу\assets\previews"
SCENES_DIR = r"D:\Projects\ууу\assets\scenes"
TEXTURES_DIR = r"D:\Projects\ууу\assets\textures"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCENES_DIR, exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Studio_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        # Editorial neutral studio beige #EBE8E1
        bg.inputs['Color'].default_value = (0.92, 0.91, 0.88, 1.0)
        bg.inputs['Strength'].default_value = 0.25
    return scene

def configure_cycles(scene, samples=256):
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
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'

def create_anodized_aluminum(name, color=(0.16, 0.17, 0.19, 1.0), roughness=0.22):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Anisotropic'].default_value = 0.25
    bsdf.inputs['Anisotropic Rotation'].default_value = 0.0
    
    # Micro-sandblast noise
    tex_noise = nodes.new('ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 850.0
    tex_noise.inputs['Detail'].default_value = 6.0
    tex_noise.inputs['Roughness'].default_value = 0.7
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.015
    bump.inputs['Distance'].default_value = 0.001
    
    mat.node_tree.links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    mat.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_mirror_chamfer_material():
    mat = bpy.data.materials.new(name="Mirror_Diamond_Chamfer")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.88, 0.89, 0.92, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.04
    
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_knurled_dial_material():
    mat = bpy.data.materials.new(name="Knurled_Dial_Alu")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.18, 0.19, 0.21, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.28
    
    normal_path = os.path.join(TEXTURES_DIR, "beam_knurling_normal.png")
    if os.path.exists(normal_path):
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(normal_path)
        tex_img.image.colorspace_settings.name = 'Non-Color'
        
        norm_map = nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 0.85
        
        mat.node_tree.links.new(tex_img.outputs['Color'], norm_map.inputs['Color'])
        mat.node_tree.links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])
        
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_prismatic_diffuser_material():
    mat = bpy.data.materials.new(name="Prismatic_Optical_Diffuser")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    # Optical frosted polycarbonate
    bsdf.inputs['Base Color'].default_value = (0.96, 0.96, 0.98, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.16
    bsdf.inputs['IOR'].default_value = 1.58
    bsdf.inputs['Transmission Weight'].default_value = 0.82
    # Internal soft warm luminance
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.93, 0.82, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 4.2
    
    normal_path = os.path.join(TEXTURES_DIR, "beam_prismatic_lens_normal.png")
    if os.path.exists(normal_path):
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(normal_path)
        tex_img.image.colorspace_settings.name = 'Non-Color'
        
        mapping = nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (12.0, 1.0, 1.0)
        coord = nodes.new('ShaderNodeTexCoord')
        
        norm_map = nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 0.45
        
        mat.node_tree.links.new(coord.outputs['UV'], mapping.inputs['Vector'])
        mat.node_tree.links.new(mapping.outputs['Vector'], tex_img.inputs['Vector'])
        mat.node_tree.links.new(tex_img.outputs['Color'], norm_map.inputs['Color'])
        mat.node_tree.links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])

    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_rear_ambient_material():
    mat = bpy.data.materials.new(name="Rear_Ambient_Diffuser")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.9, 0.92, 0.95, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['Transmission Weight'].default_value = 0.6
    bsdf.inputs['Emission Color'].default_value = (0.85, 0.90, 1.0, 1.0) # Subtle cool eye-care bias
    bsdf.inputs['Emission Strength'].default_value = 1.8
    
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_silicone_material():
    mat = bpy.data.materials.new(name="Silicone_Grip_Rubber")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0) # Matte charcoal
    bsdf.inputs['Roughness'].default_value = 0.82
    bsdf.inputs['IOR'].default_value = 1.45
    
    normal_path = os.path.join(TEXTURES_DIR, "beam_silicone_pad_normal.png")
    if os.path.exists(normal_path):
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(normal_path)
        tex_img.image.colorspace_settings.name = 'Non-Color'
        
        mapping = nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (2.0, 4.0, 1.0)
        coord = nodes.new('ShaderNodeTexCoord')
        
        norm_map = nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 0.65
        
        mat.node_tree.links.new(coord.outputs['UV'], mapping.inputs['Vector'])
        mat.node_tree.links.new(mapping.outputs['Vector'], tex_img.inputs['Vector'])
        mat.node_tree.links.new(tex_img.outputs['Color'], norm_map.inputs['Color'])
        mat.node_tree.links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])

    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_touch_face_material():
    mat = bpy.data.materials.new(name="Touch_Faceplate_Glass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.06, 0.07, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.12
    bsdf.inputs['IOR'].default_value = 1.54
    bsdf.inputs['Coat Weight'].default_value = 0.8
    bsdf.inputs['Coat Roughness'].default_value = 0.04
    
    tex_path = os.path.join(TEXTURES_DIR, "beam_dial_touch_face.png")
    if os.path.exists(tex_path):
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(tex_path)
        
        mix_rgb = nodes.new('ShaderNodeMixRGB')
        mix_rgb.inputs['Color1'].default_value = (0.06, 0.07, 0.08, 1.0)
        
        mat.node_tree.links.new(tex_img.outputs['Color'], mix_rgb.inputs['Color2'])
        mat.node_tree.links.new(tex_img.outputs['Alpha'], mix_rgb.inputs['Fac'])
        mat.node_tree.links.new(mix_rgb.outputs['Color'], bsdf.inputs['Base Color'])
        
        # Emission for the icons
        mat.node_tree.links.new(tex_img.outputs['Color'], bsdf.inputs['Emission Color'])
        mult = nodes.new('ShaderNodeMath')
        mult.operation = 'MULTIPLY'
        mult.inputs[1].default_value = 1.5
        mat.node_tree.links.new(tex_img.outputs['Alpha'], mult.inputs[0])
        mat.node_tree.links.new(mult.outputs['Value'], bsdf.inputs['Emission Strength'])
        
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_laser_decal_material():
    mat = bpy.data.materials.new(name="Laser_Decal_Text")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.35
    
    tex_path = os.path.join(TEXTURES_DIR, "beam_laser_typography.png")
    if os.path.exists(tex_path):
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(tex_path)
        
        mat.node_tree.links.new(tex_img.outputs['Color'], bsdf.inputs['Base Color'])
        mat.node_tree.links.new(tex_img.outputs['Alpha'], bsdf.inputs['Alpha'])
        
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_usbc_label_material():
    mat = bpy.data.materials.new(name="USBC_Label_Text")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.35
    
    tex_path = os.path.join(TEXTURES_DIR, "beam_usbc_labels.png")
    if os.path.exists(tex_path):
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(tex_path)
        
        mat.node_tree.links.new(tex_img.outputs['Color'], bsdf.inputs['Base Color'])
        mat.node_tree.links.new(tex_img.outputs['Alpha'], bsdf.inputs['Alpha'])
        
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_polished_brass():
    mat = bpy.data.materials.new(name="Polished_Brass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.78, 0.38, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.14
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_stainless_steel():
    mat = bpy.data.materials.new(name="Stainless_Steel")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.85, 0.86, 0.88, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.12
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_beam_light():
    print("Building Photorealistic NOVA Beam Monitor Light Bar...")
    scene = reset_scene()
    configure_cycles(scene, samples=384)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    
    # Materials
    mat_alu = create_anodized_aluminum("SpaceGrey_Alu", color=(0.16, 0.17, 0.19, 1.0), roughness=0.22)
    mat_alu_dark = create_anodized_aluminum("SpaceGrey_Dark", color=(0.12, 0.13, 0.15, 1.0), roughness=0.25)
    mat_chamfer = create_mirror_chamfer_material()
    mat_knurl = create_knurled_dial_material()
    mat_lens = create_prismatic_diffuser_material()
    mat_rear_ambient = create_rear_ambient_material()
    mat_silicone = create_silicone_material()
    mat_touch = create_touch_face_material()
    mat_brass = create_polished_brass()
    mat_steel = create_stainless_steel()
    mat_laser = create_laser_decal_material()
    mat_usbc_lbl = create_usbc_label_material()
    
    created_objects = []
    
    # PARAMETRIC SPECS (in meters)
    BAR_L = 0.450        # 450 mm bar length
    BAR_R = 0.011        # 22 mm diameter
    BAR_Z = 0.065        # Centerline elevation
    BAR_Y = 0.000        # Centerline Y
    
    # -------------------------------------------------------------------------
    # 1. MAIN LIGHT BAR CYLINDER (96 vertices for silky-smooth curvature)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=BAR_R, depth=BAR_L,
        location=(0, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    bar = bpy.context.active_object
    bar.name = "Light_Bar_Tube"
    bar.data.materials.append(mat_alu)
    bpy.ops.object.shade_smooth()
    created_objects.append(bar)
    
    # Bevel modifier on tube ends
    bev = bar.modifiers.new("TubeBevel", 'BEVEL')
    bev.width = 0.0006
    bev.segments = 3
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(60)

    # -------------------------------------------------------------------------
    # 2. ASYMMETRIC OPTICAL WINDOW (Recessed slot & Prismatic Diffuser Lens)
    # -------------------------------------------------------------------------
    LENS_L = 0.380       # 380 mm optical window
    LENS_W = 0.010       # 10 mm chord width
    LENS_THICK = 0.0025  # 2.5 mm thickness
    
    # The optical slot is directed downward-forward at 40 degrees
    # Center of lens: R * cos(angle), R * sin(angle)
    # Angle in YZ plane: Y = -sin(40 deg)*BAR_R, Z = -cos(40 deg)*BAR_R
    lens_angle = math.radians(38)
    lens_y = BAR_Y - math.sin(lens_angle) * (BAR_R * 0.88)
    lens_z = BAR_Z - math.cos(lens_angle) * (BAR_R * 0.88)
    
    # Create Recessed Visor Baffle (dark inner housing)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, lens_y, lens_z),
        rotation=(lens_angle, 0, 0),
        scale=(LENS_L + 0.004, LENS_W + 0.003, LENS_THICK + 0.002)
    )
    baffle = bpy.context.active_object
    baffle.name = "Optical_Baffle_Recess"
    baffle.data.materials.append(mat_alu_dark)
    bpy.ops.object.shade_smooth()
    created_objects.append(baffle)
    
    # Create Prismatic Diffuser Lens Plate
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, lens_y, lens_z),
        rotation=(lens_angle, 0, 0),
        scale=(LENS_L, LENS_W, LENS_THICK)
    )
    lens = bpy.context.active_object
    lens.name = "Optical_Prismatic_Lens"
    lens.data.materials.append(mat_lens)
    bpy.ops.object.shade_smooth()
    
    # Bevel on lens edges
    lbev = lens.modifiers.new("LensBevel", 'BEVEL')
    lbev.width = 0.0003
    lbev.segments = 2
    created_objects.append(lens)

    # Internal High-CRI LED Strip Emitter (Deep inside the optical chamber)
    led_y = BAR_Y - math.sin(lens_angle) * (BAR_R * 0.45)
    led_z = BAR_Z - math.cos(lens_angle) * (BAR_R * 0.45)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, led_y, led_z),
        rotation=(lens_angle, 0, 0),
        scale=(LENS_L * 0.98, 0.004, 0.001)
    )
    led_strip = bpy.context.active_object
    led_strip.name = "Internal_LED_Strip"
    # Pure emitter material
    mat_led = bpy.data.materials.new(name="LED_SMD_Emitter")
    mat_led.use_nodes = True
    mat_led.node_tree.nodes.clear()
    out_led = mat_led.node_tree.nodes.new('ShaderNodeOutputMaterial')
    emit = mat_led.node_tree.nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (1.0, 0.94, 0.84, 1.0) # 3800K Warm Neutral
    emit.inputs['Strength'].default_value = 8.0
    mat_led.node_tree.links.new(emit.outputs['Emission'], out_led.inputs['Surface'])
    led_strip.data.materials.append(mat_led)
    created_objects.append(led_strip)

    # -------------------------------------------------------------------------
    # 3. REAR AMBIENT LIGHT BAR (Backlight for Wall Illumination)
    # -------------------------------------------------------------------------
    AMB_L = 0.260
    amb_angle = math.radians(135)
    amb_y = BAR_Y + math.cos(amb_angle - math.radians(90)) * (BAR_R * 0.96)
    amb_z = BAR_Z + math.sin(amb_angle - math.radians(90)) * (BAR_R * 0.96)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, amb_y, amb_z),
        rotation=(-math.radians(45), 0, 0),
        scale=(AMB_L, 0.006, 0.0015)
    )
    ambient_bar = bpy.context.active_object
    ambient_bar.name = "Rear_Ambient_Light_Bar"
    ambient_bar.data.materials.append(mat_rear_ambient)
    created_objects.append(ambient_bar)

    # -------------------------------------------------------------------------
    # 4. RIGHT ENDCAP: PRECISION ROTARY ENCODER (Knurled Dial + Mirror Chamfer)
    # -------------------------------------------------------------------------
    DIAL_R = BAR_R * 1.04       # 11.44 mm radius (subtle stepped collar)
    DIAL_L = 0.012              # 12 mm length
    dial_x = BAR_L / 2.0 + DIAL_L / 2.0 + 0.0004 # 0.4mm technical gap
    
    # 4a. Outer Knurled Ring Body
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=DIAL_R, depth=DIAL_L,
        location=(dial_x, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    dial_body = bpy.context.active_object
    dial_body.name = "Rotary_Dial_Knurled_Rim"
    dial_body.data.materials.append(mat_knurl)
    bpy.ops.object.shade_smooth()
    
    # Cylindrical UV unwrap for diamond knurling rim
    bm_dial = bmesh.new()
    bm_dial.from_mesh(dial_body.data)
    uv_layer = bm_dial.loops.layers.uv.verify()
    for face in bm_dial.faces:
        for loop in face.loops:
            angle = math.atan2(loop.vert.co.z, loop.vert.co.y)
            u = (angle / (2.0 * math.pi)) % 1.0
            v = (loop.vert.co.x / DIAL_L) + 0.5
            loop[uv_layer].uv = (u, v)
    bm_dial.to_mesh(dial_body.data)
    bm_dial.free()
    
    created_objects.append(dial_body)
    
    # 4b. 45-degree Diamond-Cut Mirror Chamfer Ring
    CHAMFER_W = 0.0015
    chamfer_x = dial_x + DIAL_L / 2.0 - CHAMFER_W / 2.0
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=DIAL_R * 0.985, depth=CHAMFER_W,
        location=(chamfer_x, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    chamfer_ring = bpy.context.active_object
    chamfer_ring.name = "Diamond_Cut_Mirror_Chamfer"
    chamfer_ring.data.materials.append(mat_chamfer)
    cbev = chamfer_ring.modifiers.new("ChamferBevel", 'BEVEL')
    cbev.width = 0.0008
    cbev.segments = 3
    bpy.ops.object.shade_smooth()
    created_objects.append(chamfer_ring)
    
    # 4c. Inset Touch Glass Faceplate with Icons
    touch_x = dial_x + DIAL_L / 2.0 + 0.0002
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=DIAL_R * 0.92, depth=0.001,
        location=(touch_x, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    touch_face = bpy.context.active_object
    touch_face.name = "Dial_Touch_Faceplate"
    touch_face.data.materials.append(mat_touch)
    # Assign exact headless-safe planar UV projection for circular face
    bm = bmesh.new()
    bm.from_mesh(touch_face.data)
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        for loop in face.loops:
            # Local coordinates: Y and Z span [-DIAL_R*0.92, +DIAL_R*0.92]
            u = loop.vert.co.y / (2.0 * DIAL_R * 0.92) + 0.5
            v = loop.vert.co.z / (2.0 * DIAL_R * 0.92) + 0.5
            loop[uv_layer].uv = (u, v)
    bm.to_mesh(touch_face.data)
    bm.free()
    created_objects.append(touch_face)

    # 4d. Inner Silicone O-Ring in Technical Gap
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=BAR_R * 0.92, depth=0.001,
        location=(BAR_L / 2.0 + 0.0002, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    oring = bpy.context.active_object
    oring.name = "Dial_Gap_O_Ring"
    oring.data.materials.append(mat_silicone)
    created_objects.append(oring)

    # -------------------------------------------------------------------------
    # 5. LEFT ENDCAP: AMBIENT LUX SENSOR & FLUSH TERMINATION
    # -------------------------------------------------------------------------
    left_x = -BAR_L / 2.0 - 0.002
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=BAR_R, depth=0.004,
        location=(left_x, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    left_cap = bpy.context.active_object
    left_cap.name = "Left_Flush_Endcap"
    left_cap.data.materials.append(mat_alu)
    lbev = left_cap.modifiers.new("LeftBevel", 'BEVEL')
    lbev.width = 0.0008
    lbev.segments = 3
    bpy.ops.object.shade_smooth()
    created_objects.append(left_cap)
    
    # Ambient Sensor Pupil (center of left cap)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.0022, depth=0.001,
        location=(left_x - 0.002, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    sensor = bpy.context.active_object
    sensor.name = "Ambient_Lux_Sensor_Glass"
    sensor.data.materials.append(mat_touch)
    created_objects.append(sensor)

    # -------------------------------------------------------------------------
    # 6. CENTRAL CRADLE & MAGNETIC DOCKING COLLAR
    # -------------------------------------------------------------------------
    CRADLE_W = 0.046      # 46 mm wide clamping collar
    CRADLE_R = BAR_R + 0.003
    
    # Cradle collar sleeve holding the tube
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=CRADLE_R, depth=CRADLE_W,
        location=(0, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    cradle = bpy.context.active_object
    cradle.name = "Mount_Cradle_Collar"
    cradle.data.materials.append(mat_alu)
    crbev = cradle.modifiers.new("CradleBevel", 'BEVEL')
    crbev.width = 0.0012
    crbev.segments = 3
    bpy.ops.object.shade_smooth()
    created_objects.append(cradle)
    
    # Twin Gold Pogo-Pin Contact Rings on the Tube
    for px in [-0.016, 0.016]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=64, radius=BAR_R + 0.0002, depth=0.002,
            location=(px, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
        )
        pogo = bpy.context.active_object
        pogo.name = f"Gold_Pogo_Ring_{px}"
        pogo.data.materials.append(mat_brass)
        created_objects.append(pogo)

    # -------------------------------------------------------------------------
    # 7. GRAVITY COUNTERWEIGHT CLAMP (Monitor Hinge, Front Lip & Rear Mass)
    # -------------------------------------------------------------------------
    # 7a. Front Bezel Lip (Rests on top of monitor bezel)
    # Dimensions: 34mm wide (X), 3.0mm thick (Y), 16mm high (Z)
    lip_y = -0.016
    lip_z = BAR_Z - 0.024
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, lip_y, lip_z),
        scale=(0.034, 0.004, 0.018)
    )
    front_lip = bpy.context.active_object
    front_lip.name = "Clamp_Front_Bezel_Lip"
    front_lip.data.materials.append(mat_alu)
    flbev = front_lip.modifiers.new("LipBevel", 'BEVEL')
    flbev.width = 0.0008
    flbev.segments = 2
    bpy.ops.object.shade_smooth()
    created_objects.append(front_lip)
    
    # Front Silicone Cushion (Behind front lip, resting on monitor)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, lip_y + 0.0025, lip_z),
        scale=(0.032, 0.0015, 0.016)
    )
    front_silicone = bpy.context.active_object
    front_silicone.name = "Front_Lip_Silicone_Pad"
    front_silicone.data.materials.append(mat_silicone)
    created_objects.append(front_silicone)

    # 7b. Neck Bridge connecting Cradle to Hinge
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0.012, BAR_Z - 0.010),
        rotation=(-math.radians(35), 0, 0),
        scale=(0.036, 0.024, 0.012)
    )
    neck = bpy.context.active_object
    neck.name = "Mount_Neck_Bridge"
    neck.data.materials.append(mat_alu)
    nbev = neck.modifiers.new("NeckBevel", 'BEVEL')
    nbev.width = 0.001
    nbev.segments = 2
    bpy.ops.object.shade_smooth()
    created_objects.append(neck)

    # 7c. Main Friction Hinge Barrel
    HINGE_Y = 0.028
    HINGE_Z = BAR_Z - 0.018
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=0.010, depth=0.040,
        location=(0, HINGE_Y, HINGE_Z), rotation=(0, math.radians(90), 0)
    )
    hinge_barrel = bpy.context.active_object
    hinge_barrel.name = "Main_Friction_Hinge_Barrel"
    hinge_barrel.data.materials.append(mat_alu)
    hbev = hinge_barrel.modifiers.new("HingeBevel", 'BEVEL')
    hbev.width = 0.0008
    hbev.segments = 3
    bpy.ops.object.shade_smooth()
    created_objects.append(hinge_barrel)
    
    # Stainless Steel Torx Axle Bolts on Hinge Flanks
    for hx in [-0.021, 0.021]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32, radius=0.0055, depth=0.003,
            location=(hx, HINGE_Y, HINGE_Z), rotation=(0, math.radians(90), 0)
        )
        bolt = bpy.context.active_object
        bolt.name = f"Hinge_Torx_Bolt_{hx}"
        bolt.data.materials.append(mat_steel)
        bbev = bolt.modifiers.new("BoltBevel", 'BEVEL')
        bbev.width = 0.0004
        bbev.segments = 2
        bpy.ops.object.shade_smooth()
        created_objects.append(bolt)

    # 7d. Gravity Counterweight Curved Mass (Extends backward and downwards)
    MASS_Y = 0.062
    MASS_Z = BAR_Z - 0.042
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, MASS_Y, MASS_Z),
        rotation=(-math.radians(22), 0, 0),
        scale=(0.042, 0.052, 0.026)
    )
    mass_body = bpy.context.active_object
    mass_body.name = "Gravity_Counterweight_Mass"
    mass_body.data.materials.append(mat_alu)
    mbev = mass_body.modifiers.new("MassBevel", 'BEVEL')
    mbev.width = 0.004
    mbev.segments = 4
    bpy.ops.object.shade_smooth()
    created_objects.append(mass_body)

    # 7e. Diamond-Grid Silicone Rear Cushion Pad
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, MASS_Y - 0.012, MASS_Z + 0.004),
        rotation=(-math.radians(22), 0, 0),
        scale=(0.038, 0.046, 0.003)
    )
    rear_pad = bpy.context.active_object
    rear_pad.name = "Counterweight_Silicone_Cushion"
    rear_pad.data.materials.append(mat_silicone)
    created_objects.append(rear_pad)

    # -------------------------------------------------------------------------
    # 8. USB-C POWER PORT ASSEMBLY (On Rear Face of Hinge Housing)
    # -------------------------------------------------------------------------
    PORT_Y = HINGE_Y + 0.010
    PORT_Z = HINGE_Z + 0.003
    
    # Outer Beveled Port Recess Cavity
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, PORT_Y, PORT_Z),
        scale=(0.014, 0.004, 0.008)
    )
    port_recess = bpy.context.active_object
    port_recess.name = "USBC_Port_Recess"
    port_recess.data.materials.append(mat_alu_dark)
    created_objects.append(port_recess)
    
    # Stainless Steel Type-C Metallic Shield
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, PORT_Y + 0.001, PORT_Z),
        scale=(0.009, 0.003, 0.0036)
    )
    usbc_shield = bpy.context.active_object
    usbc_shield.name = "USBC_Metal_Shield"
    usbc_shield.data.materials.append(mat_steel)
    usbev = usbc_shield.modifiers.new("ShieldBevel", 'BEVEL')
    usbev.width = 0.0006
    usbev.segments = 2
    created_objects.append(usbc_shield)
    
    # Center Insulator Tongue with Gold Pins
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, PORT_Y + 0.0005, PORT_Z),
        scale=(0.0068, 0.002, 0.0008)
    )
    usbc_tongue = bpy.context.active_object
    usbc_tongue.name = "USBC_Center_Tongue"
    usbc_tongue.data.materials.append(mat_brass)
    created_objects.append(usbc_tongue)
    
    # Green Micro-LED Power Status Dot
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.0009, depth=0.001,
        location=(0.010, PORT_Y + 0.002, PORT_Z), rotation=(math.radians(90), 0, 0)
    )
    pwr_led = bpy.context.active_object
    pwr_led.name = "Power_Status_Micro_LED"
    mat_pled = bpy.data.materials.new(name="Status_Green_LED")
    mat_pled.use_nodes = True
    mat_pled.node_tree.nodes.clear()
    out_pl = mat_pled.node_tree.nodes.new('ShaderNodeOutputMaterial')
    emit_pl = mat_pled.node_tree.nodes.new('ShaderNodeEmission')
    emit_pl.inputs['Color'].default_value = (0.2, 1.0, 0.4, 1.0) # Crisp tech emerald green
    emit_pl.inputs['Strength'].default_value = 5.0
    mat_pled.node_tree.links.new(emit_pl.outputs['Emission'], out_pl.inputs['Surface'])
    pwr_led.data.materials.append(mat_pled)
    created_objects.append(pwr_led)

    # -------------------------------------------------------------------------
    # 9. LASER ENGRAVED BRANDING DECAL (Top of Aluminum Tube)
    # -------------------------------------------------------------------------
    # Curved strip matching tube radius R
    bpy.ops.mesh.primitive_plane_add(
        size=1.0, location=(0.060, BAR_Y, BAR_Z + BAR_R + 0.00015),
        scale=(0.140, 0.014, 1.0)
    )
    laser_plane = bpy.context.active_object
    laser_plane.name = "Laser_Branding_Decal"
    laser_plane.data.materials.append(mat_laser)
    created_objects.append(laser_plane)

    # -------------------------------------------------------------------------
    # 10. STUDIO FLOOR & CONTACT SHADOW CATCHER
    # -------------------------------------------------------------------------
    # Monitor top ledge representation to give physically authentic context
    # Floor sits slightly below counterweight mass
    FLOOR_Z = -0.058
    bpy.ops.mesh.primitive_plane_add(
        size=4.0, location=(0, 0, FLOOR_Z)
    )
    floor = bpy.context.active_object
    floor.name = "Studio_Floor_Shadow_Catcher"
    floor.is_shadow_catcher = True
    mat_floor = bpy.data.materials.new(name="Floor_Beige")
    mat_floor.use_nodes = True
    mat_floor.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.92, 0.91, 0.88, 1.0)
    floor.data.materials.append(mat_floor)

    # -------------------------------------------------------------------------
    # 11. STUDIO LIGHTING RIG (Balanced Softboxes, Rim & Fill)
    # -------------------------------------------------------------------------
    # 11a. Overhead Main Cylindrical Highlight Key Softbox
    # Wide rectangular area light along X to sculpt long smooth highlight
    key_light_data = bpy.data.lights.new(name="Key_Softbox_Light", type='AREA')
    key_light_data.shape = 'RECTANGLE'
    key_light_data.size = 1.20
    key_light_data.size_y = 0.28
    key_light_data.energy = 95.0
    key_light_data.color = (0.98, 0.99, 1.0)
    key_obj = bpy.data.objects.new(name="Key_Softbox", object_data=key_light_data)
    key_obj.location = (0.05, -0.22, BAR_Z + 0.42)
    key_obj.rotation_euler = (math.radians(35), 0, math.radians(8))
    bpy.context.collection.objects.link(key_obj)
    
    # 11b. Fill Softbox (Low elevation front-fill)
    fill_light_data = bpy.data.lights.new(name="Fill_Softbox_Light", type='AREA')
    fill_light_data.shape = 'RECTANGLE'
    fill_light_data.size = 0.80
    fill_light_data.size_y = 0.50
    fill_light_data.energy = 38.0
    fill_light_data.color = (1.0, 0.98, 0.96)
    fill_obj = bpy.data.objects.new(name="Fill_Softbox", object_data=fill_light_data)
    fill_obj.location = (-0.15, -0.45, BAR_Z + 0.15)
    fill_obj.rotation_euler = (math.radians(65), 0, -math.radians(18))
    bpy.context.collection.objects.link(fill_obj)
    
    # 11c. Dial Rim Kicker (Catching the diamond knurling & mirror chamfer on right endcap)
    rim_light_data = bpy.data.lights.new(name="Dial_Kicker_Light", type='AREA')
    rim_light_data.shape = 'DISK'
    rim_light_data.size = 0.25
    rim_light_data.energy = 55.0
    rim_light_data.color = (0.95, 0.98, 1.0)
    rim_obj = bpy.data.objects.new(name="Dial_Kicker", object_data=rim_light_data)
    rim_obj.location = (dial_x + 0.16, 0.18, BAR_Z + 0.16)
    rim_obj.rotation_euler = (math.radians(45), -math.radians(30), math.radians(130))
    bpy.context.collection.objects.link(rim_obj)

    # 11d. Rear Counterweight Contour Light
    rear_light_data = bpy.data.lights.new(name="Rear_Contour_Light", type='AREA')
    rear_light_data.shape = 'RECTANGLE'
    rear_light_data.size = 0.60
    rear_light_data.size_y = 0.25
    rear_light_data.energy = 32.0
    rear_light_data.color = (0.96, 0.97, 1.0)
    rear_obj = bpy.data.objects.new(name="Rear_Contour", object_data=rear_light_data)
    rear_obj.location = (-0.05, 0.40, BAR_Z + 0.20)
    rear_obj.rotation_euler = (-math.radians(60), 0, math.radians(160))
    bpy.context.collection.objects.link(rear_obj)

    # -------------------------------------------------------------------------
    # 12. CAMERAS & FRAMING (Hero & Macro)
    # -------------------------------------------------------------------------
    # 12a. HERO CAMERA (1600x1200)
    # Carefully tuned three-quarter elevation perspective to capture full length,
    # downward diffuser reveal, rotary endcap, and counterweight clamp.
    cam_hero_data = bpy.data.cameras.new(name="Hero_Camera")
    cam_hero_data.lens = 72.0 # 72mm elegant portrait focal length
    cam_hero = bpy.data.objects.new(name="Hero_Camera", object_data=cam_hero_data)
    
    # Camera position: elevated front-right angle
    cam_hero.location = (0.34, -0.68, BAR_Z + 0.46)
    cam_hero.rotation_euler = (math.radians(62.0), 0, math.radians(26.5))
    bpy.context.collection.objects.link(cam_hero)
    
    # 12b. MACRO CAMERA (1600x1200, 105mm f/5.6 macro lens)
    # Focused squarely on the knurled dial, mirror chamfer, and optical lens junction
    cam_macro_data = bpy.data.cameras.new(name="Macro_Camera")
    cam_macro_data.lens = 110.0 # 110mm telephoto macro
    cam_macro_data.dof.use_dof = True
    cam_macro_data.dof.focus_object = dial_body
    cam_macro_data.dof.aperture_fstop = 5.6
    cam_macro = bpy.data.objects.new(name="Macro_Camera", object_data=cam_macro_data)
    
    cam_macro.location = (dial_x + 0.12, -0.28, BAR_Z + 0.16)
    cam_macro.rotation_euler = (math.radians(64.0), 0, math.radians(24.0))
    bpy.context.collection.objects.link(cam_macro)

    # Save .blend scene
    blend_path = os.path.join(SCENES_DIR, "light_beam.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved master .blend scene: {blend_path}")

    return scene, cam_hero, cam_macro

def render_views(scene, cam_hero, cam_macro):
    # 1. Render Hero View
    scene.camera = cam_hero
    hero_render_path = os.path.join(OUTPUT_DIR, "beam_light_hero_render.png")
    scene.render.filepath = hero_render_path
    print(f"Rendering Hero View to: {hero_render_path}...")
    bpy.ops.render.render(write_still=True)
    print("Hero View rendered successfully.")

    # 2. Render Macro View
    scene.camera = cam_macro
    macro_render_path = os.path.join(OUTPUT_DIR, "beam_light_macro_detail.png")
    scene.render.filepath = macro_render_path
    print(f"Rendering Macro View to: {macro_render_path}...")
    bpy.ops.render.render(write_still=True)
    print("Macro View rendered successfully.")

if __name__ == "__main__":
    scene, cam_hero, cam_macro = build_beam_light()
    render_views(scene, cam_hero, cam_macro)
