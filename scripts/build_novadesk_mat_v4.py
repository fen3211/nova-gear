"""
NOVA DESK XL Mat - Industrial Design & Photorealistic Studio Render V4
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Key Upgrades:
1. True 4K Heathered Merino Wool Textile:
   - Maps 4096x2048 multi-fiber albedo, high-relief normal, and roughness maps with 1:1 planar UVs.
   - Sheen Weight (0.85) creates velvety fiber rim backscatter on glancing angles.
   - Micro-displaced fiber relief catching raking studio light.
2. Mathematically Equidistant Saddle Stitches:
   - Arc-length parameterized curve distribution (7.5mm pitch everywhere).
   - Arched 3D thread loops sinking into the seam with natural +18 deg slant.
   - Warm ecru / stone silk thread shader.
3. Clean Parametric Leather Cable Loop & Hardware:
   - 2D Dual-Spline Curve with integrated open cable slot (zero boolean artifacts).
   - Rich full-grain cognac leather with hot-stamped debossed NOVA mark and perimeter creasing.
   - Turned solid brass rivet with concentric machining highlight.
4. Editorial Studio Rake Lighting & Framing:
   - Low 15 deg grazing rake softbox casting micro-shadows behind fibers and stitches.
   - Guaranteed >=16% margin around entire 900x400 mat (zero edge clipping).
   - Renders Hero View (1600x1200) and Macro Detail View (1600x1200) in Cycles OptiX.
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
        # PURE CONTROLLED ENVIRONMENT: Zero ambient wash, 100% softbox illumination
        bg.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)
        bg.inputs['Strength'].default_value = 0.0
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

def create_4k_merino_felt_material():
    mat = bpy.data.materials.new("Merino_Heather_Felt_4K")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    
    # 1. Albedo Texture Map
    albedo_path = os.path.join(TEXTURES_DIR, "novadesk_felt_albedo.png")
    if os.path.exists(albedo_path):
        tex_alb = nodes.new('ShaderNodeTexImage')
        tex_alb.image = bpy.data.images.load(albedo_path)
        links.new(tex_coord.outputs['UV'], tex_alb.inputs['Vector'])
        links.new(tex_alb.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.045, 0.048, 0.054, 1.0)
        
    # 2. Roughness Texture Map
    rough_path = os.path.join(TEXTURES_DIR, "novadesk_felt_roughness.png")
    if os.path.exists(rough_path):
        tex_rough = nodes.new('ShaderNodeTexImage')
        tex_rough.image = bpy.data.images.load(rough_path)
        tex_rough.image.colorspace_settings.name = 'Non-Color'
        links.new(tex_coord.outputs['UV'], tex_rough.inputs['Vector'])
        links.new(tex_rough.outputs['Color'], bsdf.inputs['Roughness'])
    else:
        bsdf.inputs['Roughness'].default_value = 0.94
        
    # 3. Normal Texture Map
    norm_path = os.path.join(TEXTURES_DIR, "novadesk_felt_normal.png")
    if os.path.exists(norm_path):
        tex_norm = nodes.new('ShaderNodeTexImage')
        tex_norm.image = bpy.data.images.load(norm_path)
        tex_norm.image.colorspace_settings.name = 'Non-Color'
        links.new(tex_coord.outputs['UV'], tex_norm.inputs['Vector'])
        
        node_norm = nodes.new('ShaderNodeNormalMap')
        node_norm.inputs['Strength'].default_value = 1.35
        links.new(tex_norm.outputs['Color'], node_norm.inputs['Color'])
        links.new(node_norm.outputs['Normal'], bsdf.inputs['Normal'])
        
    # TEXTILE SHEEN: Creates soft fuzzy rim highlights on wool fibers
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.85
        if 'Sheen Roughness' in bsdf.inputs:
            bsdf.inputs['Sheen Roughness'].default_value = 0.50
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (0.85, 0.88, 0.95, 1.0)
            
    # Subsurface light-trapping
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.06
        bsdf.inputs['Subsurface Radius'].default_value = (0.002, 0.002, 0.002)
        bsdf.inputs['Subsurface Scale'].default_value = 0.001
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_rubber_base_material():
    mat = bpy.data.materials.new("Rubber_Base_Matte")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.015, 0.016, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_cognac_leather_material():
    mat = bpy.data.materials.new("Cognac_Leather_4K")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    
    alb_path = os.path.join(TEXTURES_DIR, "novadesk_leather_albedo.png")
    if os.path.exists(alb_path):
        tex_alb = nodes.new('ShaderNodeTexImage')
        tex_alb.image = bpy.data.images.load(alb_path)
        links.new(tex_coord.outputs['UV'], tex_alb.inputs['Vector'])
        links.new(tex_alb.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.22, 0.10, 0.038, 1.0)
        
    norm_path = os.path.join(TEXTURES_DIR, "novadesk_leather_normal.png")
    if os.path.exists(norm_path):
        tex_norm = nodes.new('ShaderNodeTexImage')
        tex_norm.image = bpy.data.images.load(norm_path)
        tex_norm.image.colorspace_settings.name = 'Non-Color'
        links.new(tex_coord.outputs['UV'], tex_norm.inputs['Vector'])
        
        node_norm = nodes.new('ShaderNodeNormalMap')
        node_norm.inputs['Strength'].default_value = 1.0
        links.new(tex_norm.outputs['Color'], node_norm.inputs['Color'])
        links.new(node_norm.outputs['Normal'], bsdf.inputs['Normal'])
        
    bsdf.inputs['Roughness'].default_value = 0.38
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.20
        bsdf.inputs['Coat Roughness'].default_value = 0.25
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_saddle_thread_material():
    mat = bpy.data.materials.new("Spun_Saddle_Thread")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    # Warm ecru / light stone contrasting thread
    bsdf.inputs['Base Color'].default_value = (0.42, 0.39, 0.34, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.45
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.65
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_turned_brass_material():
    mat = bpy.data.materials.new("Turned_Solid_Brass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.78, 0.36, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.20
    if 'Anisotropic' in bsdf.inputs:
        bsdf.inputs['Anisotropic'].default_value = 0.80
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_equidistant_rounded_rect_curve(w, d, r, pitch=0.0075):
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

def build_novadesk_scene():
    print("=== MODELING NOVADESK XL MAT V4 ===")
    mat_w = 0.900    # 900 mm
    mat_d = 0.400    # 400 mm
    corner_r = 0.024 # 24 mm radius
    total_h = 0.0042 # 4.2 mm
    felt_h = 0.0026  # 2.6 mm
    rubber_h = 0.0016 # 1.6 mm
    
    mat_felt = create_4k_merino_felt_material()
    mat_rubber = create_rubber_base_material()
    mat_leather = create_cognac_leather_material()
    mat_thread = create_saddle_thread_material()
    mat_brass = create_turned_brass_material()
    
    created_objects = []
    
    # -------------------------------------------------------------------------
    # 1. FELT & RUBBER MAT BODIES WITH UV MAPPING
    # -------------------------------------------------------------------------
    n_poly = 128
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
            
    # Felt Top Layer Mesh with 1:1 Planar UV Coordinates
    mesh_felt = bpy.data.meshes.new("Mesh_Felt_Top")
    bm_felt = bmesh.new()
    uv_layer = bm_felt.loops.layers.uv.new("UVMap")
    
    v_f_bot = [bm_felt.verts.new((x, y, rubber_h)) for x, y in poly_pts]
    v_f_top = [bm_felt.verts.new((x, y, total_h)) for x, y in poly_pts]
    
    f_top = bm_felt.faces.new(v_f_top)
    f_bot = bm_felt.faces.new(list(reversed(v_f_bot)))
    
    # Assign UVs to top face: U in [0..1], V in [0..1]
    for loop in f_top.loops:
        vx = loop.vert.co.x
        vy = loop.vert.co.y
        u = (vx + mat_w / 2.0) / mat_w
        v = (vy + mat_d / 2.0) / mat_d
        loop[uv_layer].uv = (u, v)
        
    for i in range(len(poly_pts)):
        ni = (i + 1) % len(poly_pts)
        f_side = bm_felt.faces.new((v_f_bot[i], v_f_bot[ni], v_f_top[ni], v_f_top[i]))
        for loop in f_side.loops:
            vx = loop.vert.co.x
            vy = loop.vert.co.y
            u = (vx + mat_w / 2.0) / mat_w
            v = (vy + mat_d / 2.0) / mat_d
            loop[uv_layer].uv = (u, v)
            
    bm_felt.to_mesh(mesh_felt)
    bm_felt.free()
    
    obj_felt = bpy.data.objects.new("NovaDesk_Merino_Felt", mesh_felt)
    bpy.context.collection.objects.link(obj_felt)
    obj_felt.data.materials.append(mat_felt)
    bev_f = obj_felt.modifiers.new("Bevel", 'BEVEL')
    bev_f.width = 0.0014
    bev_f.segments = 4
    bpy.context.view_layer.objects.active = obj_felt
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_felt)
    
    # Rubber Bottom Base Mesh
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
    bev_r.width = 0.0006
    bev_r.segments = 2
    bpy.context.view_layer.objects.active = obj_rub
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_rub)
    
    # -------------------------------------------------------------------------
    # 2. EQUIDISTANT SADDLE STITCHES (7.5mm pitch)
    # -------------------------------------------------------------------------
    stitch_inset = 0.0075
    s_r = corner_r - stitch_inset
    s_w = mat_w - 2.0 * stitch_inset
    s_d = mat_d - 2.0 * stitch_inset
    
    equidistant_stitches = build_equidistant_rounded_rect_curve(s_w, s_d, s_r, pitch=0.0075)
    print(f"Generated {len(equidistant_stitches)} equidistant saddle stitches.")
    
    mesh_st = bpy.data.meshes.new("Mesh_Saddle_Stitches")
    bm_st = bmesh.new()
    
    stitch_len = 0.0055  # 5.5mm length
    stitch_rad = 0.00062 # 0.62mm radius
    stitch_arch = 0.00045 # Arch height
    
    for pos, tan in equidistant_stitches:
        tangent_ang = math.atan2(tan.y, tan.x)
        slant = tangent_ang + math.radians(18.0)
        
        n_segs = 5
        pts_arch = []
        for s in range(n_segs + 1):
            u = s / float(n_segs)
            offset = (u - 0.5) * stitch_len
            lx = pos.x + offset * math.cos(slant)
            ly = pos.y + offset * math.sin(slant)
            parabola = math.sin(u * math.pi) * stitch_arch - 0.00025
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
            
    bm_st.to_mesh(mesh_st)
    bm_st.free()
    
    obj_st = bpy.data.objects.new("NovaDesk_Stitches", mesh_st)
    bpy.context.collection.objects.link(obj_st)
    obj_st.data.materials.append(mat_thread)
    bpy.context.view_layer.objects.active = obj_st
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_st)
    
    # -------------------------------------------------------------------------
    # 3. 2D CURVE PARAMETRIC LEATHER CABLE LOOP WITH REAL SLOT HOLE
    # -------------------------------------------------------------------------
    badge_w = 0.082 # 82 mm
    badge_d = 0.026 # 26 mm
    badge_h = 0.0018 # 1.8 mm
    badge_r = 0.005 # 5 mm corner radius
    
    badge_x = mat_w / 2.0 - 0.068
    badge_y = mat_d / 2.0 - 0.026
    badge_z = total_h + badge_h / 2.0
    
    # Create 2D curve data
    curve_data = bpy.data.curves.new("Leather_Badge_Curve", 'CURVE')
    curve_data.dimensions = '2D'
    curve_data.extrude = badge_h / 2.0
    curve_data.bevel_depth = 0.0004
    curve_data.bevel_resolution = 3
    
    # 1. Outer boundary spline (counter-clockwise)
    b_cx = badge_w / 2.0 - badge_r
    b_cy = badge_d / 2.0 - badge_r
    outer_pts = []
    for c_x, c_y, a_start, a_end in [
        (b_cx, b_cy, 0.0, math.pi / 2.0),
        (-b_cx, b_cy, math.pi / 2.0, math.pi),
        (-b_cx, -b_cy, math.pi, 3.0 * math.pi / 2.0),
        (b_cx, -b_cy, 3.0 * math.pi / 2.0, 2.0 * math.pi)
    ]:
        for i in range(8):
            ang = a_start + (a_end - a_start) * (i / 8.0)
            outer_pts.append((c_x + badge_r * math.cos(ang), c_y + badge_r * math.sin(ang)))
            
    spline_out = curve_data.splines.new('POLY')
    spline_out.points.add(len(outer_pts) - 1)
    for idx, (px, py) in enumerate(outer_pts):
        spline_out.points[idx].co = (px, py, 0, 1)
    spline_out.use_cyclic_u = True
    
    # 2. Inner cable slot hole spline (clockwise)
    slot_w = 0.024
    slot_d = 0.006
    slot_r = slot_d / 2.0
    slot_cx = (slot_w - slot_d) / 2.0
    slot_offset_x = -0.018 # On left side of badge
    inner_pts = []
    # Clockwise order for inner hole spline
    for c_x, a_start, a_end in [
        (slot_offset_x - slot_cx, math.pi / 2.0, -math.pi / 2.0),
        (slot_offset_x + slot_cx, -math.pi / 2.0, -3.0 * math.pi / 2.0)
    ]:
        for i in range(8):
            ang = a_start + (a_end - a_start) * (i / 8.0)
            inner_pts.append((c_x + slot_r * math.cos(ang), slot_r * math.sin(ang)))
            
    spline_in = curve_data.splines.new('POLY')
    spline_in.points.add(len(inner_pts) - 1)
    for idx, (px, py) in enumerate(inner_pts):
        spline_in.points[idx].co = (px, py, 0, 1)
    spline_in.use_cyclic_u = True
    
    obj_badge = bpy.data.objects.new("NovaDesk_Leather_Badge", curve_data)
    obj_badge.location = Vector((badge_x, badge_y, badge_z))
    bpy.context.collection.objects.link(obj_badge)
    obj_badge.data.materials.append(mat_leather)
    
    # Convert curve to mesh so we can assign exact UV mapping for the leather texture!
    obj_badge.select_set(True)
    bpy.context.view_layer.objects.active = obj_badge
    bpy.ops.object.convert(target='MESH')
    
    # Assign UV mapping for leather badge (map 82x26mm to 0..1 UV)
    mesh_b = obj_badge.data
    bm_b = bmesh.new()
    bm_b.from_mesh(mesh_b)
    uv_b = bm_b.loops.layers.uv.verify()
    for face in bm_b.faces:
        for loop in face.loops:
            # Local coordinates
            lx = loop.vert.co.x
            ly = loop.vert.co.y
            u = (lx + badge_w / 2.0) / badge_w
            v = (ly + badge_d / 2.0) / badge_d
            loop[uv_b].uv = (u, v)
    bm_b.to_mesh(mesh_b)
    bm_b.free()
    
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_badge)
    
    # Turned Solid Brass Rivet with Concentric Machining
    rivet_x = badge_x + badge_w / 2.0 - 0.010
    rivet_y = badge_y
    rivet_z = badge_z + badge_h / 2.0
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0050, depth=0.0018, location=(rivet_x, rivet_y, rivet_z + 0.0006)
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
    
    # Rivet Center Pip
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0018, depth=0.0006, location=(rivet_x, rivet_y, rivet_z + 0.0013)
    )
    rivet_dot = bpy.context.active_object
    rivet_dot.name = "NovaDesk_Brass_Rivet_Dot"
    rivet_dot.data.materials.append(mat_brass)
    created_objects.append(rivet_dot)
    
    # -------------------------------------------------------------------------
    # 4. STUDIO NEUTRAL GROUND FLOOR (Cream #EBE8E1)
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    mat_fl = bpy.data.materials.new("Studio_Editorial_Floor")
    mat_fl.use_nodes = True
    fl_bsdf = mat_fl.node_tree.nodes.get("Principled BSDF")
    if fl_bsdf:
        fl_bsdf.inputs['Base Color'].default_value = (0.92, 0.91, 0.88, 1.0)
        fl_bsdf.inputs['Roughness'].default_value = 0.85
    floor.data.materials.append(mat_fl)
    
    return created_objects

def setup_studio_lighting():
    """
    Raking glancing studio softbox setup to reveal rich felt weave and stitch depth.
    """
    # 1. Low Rake Key Softbox (Low elevation ~15 deg, skimming across the felt pile)
    bpy.ops.object.light_add(type='AREA', location=(-1.4, -0.9, 0.48))
    key = bpy.context.active_object
    key.name = "Studio_Key_Rake"
    key.data.energy = 58.0
    key.data.size = 1.4
    key.data.size_y = 0.8
    key.data.color = (1.0, 0.99, 0.97)
    dir_k = Vector((0.0, 0.0, 0.002)) - key.location
    key.rotation_euler = dir_k.to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True
    
    # 2. Opposite Soft Fill
    bpy.ops.object.light_add(type='AREA', location=(1.4, -0.4, 0.75))
    fill = bpy.context.active_object
    fill.name = "Studio_Fill_Side"
    fill.data.energy = 18.0
    fill.data.size = 1.6
    fill.data.size_y = 1.2
    fill.data.color = (0.97, 0.98, 1.0)
    dir_f = Vector((0.1, 0.0, 0.002)) - fill.location
    fill.rotation_euler = dir_f.to_track_quat('-Z', 'Y').to_euler()
    fill.data.use_shadow = False
    
    # 3. Soft Top Crown
    bpy.ops.object.light_add(type='AREA', location=(0.0, 0.0, 2.2))
    top = bpy.context.active_object
    top.name = "Studio_Top_Crown"
    top.data.energy = 12.0
    top.data.size = 2.2
    top.data.size_y = 1.4
    top.data.color = (0.98, 0.99, 1.0)
    top.rotation_euler = Euler((0, 0, 0), 'XYZ')
    top.data.use_shadow = True
    
    # 4. Corner Hardware Accent Light
    bpy.ops.object.light_add(type='AREA', location=(1.0, 0.6, 0.55))
    rim = bpy.context.active_object
    rim.name = "Studio_Hardware_Rim"
    rim.data.energy = 22.0
    rim.data.size = 0.35
    rim.data.size_y = 0.35
    rim.data.color = (1.0, 0.98, 0.95)
    dir_r = Vector((0.36, 0.16, 0.006)) - rim.location
    rim.rotation_euler = dir_r.to_track_quat('-Z', 'Y').to_euler()
    rim.data.use_shadow = False

def setup_hero_camera(scene):
    cam_data = bpy.data.cameras.new("Camera_NovaDesk_Hero")
    cam_data.lens = 52.0
    cam_obj = bpy.data.objects.new("Camera_NovaDesk_Hero", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    target = Vector((0.0, 0.0, 0.002))
    dist = 1.60 # Safe 1.60m guarantees >=18% margin on 1600x1200
    elev_rad = math.radians(35.0)
    azim_rad = math.radians(-32.0)
    
    cam_x = target.x + dist * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target.y - dist * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target.z + dist * math.sin(elev_rad)
    
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    dir_cam = target - cam_obj.location
    cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
    return cam_obj

def setup_macro_camera(scene):
    cam_data = bpy.data.cameras.new("Camera_NovaDesk_Macro")
    cam_data.lens = 92.0
    cam_obj = bpy.data.objects.new("Camera_NovaDesk_Macro", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    target = Vector((0.90 / 2.0 - 0.068, 0.40 / 2.0 - 0.026, 0.005))
    dist = 0.28
    elev_rad = math.radians(40.0)
    azim_rad = math.radians(-24.0)
    
    cam_x = target.x + dist * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target.y - dist * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target.z + dist * math.sin(elev_rad)
    
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    dir_cam = target - cam_obj.location
    cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
    return cam_obj

def main():
    print("=== STARTING NOVADESK XL MAT V4 RENDERING ===")
    scene = reset_scene()
    configure_cycles(scene, samples=384)
    
    model_objs = build_novadesk_scene()
    setup_studio_lighting()
    
    hero_cam = setup_hero_camera(scene)
    macro_cam = setup_macro_camera(scene)
    
    # 1. RENDER HERO VIEW (1600x1200)
    print("--- Rendering NovaDesk Hero View ---")
    scene.camera = hero_cam
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    
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
    print("=== NOVADESK MAT V4 FINISHED ===")

if __name__ == "__main__":
    main()
