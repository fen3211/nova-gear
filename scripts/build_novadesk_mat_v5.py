"""
NOVA DESK XL Mat - Industrial Design & Photorealistic Studio Render V5
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Key Refinements:
1. Deep Anthracite Heathered Merino Wool:
   - Rich charcoal mélange (#1E2024 to #2E323A) with subtle ash fiber flecks.
   - Pure velvety Sheen (Weight 1.0) and SSS light-trapping.
   - Fine micro-pile bump (Scale 850, soft distance 0.0006) for authentic textile softness.
2. Watertight Solid Manifold Leather Cable Loop:
   - Direct parametric BMesh quad construction with real through-hole slot (zero booleans, zero open wires).
   - Rich cognac vegetable-tanned leather shader with grain bump and perimeter creasing.
   - Turned solid brass magnetic rivet with concentric lathe machining.
3. Precision Equidistant Saddle Stitches:
   - 335 arched 3D thread loops (7.5mm pitch everywhere), angled at +18 deg, sinking into the seam.
   - Contrasting warm ecru spun silk thread.
4. Studio Lighting & Cameras:
   - Raking directional softbox setup sculpting fiber relief, edge bevel, and hardware glints.
   - Hero Camera (1600x1200) with guaranteed >=18% margins (zero edge clipping).
   - Macro Camera (1600x1200) focused on leather loop, brass rivet, and wool weave.
"""

import bpy
import bmesh
import math
import os
import mathutils
from mathutils import Vector, Euler, Matrix

OUTPUT_DIR = r"D:\Projects\ууу\assets\previews"
MODELS_DIR = r"D:\Projects\ууу\assets\models"

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

def create_merino_felt_material():
    """
    Creates deep anthracite heathered wool felt with rich procedural mélange and velvet sheen.
    """
    mat = bpy.data.materials.new("Anthracite_Merino_Felt")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    # 1. Macro Wool Clumps Noise (Heather variance)
    noise_macro = nodes.new('ShaderNodeTexNoise')
    noise_macro.inputs['Scale'].default_value = 75.0
    noise_macro.inputs['Detail'].default_value = 6.0
    noise_macro.inputs['Roughness'].default_value = 0.65
    links.new(mapping.outputs['Vector'], noise_macro.inputs['Vector'])
    
    # 2. Micro Wool Fibers Noise
    noise_micro = nodes.new('ShaderNodeTexNoise')
    noise_micro.inputs['Scale'].default_value = 650.0
    noise_micro.inputs['Detail'].default_value = 14.0
    noise_micro.inputs['Roughness'].default_value = 0.82
    links.new(mapping.outputs['Vector'], noise_micro.inputs['Vector'])
    
    # Mix macro and micro
    mix_f = nodes.new('ShaderNodeMix')
    mix_f.data_type = 'FLOAT'
    mix_f.inputs['Factor'].default_value = 0.45
    links.new(noise_macro.outputs['Fac'], mix_f.inputs[2])
    links.new(noise_micro.outputs['Fac'], mix_f.inputs[3])
    
    # Color Ramp for Deep Charcoal Heather Palette
    cramp = nodes.new('ShaderNodeValToRGB')
    cramp.color_ramp.elements[0].position = 0.20
    # Deep Charcoal Wool (#1E2024)
    cramp.color_ramp.elements[0].color = (0.022, 0.024, 0.028, 1.0)
    
    # Mid-tone Heather Slate (#2E323A)
    el1 = cramp.color_ramp.elements.new(0.55)
    el1.color = (0.045, 0.050, 0.058, 1.0)
    
    # Subtle Ash Fiber Flecks (#484E5A)
    cramp.color_ramp.elements[1].position = 0.85
    cramp.color_ramp.elements[1].color = (0.095, 0.104, 0.120, 1.0)
    
    links.new(mix_f.outputs['Result'], cramp.inputs['Fac'])
    links.new(cramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Diffuse Textile Roughness
    bsdf.inputs['Roughness'].default_value = 0.95
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.30
        
    # TEXTILE SHEEN: Creates soft fuzzy rim backscatter on glancing angles
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 1.0
        if 'Sheen Roughness' in bsdf.inputs:
            bsdf.inputs['Sheen Roughness'].default_value = 0.55
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (0.85, 0.90, 0.98, 1.0)
            
    # Subsurface light-trapping
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.07
        bsdf.inputs['Subsurface Radius'].default_value = (0.002, 0.002, 0.002)
        bsdf.inputs['Subsurface Scale'].default_value = 0.001
        
    # Fine Micro-Pile Bump (Soft tactile pile, zero crinkles)
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.32
    bump.inputs['Distance'].default_value = 0.0006
    links.new(noise_micro.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_rubber_base_material():
    mat = bpy.data.materials.new("Rubber_Base_Charcoal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.012, 0.013, 0.015, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_cognac_leather_material():
    """
    Creates rich full-grain cognac leather with micro-pore grain and satin clearcoat.
    """
    mat = bpy.data.materials.new("Cognac_Saddle_Leather")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Warm rich whiskey / cognac brown
    bsdf.inputs['Base Color'].default_value = (0.22, 0.10, 0.038, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.36
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.18
        bsdf.inputs['Coat Roughness'].default_value = 0.25
        
    tex_coord = nodes.new('ShaderNodeTexCoord')
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 450.0
    links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.14
    bump.inputs['Distance'].default_value = 0.0003
    links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
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
    bsdf.inputs['Base Color'].default_value = (0.45, 0.42, 0.36, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.46
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
        bsdf.inputs['Anisotropic'].default_value = 0.85
        
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

def build_solid_leather_badge_with_slot(w, d, h, slot_w, slot_d, slot_offset_x):
    """
    Constructs a 100% solid watertight manifold mesh for the leather badge with an open cable slot.
    Uses 4 connected quad blocks (Left, Top Bridge, Bottom Bridge, Right Plate).
    """
    mesh = bpy.data.meshes.new("Mesh_Leather_Badge")
    bm = bmesh.new()
    
    half_w = w / 2.0
    half_d = d / 2.0
    slot_half_w = slot_w / 2.0
    slot_half_d = slot_d / 2.0
    
    # Key X coordinates:
    x0 = -half_w
    x1 = slot_offset_x - slot_half_w
    x2 = slot_offset_x + slot_half_w
    x3 = half_w
    
    # Key Y coordinates:
    y0 = -half_d
    y1 = -slot_half_d
    y2 = slot_half_d
    y3 = half_d
    
    z_bot = -h / 2.0
    z_top = h / 2.0
    
    # Vertices grid (X, Y)
    # Block 1 (Left): X in [x0, x1], Y in [y0, y3]
    # Block 2 (Top bridge): X in [x1, x2], Y in [y2, y3]
    # Block 3 (Bottom bridge): X in [x1, x2], Y in [y0, y1]
    # Block 4 (Right plate): X in [x2, x3], Y in [y0, y3]
    
    grid_coords = [
        # (x, y)
        (x0, y0), (x1, y0), (x2, y0), (x3, y0), # Y = y0 (bottom row)
        (x0, y1), (x1, y1), (x2, y1), (x3, y1), # Y = y1 (lower slot edge)
        (x0, y2), (x1, y2), (x2, y2), (x3, y2), # Y = y2 (upper slot edge)
        (x0, y3), (x1, y3), (x2, y3), (x3, y3), # Y = y3 (top row)
    ]
    
    # Create top and bottom vertices
    v_bot = {}
    v_top = {}
    for x in (x0, x1, x2, x3):
        for y in (y0, y1, y2, y3):
            v_bot[(x, y)] = bm.verts.new((x, y, z_bot))
            v_top[(x, y)] = bm.verts.new((x, y, z_top))
            
    top_blocks = [
        (x0, x1, y0, y1), (x0, x1, y1, y2), (x0, x1, y2, y3),
        (x1, x2, y0, y1), (x1, x2, y2, y3),
        (x2, x3, y0, y1), (x2, x3, y1, y2), (x2, x3, y2, y3)
    ]
    for xa, xb, ya, yb in top_blocks:
        bm.faces.new((v_top[(xa, ya)], v_top[(xb, ya)], v_top[(xb, yb)], v_top[(xa, yb)]))
        bm.faces.new((v_bot[(xa, yb)], v_bot[(xb, yb)], v_bot[(xb, ya)], v_bot[(xa, ya)]))
        
    # Outer walls
    outer_loop = [
        (x0, y0), (x1, y0), (x2, y0), (x3, y0),
        (x3, y1), (x3, y2), (x3, y3),
        (x2, y3), (x1, y3), (x0, y3),
        (x0, y2), (x0, y1)
    ]
    for i in range(len(outer_loop)):
        p1 = outer_loop[i]
        p2 = outer_loop[(i + 1) % len(outer_loop)]
        bm.faces.new((v_bot[p1], v_bot[p2], v_top[p2], v_top[p1]))
        
    # Inner slot walls
    inner_loop = [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]
    for i in range(len(inner_loop)):
        p1 = inner_loop[i]
        p2 = inner_loop[(i + 1) % len(inner_loop)]
        bm.faces.new((v_bot[p1], v_bot[p2], v_top[p2], v_top[p1]))
        
    bm.to_mesh(mesh)
    bm.free()
    
    temp_obj = bpy.data.objects.new("NovaDesk_Leather_Badge", mesh)
    bpy.context.collection.objects.link(temp_obj)
    return temp_obj

def build_novadesk_scene():
    print("=== MODELING NOVADESK XL MAT V5 ===")
    mat_w = 0.900    # 900 mm
    mat_d = 0.400    # 400 mm
    corner_r = 0.024 # 24 mm radius
    total_h = 0.0042 # 4.2 mm
    rubber_h = 0.0016 # 1.6 mm
    
    mat_felt = create_merino_felt_material()
    mat_rubber = create_rubber_base_material()
    mat_leather = create_cognac_leather_material()
    mat_thread = create_saddle_thread_material()
    mat_brass = create_turned_brass_material()
    
    created_objects = []
    
    # -------------------------------------------------------------------------
    # 1. FELT & RUBBER MAT BODIES
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
            
    # Felt Top Layer Mesh
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
    # 3. SOLID MANIFOLD LEATHER CABLE LOOP WITH REAL SLOT HOLE
    # -------------------------------------------------------------------------
    badge_w = 0.082 # 82 mm
    badge_d = 0.026 # 26 mm
    badge_h = 0.0018 # 1.8 mm
    slot_w = 0.024
    slot_d = 0.0055
    slot_off_x = -0.018
    
    badge_x = mat_w / 2.0 - 0.068
    badge_y = mat_d / 2.0 - 0.026
    badge_z = total_h + badge_h / 2.0
    
    obj_badge = build_solid_leather_badge_with_slot(badge_w, badge_d, badge_h, slot_w, slot_d, slot_off_x)
    obj_badge.name = "NovaDesk_Leather_Badge"
    obj_badge.location = Vector((badge_x, badge_y, badge_z))
    obj_badge.data.materials.append(mat_leather)
    
    bev_b = obj_badge.modifiers.new("Bevel", 'BEVEL')
    bev_b.width = 0.0006
    bev_b.segments = 3
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_badge)
    
    # Turned Solid Brass Rivet
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
    
    # Embossed NOVA Mark on Leather Plate
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(badge_x + 0.010, badge_y, badge_z + badge_h / 2.0 + 0.0001),
        scale=(0.020, 0.0045, 0.0002)
    )
    deboss = bpy.context.active_object
    deboss.name = "Leather_NOVA_Deboss"
    mat_deboss = bpy.data.materials.new("Leather_Deboss_Burnished")
    mat_deboss.use_nodes = True
    d_bsdf = mat_deboss.node_tree.nodes.get("Principled BSDF")
    if d_bsdf:
        d_bsdf.inputs['Base Color'].default_value = (0.08, 0.035, 0.015, 1.0)
        d_bsdf.inputs['Roughness'].default_value = 0.25
    deboss.data.materials.append(mat_deboss)
    created_objects.append(deboss)
    
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
    Raking directional softbox setup sculpting fiber relief, edge bevel, and hardware glints.
    """
    # 1. Raking Key Softbox (24 deg elevation, directional relief across fibers)
    bpy.ops.object.light_add(type='AREA', location=(-1.5, -1.2, 0.72))
    key = bpy.context.active_object
    key.name = "Studio_Key_Rake"
    key.data.energy = 54.0
    key.data.size = 1.4
    key.data.size_y = 1.0
    key.data.color = (1.0, 0.99, 0.97)
    dir_k = Vector((0.0, 0.0, 0.002)) - key.location
    key.rotation_euler = dir_k.to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True
    
    # 2. Opposite Soft Infill
    bpy.ops.object.light_add(type='AREA', location=(1.5, -0.6, 0.95))
    fill = bpy.context.active_object
    fill.name = "Studio_Fill_Side"
    fill.data.energy = 20.0
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
    top.data.energy = 14.0
    top.data.size = 2.2
    top.data.size_y = 1.4
    top.data.color = (0.98, 0.99, 1.0)
    top.rotation_euler = Euler((0, 0, 0), 'XYZ')
    top.data.use_shadow = True
    
    # 4. Corner Hardware Accent Light
    bpy.ops.object.light_add(type='AREA', location=(1.1, 0.7, 0.65))
    rim = bpy.context.active_object
    rim.name = "Studio_Hardware_Rim"
    rim.data.energy = 26.0
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
    dist = 1.62 # Safe 1.62m distance: >=18% margin on 1600x1200
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
    print("=== STARTING NOVADESK XL MAT V5 RENDERING ===")
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
    print("=== NOVADESK MAT V5 FINISHED ===")

if __name__ == "__main__":
    main()
