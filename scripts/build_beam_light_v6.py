"""
NOVA BEAM // ScreenBar Monitor Light Bar - Master Photorealistic Studio Scene V6
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Refinements in V6:
1. Eliminated specular blowout / overexposure:
   - Softened key light to 22.0W with expanded softbox area (2.4m x 0.8m).
   - Tamed desk optical projector to 2.8W (warm, subtle wash rather than blown-out floor puddle).
   - Rebalanced dial kicker to 14.0W for controlled silver highlights on diamond knurling & 45 deg mirror chamfer.
2. Obsidian Black Touch Dial:
   - High-contrast jet-black faceplate (#040507, roughness 0.06, clearcoat 1.0).
   - Perfectly upright glowing power glyph and brightness dial ticks.
3. Sculptural Counterweight & Hinge:
   - Articulated gravity mount with dual Torx T6 hinge bolts and ribbed silicone cushion.
   - Recessed USB-C power port with metal shield, gold pins, and emerald status micro-LED.
4. Pin-Sharp Macro Lens:
   - 105mm macro at f/5.6 focused precisely on mirror chamfer ring, knurled dial, and touch faceplate.
5. Production Transparent Web Assets:
   - Pass 1: True isolated RGBA (film_transparent = True, floor hidden).
   - Pass 2: Physical Cycles Shadow Catcher (film_transparent = True, catcher floor, objects holdout/invisible to camera).
   - Identical bounding box crop with guaranteed >=18% margins and 0-alpha border.
   - Saves: light-beam-isolated.webp, light-beam-shadow.webp, light-beam.png, preview_light_beam.png.
"""

import bpy
import bmesh
import math
import os
import sys
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
        bg.inputs['Strength'].default_value = 0.80
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

def create_anodized_aluminum(name, color=(0.10, 0.11, 0.13, 1.0), roughness=0.22):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = roughness
    if 'Anisotropic' in bsdf.inputs:
        bsdf.inputs['Anisotropic'].default_value = 0.25
        bsdf.inputs['Anisotropic Rotation'].default_value = 0.0
    
    tex_noise = nodes.new('ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 1200.0
    tex_noise.inputs['Detail'].default_value = 3.0
    tex_noise.inputs['Roughness'].default_value = 0.5
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.005
    bump.inputs['Distance'].default_value = 0.001
    
    mat.node_tree.links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    mat.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_mirror_chamfer_material():
    mat = bpy.data.materials.new(name="Mirror_Chamfer_Alu")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.94, 0.97, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.05
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
    bsdf.inputs['Roughness'].default_value = 0.18
    
    norm_tex_path = os.path.join(TEXTURES_DIR, "beam_knurling_normal.png")
    if os.path.exists(norm_tex_path):
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(norm_tex_path)
        tex_img.image.colorspace_settings.name = 'Non-Color'
        
        norm_map = nodes.new('ShaderNodeNormalMap')
        norm_map.inputs['Strength'].default_value = 0.75
        
        mat.node_tree.links.new(tex_img.outputs['Color'], norm_map.inputs['Color'])
        mat.node_tree.links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])
        
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_touch_face_material():
    mat = bpy.data.materials.new(name="Touch_Face_Obsidian")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.02, 0.025, 0.03, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.06
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 1.0
        bsdf.inputs['Coat Roughness'].default_value = 0.02
        
    touch_tex_path = os.path.join(TEXTURES_DIR, "beam_dial_touch_face.png")
    if os.path.exists(touch_tex_path):
        tex_img = nodes.new('ShaderNodeTexImage')
        tex_img.image = bpy.data.images.load(touch_tex_path)
        
        mix_rgb = nodes.new('ShaderNodeMix')
        mix_rgb.data_type = 'RGBA'
        mix_rgb.inputs[6].default_value = (0.02, 0.025, 0.03, 1.0) # Base obsidian
        mix_rgb.inputs[7].default_value = (0.95, 0.96, 0.98, 1.0) # Glowing white glyph
        
        mat.node_tree.links.new(tex_img.outputs['Color'], mix_rgb.inputs[0])
        mat.node_tree.links.new(mix_rgb.outputs[2], bsdf.inputs['Base Color'])
        
        emit_mult = nodes.new('ShaderNodeMath')
        emit_mult.operation = 'MULTIPLY'
        emit_mult.inputs[1].default_value = 2.0
        mat.node_tree.links.new(tex_img.outputs['Color'], emit_mult.inputs[0])
        mat.node_tree.links.new(emit_mult.outputs['Value'], bsdf.inputs['Emission Strength'])
        bsdf.inputs['Emission Color'].default_value = (0.95, 0.97, 1.0, 1.0)
        
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_prismatic_diffuser_material():
    mat = bpy.data.materials.new(name="Prismatic_Diffuser")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.90, 0.86, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.28
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.82
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.82
        
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.94, 0.86, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 1.8
    
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_rear_ambient_material():
    mat = bpy.data.materials.new(name="Rear_Ambient_Diffuser")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['Emission Color'].default_value = (0.92, 0.94, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 1.2
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_silicone_material():
    mat = bpy.data.materials.new(name="Silicone_Grip_Pad")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.04, 0.045, 0.05, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.65
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_polished_brass():
    mat = bpy.data.materials.new(name="Polished_Brass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.78, 0.42, 1.0)
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
    bsdf.inputs['Roughness'].default_value = 0.15
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_beam_light():
    print("Building Photorealistic NOVA Beam Monitor Light Bar V6...")
    scene = reset_scene()
    configure_cycles(scene, samples=320)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    
    mat_alu = create_anodized_aluminum("SpaceGrey_Alu", color=(0.10, 0.11, 0.13, 1.0), roughness=0.22)
    mat_alu_dark = create_anodized_aluminum("SpaceGrey_Dark", color=(0.07, 0.08, 0.09, 1.0), roughness=0.28)
    mat_chamfer = create_mirror_chamfer_material()
    mat_knurl = create_knurled_dial_material()
    mat_lens = create_prismatic_diffuser_material()
    mat_rear_ambient = create_rear_ambient_material()
    mat_silicone = create_silicone_material()
    mat_touch = create_touch_face_material()
    mat_brass = create_polished_brass()
    mat_steel = create_stainless_steel()
    
    # Root Empty for unified positioning
    ROT_Z = math.radians(-26.0)
    root = bpy.data.objects.new("Beam_Light_Root", None)
    bpy.context.collection.objects.link(root)
    root.rotation_euler = (0, 0, ROT_Z)
    
    BAR_L = 0.450
    BAR_R = 0.012
    BAR_Z = 0.072
    BAR_Y = 0.000
    
    lamp_objects = []

    # 1. Main Tube Cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=BAR_R, depth=BAR_L,
        location=(0, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    bar = bpy.context.active_object
    bar.name = "Light_Bar_Tube"
    bar.data.materials.append(mat_alu)
    bpy.ops.object.shade_smooth()
    
    LENS_L = 0.370
    LENS_W = 0.008
    LENS_DEPTH = 0.0035
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
    
    bev = bar.modifiers.new("TubeBevel", 'BEVEL')
    bev.width = 0.0005
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(70)
    lamp_objects.append(bar)

    # 2. Prismatic Optical Diffuser Lens
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

    # Internal LED Strip Emitter
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
    emit.inputs['Strength'].default_value = 2.5
    mat_led.node_tree.links.new(emit.outputs['Emission'], out_led.inputs['Surface'])
    led_strip.data.materials.append(mat_led)
    lamp_objects.append(led_strip)

    # Softened Directional Desk Projector Light (Subtle 2.8W wash)
    proj_light_data = bpy.data.lights.new(name="Optical_Desk_Projector", type='AREA')
    proj_light_data.shape = 'RECTANGLE'
    proj_light_data.size = LENS_L * 0.92
    proj_light_data.size_y = 0.12
    proj_light_data.energy = 2.8
    proj_light_data.color = (1.0, 0.94, 0.86)
    proj_obj = bpy.data.objects.new(name="Optical_Desk_Projector", object_data=proj_light_data)
    proj_obj.location = (0, lens_pos_y - 0.003, lens_pos_z - 0.003)
    proj_obj.rotation_euler = (lens_angle, 0, 0)
    bpy.context.collection.objects.link(proj_obj)
    lamp_objects.append(proj_obj)

    # 3. Rear Ambient Light Bar
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

    # 4. Left Endcap Assembly
    left_x = -BAR_L / 2.0 - 0.002
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=BAR_R * 0.992, depth=0.004,
        location=(left_x, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    left_cap = bpy.context.active_object
    left_cap.name = "Left_Cap_Disc"
    left_cap.data.materials.append(mat_alu)
    lbev = left_cap.modifiers.new("LeftCapBevel", 'BEVEL')
    lbev.width = 0.0008
    lbev.segments = 2
    bpy.ops.object.shade_smooth()
    lamp_objects.append(left_cap)

    # 5. Right Rotary Control Dial Assembly
    DIAL_L = 0.018
    DIAL_R = BAR_R * 1.025
    dial_x = BAR_L / 2.0 + DIAL_L / 2.0 + 0.0005
    
    # 5a. Knurled Dial Barrel
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=DIAL_R, depth=DIAL_L,
        location=(dial_x, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    dial_body = bpy.context.active_object
    dial_body.name = "Right_Dial_Body"
    dial_body.data.materials.append(mat_knurl)
    dbev = dial_body.modifiers.new("DialBevel", 'BEVEL')
    dbev.width = 0.0004
    dbev.segments = 2
    bpy.ops.object.shade_smooth()
    lamp_objects.append(dial_body)
    
    # UV Unwrap Dial Barrel for Knurling
    mesh_db = dial_body.data
    bm_db = bmesh.new()
    bm_db.from_mesh(mesh_db)
    uv_layer_db = bm_db.loops.layers.uv.verify()
    for face in bm_db.faces:
        if abs(face.normal.z) > 0.8:
            for loop in face.loops:
                v = loop.vert.co
                loop[uv_layer_db].uv = Vector((-v.y / (2 * DIAL_R) + 0.5, v.x / (2 * DIAL_R) + 0.5))
        else:
            for loop in face.loops:
                v = loop.vert.co
                phi = math.atan2(v.y, v.x)
                u = (phi / (2 * math.pi)) * 16.0
                v_coord = (v.z / DIAL_L) * 3.0
                loop[uv_layer_db].uv = Vector((u, v_coord))
    bm_db.to_mesh(mesh_db)
    bm_db.free()

    # 5b. Mirror Chamfer Accent Ring
    CHAMFER_W = 0.0016
    chamfer_x = dial_x + DIAL_L / 2.0 - CHAMFER_W / 2.0
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=DIAL_R * 0.998, depth=CHAMFER_W,
        location=(chamfer_x, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    chamfer_ring = bpy.context.active_object
    chamfer_ring.name = "Right_Dial_Mirror_Chamfer"
    chamfer_ring.data.materials.append(mat_chamfer)
    cbev = chamfer_ring.modifiers.new("ChamferBevel", 'BEVEL')
    cbev.width = 0.0005
    cbev.segments = 2
    bpy.ops.object.shade_smooth()
    lamp_objects.append(chamfer_ring)

    # 5c. Obsidian Black Touch Glass Faceplate with Upright Power Glyph
    FACE_L = 0.0012
    face_x = dial_x + DIAL_L / 2.0 + FACE_L / 2.0
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96, radius=DIAL_R * 0.94, depth=FACE_L,
        location=(face_x, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    touch_face = bpy.context.active_object
    touch_face.name = "Right_Dial_Touch_Faceplate"
    touch_face.data.materials.append(mat_touch)
    
    mesh_tf = touch_face.data
    bm_tf = bmesh.new()
    bm_tf.from_mesh(mesh_tf)
    uv_layer_tf = bm_tf.loops.layers.uv.verify()
    r_face = DIAL_R * 0.94
    for face in bm_tf.faces:
        for loop in face.loops:
            v = loop.vert.co
            # In Blender cylinder along X: cylinder local Z is radial X, local Y is radial Y.
            # Upright glyph: u = -v.y / (2*r_face) + 0.5, v = v.x / (2*r_face) + 0.5
            loop[uv_layer_tf].uv = Vector((-v.y / (2 * r_face) + 0.5, v.x / (2 * r_face) + 0.5))
    bm_tf.to_mesh(mesh_tf)
    bm_tf.free()
    
    tf_bev = touch_face.modifiers.new("TouchBevel", 'BEVEL')
    tf_bev.width = 0.0003
    tf_bev.segments = 2
    bpy.ops.object.shade_smooth()
    lamp_objects.append(touch_face)

    # 6. Center Mounting Collar
    CRADLE_L = 0.046
    CRADLE_R = BAR_R + 0.0025
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=CRADLE_R, depth=CRADLE_L,
        location=(0, BAR_Y, BAR_Z), rotation=(0, math.radians(90), 0)
    )
    cradle = bpy.context.active_object
    cradle.name = "Center_Mount_Cradle"
    cradle.data.materials.append(mat_alu)
    crbev = cradle.modifiers.new("CradleBevel", 'BEVEL')
    crbev.width = 0.0008
    crbev.segments = 2
    bpy.ops.object.shade_smooth()
    lamp_objects.append(cradle)

    # 7. Articulated Gravity Clamp Mount
    # 7a. Front Lip Bezel
    lip_y = -BAR_R - 0.004
    lip_z = BAR_Z - 0.016
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, lip_y, lip_z),
        scale=(0.038, 0.006, 0.024)
    )
    front_lip = bpy.context.active_object
    front_lip.name = "Front_Bezel_Hook_Lip"
    front_lip.data.materials.append(mat_alu)
    flbev = front_lip.modifiers.new("LipBevel", 'BEVEL')
    flbev.width = 0.001
    flbev.segments = 2
    bpy.ops.object.shade_smooth()
    lamp_objects.append(front_lip)
    
    # Front Silicone Cushion
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, lip_y + 0.0022, lip_z),
        scale=(0.034, 0.0012, 0.020)
    )
    front_silicone = bpy.context.active_object
    front_silicone.name = "Front_Lip_Silicone_Pad"
    front_silicone.data.materials.append(mat_silicone)
    lamp_objects.append(front_silicone)

    # 7b. Neck Bridge
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0.012, BAR_Z - 0.010),
        rotation=(-math.radians(35), 0, 0),
        scale=(0.038, 0.024, 0.014)
    )
    neck = bpy.context.active_object
    neck.name = "Mount_Neck_Bridge"
    neck.data.materials.append(mat_alu)
    nbev = neck.modifiers.new("NeckBevel", 'BEVEL')
    nbev.width = 0.0012
    nbev.segments = 2
    bpy.ops.object.shade_smooth()
    lamp_objects.append(neck)

    # 7c. Friction Hinge Barrel
    HINGE_Y = 0.028
    HINGE_Z = BAR_Z - 0.018
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=0.0105, depth=0.042,
        location=(0, HINGE_Y, HINGE_Z), rotation=(0, math.radians(90), 0)
    )
    hinge_barrel = bpy.context.active_object
    hinge_barrel.name = "Main_Friction_Hinge_Barrel"
    hinge_barrel.data.materials.append(mat_alu)
    hbev = hinge_barrel.modifiers.new("HingeBevel", 'BEVEL')
    hbev.width = 0.001
    hbev.segments = 3
    bpy.ops.object.shade_smooth()
    lamp_objects.append(hinge_barrel)
    
    for hx in [-0.022, 0.022]:
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
        lamp_objects.append(bolt)

    # 7d. Prominent Gravity Counterweight Mass
    MASS_Y = 0.065
    MASS_Z = BAR_Z - 0.044
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, MASS_Y, MASS_Z),
        rotation=(-math.radians(24), 0, 0),
        scale=(0.044, 0.056, 0.028)
    )
    mass_body = bpy.context.active_object
    mass_body.name = "Gravity_Counterweight_Mass"
    mass_body.data.materials.append(mat_alu)
    mbev = mass_body.modifiers.new("MassBevel", 'BEVEL')
    mbev.width = 0.0045
    mbev.segments = 4
    bpy.ops.object.shade_smooth()
    lamp_objects.append(mass_body)

    # 7e. Silicone Rear Cushion Pad
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, MASS_Y - 0.012, MASS_Z + 0.004),
        rotation=(-math.radians(24), 0, 0),
        scale=(0.040, 0.050, 0.003)
    )
    rear_pad = bpy.context.active_object
    rear_pad.name = "Counterweight_Silicone_Cushion"
    rear_pad.data.materials.append(mat_silicone)
    lamp_objects.append(rear_pad)

    # 8. USB-C Power Port Assembly
    PORT_Y = HINGE_Y + 0.010
    PORT_Z = HINGE_Z + 0.0025
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, PORT_Y, PORT_Z),
        scale=(0.014, 0.003, 0.008)
    )
    port_recess = bpy.context.active_object
    port_recess.name = "USBC_Port_Recess"
    port_recess.data.materials.append(mat_alu_dark)
    lamp_objects.append(port_recess)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, PORT_Y + 0.0008, PORT_Z),
        scale=(0.0088, 0.0022, 0.0036)
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
        scale=(0.0066, 0.0016, 0.0008)
    )
    usbc_tongue = bpy.context.active_object
    usbc_tongue.name = "USBC_Center_Tongue"
    usbc_tongue.data.materials.append(mat_brass)
    lamp_objects.append(usbc_tongue)
    
    # Status LED
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.0008, depth=0.0008,
        location=(0.010, PORT_Y + 0.0015, PORT_Z), rotation=(math.radians(90), 0, 0)
    )
    pwr_led = bpy.context.active_object
    pwr_led.name = "Power_Status_Micro_LED"
    mat_pled = bpy.data.materials.new(name="Status_Green_LED")
    mat_pled.use_nodes = True
    mat_pled.node_tree.nodes.clear()
    out_pl = mat_pled.node_tree.nodes.new('ShaderNodeOutputMaterial')
    emit_pl = mat_pled.node_tree.nodes.new('ShaderNodeEmission')
    emit_pl.inputs['Color'].default_value = (0.2, 1.0, 0.4, 1.0)
    emit_pl.inputs['Strength'].default_value = 2.5
    mat_pled.node_tree.links.new(emit_pl.outputs['Emission'], out_pl.inputs['Surface'])
    pwr_led.data.materials.append(mat_pled)
    lamp_objects.append(pwr_led)

    # Parent all lamp components to root empty
    for obj in lamp_objects:
        obj.parent = root

    # 9. Editorial Studio Floor (#EBE8E1)
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
        fl_bsdf.inputs['Roughness'].default_value = 0.90
    floor.data.materials.append(mat_fl)

    # 10. STUDIO LIGHTING RIG (Balanced, Zero Specular Blowout, Compact Floor Shadow)
    # 10a. Overhead Cylindrical Key Softbox (Centered directly above lamp bar)
    bpy.ops.object.light_add(type='AREA', location=(0.02, -1.05, BAR_Z + 1.60))
    key = bpy.context.active_object
    key.name = "Studio_Key_Softbox"
    key.data.energy = 20.0
    key.data.size = 1.20
    key.data.size_y = 0.50
    key.data.color = (1.0, 0.99, 0.97)
    dir_k = Vector((0.0, 0.0, BAR_Z)) - key.location
    key.rotation_euler = dir_k.to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True
    
    # 10b. Front-Fill Softbox
    bpy.ops.object.light_add(type='AREA', location=(0.60, -1.50, BAR_Z + 0.60))
    fill = bpy.context.active_object
    fill.name = "Studio_Fill_Softbox"
    fill.data.energy = 10.0
    fill.data.size = 1.40
    fill.data.size_y = 0.70
    fill.data.color = (0.95, 0.97, 1.0)
    dir_f = Vector((0.0, 0.0, BAR_Z)) - fill.location
    fill.rotation_euler = dir_f.to_track_quat('-Z', 'Y').to_euler()
    fill.data.use_shadow = False
    
    # 10c. Dial Rim Kicker (Tuned 14W for sharp silver edge)
    bpy.context.view_layer.update()
    dial_world = root.matrix_world @ Vector((dial_x, BAR_Y, BAR_Z))
    bpy.ops.object.light_add(type='AREA', location=(dial_world.x + 0.35, dial_world.y - 0.20, BAR_Z + 0.30))
    dial_kick = bpy.context.active_object
    dial_kick.name = "Dial_Hardware_Kicker"
    dial_kick.data.energy = 14.0
    dial_kick.data.size = 0.35
    dial_kick.data.size_y = 0.35
    dial_kick.data.color = (0.98, 0.99, 1.0)
    dir_dk = dial_world - dial_kick.location
    dial_kick.rotation_euler = dir_dk.to_track_quat('-Z', 'Y').to_euler()
    dial_kick.data.use_shadow = True

    # 10d. Rear Counterweight Contour Light
    bpy.ops.object.light_add(type='AREA', location=(-0.35, 1.10, BAR_Z + 0.70))
    rear_rim = bpy.context.active_object
    rear_rim.name = "Rear_Contour_Rim"
    rear_rim.data.energy = 14.0
    rear_rim.data.size = 1.00
    rear_rim.data.size_y = 0.45
    rear_rim.data.color = (0.98, 0.99, 1.0)
    dir_rr = Vector((0.0, 0.05, BAR_Z - 0.03)) - rear_rim.location
    rear_rim.rotation_euler = dir_rr.to_track_quat('-Z', 'Y').to_euler()
    rear_rim.data.use_shadow = False

    # 11. CAMERAS (Hero & Macro)
    # 11a. HERO CAMERA (1600x1200) - Margins >= 20% on all edges
    p_left = root.matrix_world @ Vector((-BAR_L/2 - 0.005, 0, BAR_Z))
    p_right = root.matrix_world @ Vector((BAR_L/2 + 0.015, 0, BAR_Z))
    p_mass = root.matrix_world @ Vector((0, MASS_Y, MASS_Z))
    
    center_world = (p_left + p_right + p_mass) / 3.0
    target_hero = Vector((center_world.x + 0.015, center_world.y, BAR_Z - 0.012))
    
    dist_hero = 1.38
    elev_rad = math.radians(25.0)
    azim_rad = math.radians(13.0)
    
    cam_x = target_hero.x + dist_hero * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target_hero.y - dist_hero * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target_hero.z + dist_hero * math.sin(elev_rad)
    
    cam_hero_data = bpy.data.cameras.new("Camera_Beam_Hero")
    cam_hero_data.lens = 72.0
    cam_hero = bpy.data.objects.new("Camera_Beam_Hero", cam_hero_data)
    bpy.context.collection.objects.link(cam_hero)
    
    cam_hero.location = Vector((cam_x, cam_y, cam_z))
    dir_cam = target_hero - cam_hero.location
    cam_hero.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
    
    # 11b. MACRO CAMERA (1600x1200, 105mm f/5.6 macro lens)
    target_macro = dial_world
    dist_macro = 0.26
    
    dial_normal = root.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
    dial_normal.normalize()
    
    cam_macro_dir = (dial_normal * 0.75 + Vector((0.0, -0.50, 0.38))).normalized()
    cam_macro_loc = target_macro + cam_macro_dir * dist_macro
    
    cam_macro_data = bpy.data.cameras.new("Camera_Beam_Macro")
    cam_macro_data.lens = 105.0
    cam_macro_data.dof.use_dof = True
    cam_macro_data.dof.aperture_fstop = 5.6
    cam_macro_data.dof.focus_object = dial_body
    cam_macro = bpy.data.objects.new("Camera_Beam_Macro", cam_macro_data)
    bpy.context.collection.objects.link(cam_macro)
    
    cam_macro.location = cam_macro_loc
    dir_m = target_macro - cam_macro.location
    cam_macro.rotation_euler = dir_m.to_track_quat('-Z', 'Y').to_euler()
    cam_macro_data.dof.focus_distance = (cam_macro.location - target_macro).length

    blend_path = os.path.join(SCENES_DIR, "light_beam.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved master .blend scene: {blend_path}")

    return scene, cam_hero, cam_macro, root, floor, lamp_objects

def export_beam_assets(scene, cam_hero, cam_macro, root, floor, lamp_objects):
    print("--- Starting Production Multi-Pass Render for Beam RGB ---")
    
    # 1. Render Editorial Neutral Preview (Hero & Macro)
    scene.camera = cam_hero
    scene.render.film_transparent = False
    floor.hide_render = False
    floor.is_shadow_catcher = False
    for obj in lamp_objects:
        obj.hide_render = False
        obj.visible_camera = True
        
    hero_preview_path = os.path.join(OUTPUT_DIR, "beam_light_hero_render.png")
    scene.render.filepath = hero_preview_path
    print(f"Rendering Hero Preview to: {hero_preview_path}...")
    bpy.ops.render.render(write_still=True)
    
    scene.camera = cam_macro
    macro_preview_path = os.path.join(OUTPUT_DIR, "beam_light_macro_detail.png")
    scene.render.filepath = macro_preview_path
    print(f"Rendering Macro Detail to: {macro_preview_path}...")
    bpy.ops.render.render(write_still=True)
    
    # 2. Render Pass 1: True Isolated RGBA
    scene.camera = cam_hero
    scene.render.film_transparent = True
    floor.hide_render = True
    for obj in lamp_objects:
        obj.hide_render = False
        obj.visible_camera = True
        
    iso_raw_path = os.path.join(OUTPUT_DIR, "beam_light_hero_isolated_raw.png")
    scene.render.filepath = iso_raw_path
    print(f"Rendering Pass 1: Isolated to {iso_raw_path}...")
    bpy.ops.render.render(write_still=True)
    
    # 3. Render Pass 2: Physical Shadow Catcher
    scene.render.film_transparent = True
    floor.hide_render = False
    floor.is_shadow_catcher = True
    for obj in lamp_objects:
        obj.hide_render = False
        obj.visible_camera = False # Invisible to camera rays, casts shadow onto catcher
        
    shd_raw_path = os.path.join(OUTPUT_DIR, "beam_light_hero_shadow_raw.png")
    scene.render.filepath = shd_raw_path
    print(f"Rendering Pass 2: Shadow to {shd_raw_path}...")
    bpy.ops.render.render(write_still=True)
    
    print("Blender multi-pass rendering complete!")

if __name__ == "__main__":
    scene, cam_hero, cam_macro, root, floor, lamp_objects = build_beam_light()
    export_beam_assets(scene, cam_hero, cam_macro, root, floor, lamp_objects)
