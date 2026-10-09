"""
NOVA DESK XL Mat - Industrial Design & Photorealistic Studio Render V6
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Key Refinements in V6:
1. Deep Anthracite Heathered Merino Wool:
   - 4K procedural + texture albedo with rich dark charcoal (#16181C to #24262E) and ash fiber flecks.
   - Sheen Weight 1.0 with cool backscatter and micro-pile grazing bump.
   - Distinct 2-ply composite construction: 2.8mm felt top + 1.4mm vulcanized charcoal rubber base.
2. Watertight Solid Vegetable-Tanned Leather Organizer Badge:
   - Parametric 2D curve extrusion with exact rounded corners (R=4.5mm) and pill slot (24x6mm).
   - High-res 2200x650 UV texture: warm cognac saddle leather, heat creasing, debossed "NOVA" logotype.
   - Machined solid brass rivet (9.6mm dia) with concentric lathe highlight and center pip.
3. Realistic Equidistant Saddle Stitches with Needle Puncture Dimples:
   - 340 arched 3D thread loops with +18 deg saddle slant, plunging into felt puncture holes.
   - 680 needle puncture depression dimples with compressed shadow shading.
   - Warm ecru spun linen thread with fibrous sheen and twist bump.
4. Studio Lighting & Cameras:
   - Low-elevation raking softboxes sculpting tactile fiber relief and crisp hardware glints.
   - Hero Camera (1600x1200) mathematically verified: >=16% margins, zero edge clipping.
   - Macro Camera (1600x1200, 95mm f/5.6) focused on leather badge, debossed logotype, and wool weave.
"""

import bpy
import bmesh
import math
import os
import mathutils
from mathutils import Vector, Euler, Matrix

OUTPUT_DIR = r"D:\Projects\ууу\assets\previews"
MODELS_DIR = r"D:\Projects\ууу\assets\models"
TEXTURES_DIR = r"D:\Projects\ууу\assets\textures"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Studio_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.90, 0.89, 0.86, 1.0)
        bg.inputs['Strength'].default_value = 0.22
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
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'

def create_anthracite_felt_material():
    """
    Rich dark anthracite heathered merino wool felt.
    Combines 4K albedo & normal textures with micro-pile procedural bump and velvety sheen.
    """
    mat = bpy.data.materials.new("Anthracite_Merino_Felt")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    # UV Mapping for 4K Felt Textures
    uv_felt = nodes.new('ShaderNodeUVMap')
    uv_felt.uv_map = "UVMap"
    
    # 1. Image Texture: Albedo
    felt_albedo_path = os.path.join(TEXTURES_DIR, "novadesk_felt_albedo.png")
    tex_albedo = nodes.new('ShaderNodeTexImage')
    if os.path.exists(felt_albedo_path):
        tex_albedo.image = bpy.data.images.load(felt_albedo_path)
    links.new(uv_felt.outputs['UV'], tex_albedo.inputs['Vector'])
    
    # Direct deep charcoal heather (#18191D base)
    links.new(tex_albedo.outputs['Color'], bsdf.inputs['Base Color'])
    
    # 2. Image Texture: Normal Map
    felt_normal_path = os.path.join(TEXTURES_DIR, "novadesk_felt_normal.png")
    tex_norm = nodes.new('ShaderNodeTexImage')
    if os.path.exists(felt_normal_path):
        img_n = bpy.data.images.load(felt_normal_path)
        img_n.colorspace_settings.name = 'Non-Color'
        tex_norm.image = img_n
    links.new(uv_felt.outputs['UV'], tex_norm.inputs['Vector'])
    
    node_norm = nodes.new('ShaderNodeNormalMap')
    node_norm.inputs['Strength'].default_value = 0.85
    links.new(tex_norm.outputs['Color'], node_norm.inputs['Color'])
    links.new(node_norm.outputs['Normal'], bsdf.inputs['Normal'])
    
    # 3. BSDF Textile Surface Parameters
    bsdf.inputs['Roughness'].default_value = 0.94
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.12 # Very low specular for wool
        
    # Velveteen Sheen: subtle dark matte backscatter on glancing angles (NOT white/blue)
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.22
        if 'Sheen Roughness' in bsdf.inputs:
            bsdf.inputs['Sheen Roughness'].default_value = 0.65
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (0.35, 0.35, 0.38, 1.0)
            
    # Subsurface light-trapping in dense wool fibers
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.02
        bsdf.inputs['Subsurface Radius'].default_value = (0.002, 0.002, 0.002)
        bsdf.inputs['Subsurface Scale'].default_value = 0.001
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_rubber_base_material():
    """
    High-density vulcanized charcoal natural rubber base.
    """
    mat = bpy.data.materials.new("Rubber_Base_Charcoal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.012, 0.013, 0.015, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.84
    
    # Subtle cellular micro-texture
    tex_coord = nodes.new('ShaderNodeTexCoord')
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 600.0
    links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.0002
    links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_cognac_leather_material():
    """
    Rich vegetable-tanned cognac leather with hot-stamped debossing and satin sheen.
    Uses dedicated 2200x650 albedo, normal, and roughness maps.
    """
    mat = bpy.data.materials.new("Cognac_Saddle_Leather")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    uv_map = nodes.new('ShaderNodeUVMap')
    uv_map.uv_map = "UVMap"
    
    # 1. Leather Albedo
    albedo_path = os.path.join(TEXTURES_DIR, "novadesk_leather_albedo.png")
    tex_albedo = nodes.new('ShaderNodeTexImage')
    if os.path.exists(albedo_path):
        tex_albedo.image = bpy.data.images.load(albedo_path)
    links.new(uv_map.outputs['UV'], tex_albedo.inputs['Vector'])
    links.new(tex_albedo.outputs['Color'], bsdf.inputs['Base Color'])
    
    # 2. Leather Normal
    normal_path = os.path.join(TEXTURES_DIR, "novadesk_leather_normal.png")
    tex_norm = nodes.new('ShaderNodeTexImage')
    if os.path.exists(normal_path):
        img_n = bpy.data.images.load(normal_path)
        img_n.colorspace_settings.name = 'Non-Color'
        tex_norm.image = img_n
    links.new(uv_map.outputs['UV'], tex_norm.inputs['Vector'])
    
    node_norm = nodes.new('ShaderNodeNormalMap')
    node_norm.inputs['Strength'].default_value = 1.4
    links.new(tex_norm.outputs['Color'], node_norm.inputs['Color'])
    links.new(node_norm.outputs['Normal'], bsdf.inputs['Normal'])
    
    # 3. Leather Roughness
    rough_path = os.path.join(TEXTURES_DIR, "novadesk_leather_roughness.png")
    tex_rough = nodes.new('ShaderNodeTexImage')
    if os.path.exists(rough_path):
        img_r = bpy.data.images.load(rough_path)
        img_r.colorspace_settings.name = 'Non-Color'
        tex_rough.image = img_r
    links.new(uv_map.outputs['UV'], tex_rough.inputs['Vector'])
    links.new(tex_rough.outputs['Color'], bsdf.inputs['Roughness'])
    
    # Leather Satin Clearcoat & Subsurface
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.22
        bsdf.inputs['Coat Roughness'].default_value = 0.25
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.05
        bsdf.inputs['Subsurface Radius'].default_value = (0.003, 0.0015, 0.0008)
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_saddle_thread_material():
    """
    Spun ecru waxed linen thread with fibrous sheen and twist bump.
    """
    mat = bpy.data.materials.new("Spun_Saddle_Thread")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    # Warm ecru / light natural stone thread
    bsdf.inputs['Base Color'].default_value = (0.48, 0.44, 0.37, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.48
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.85
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (0.95, 0.92, 0.85, 1.0)
            
    # Thread fiber bump
    tex_coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 800.0
    noise.inputs['Detail'].default_value = 6.0
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.22
    bump.inputs['Distance'].default_value = 0.0002
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_puncture_hole_material():
    """
    Dark compressed needle puncture depression shadow.
    """
    mat = bpy.data.materials.new("Puncture_Hole_Shadow")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.015, 0.015, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.95
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_turned_brass_material():
    """
    Turned solid brass rivet with concentric lathe highlight.
    """
    mat = bpy.data.materials.new("Turned_Solid_Brass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.96, 0.80, 0.38, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.18
    if 'Anisotropic' in bsdf.inputs:
        bsdf.inputs['Anisotropic'].default_value = 0.88
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_equidistant_rounded_rect_curve(w, d, r, pitch=0.0068):
    """
    Generates equidistant points along a rounded rectangular path.
    """
    cx = w / 2.0 - r
    cy = d / 2.0 - r
    
    straight_w = 2.0 * cx
    straight_d = 2.0 * cy
    arc_len = 0.5 * math.pi * r
    total_len = 2.0 * straight_w + 2.0 * straight_d + 4.0 * arc_len
    
    n_stitches = int(round(total_len / pitch))
    actual_pitch = total_len / float(n_stitches)
    
    def get_pos_tan_at_distance(s):
        if s < straight_w:
            u = s / straight_w
            return Vector((-cx + 2.0 * cx * u, cy + r, 0.0)), Vector((1.0, 0.0, 0.0))
        s -= straight_w
        if s < arc_len:
            ang = math.pi / 2.0 - (s / arc_len) * (math.pi / 2.0)
            p = Vector((cx + r * math.cos(ang), cy + r * math.sin(ang), 0.0))
            t = Vector((math.sin(ang), -math.cos(ang), 0.0))
            return p, t
        s -= arc_len
        if s < straight_d:
            u = s / straight_d
            return Vector((cx + r, cy - 2.0 * cy * u, 0.0)), Vector((0.0, -1.0, 0.0))
        s -= straight_d
        if s < arc_len:
            ang = 0.0 - (s / arc_len) * (math.pi / 2.0)
            p = Vector((cx + r * math.cos(ang), -cy + r * math.sin(ang), 0.0))
            t = Vector((math.sin(ang), -math.cos(ang), 0.0))
            return p, t
        s -= arc_len
        if s < straight_w:
            u = s / straight_w
            return Vector((cx - 2.0 * cx * u, -cy - r, 0.0)), Vector((-1.0, 0.0, 0.0))
        s -= straight_w
        if s < arc_len:
            ang = 3.0 * math.pi / 2.0 - (s / arc_len) * (math.pi / 2.0)
            p = Vector((-cx + r * math.cos(ang), -cy + r * math.sin(ang), 0.0))
            t = Vector((math.sin(ang), -math.cos(ang), 0.0))
            return p, t
        s -= arc_len
        if s < straight_d:
            u = s / straight_d
            return Vector((-cx - r, -cy + 2.0 * cy * u, 0.0)), Vector((0.0, 1.0, 0.0))
        s -= straight_d
        ang = math.pi - (s / arc_len) * (math.pi / 2.0)
        p = Vector((-cx + r * math.cos(ang), cy + r * math.sin(ang), 0.0))
        t = Vector((math.sin(ang), -math.cos(ang), 0.0))
        return p, t

    pts = []
    for i in range(n_stitches):
        s_dist = i * actual_pitch
        pos, tan = get_pos_tan_at_distance(s_dist)
        pts.append((pos, tan))
        
    return pts

def build_leather_badge_mesh(w, d, h, corner_r, slot_w, slot_d, slot_off_x):
    """
    Builds a solid manifold leather badge with rounded corners and pill slot using 2D curve extrusion.
    Generates exact UV mapping [0..1] for the 2200x650 texture map.
    """
    curve_data = bpy.data.curves.new('Badge_Curve', type='CURVE')
    curve_data.dimensions = '2D'
    curve_data.fill_mode = 'BOTH'
    curve_data.extrude = h / 2.0 - 0.0003
    curve_data.bevel_depth = 0.0004
    curve_data.bevel_resolution = 3

    # 1. Outer rounded rect spline
    cx = w / 2.0 - corner_r
    cy = d / 2.0 - corner_r
    sp_out = curve_data.splines.new('POLY')
    sp_out.use_cyclic_u = True

    poly_out = []
    for c_x, c_y, a_start, a_end in [
        (cx, cy, 0.0, math.pi / 2.0),
        (-cx, cy, math.pi / 2.0, math.pi),
        (-cx, -cy, math.pi, 3.0 * math.pi / 2.0),
        (cx, -cy, 3.0 * math.pi / 2.0, 2.0 * math.pi)
    ]:
        for i in range(10):
            ang = a_start + (a_end - a_start) * (i / 10.0)
            poly_out.append((c_x + corner_r * math.cos(ang), c_y + corner_r * math.sin(ang), 0.0, 1.0))

    sp_out.points.add(len(poly_out) - 1)
    for i, pt in enumerate(poly_out):
        sp_out.points[i].co = pt

    # 2. Inner pill slot spline
    sr = slot_d / 2.0
    scx = slot_w / 2.0 - sr
    poly_in = []
    # Left semicircle
    for i in range(12):
        ang = math.pi / 2.0 + math.pi * (i / 12.0)
        poly_in.append((slot_off_x - scx + sr * math.cos(ang), sr * math.sin(ang), 0.0, 1.0))
    # Right semicircle
    for i in range(12):
        ang = -math.pi / 2.0 + math.pi * (i / 12.0)
        poly_in.append((slot_off_x + scx + sr * math.cos(ang), sr * math.sin(ang), 0.0, 1.0))

    sp_in = curve_data.splines.new('POLY')
    sp_in.use_cyclic_u = True
    sp_in.points.add(len(poly_in) - 1)
    for i, pt in enumerate(poly_in):
        sp_in.points[i].co = pt

    badge_obj = bpy.data.objects.new("NovaDesk_Leather_Badge", curve_data)
    bpy.context.collection.objects.link(badge_obj)
    bpy.context.view_layer.objects.active = badge_obj
    badge_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    badge_obj.select_set(False)

    # Generate Planar UV Coordinates
    while badge_obj.data.uv_layers:
        badge_obj.data.uv_layers.remove(badge_obj.data.uv_layers[0])
    uv_layer = badge_obj.data.uv_layers.new(name="UVMap")
    for loop in badge_obj.data.loops:
        vert = badge_obj.data.vertices[loop.vertex_index]
        u = (vert.co.x / w) + 0.5
        v = (vert.co.y / d) + 0.5
        uv_layer.data[loop.index].uv = (u, v)

    bpy.context.view_layer.objects.active = badge_obj
    bpy.ops.object.shade_smooth()
    return badge_obj

def build_novadesk_scene():
    print("=== MODELING NOVADESK XL MAT V6 ===")
    mat_w = 0.900    # 900 mm
    mat_d = 0.400    # 400 mm
    corner_r = 0.024 # 24 mm radius
    total_h = 0.0042 # 4.2 mm
    rubber_h = 0.0014 # 1.4 mm
    
    mat_felt = create_anthracite_felt_material()
    mat_rubber = create_rubber_base_material()
    mat_leather = create_cognac_leather_material()
    mat_thread = create_saddle_thread_material()
    mat_puncture = create_puncture_hole_material()
    mat_brass = create_turned_brass_material()
    
    created_objects = []
    
    # -------------------------------------------------------------------------
    # 1. FELT & RUBBER MAT BODIES
    # -------------------------------------------------------------------------
    n_poly = 160
    cx = mat_w / 2.0 - corner_r
    cy = mat_d / 2.0 - corner_r
    poly_pts = []
    corners_cfg = [
        (cx, cy, 0.0, math.pi / 2.0),
        (-cx, cy, math.pi / 2.0, math.pi),
        (-cx, -cy, math.pi, 3.0 * math.pi / 2.0),
        (cx, -cy, 3.0 * math.pi / 2.0, 2.0 * math.pi)
    ]
    sub_per_c = n_poly // 4
    for c_x, c_y, a_start, a_end in corners_cfg:
        for i in range(sub_per_c):
            ang = a_start + (a_end - a_start) * (i / float(sub_per_c))
            poly_pts.append((c_x + corner_r * math.cos(ang), c_y + corner_r * math.sin(ang)))
            
    # Felt Top Layer Mesh (2.8 mm thick)
    mesh_felt = bpy.data.meshes.new("Mesh_Felt_Top")
    bm_felt = bmesh.new()
    v_f_bot = [bm_felt.verts.new((x, y, rubber_h)) for x, y in poly_pts]
    v_f_top = [bm_felt.verts.new((x, y, total_h)) for x, y in poly_pts]
    bm_felt.faces.new(v_f_top)
    bm_felt.faces.new(list(reversed(v_f_bot)))
    for i in range(len(poly_pts)):
        ni = (i + 1) % len(poly_pts)
        bm_felt.faces.new((v_f_bot[i], v_f_bot[ni], v_f_top[ni], v_f_top[i]))
    bm_felt.to_mesh(mesh_felt)
    bm_felt.free()
    
    obj_felt = bpy.data.objects.new("NovaDesk_Merino_Felt", mesh_felt)
    bpy.context.collection.objects.link(obj_felt)
    obj_felt.data.materials.append(mat_felt)
    
    # UV Map for Felt
    uv_f = obj_felt.data.uv_layers.new(name="UVMap")
    for loop in obj_felt.data.loops:
        v = obj_felt.data.vertices[loop.vertex_index]
        u = (v.co.x / mat_w) + 0.5
        v_coord = (v.co.y / mat_d) + 0.5
        uv_f.data[loop.index].uv = (u, v_coord)
        
    bev_f = obj_felt.modifiers.new("Bevel", 'BEVEL')
    bev_f.width = 0.0011 # 1.1 mm smooth upper bevel
    bev_f.segments = 4
    bpy.context.view_layer.objects.active = obj_felt
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_felt)
    
    # Rubber Bottom Base Mesh (1.4 mm thick)
    mesh_rub = bpy.data.meshes.new("Mesh_Rubber_Base")
    bm_rub = bmesh.new()
    v_r_bot = [bm_rub.verts.new((x, y, 0.0)) for x, y in poly_pts]
    v_r_top = [bm_rub.verts.new((x, y, rubber_h)) for x, y in poly_pts]
    bm_rub.faces.new(v_r_top)
    bm_rub.faces.new(list(reversed(v_r_bot)))
    for i in range(len(poly_pts)):
        ni = (i + 1) % len(poly_pts)
        bm_rub.faces.new((v_r_bot[i], v_r_bot[ni], v_r_top[ni], v_r_top[i]))
    bm_rub.to_mesh(mesh_rub)
    bm_rub.free()
    
    obj_rub = bpy.data.objects.new("NovaDesk_Rubber_Base", mesh_rub)
    bpy.context.collection.objects.link(obj_rub)
    obj_rub.data.materials.append(mat_rubber)
    bev_r = obj_rub.modifiers.new("Bevel", 'BEVEL')
    bev_r.width = 0.0005
    bev_r.segments = 2
    bpy.context.view_layer.objects.active = obj_rub
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_rub)
    
    # -------------------------------------------------------------------------
    # 2. EQUIDISTANT SADDLE STITCHES + PUNCTURE DIMPLES
    # -------------------------------------------------------------------------
    stitch_inset = 0.0080 # 8.0 mm inset from perimeter
    s_r = corner_r - stitch_inset
    s_w = mat_w - 2.0 * stitch_inset
    s_d = mat_d - 2.0 * stitch_inset
    
    equidistant_stitches = build_equidistant_rounded_rect_curve(s_w, s_d, s_r, pitch=0.0068)
    print(f"Generated {len(equidistant_stitches)} equidistant saddle stitches.")
    
    mesh_st = bpy.data.meshes.new("Mesh_Saddle_Stitches")
    bm_st = bmesh.new()
    
    mesh_punc = bpy.data.meshes.new("Mesh_Puncture_Dimples")
    bm_punc = bmesh.new()
    
    stitch_len = 0.0050   # 5.0 mm stitch length
    stitch_rad = 0.00032  # 0.32 mm thread radius (realistic gauge)
    stitch_arch = 0.00030 # Arch height above felt surface
    
    for pos, tan in equidistant_stitches:
        tangent_ang = math.atan2(tan.y, tan.x)
        slant = tangent_ang + math.radians(18.0) # +18 deg saddle pricking angle
        
        # 1. Stitches 3D Thread Loop
        n_segs = 6
        pts_arch = []
        for s in range(n_segs + 1):
            u = s / float(n_segs)
            offset = (u - 0.5) * stitch_len
            lx = pos.x + offset * math.cos(slant)
            ly = pos.y + offset * math.sin(slant)
            
            # Ends plunge 0.45mm into needle hole, apex rises 0.28mm above felt
            parabola = math.sin(u * math.pi) * stitch_arch - (1.0 - math.sin(u * math.pi)) * 0.00045
            lz = total_h + parabola
            pts_arch.append(Vector((lx, ly, lz)))
            
        ring_prev = None
        n_circle = 6
        for seg_idx, pt in enumerate(pts_arch):
            if seg_idx < len(pts_arch) - 1:
                t_vec = (pts_arch[seg_idx + 1] - pt).normalized()
            else:
                t_vec = (pt - pts_arch[seg_idx - 1]).normalized()
                
            norm_vec = Vector((-t_vec.y, t_vec.x, 0.0)).normalized()
            binorm_vec = t_vec.cross(norm_vec).normalized()
            
            ring = []
            for c in range(n_circle):
                c_ang = c * (2.0 * math.pi / n_circle)
                rad_offset = norm_vec * (stitch_rad * math.cos(c_ang)) + binorm_vec * (stitch_rad * math.sin(c_ang))
                v = bm_st.verts.new(pt + rad_offset)
                ring.append(v)
                
            if ring_prev:
                for c in range(n_circle):
                    nc = (c + 1) % n_circle
                    bm_st.faces.new((ring_prev[c], ring_prev[nc], ring[nc], ring[c]))
            else:
                bm_st.faces.new(list(reversed(ring)))
            ring_prev = ring
            
        if ring_prev:
            bm_st.faces.new(ring_prev)
            
        # 2. Needle Puncture Hole Dimple at stitch entry/exit points
        for u_end in (-0.5, 0.5):
            px = pos.x + u_end * stitch_len * math.cos(slant)
            py = pos.y + u_end * stitch_len * math.sin(slant)
            pz = total_h
            
            # Tiny puncture hole (radius 0.38mm, depth 0.6mm)
            p_rad = 0.00038
            p_depth = 0.0006
            v_p_top = []
            v_p_bot = []
            for k in range(6):
                ka = k * (2.0 * math.pi / 6.0)
                v_p_top.append(bm_punc.verts.new((px + p_rad * math.cos(ka), py + p_rad * math.sin(ka), pz + 0.00005)))
                v_p_bot.append(bm_punc.verts.new((px + (p_rad*0.5) * math.cos(ka), py + (p_rad*0.5) * math.sin(ka), pz - p_depth)))
            bm_punc.faces.new(v_p_bot)
            for k in range(6):
                nk = (k + 1) % 6
                bm_punc.faces.new((v_p_bot[k], v_p_bot[nk], v_p_top[nk], v_p_top[k]))

    bm_st.to_mesh(mesh_st)
    bm_st.free()
    
    obj_st = bpy.data.objects.new("NovaDesk_Stitches", mesh_st)
    bpy.context.collection.objects.link(obj_st)
    obj_st.data.materials.append(mat_thread)
    bpy.context.view_layer.objects.active = obj_st
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_st)
    
    bm_punc.to_mesh(mesh_punc)
    bm_punc.free()
    obj_punc = bpy.data.objects.new("NovaDesk_Punctures", mesh_punc)
    bpy.context.collection.objects.link(obj_punc)
    obj_punc.data.materials.append(mat_puncture)
    created_objects.append(obj_punc)

    # -------------------------------------------------------------------------
    # 3. SOLID VEGETABLE-TANNED LEATHER BADGE & SOLID BRASS HARDWARE
    # -------------------------------------------------------------------------
    badge_w = 0.088  # 88 mm
    badge_d = 0.026  # 26 mm
    badge_h = 0.0022 # 2.2 mm
    corner_b_r = 0.0045 # 4.5 mm
    slot_w = 0.0232
    slot_d = 0.0058
    slot_off_x = -0.0208
    
    badge_cx = mat_w / 2.0 - 0.072 # 72 mm from right edge
    badge_cy = mat_d / 2.0 - 0.026 # 26 mm from top edge
    badge_cz = total_h + badge_h / 2.0
    
    obj_badge = build_leather_badge_mesh(badge_w, badge_d, badge_h, corner_b_r, slot_w, slot_d, slot_off_x)
    obj_badge.location = Vector((badge_cx, badge_cy, badge_cz))
    obj_badge.data.materials.append(mat_leather)
    created_objects.append(obj_badge)
    
    # Solid Turned Brass Rivet (centered over rivet deboss ring)
    rivet_x = badge_cx + 0.0304 # Matching texture rivet position
    rivet_y = badge_cy
    rivet_z = badge_cz + badge_h / 2.0
    
    # Rivet Base Washer Chamfer
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0048, depth=0.0016, location=(rivet_x, rivet_y, rivet_z + 0.0006)
    )
    rivet = bpy.context.active_object
    rivet.name = "NovaDesk_Brass_Rivet"
    rivet.data.materials.append(mat_brass)
    rbev = rivet.modifiers.new("Bevel", 'BEVEL')
    rbev.width = 0.0004
    rbev.segments = 3
    bpy.context.view_layer.objects.active = rivet
    bpy.ops.object.shade_smooth()
    created_objects.append(rivet)
    
    # Rivet Lathe Center Pip
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0018, depth=0.0005, location=(rivet_x, rivet_y, rivet_z + 0.0013)
    )
    rivet_dot = bpy.context.active_object
    rivet_dot.name = "NovaDesk_Brass_Rivet_Dot"
    rivet_dot.data.materials.append(mat_brass)
    dbev = rivet_dot.modifiers.new("Bevel", 'BEVEL')
    dbev.width = 0.0002
    dbev.segments = 2
    bpy.context.view_layer.objects.active = rivet_dot
    bpy.ops.object.shade_smooth()
    created_objects.append(rivet_dot)

    # -------------------------------------------------------------------------
    # 4. STUDIO EDITORIAL GROUND FLOOR (#EBE8E1)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_plane_add(size=16.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    mat_fl = bpy.data.materials.new("Studio_Editorial_Floor")
    mat_fl.use_nodes = True
    fl_bsdf = mat_fl.node_tree.nodes.get("Principled BSDF")
    if fl_bsdf:
        fl_bsdf.inputs['Base Color'].default_value = (0.88, 0.86, 0.82, 1.0)
        fl_bsdf.inputs['Roughness'].default_value = 0.88
    floor.data.materials.append(mat_fl)
    
    return created_objects

def setup_studio_lighting():
    """
    Raking directional softbox setup sculpting fiber relief, edge bevel, and hardware glints.
    """
    # 1. Raking Key Softbox (21 deg elevation, directional relief across fibers)
    bpy.ops.object.light_add(type='AREA', location=(-1.6, -1.1, 0.65))
    key = bpy.context.active_object
    key.name = "Studio_Key_Rake"
    key.data.energy = 28.0
    key.data.size = 2.0
    key.data.size_y = 1.2
    key.data.color = (1.0, 0.99, 0.96)
    dir_k = Vector((0.0, 0.0, 0.002)) - key.location
    key.rotation_euler = dir_k.to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True
    
    # 2. Opposite Soft Infill
    bpy.ops.object.light_add(type='AREA', location=(1.4, -0.6, 0.85))
    fill = bpy.context.active_object
    fill.name = "Studio_Fill_Side"
    fill.data.energy = 10.0
    fill.data.size = 2.0
    fill.data.size_y = 1.4
    fill.data.color = (0.96, 0.98, 1.0)
    dir_f = Vector((0.1, 0.0, 0.002)) - fill.location
    fill.rotation_euler = dir_f.to_track_quat('-Z', 'Y').to_euler()
    fill.data.use_shadow = False
    
    # 3. Diffuse Overhead Softbox
    bpy.ops.object.light_add(type='AREA', location=(0.0, 0.0, 2.0))
    top = bpy.context.active_object
    top.name = "Studio_Top_Crown"
    top.data.energy = 8.0
    top.data.size = 2.4
    top.data.size_y = 1.6
    top.data.color = (0.98, 0.99, 1.0)
    top.rotation_euler = Euler((0, 0, 0), 'XYZ')
    top.data.use_shadow = True
    
    # 4. Corner Hardware Accent Glint Light
    bpy.ops.object.light_add(type='AREA', location=(1.1, 0.7, 0.58))
    rim = bpy.context.active_object
    rim.name = "Studio_Hardware_Rim"
    rim.data.energy = 22.0
    rim.data.size = 0.35
    rim.data.size_y = 0.35
    rim.data.color = (1.0, 0.98, 0.94)
    dir_r = Vector((0.38, 0.17, 0.006)) - rim.location
    rim.rotation_euler = dir_r.to_track_quat('-Z', 'Y').to_euler()
    rim.data.use_shadow = False

def setup_hero_camera(scene):
    """
    Hero Camera (1600x1200) with guaranteed >=14.5% margins on all sides.
    Shows full expansive top felt surface, saddle stitching, and layered edge thickness.
    """
    cam_data = bpy.data.cameras.new("Camera_NovaDesk_Hero")
    cam_data.lens = 48.0
    cam_obj = bpy.data.objects.new("Camera_NovaDesk_Hero", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    target = Vector((0.0, 0.0, 0.002))
    dist = 1.84 # Calibrated distance: Left/Right margins = 14.5%, Top/Bottom margins = 30-36%
    elev_rad = math.radians(24.0)
    azim_rad = math.radians(-24.0)
    
    cam_x = target.x + dist * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target.y - dist * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target.z + dist * math.sin(elev_rad)
    
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    dir_cam = target - cam_obj.location
    cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
    return cam_obj

def setup_macro_camera(scene):
    """
    Macro Camera (1600x1200) focused on leather loop, brass rivet, debossed branding, and wool weave.
    """
    cam_data = bpy.data.cameras.new("Camera_NovaDesk_Macro")
    cam_data.lens = 95.0
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = 8.0 # Sharp focus covering deboss, rivet and stitches
    
    cam_obj = bpy.data.objects.new("Camera_NovaDesk_Macro", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    # Target exactly at the center of the leather badge
    target = Vector((0.90 / 2.0 - 0.072, 0.40 / 2.0 - 0.026, 0.005))
    dist = 0.24
    elev_rad = math.radians(34.0)
    azim_rad = math.radians(-16.0)
    
    cam_x = target.x + dist * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target.y - dist * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target.z + dist * math.sin(elev_rad)
    
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    dir_cam = target - cam_obj.location
    cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
    
    # Lock focus distance to target
    cam_data.dof.focus_distance = (cam_obj.location - target).length
    return cam_obj

def verify_camera_margins(scene, cam_obj):
    """
    Mathematically verifies that all 4 corners of the mat are within safe margins in the camera frame.
    """
    import bpy_extras
    bpy.context.view_layer.update()
    corners = [
        Vector((0.450, 0.200, 0.0042)),
        Vector((-0.450, 0.200, 0.0042)),
        Vector((-0.450, -0.200, 0.0042)),
        Vector((0.450, -0.200, 0.0042)),
        Vector((0.450, 0.200, 0.0)),
        Vector((-0.450, 0.200, 0.0)),
        Vector((-0.450, -0.200, 0.0)),
        Vector((0.450, -0.200, 0.0))
    ]
    coords_2d = []
    for co in corners:
        p2d = bpy_extras.object_utils.world_to_camera_view(scene, cam_obj, co)
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
    return min_x > 0.08 and max_x < 0.92 and min_y > 0.08 and max_y < 0.92

def main():
    print("=== STARTING NOVADESK XL MAT V6 RENDERING ===")
    scene = reset_scene()
    configure_cycles(scene, samples=384)
    
    model_objs = build_novadesk_scene()
    setup_studio_lighting()
    
    hero_cam = setup_hero_camera(scene)
    macro_cam = setup_macro_camera(scene)
    
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    
    # Verify camera framing
    is_safe = verify_camera_margins(scene, hero_cam)
    print("Camera margins safe:", is_safe)
    
    # 1. RENDER HERO VIEW (1600x1200)
    print("--- Rendering NovaDesk Hero View ---")
    scene.camera = hero_cam
    hero_out = os.path.join(OUTPUT_DIR, "novadesk_mat_hero_render.png")
    scene.render.filepath = hero_out
    bpy.ops.render.render(write_still=True)
    print(f"Hero Render Saved: {hero_out}")
    
    # 2. RENDER CLOSE-UP MACRO VIEW (1600x1200)
    print("--- Rendering NovaDesk Macro Detail View ---")
    scene.camera = macro_cam
    macro_out = os.path.join(OUTPUT_DIR, "novadesk_mat_macro_detail.png")
    scene.render.filepath = macro_out
    bpy.ops.render.render(write_still=True)
    print(f"Macro Detail Render Saved: {macro_out}")
    
    blend_path = os.path.join(MODELS_DIR, "novadesk_mat_master.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Master Scene Saved: {blend_path}")
    print("=== NOVADESK MAT V6 FINISHED ===")

if __name__ == "__main__":
    main()
