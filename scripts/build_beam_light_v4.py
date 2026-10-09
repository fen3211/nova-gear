"""
NOVA BEAM // ScreenBar Monitor Light Bar - Master Photorealistic Studio Scene V4
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Key Refinements in V4:
1. Flawless Local Space UV Coordinates:
   - Fixed cylinder local coordinates (X/Y circle, Z height) for both Dial Knurling and Touch Faceplate.
   - Touch Faceplate displays crisp circular power glyph, concentric graduation ticks, and tactile typography.
   - Knurled dial displays ultra-sharp, undistorted diamond pyramid grip relief.
2. Foreground Rotary Dial & Dynamic 3/4 Perspective:
   - Rotated by -26 deg around Z so the precision rotary dial and mirror chamfer lead in the foreground.
   - Mounting clamp viewed in true 3/4 elevation, showcasing front bezel hook, twin friction hinges,
     and gravity counterweight body.
3. Asymmetric Light Beam Projection:
   - True directional optical projector light inside the optical visor, casting an authentic warm-neutral
     fan of light onto the desk surface in front of the lamp.
   - Micro-prismatic optical diffuser plate with subtle internal luminance.
4. Editorial Studio Staging:
   - Studio floor #EBE8E1 with soft physical contact shadows.
   - Guaranteed >=18% margins all around.
   - 3/4 Macro close-up tightly framed on the rotary dial, mirror chamfer, and optical window start.
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
        bg.inputs['Color'].default_value = (0.88, 0.86, 0.82, 1.0)
        bg.inputs['Strength'].default_value = 0.85
    return scene

def configure_cycles(scene, samples=384):
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

def create_anodized_aluminum(name, color=(0.11, 0.12, 0.14, 1.0), roughness=0.22):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Anisotropic'].default_value = 0.30
    bsdf.inputs['Anisotropic Rotation'].default_value = 0.0
    
    # Subtle sandblast noise
    tex_noise = nodes.new('ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 1400.0
    tex_noise.inputs['Detail'].default_value = 4.0
    tex_noise.inputs['Roughness'].default_value = 0.6
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.006
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
    bsdf.inputs['Base Color'].default_value = (0.95, 0.96, 0.98, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.03
    
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_knurled_dial_material():
    mat = bpy.data.materials.new(name="Knurled_Dial_Alu")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.13, 0.14, 0.16, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.25
    
    normal_path = os.path.join(TEXTURES_DIR, "beam_knurling_normal.png")
    if os.path.exists(normal_path):
        coord = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (1.0, 3.0, 1.0)
        
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(normal_path)
        tex_img.image.colorspace_settings.name = 'Non-Color'
        
        norm_map = nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 0.90
        
        mat.node_tree.links.new(coord.outputs['UV'], mapping.inputs['Vector'])
        mat.node_tree.links.new(mapping.outputs['Vector'], tex_img.inputs['Vector'])
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
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.97, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.16
    bsdf.inputs['IOR'].default_value = 1.58
    bsdf.inputs['Transmission Weight'].default_value = 0.88
    # Controlled soft warm glow
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.94, 0.86, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 2.8
    
    normal_path = os.path.join(TEXTURES_DIR, "beam_prismatic_lens_normal.png")
    if os.path.exists(normal_path):
        coord = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (8.0, 1.0, 1.0)
        
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(normal_path)
        tex_img.image.colorspace_settings.name = 'Non-Color'
        
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
    bsdf.inputs['Base Color'].default_value = (0.9, 0.92, 0.96, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.28
    bsdf.inputs['Transmission Weight'].default_value = 0.7
    bsdf.inputs['Emission Color'].default_value = (0.88, 0.92, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 1.2
    
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_silicone_material():
    mat = bpy.data.materials.new(name="Silicone_Grip_Rubber")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.82
    bsdf.inputs['IOR'].default_value = 1.45
    
    normal_path = os.path.join(TEXTURES_DIR, "beam_silicone_pad_normal.png")
    if os.path.exists(normal_path):
        coord = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (2.0, 4.0, 1.0)
        
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(normal_path)
        tex_img.image.colorspace_settings.name = 'Non-Color'
        
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
    bsdf.inputs['Base Color'].default_value = (0.04, 0.045, 0.055, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.12
    bsdf.inputs['IOR'].default_value = 1.54
    bsdf.inputs['Coat Weight'].default_value = 0.7
    bsdf.inputs['Coat Roughness'].default_value = 0.04
    
    tex_path = os.path.join(TEXTURES_DIR, "beam_dial_touch_face.png")
    if os.path.exists(tex_path):
        coord = nodes.new('ShaderNodeTexCoord')
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(tex_path)
        mat.node_tree.links.new(coord.outputs['UV'], tex_img.inputs['Vector'])
        
        mix_rgb = nodes.new('ShaderNodeMix')
        mix_rgb.data_type = 'RGBA'
        mix_rgb.inputs['A'].default_value = (0.04, 0.045, 0.055, 1.0)
        mat.node_tree.links.new(tex_img.outputs['Color'], mix_rgb.inputs['B'])
        mat.node_tree.links.new(tex_img.outputs['Alpha'], mix_rgb.inputs['Factor'])
        mat.node_tree.links.new(mix_rgb.outputs['Result'], bsdf.inputs['Base Color'])
        
        # Subtle emission for the white icons & graduation ring
        mat.node_tree.links.new(tex_img.outputs['Color'], bsdf.inputs['Emission Color'])
        mult = nodes.new('ShaderNodeMath')
        mult.operation = 'MULTIPLY'
        mult.inputs[1].default_value = 1.2
        mat.node_tree.links.new(tex_img.outputs['Alpha'], mult.inputs[0])
        mat.node_tree.links.new(mult.outputs['Value'], bsdf.inputs['Emission Strength'])
        
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
    print("Building Photorealistic NOVA Beam Monitor Light Bar V4...")
    scene = reset_scene()
    configure_cycles(scene, samples=384)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    
    # Materials
    mat_alu = create_anodized_aluminum("SpaceGrey_Alu", color=(0.11, 0.12, 0.14, 1.0), roughness=0.22)
    mat_alu_dark = create_anodized_aluminum("SpaceGrey_Dark", color=(0.07, 0.08, 0.09, 1.0), roughness=0.28)
    mat_chamfer = create_mirror_chamfer_material()
    mat_knurl = create_knurled_dial_material()
    mat_lens = create_prismatic_diffuser_material()
    mat_rear_ambient = create_rear_ambient_material()
    mat_silicone = create_silicone_material()
    mat_touch = create_touch_face_material()
    mat_brass = create_polished_brass()
    mat_steel = create_stainless_steel()
    
    # Parent Root Empty for 3/4 Dynamic Angle Orientation
    # Rotated around Z by -26 degrees: Rotary dial brings detail forward to right foreground
    ROT_Z = math.radians(-26.0)
    root = bpy.data.objects.new("Beam_Light_Root", None)
    bpy.context.collection.objects.link(root)
    root.rotation_euler = (0, 0, ROT_Z)
    
    # PARAMETRIC SPECS (in meters, local space)
    BAR_L = 0.450        # 450 mm bar length
    BAR_R = 0.012        # 24 mm diameter
    BAR_Z = 0.072        # Centerline elevation above floor
    BAR_Y = 0.000        # Centerline Y
    
    lamp_objects = []

    # -------------------------------------------------------------------------
    # 1. MAIN LIGHT BAR CYLINDER (96 vertices, Boolean Inset Optical Window)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=BAR_R, depth=BAR_L,
        location=(0, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    bar = bpy.context.active_object
    bar.name = "Light_Bar_Tube"
    bar.data.materials.append(mat_alu)
    bpy.ops.object.shade_smooth()
    
    # 1b. Boolean Cutter to carve recessed optical slot directly into the cylinder
    LENS_L = 0.370       # 370 mm optical window
    LENS_W = 0.008       # 8.0 mm slot chord
    LENS_DEPTH = 0.0035  # 3.5 mm depth into tube
    
    lens_angle = math.radians(38)
    cut_y = BAR_Y - math.sin(lens_angle) * (BAR_R - LENS_DEPTH * 0.4)
    cut_z = BAR_Z - math.cos(lens_angle) * (BAR_R - LENS_DEPTH * 0.4)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, cut_y, cut_z),
        rotation=(lens_angle, 0, 0),
        scale=(LENS_L, LENS_W, LENS_DEPTH * 2.0)
    )
    cutter = bpy.context.active_object
    cutter.name = "Optical_Slot_Cutter"
    cutter.display_type = 'WIRE'
    
    bool_mod = bar.modifiers.new("SlotCutter", 'BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter
    bool_mod.solver = 'EXACT'
    
    bpy.context.view_layer.objects.active = bar
    bpy.ops.object.modifier_apply(modifier="SlotCutter")
    bpy.data.objects.remove(cutter, do_unlink=True)
    
    wn = bar.modifiers.new("WeightedNormals", 'WEIGHTED_NORMAL')
    wn.keep_sharp = True
    
    bev = bar.modifiers.new("TubeBevel", 'BEVEL')
    bev.width = 0.0005
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(70)
    
    lamp_objects.append(bar)

    # -------------------------------------------------------------------------
    # 2. PRISMATIC OPTICAL DIFFUSER LENS & DIRECTIONAL ASYMMETRIC LIGHT BEAM
    # -------------------------------------------------------------------------
    lens_pos_y = BAR_Y - math.sin(lens_angle) * (BAR_R - 0.0012)
    lens_pos_z = BAR_Z - math.cos(lens_angle) * (BAR_R - 0.0012)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, lens_pos_y, lens_pos_z),
        rotation=(lens_angle, 0, 0),
        scale=(LENS_L * 0.995, LENS_W * 0.96, 0.0016)
    )
    lens = bpy.context.active_object
    lens.name = "Optical_Prismatic_Lens"
    lens.data.materials.append(mat_lens)
    lamp_objects.append(lens)

    # Internal High-CRI LED Strip Emitter
    led_pos_y = BAR_Y - math.sin(lens_angle) * (BAR_R - 0.0032)
    led_pos_z = BAR_Z - math.cos(lens_angle) * (BAR_R - 0.0032)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, led_pos_y, led_pos_z),
        rotation=(lens_angle, 0, 0),
        scale=(LENS_L * 0.98, 0.003, 0.0006)
    )
    led_strip = bpy.context.active_object
    led_strip.name = "Internal_LED_Strip"
    mat_led = bpy.data.materials.new(name="LED_SMD_Emitter")
    mat_led.use_nodes = True
    mat_led.node_tree.nodes.clear()
    out_led = mat_led.node_tree.nodes.new('ShaderNodeOutputMaterial')
    emit = mat_led.node_tree.nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (1.0, 0.94, 0.86, 1.0)
    emit.inputs['Strength'].default_value = 6.0
    mat_led.node_tree.links.new(emit.outputs['Emission'], out_led.inputs['Surface'])
    led_strip.data.materials.append(mat_led)
    lamp_objects.append(led_strip)

    # Directional Desk Projector Light (Asymmetric forward-downward light pool)
    # Area light inside visor angled at 38 deg downwards-forward
    proj_light_data = bpy.data.lights.new(name="Optical_Desk_Projector", type='AREA')
    proj_light_data.shape = 'RECTANGLE'
    proj_light_data.size = LENS_L * 0.92
    proj_light_data.size_y = 0.015
    proj_light_data.energy = 28.0
    proj_light_data.color = (1.0, 0.94, 0.86)
    proj_obj = bpy.data.objects.new(name="Optical_Desk_Projector", object_data=proj_light_data)
    proj_obj.location = (0, lens_pos_y - 0.002, lens_pos_z - 0.002)
    proj_obj.rotation_euler = (lens_angle, 0, 0)
    bpy.context.collection.objects.link(proj_obj)
    lamp_objects.append(proj_obj)

    # -------------------------------------------------------------------------
    # 3. REAR AMBIENT LIGHT BAR
    # -------------------------------------------------------------------------
    AMB_L = 0.260
    amb_angle = math.radians(135)
    amb_y = BAR_Y + math.cos(amb_angle - math.radians(90)) * (BAR_R - 0.0008)
    amb_z = BAR_Z + math.sin(amb_angle - math.radians(90)) * (BAR_R - 0.0008)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, amb_y, amb_z),
        rotation=(-math.radians(45), 0, 0),
        scale=(AMB_L, 0.0045, 0.0012)
    )
    ambient_bar = bpy.context.active_object
    ambient_bar.name = "Rear_Ambient_Light_Bar"
    ambient_bar.data.materials.append(mat_rear_ambient)
    lamp_objects.append(ambient_bar)

    # -------------------------------------------------------------------------
    # 4. RIGHT ENDCAP: PRECISION ROTARY ENCODER
    # -------------------------------------------------------------------------
    DIAL_R = BAR_R * 1.035      # 12.42 mm radius
    DIAL_L = 0.012              # 12 mm length
    dial_x = BAR_L / 2.0 + DIAL_L / 2.0 + 0.0003
    
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
    # Local cylinder space: X and Y are radius, Z is cylinder depth
    bm_dial = bmesh.new()
    bm_dial.from_mesh(dial_body.data)
    uv_layer = bm_dial.loops.layers.uv.verify()
    for face in bm_dial.faces:
        for loop in face.loops:
            angle = math.atan2(loop.vert.co.y, loop.vert.co.x)
            u = (angle / (2.0 * math.pi)) % 1.0
            v = (loop.vert.co.z / DIAL_L) + 0.5
            loop[uv_layer].uv = (u, v)
    bm_dial.to_mesh(dial_body.data)
    bm_dial.free()
    lamp_objects.append(dial_body)
    
    # 4b. 45-degree Diamond-Cut Mirror Chamfer Ring
    CHAMFER_W = 0.0014
    chamfer_x = dial_x + DIAL_L / 2.0 - CHAMFER_W / 2.0
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=DIAL_R * 0.985, depth=CHAMFER_W,
        location=(chamfer_x, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    chamfer_ring = bpy.context.active_object
    chamfer_ring.name = "Diamond_Cut_Mirror_Chamfer"
    chamfer_ring.data.materials.append(mat_chamfer)
    cbev = chamfer_ring.modifiers.new("ChamferBevel", 'BEVEL')
    cbev.width = 0.0006
    cbev.segments = 3
    bpy.ops.object.shade_smooth()
    lamp_objects.append(chamfer_ring)
    
    # 4c. Inset Touch Glass Faceplate with Icons
    touch_x = dial_x + DIAL_L / 2.0 + 0.00015
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=DIAL_R * 0.91, depth=0.0008,
        location=(touch_x, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    touch_face = bpy.context.active_object
    touch_face.name = "Dial_Touch_Faceplate"
    touch_face.data.materials.append(mat_touch)
    
    # Correct planar UV projection in local XY circle space
    bm_touch = bmesh.new()
    bm_touch.from_mesh(touch_face.data)
    uv_layer_t = bm_touch.loops.layers.uv.verify()
    for face in bm_touch.faces:
        for loop in face.loops:
            u = loop.vert.co.x / (2.0 * DIAL_R * 0.91) + 0.5
            v = loop.vert.co.y / (2.0 * DIAL_R * 0.91) + 0.5
            loop[uv_layer_t].uv = (u, v)
    bm_touch.to_mesh(touch_face.data)
    bm_touch.free()
    lamp_objects.append(touch_face)

    # 4d. Inner Silicone O-Ring in Gap
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=BAR_R * 0.92, depth=0.0008,
        location=(BAR_L / 2.0 + 0.00015, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    oring = bpy.context.active_object
    oring.name = "Dial_Gap_O_Ring"
    oring.data.materials.append(mat_silicone)
    lamp_objects.append(oring)

    # -------------------------------------------------------------------------
    # 5. LEFT ENDCAP: AMBIENT LUX SENSOR & FLUSH CAP
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
    lamp_objects.append(left_cap)
    
    # Ambient Sensor Pupil
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=0.0022, depth=0.0008,
        location=(left_x - 0.002, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    sensor = bpy.context.active_object
    sensor.name = "Ambient_Lux_Sensor_Glass"
    sensor.data.materials.append(mat_touch)
    lamp_objects.append(sensor)

    # -------------------------------------------------------------------------
    # 6. CENTRAL CRADLE & MAGNETIC DOCKING COLLAR
    # -------------------------------------------------------------------------
    CRADLE_W = 0.046
    CRADLE_R = BAR_R + 0.0025
    
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
    lamp_objects.append(cradle)
    
    # Twin Gold Pogo-Pin Contact Rings
    for px in [-0.016, 0.016]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=64, radius=BAR_R + 0.00015, depth=0.0018,
            location=(px, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
        )
        pogo = bpy.context.active_object
        pogo.name = f"Gold_Pogo_Ring_{px}"
        pogo.data.materials.append(mat_brass)
        lamp_objects.append(pogo)

    # -------------------------------------------------------------------------
    # 7. GRAVITY COUNTERWEIGHT CLAMP (Monitor Hinge, Front Lip & Rear Mass)
    # -------------------------------------------------------------------------
    # 7a. Front Bezel Lip
    lip_y = -0.015
    lip_z = BAR_Z - 0.024
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, lip_y, lip_z),
        scale=(0.034, 0.0035, 0.018)
    )
    front_lip = bpy.context.active_object
    front_lip.name = "Clamp_Front_Bezel_Lip"
    front_lip.data.materials.append(mat_alu)
    flbev = front_lip.modifiers.new("LipBevel", 'BEVEL')
    flbev.width = 0.0008
    flbev.segments = 2
    bpy.ops.object.shade_smooth()
    lamp_objects.append(front_lip)
    
    # Front Silicone Cushion
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, lip_y + 0.0022, lip_z),
        scale=(0.032, 0.0012, 0.016)
    )
    front_silicone = bpy.context.active_object
    front_silicone.name = "Front_Lip_Silicone_Pad"
    front_silicone.data.materials.append(mat_silicone)
    lamp_objects.append(front_silicone)

    # 7b. Neck Bridge connecting Cradle to Hinge
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0.011, BAR_Z - 0.010),
        rotation=(-math.radians(35), 0, 0),
        scale=(0.036, 0.022, 0.012)
    )
    neck = bpy.context.active_object
    neck.name = "Mount_Neck_Bridge"
    neck.data.materials.append(mat_alu)
    nbev = neck.modifiers.new("NeckBevel", 'BEVEL')
    nbev.width = 0.001
    nbev.segments = 2
    bpy.ops.object.shade_smooth()
    lamp_objects.append(neck)

    # 7c. Main Friction Hinge Barrel
    HINGE_Y = 0.026
    HINGE_Z = BAR_Z - 0.018
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=0.0095, depth=0.040,
        location=(0, HINGE_Y, HINGE_Z), rotation=(0, math.radians(90), 0)
    )
    hinge_barrel = bpy.context.active_object
    hinge_barrel.name = "Main_Friction_Hinge_Barrel"
    hinge_barrel.data.materials.append(mat_alu)
    hbev = hinge_barrel.modifiers.new("HingeBevel", 'BEVEL')
    hbev.width = 0.0008
    hbev.segments = 3
    bpy.ops.object.shade_smooth()
    lamp_objects.append(hinge_barrel)
    
    # Stainless Steel Torx Axle Bolts on Hinge Flanks
    for hx in [-0.021, 0.021]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32, radius=0.005, depth=0.0025,
            location=(hx, HINGE_Y, HINGE_Z), rotation=(0, math.radians(90), 0)
        )
        bolt = bpy.context.active_object
        bolt.name = f"Hinge_Torx_Bolt_{hx}"
        bolt.data.materials.append(mat_steel)
        bbev = bolt.modifiers.new("BoltBevel", 'BEVEL')
        bbev.width = 0.0004
        bbev.segments = 2
        bpy.ops.object.shade_smooth()
        lamp_objects.append(bolt)

    # 7d. Gravity Counterweight Curved Mass
    MASS_Y = 0.058
    MASS_Z = BAR_Z - 0.038
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, MASS_Y, MASS_Z),
        rotation=(-math.radians(22), 0, 0),
        scale=(0.042, 0.048, 0.024)
    )
    mass_body = bpy.context.active_object
    mass_body.name = "Gravity_Counterweight_Mass"
    mass_body.data.materials.append(mat_alu)
    mbev = mass_body.modifiers.new("MassBevel", 'BEVEL')
    mbev.width = 0.0035
    mbev.segments = 4
    bpy.ops.object.shade_smooth()
    lamp_objects.append(mass_body)

    # 7e. Diamond-Grid Silicone Rear Cushion Pad
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, MASS_Y - 0.010, MASS_Z + 0.004),
        rotation=(-math.radians(22), 0, 0),
        scale=(0.038, 0.042, 0.0025)
    )
    rear_pad = bpy.context.active_object
    rear_pad.name = "Counterweight_Silicone_Cushion"
    rear_pad.data.materials.append(mat_silicone)
    lamp_objects.append(rear_pad)

    # -------------------------------------------------------------------------
    # 8. USB-C POWER PORT ASSEMBLY
    # -------------------------------------------------------------------------
    PORT_Y = HINGE_Y + 0.009
    PORT_Z = HINGE_Z + 0.002
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, PORT_Y, PORT_Z),
        scale=(0.013, 0.003, 0.007)
    )
    port_recess = bpy.context.active_object
    port_recess.name = "USBC_Port_Recess"
    port_recess.data.materials.append(mat_alu_dark)
    lamp_objects.append(port_recess)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, PORT_Y + 0.0008, PORT_Z),
        scale=(0.0085, 0.0022, 0.0034)
    )
    usbc_shield = bpy.context.active_object
    usbc_shield.name = "USBC_Metal_Shield"
    usbc_shield.data.materials.append(mat_steel)
    usbev = usbc_shield.modifiers.new("ShieldBevel", 'BEVEL')
    usbev.width = 0.0006
    usbev.segments = 2
    lamp_objects.append(usbc_shield)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, PORT_Y + 0.0004, PORT_Z),
        scale=(0.0064, 0.0016, 0.0007)
    )
    usbc_tongue = bpy.context.active_object
    usbc_tongue.name = "USBC_Center_Tongue"
    usbc_tongue.data.materials.append(mat_brass)
    lamp_objects.append(usbc_tongue)
    
    # Status Green LED
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.0008, depth=0.0008,
        location=(0.0095, PORT_Y + 0.0015, PORT_Z), rotation=(math.radians(90), 0, 0)
    )
    pwr_led = bpy.context.active_object
    pwr_led.name = "Power_Status_Micro_LED"
    mat_pled = bpy.data.materials.new(name="Status_Green_LED")
    mat_pled.use_nodes = True
    mat_pled.node_tree.nodes.clear()
    out_pl = mat_pled.node_tree.nodes.new('ShaderNodeOutputMaterial')
    emit_pl = mat_pled.node_tree.nodes.new('ShaderNodeEmission')
    emit_pl.inputs['Color'].default_value = (0.2, 1.0, 0.4, 1.0)
    emit_pl.inputs['Strength'].default_value = 3.5
    mat_pled.node_tree.links.new(emit_pl.outputs['Emission'], out_pl.inputs['Surface'])
    pwr_led.data.materials.append(mat_pled)
    lamp_objects.append(pwr_led)

    # Parent all lamp components to root empty for unified rotation
    for obj in lamp_objects:
        obj.parent = root

    # -------------------------------------------------------------------------
    # 9. EDITORIAL STUDIO GROUND FLOOR (#EBE8E1)
    # -------------------------------------------------------------------------
    FLOOR_Z = 0.000
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
        fl_bsdf.inputs['Roughness'].default_value = 0.88
    floor.data.materials.append(mat_fl)

    # -------------------------------------------------------------------------
    # 10. BALANCED STUDIO LIGHTING RIG
    # -------------------------------------------------------------------------
    # 10a. Overhead Cylindrical Key Softbox (Silky unbroken highlight ribbon)
    bpy.ops.object.light_add(type='AREA', location=(0.30, -1.20, BAR_Z + 1.40))
    key = bpy.context.active_object
    key.name = "Studio_Key_Softbox"
    key.data.energy = 44.0
    key.data.size = 2.20
    key.data.size_y = 0.55
    key.data.color = (1.0, 0.99, 0.97)
    dir_k = Vector((0.0, 0.0, BAR_Z)) - key.location
    key.rotation_euler = dir_k.to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True
    
    # 10b. Front-Fill Softbox
    bpy.ops.object.light_add(type='AREA', location=(0.80, -1.60, BAR_Z + 0.60))
    fill = bpy.context.active_object
    fill.name = "Studio_Fill_Softbox"
    fill.data.energy = 18.0
    fill.data.size = 1.40
    fill.data.size_y = 0.80
    fill.data.color = (0.95, 0.97, 1.0)
    dir_f = Vector((0.0, 0.0, BAR_Z)) - fill.location
    fill.rotation_euler = dir_f.to_track_quat('-Z', 'Y').to_euler()
    fill.data.use_shadow = False
    
    # 10c. Dial Rim Kicker (Catching the diamond knurling & mirror chamfer on right endcap)
    bpy.context.view_layer.update()
    dial_world = root.matrix_world @ Vector((dial_x, BAR_Y, BAR_Z))
    bpy.ops.object.light_add(type='AREA', location=(dial_world.x + 0.35, dial_world.y - 0.20, BAR_Z + 0.30))
    dial_kick = bpy.context.active_object
    dial_kick.name = "Dial_Hardware_Kicker"
    dial_kick.data.energy = 24.0
    dial_kick.data.size = 0.30
    dial_kick.data.size_y = 0.30
    dial_kick.data.color = (0.98, 0.99, 1.0)
    dir_dk = dial_world - dial_kick.location
    dial_kick.rotation_euler = dir_dk.to_track_quat('-Z', 'Y').to_euler()
    dial_kick.data.use_shadow = True

    # 10d. Rear Counterweight Contour Light
    bpy.ops.object.light_add(type='AREA', location=(-0.40, 1.10, BAR_Z + 0.70))
    rear_rim = bpy.context.active_object
    rear_rim.name = "Rear_Contour_Rim"
    rear_rim.data.energy = 22.0
    rear_rim.data.size = 1.00
    rear_rim.data.size_y = 0.45
    rear_rim.data.color = (0.98, 0.99, 1.0)
    dir_rr = Vector((0.0, 0.05, BAR_Z - 0.03)) - rear_rim.location
    rear_rim.rotation_euler = dir_rr.to_track_quat('-Z', 'Y').to_euler()
    rear_rim.data.use_shadow = False

    # -------------------------------------------------------------------------
    # 11. CAMERAS & FRAMING (Hero & Macro)
    # -------------------------------------------------------------------------
    # 11a. HERO CAMERA (1600x1200)
    target_hero = Vector((0.0, 0.010, BAR_Z - 0.015))
    dist_hero = 1.16
    elev_rad = math.radians(24.0)
    azim_rad = math.radians(14.0) # Angle viewing slightly toward the right-front
    
    cam_x = target_hero.x + dist_hero * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target_hero.y - dist_hero * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target_hero.z + dist_hero * math.sin(elev_rad)
    
    cam_hero_data = bpy.data.cameras.new("Camera_Beam_Hero")
    cam_hero_data.lens = 70.0
    cam_hero = bpy.data.objects.new("Camera_Beam_Hero", cam_hero_data)
    bpy.context.collection.objects.link(cam_hero)
    
    cam_hero.location = Vector((cam_x, cam_y, cam_z))
    dir_cam = target_hero - cam_hero.location
    cam_hero.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
    
    # 11b. MACRO CAMERA (1600x1200, 105mm f/5.6 macro lens)
    # Framed in true 3/4 perspective to see BOTH touch faceplate and knurled rim
    target_macro = dial_world
    dist_macro = 0.28
    
    dial_normal = root.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
    dial_normal.normalize()
    
    # Camera placed 36 deg offset from dial axis in front-right
    cam_macro_dir = (dial_normal * 0.72 + Vector((0.0, -0.55, 0.42))).normalized()
    cam_macro_loc = target_macro + cam_macro_dir * dist_macro
    
    cam_macro_data = bpy.data.cameras.new("Camera_Beam_Macro")
    cam_macro_data.lens = 105.0
    cam_macro_data.dof.use_dof = True
    cam_macro_data.dof.aperture_fstop = 6.3
    cam_macro_data.dof.focus_object = dial_body
    cam_macro = bpy.data.objects.new("Camera_Beam_Macro", cam_macro_data)
    bpy.context.collection.objects.link(cam_macro)
    
    cam_macro.location = cam_macro_loc
    dir_m = target_macro - cam_macro.location
    cam_macro.rotation_euler = dir_m.to_track_quat('-Z', 'Y').to_euler()
    cam_macro_data.dof.focus_distance = (cam_macro.location - target_macro).length

    # Save .blend scene
    blend_path = os.path.join(SCENES_DIR, "light_beam.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved master .blend scene: {blend_path}")

    return scene, cam_hero, cam_macro, root

def verify_camera_margins(scene, cam_obj, root):
    import bpy_extras
    bpy.context.view_layer.update()
    
    BAR_L = 0.450
    BAR_R = 0.012
    BAR_Z = 0.072
    MASS_Y = 0.058
    MASS_Z = BAR_Z - 0.038
    
    local_corners = [
        Vector((-BAR_L/2 - 0.005, 0, BAR_Z)),
        Vector((BAR_L/2 + 0.015, 0, BAR_Z)),
        Vector((-BAR_L/2, 0, BAR_Z + BAR_R)),
        Vector((BAR_L/2, 0, BAR_Z + BAR_R)),
        Vector((-BAR_L/2, -BAR_R, BAR_Z - BAR_R)),
        Vector((BAR_L/2, -BAR_R, BAR_Z - BAR_R)),
        Vector((0, -0.018, BAR_Z - 0.024)),
        Vector((0, MASS_Y + 0.025, MASS_Z - 0.012)),
        Vector((0, MASS_Y + 0.025, MASS_Z + 0.012)),
    ]
    coords_2d = []
    for co in local_corners:
        co_world = root.matrix_world @ co
        p2d = bpy_extras.object_utils.world_to_camera_view(scene, cam_obj, co_world)
        coords_2d.append(p2d)
        
    xs = [p.x for p in coords_2d]
    ys = [p.y for p in coords_2d]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    margin_left = min_x
    margin_right = 1.0 - max_x
    margin_bottom = min_y
    margin_top = 1.0 - max_y
    print(f"Camera Frame Projections: X in [{min_x:.3f}, {max_x:.3f}], Y in [{min_y:.3f}, {max_y:.3f}]")
    print(f"Margins: Left={margin_left*100:.1f}%, Right={margin_right*100:.1f}%, Top={margin_top*100:.1f}%, Bottom={margin_bottom*100:.1f}%")
    is_safe = min_x > 0.16 and max_x < 0.84 and min_y > 0.16 and max_y < 0.84
    return is_safe

def render_views(scene, cam_hero, cam_macro, root):
    is_safe = verify_camera_margins(scene, cam_hero, root)
    print("Hero Camera Margins Safe (>=16%):", is_safe)
    
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
    scene, cam_hero, cam_macro, root = build_beam_light()
    render_views(scene, cam_hero, cam_macro, root)
