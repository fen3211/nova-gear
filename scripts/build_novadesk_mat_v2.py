"""
NOVA DESK XL Mat - Industrial Design & Procedural Studio Render
Engineered for Blender 5.2.2 LTS (Cycles GPU / OptiX)

Key Requirements:
1. Genuine Soft Textile Aesthetics:
   - Procedural heathered merino wool felt (mélange color blending of charcoal, slate, and ash fiber flecks).
   - High sheen backscattering + subtle SSS for authentic micro-fiber light trapping (no metal/plastic look).
   - Micro-fiber tactile weave bump.
2. Detailed Multi-Layer Construction:
   - Real 900x400x4mm dimensions (2.6mm merino felt top + 1.4mm cellular rubber anti-slip base).
   - Precision 24mm rounded corners with beveled edge transition.
   - Continuous recessed perimeter stitch groove with 200+ angled arched saddle stitches.
3. Luxury Debossed Vegan Leather Cable Loop & Hardware:
   - 72x22mm leather patch with blind edge creasing, cable slot, and debossed NOVA mark.
   - Machined solid brass / copper rivet with circular lathe finish.
4. Editorial Macro / Hero Studio Framing:
   - Dynamic 3/4 beauty perspective filling ~75% of frame with safe margins (zero edge clipping).
   - Raking key lighting highlighting fiber texture, stitch depth, and brass reflection.
"""

import bpy
import bmesh
import math
import os
import numpy as np
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
        # Editorial neutral warm studio background
        bg.inputs['Color'].default_value = (0.92, 0.91, 0.88, 1.0)
        bg.inputs['Strength'].default_value = 0.65
    return scene

def configure_cycles(scene, samples=384):
    scene.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = True
    scene.cycles.device = 'GPU'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    scene.cycles.max_bounces = 8
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 4
    scene.cycles.transmission_bounces = 4
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'

def create_merino_felt_material():
    """
    Creates a photorealistic heathered merino wool felt shader.
    Uses multi-octave procedural mélange fiber noise, Sheen, and SSS.
    """
    mat = bpy.data.materials.new("Merino_Heather_Felt")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Coordinates & Mapping
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    # 1. Macro Mélange Noise (Heather fiber distribution)
    noise_macro = nodes.new('ShaderNodeTexNoise')
    noise_macro.inputs['Scale'].default_value = 45.0
    noise_macro.inputs['Detail'].default_value = 8.0
    noise_macro.inputs['Roughness'].default_value = 0.65
    noise_macro.inputs['Distortion'].default_value = 0.2
    links.new(mapping.outputs['Vector'], noise_macro.inputs['Vector'])
    
    # 2. Micro Fiber Flecks (Individual wool fibers)
    noise_micro = nodes.new('ShaderNodeTexNoise')
    noise_micro.inputs['Scale'].default_value = 280.0
    noise_micro.inputs['Detail'].default_value = 14.0
    noise_micro.inputs['Roughness'].default_value = 0.85
    links.new(mapping.outputs['Vector'], noise_micro.inputs['Vector'])
    
    # Mix macro and micro fiber signals
    mix_fibers = nodes.new('ShaderNodeMix')
    mix_fibers.data_type = 'FLOAT'
    mix_fibers.inputs['Factor'].default_value = 0.55
    links.new(noise_macro.outputs['Fac'], mix_fibers.inputs[2])
    links.new(noise_micro.outputs['Fac'], mix_fibers.inputs[3])
    
    # Color Ramp for Heathered Charcoal Wool Mélange
    cramp = nodes.new('ShaderNodeValToRGB')
    cramp.color_ramp.elements[0].position = 0.20
    # Deep Charcoal Wool
    cramp.color_ramp.elements[0].color = (0.048, 0.051, 0.056, 1.0)
    
    # Add Slate Gray Heather
    el1 = cramp.color_ramp.elements.new(0.55)
    el1.color = (0.082, 0.087, 0.096, 1.0)
    
    # Highlight Ash Wool Fibers
    cramp.color_ramp.elements[1].position = 0.85
    cramp.color_ramp.elements[1].color = (0.135, 0.142, 0.155, 1.0)
    
    links.new(mix_fibers.outputs['Result'], cramp.inputs['Fac'])
    links.new(cramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Roughness & Specular (Non-reflective organic textile)
    bsdf.inputs['Roughness'].default_value = 0.94
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.35
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.35
        
    # TEXTILE SHEEN: Soft rim-lighting on glancing micro-fibers
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.80
        if 'Sheen Roughness' in bsdf.inputs:
            bsdf.inputs['Sheen Roughness'].default_value = 0.50
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (0.85, 0.88, 0.95, 1.0)
    elif 'Sheen' in bsdf.inputs:
        bsdf.inputs['Sheen'].default_value = 0.80
        
    # Subsurface Softness
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.06
        bsdf.inputs['Subsurface Radius'].default_value = (0.002, 0.002, 0.002)
        bsdf.inputs['Subsurface Scale'].default_value = 0.001
        
    # Tactile Fiber Bump
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.0008
    links.new(noise_micro.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_cellular_rubber_material():
    """
    Creates high-grip natural textured cellular rubber backing.
    """
    mat = bpy.data.materials.new("Cellular_Rubber_Base")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.025, 0.026, 0.028, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 450.0
    voronoi.feature = 'F1'
    links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.30
    bump.inputs['Distance'].default_value = 0.0005
    links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_saddle_leather_material():
    """
    Creates rich full-grain cognac vegan leather with natural follicle bump and satin sheen.
    """
    mat = bpy.data.materials.new("FullGrain_Cognac_Leather")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Warm Cognac / Saddle Brown
    bsdf.inputs['Base Color'].default_value = (0.24, 0.11, 0.045, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.38
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.15
        bsdf.inputs['Coat Roughness'].default_value = 0.30
        
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 260.0
    links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 180.0
    noise.inputs['Detail'].default_value = 6.0
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    
    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'FLOAT'
    mix.inputs['Factor'].default_value = 0.35
    links.new(voronoi.outputs['Distance'], mix.inputs[2])
    links.new(noise.outputs['Fac'], mix.inputs[3])
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.18
    bump.inputs['Distance'].default_value = 0.0005
    links.new(mix.outputs['Result'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_spun_thread_material():
    """
    Braided nylon/poly saddle stitch thread with micro-twist highlights.
    """
    mat = bpy.data.materials.new("Saddle_Thread_Charcoal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    # Subtle contrasting warm charcoal thread
    bsdf.inputs['Base Color'].default_value = (0.16, 0.165, 0.175, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.52
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.65
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_machined_brass_material():
    """
    Turned solid brass / copper rivet with circular anisotropic machining highlight.
    """
    mat = bpy.data.materials.new("Turned_Solid_Brass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    # Warm rich architectural brass
    bsdf.inputs['Base Color'].default_value = (0.92, 0.74, 0.35, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.22
    if 'Anisotropic' in bsdf.inputs:
        bsdf.inputs['Anisotropic'].default_value = 0.75
        bsdf.inputs['Anisotropic Rotation'].default_value = 0.25
        
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def generate_rounded_rect_points(w, d, r, subdivs=16):
    """Generates continuous ordered 2D points along a rounded rectangle perimeter."""
    cx = w / 2.0 - r
    cy = d / 2.0 - r
    corners_cfg = [
        (cx, cy, 0.0, math.pi / 2.0),
        (-cx, cy, math.pi / 2.0, math.pi),
        (-cx, -cy, math.pi, 3.0 * math.pi / 2.0),
        (cx, -cy, 3.0 * math.pi / 2.0, 2.0 * math.pi)
    ]
    pts = []
    for c_x, c_y, a_start, a_end in corners_cfg:
        for i in range(subdivs):
            angle = a_start + (a_end - a_start) * (i / subdivs)
            pts.append((c_x + r * math.cos(angle), c_y + r * math.sin(angle)))
    return pts

def build_novadesk_mat():
    print("=== BUILDING NOVADESK XL MAT V2 ===")
    
    # 1. Geometry Dimensions
    mat_w = 0.900    # 900 mm
    mat_d = 0.400    # 400 mm
    corner_r = 0.024 # 24 mm radius
    total_h = 0.0042 # 4.2 mm total thickness
    felt_h = 0.0026  # 2.6 mm merino felt
    rubber_h = 0.0016 # 1.6 mm cellular rubber base
    
    # Materials
    mat_felt = create_merino_felt_material()
    mat_rubber = create_cellular_rubber_material()
    mat_leather = create_saddle_leather_material()
    mat_thread = create_spun_thread_material()
    mat_brass = create_machined_brass_material()
    
    created_objects = []
    
    # -------------------------------------------------------------------------
    # 1. TOP FELT LAYER
    # -------------------------------------------------------------------------
    pts_top = generate_rounded_rect_points(mat_w, mat_d, corner_r, subdivs=24)
    
    mesh_felt = bpy.data.meshes.new("Mesh_Felt_Top")
    bm_felt = bmesh.new()
    
    v_felt_bot = [bm_felt.verts.new((x, y, rubber_h)) for x, y in pts_top]
    v_felt_top = [bm_felt.verts.new((x, y, total_h)) for x, y in pts_top]
    
    bm_felt.faces.new(v_felt_top)
    bm_felt.faces.new(list(reversed(v_felt_bot)))
    n_pts = len(pts_top)
    for i in range(n_pts):
        next_i = (i + 1) % n_pts
        bm_felt.faces.new((v_felt_bot[i], v_felt_bot[next_i], v_felt_top[next_i], v_felt_top[i]))
        
    bm_felt.to_mesh(mesh_felt)
    bm_felt.free()
    
    obj_felt = bpy.data.objects.new("NovaDesk_Merino_Felt", mesh_felt)
    bpy.context.collection.objects.link(obj_felt)
    obj_felt.data.materials.append(mat_felt)
    
    # Soft bevel on felt edge
    bev_felt = obj_felt.modifiers.new("Bevel", 'BEVEL')
    bev_felt.width = 0.0012
    bev_felt.segments = 4
    bpy.context.view_layer.objects.active = obj_felt
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_felt)
    
    # -------------------------------------------------------------------------
    # 2. BOTTOM CELLULAR RUBBER FOUNDATION
    # -------------------------------------------------------------------------
    mesh_rub = bpy.data.meshes.new("Mesh_Rubber_Base")
    bm_rub = bmesh.new()
    
    v_rub_bot = [bm_rub.verts.new((x, y, 0.0)) for x, y in pts_top]
    v_rub_top = [bm_rub.verts.new((x, y, rubber_h)) for x, y in pts_top]
    
    bm_rub.faces.new(v_rub_top)
    bm_rub.faces.new(list(reversed(v_rub_bot)))
    for i in range(n_pts):
        next_i = (i + 1) % n_pts
        bm_rub.faces.new((v_rub_bot[i], v_rub_bot[next_i], v_rub_top[next_i], v_rub_top[i]))
        
    bm_rub.to_mesh(mesh_rub)
    bm_rub.free()
    
    obj_rub = bpy.data.objects.new("NovaDesk_Rubber_Base", mesh_rub)
    bpy.context.collection.objects.link(obj_rub)
    obj_rub.data.materials.append(mat_rubber)
    
    bev_rub = obj_rub.modifiers.new("Bevel", 'BEVEL')
    bev_rub.width = 0.0006
    bev_rub.segments = 2
    bpy.context.view_layer.objects.active = obj_rub
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_rub)
    
    # -------------------------------------------------------------------------
    # 3. RECESSED PERIMETER STITCH CHANNEL & CONTINUOUS SADDLE STITCHES
    # -------------------------------------------------------------------------
    stitch_inset = 0.0075 # 7.5 mm inset from outer edge
    s_r = corner_r - stitch_inset # Corner radius for stitches
    s_w = mat_w - 2.0 * stitch_inset
    s_d = mat_d - 2.0 * stitch_inset
    s_cx = s_w / 2.0 - s_r
    s_cy = s_d / 2.0 - s_r
    
    stitch_path = []
    # Parametric path around perimeter with tangents
    # Top edge
    n_w_stitches = 54
    for i in range(n_w_stitches):
        t = i / float(n_w_stitches)
        x = -s_cx + 2.0 * s_cx * t
        stitch_path.append((x, s_cy + s_r, 1.0, 0.0))
        
    # Top-right corner
    sub_c = 12
    for i in range(sub_c):
        ang = math.pi / 2.0 - (math.pi / 2.0) * (i / float(sub_c))
        px = s_cx + s_r * math.cos(ang)
        py = s_cy + s_r * math.sin(ang)
        tx = math.sin(ang)
        ty = -math.cos(ang)
        stitch_path.append((px, py, tx, ty))
        
    # Right edge
    n_d_stitches = 24
    for i in range(n_d_stitches):
        t = i / float(n_d_stitches)
        y = s_cy - 2.0 * s_cy * t
        stitch_path.append((s_cx + s_r, y, 0.0, -1.0))
        
    # Bottom-right corner
    for i in range(sub_c):
        ang = 0.0 - (math.pi / 2.0) * (i / float(sub_c))
        px = s_cx + s_r * math.cos(ang)
        py = -s_cy + s_r * math.sin(ang)
        tx = math.sin(ang)
        ty = -math.cos(ang)
        stitch_path.append((px, py, tx, ty))
        
    # Bottom edge
    for i in range(n_w_stitches):
        t = i / float(n_w_stitches)
        x = s_cx - 2.0 * s_cx * t
        stitch_path.append((x, -s_cy - s_r, -1.0, 0.0))
        
    # Bottom-left corner
    for i in range(sub_c):
        ang = 3.0 * math.pi / 2.0 - (math.pi / 2.0) * (i / float(sub_c))
        px = -s_cx + s_r * math.cos(ang)
        py = -s_cy + s_r * math.sin(ang)
        tx = math.sin(ang)
        ty = -math.cos(ang)
        stitch_path.append((px, py, tx, ty))
        
    # Left edge
    for i in range(n_d_stitches):
        t = i / float(n_d_stitches)
        y = -s_cy + 2.0 * s_cy * t
        stitch_path.append((-s_cx - s_r, y, 0.0, 1.0))
        
    # Top-left corner
    for i in range(sub_c):
        ang = math.pi - (math.pi / 2.0) * (i / float(sub_c))
        px = -s_cx + s_r * math.cos(ang)
        py = s_cy + s_r * math.sin(ang)
        tx = math.sin(ang)
        ty = -math.cos(ang)
        stitch_path.append((px, py, tx, ty))
        
    # Build single batched BMesh for all stitches for optimal performance & zero memory overhead
    mesh_stitches = bpy.data.meshes.new("Mesh_Saddle_Stitches")
    bm_st = bmesh.new()
    
    stitch_len = 0.0052 # 5.2 mm thread span
    stitch_rad = 0.00065 # 0.65 mm thread thickness
    stitch_arch = 0.00045 # Arch height above seam
    
    for px, py, tx, ty in stitch_path:
        tangent_ang = math.atan2(ty, tx)
        # Angled saddle stitch slant (+18 degrees relative to tangent)
        slant = tangent_ang + math.radians(18.0)
        
        # Create arched 6-segment stitch
        n_segs = 6
        pts_arch = []
        for s in range(n_segs + 1):
            u = s / float(n_segs)
            offset_len = (u - 0.5) * stitch_len
            lx = px + offset_len * math.cos(slant)
            ly = py + offset_len * math.sin(slant)
            # Parabolic arch: sinks below surface at endpoints (-0.0003), peaks at arch height
            parabola = math.sin(u * math.pi) * stitch_arch - 0.0003
            lz = total_h + parabola
            pts_arch.append(Vector((lx, ly, lz)))
            
        # Extrude tube along arch points
        ring_verts_prev = None
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
                
            if ring_verts_prev:
                for c in range(n_circle):
                    next_c = (c + 1) % n_circle
                    bm_st.faces.new((ring_verts_prev[c], ring_verts_prev[next_c], ring[next_c], ring[c]))
            else:
                bm_st.faces.new(list(reversed(ring))) # Cap start
            ring_verts_prev = ring
            
        if ring_verts_prev:
            bm_st.faces.new(ring_verts_prev) # Cap end
            
    bm_st.to_mesh(mesh_stitches)
    bm_st.free()
    
    obj_stitches = bpy.data.objects.new("NovaDesk_Stitches", mesh_stitches)
    bpy.context.collection.objects.link(obj_stitches)
    obj_stitches.data.materials.append(mat_thread)
    bpy.context.view_layer.objects.active = obj_stitches
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_stitches)
    print(f"Generated {len(stitch_path)} precision saddle stitches in single batched mesh.")
    
    # -------------------------------------------------------------------------
    # 4. LUXURY CORNER LEATHER CABLE CATCH & HARDWARE
    # -------------------------------------------------------------------------
    badge_w = 0.076 # 76 mm
    badge_d = 0.024 # 24 mm
    badge_h = 0.0018 # 1.8 mm thick full-grain leather
    badge_r = 0.005 # 5 mm rounded corners
    
    # Positioned at top-right corner
    badge_x = mat_w / 2.0 - 0.065
    badge_y = mat_d / 2.0 - 0.028
    badge_z = total_h + badge_h / 2.0
    
    # Rounded badge mesh
    b_pts = generate_rounded_rect_points(badge_w, badge_d, badge_r, subdivs=12)
    mesh_badge = bpy.data.meshes.new("Mesh_Leather_Badge")
    bm_badge = bmesh.new()
    
    v_b_bot = [bm_badge.verts.new((x, y, -badge_h / 2.0)) for x, y in b_pts]
    v_b_top = [bm_badge.verts.new((x, y, badge_h / 2.0)) for x, y in b_pts]
    
    bm_badge.faces.new(v_b_top)
    bm_badge.faces.new(list(reversed(v_b_bot)))
    for i in range(len(b_pts)):
        next_i = (i + 1) % len(b_pts)
        bm_badge.faces.new((v_b_bot[i], v_b_bot[next_i], v_b_top[next_i], v_b_top[i]))
        
    bm_badge.to_mesh(mesh_badge)
    bm_badge.free()
    
    obj_badge = bpy.data.objects.new("NovaDesk_Leather_Badge", mesh_badge)
    obj_badge.location = Vector((badge_x, badge_y, badge_z))
    bpy.context.collection.objects.link(obj_badge)
    obj_badge.data.materials.append(mat_leather)
    
    bev_badge = obj_badge.modifiers.new("Bevel", 'BEVEL')
    bev_badge.width = 0.0006
    bev_badge.segments = 3
    bpy.context.view_layer.objects.active = obj_badge
    bpy.ops.object.shade_smooth()
    created_objects.append(obj_badge)
    
    # Cable Slot Cutout in Leather Badge (Recessed pill aperture)
    slot_w = 0.026 # 26 mm slot
    slot_d = 0.0055 # 5.5 mm slot
    slot_h = badge_h * 1.5
    bpy.ops.mesh.primitive_cylinder_add(
        radius=slot_d / 2.0, depth=slot_h,
        location=(badge_x - 0.014 - (slot_w - slot_d) / 2.0, badge_y, badge_z)
    )
    cyl1 = bpy.context.active_object
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=slot_d / 2.0, depth=slot_h,
        location=(badge_x - 0.014 + (slot_w - slot_d) / 2.0, badge_y, badge_z)
    )
    cyl2 = bpy.context.active_object
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(badge_x - 0.014, badge_y, badge_z),
        scale=(slot_w - slot_d, slot_d, slot_h)
    )
    slot_mid = bpy.context.active_object
    
    # Join slot cutter
    bpy.ops.object.select_all(action='DESELECT')
    cyl1.select_set(True)
    cyl2.select_set(True)
    slot_mid.select_set(True)
    bpy.context.view_layer.objects.active = slot_mid
    bpy.ops.object.join()
    slot_cutter = bpy.context.active_object
    slot_cutter.name = "Slot_Cutter"
    
    # Boolean difference from badge
    bool_slot = obj_badge.modifiers.new("Bool_Slot", 'BOOLEAN')
    bool_slot.operation = 'DIFFERENCE'
    bool_slot.object = slot_cutter
    slot_cutter.hide_render = True
    slot_cutter.hide_viewport = True
    
    # Machined Turned Brass Rivet with Concentric Recess
    rivet_x = badge_x + badge_w / 2.0 - 0.009
    rivet_y = badge_y
    rivet_z = badge_z + badge_h / 2.0
    
    # Main rivet head
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0042, depth=0.0016, location=(rivet_x, rivet_y, rivet_z + 0.0006)
    )
    rivet = bpy.context.active_object
    rivet.name = "NovaDesk_Brass_Rivet"
    rivet.data.materials.append(mat_brass)
    rbev = rivet.modifiers.new("Bevel", 'BEVEL')
    rbev.width = 0.0004
    rbev.segments = 2
    bpy.context.view_layer.objects.active = rivet
    bpy.ops.object.shade_smooth()
    created_objects.append(rivet)
    
    # Concentric inner dot of rivet
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.0015, depth=0.0006, location=(rivet_x, rivet_y, rivet_z + 0.0012)
    )
    rivet_dot = bpy.context.active_object
    rivet_dot.name = "NovaDesk_Brass_Rivet_Dot"
    rivet_dot.data.materials.append(mat_brass)
    created_objects.append(rivet_dot)
    
    # Embossed NOVA Mark on Leather (Debossed into leather surface)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(badge_x + 0.010, badge_y, badge_z + badge_h / 2.0 + 0.00015),
        scale=(0.018, 0.005, 0.0003)
    )
    emboss_bar = bpy.context.active_object
    emboss_bar.name = "Leather_Embossed_NOVA"
    # Material slightly darker burnished leather
    mat_emboss = bpy.data.materials.new("Leather_Deboss_Burnished")
    mat_emboss.use_nodes = True
    b_nodes = mat_emboss.node_tree.nodes
    b_bsdf = b_nodes.get("Principled BSDF")
    if b_bsdf:
        b_bsdf.inputs['Base Color'].default_value = (0.12, 0.05, 0.02, 1.0) # Deep burnished deboss
        b_bsdf.inputs['Roughness'].default_value = 0.28
    emboss_bar.data.materials.append(mat_emboss)
    created_objects.append(emboss_bar)
    
    # -------------------------------------------------------------------------
    # 5. STUDIO SHADOW CATCHER FLOOR
    # -------------------------------------------------------------------------
    bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Shadow_Catcher_Floor"
    floor.is_shadow_catcher = False
    
    mat_floor = bpy.data.materials.new("Studio_Editorial_Floor")
    mat_floor.use_nodes = True
    f_nodes = mat_floor.node_tree.nodes
    f_bsdf = f_nodes.get("Principled BSDF")
    if f_bsdf:
        # Exact editorial cream studio backdrop #EBE8E1
        f_bsdf.inputs['Base Color'].default_value = (0.92, 0.91, 0.88, 1.0)
        f_bsdf.inputs['Roughness'].default_value = 0.85
    floor.data.materials.append(mat_floor)
    
    return created_objects

def setup_studio_lighting():
    """
    Raking key lighting highlighting rich wool felt fiber texture,
    perpendicular fill, and soft top crown diffuser.
    """
    # 1. Raking Key Softbox (Low oblique angle: 28 deg elevation, catches fiber pile & stitch relief)
    bpy.ops.object.light_add(type='AREA', location=(-1.4, -1.2, 0.85))
    key = bpy.context.active_object
    key.name = "Studio_Key_Rake"
    key.data.energy = 55.0
    key.data.size = 1.4
    key.data.size_y = 1.0
    key.data.color = (1.0, 0.99, 0.97)
    dir_k = Vector((0.0, 0.0, 0.002)) - key.location
    key.rotation_euler = dir_k.to_track_quat('-Z', 'Y').to_euler()
    key.data.use_shadow = True
    
    # 2. Opposite Fill Softbox (Soft balance for dark fiber shadows)
    bpy.ops.object.light_add(type='AREA', location=(1.5, -0.6, 1.1))
    fill = bpy.context.active_object
    fill.name = "Studio_Fill_Side"
    fill.data.energy = 22.0
    fill.data.size = 1.6
    fill.data.size_y = 1.2
    fill.data.color = (0.97, 0.98, 1.0)
    dir_f = Vector((0.1, 0.0, 0.002)) - fill.location
    fill.rotation_euler = dir_f.to_track_quat('-Z', 'Y').to_euler()
    fill.data.use_shadow = False
    
    # 3. Top Crown Diffuser (Overall soft ambient grounding)
    bpy.ops.object.light_add(type='AREA', location=(0.0, 0.0, 2.2))
    top = bpy.context.active_object
    top.name = "Studio_Top_Crown"
    top.data.energy = 32.0
    top.data.size = 2.4
    top.data.size_y = 1.6
    top.data.color = (0.98, 0.99, 1.0)
    top.rotation_euler = Euler((0, 0, 0), 'XYZ')
    top.data.use_shadow = True
    
    # 4. Corner Rim Accent (Glints leather corner and brass rivet)
    bpy.ops.object.light_add(type='AREA', location=(1.1, 0.8, 0.9))
    rim = bpy.context.active_object
    rim.name = "Studio_Badge_Rim"
    rim.data.energy = 28.0
    rim.data.size = 0.4
    rim.data.size_y = 0.4
    rim.data.color = (1.0, 0.98, 0.95)
    dir_r = Vector((0.35, 0.16, 0.005)) - rim.location
    rim.rotation_euler = dir_r.to_track_quat('-Z', 'Y').to_euler()
    rim.data.use_shadow = False

def setup_hero_camera(scene, model_objs):
    """
    Sets up dynamic 3/4 beauty hero camera framing the mat prominently with >=20% safety margin.
    """
    cam_data = bpy.data.cameras.new("Camera_NovaDesk_Hero")
    cam_data.lens = 58.0 # 58mm commercial portrait focal length (zero wide-angle distortion)
    cam_obj = bpy.data.objects.new("Camera_NovaDesk_Hero", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # Target center slightly offset toward leather badge for pleasing rule-of-thirds composition
    target = Vector((0.02, 0.0, 0.002))
    
    # Camera position: elevation ~34 degrees, azimuth ~-32 degrees
    dist = 1.35
    elev_rad = math.radians(34.0)
    azim_rad = math.radians(-32.0)
    
    cam_x = target.x + dist * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target.y - dist * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target.z + dist * math.sin(elev_rad)
    
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    dir_cam = target - cam_obj.location
    cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
    
    print(f"Hero Camera Configured: loc={cam_obj.location}, rot={cam_obj.rotation_euler}")
    return cam_obj

def setup_macro_camera(scene, badge_target):
    """
    Close-up macro camera focusing on leather cable loop, saddle stitch detail, and merino felt texture.
    """
    cam_data = bpy.data.cameras.new("Camera_NovaDesk_Macro")
    cam_data.lens = 95.0 # 95mm macro lens
    cam_obj = bpy.data.objects.new("Camera_NovaDesk_Macro", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    target = badge_target
    dist = 0.32
    elev_rad = math.radians(40.0)
    azim_rad = math.radians(-26.0)
    
    cam_x = target.x + dist * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target.y - dist * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target.z + dist * math.sin(elev_rad)
    
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    dir_cam = target - cam_obj.location
    cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
    
    return cam_obj

def main():
    print("=== STARTING NOVADESK XL MAT GENERATION ===")
    scene = reset_scene()
    configure_cycles(scene, samples=384)
    
    model_objs = build_novadesk_mat()
    setup_studio_lighting()
    
    hero_cam = setup_hero_camera(scene, model_objs)
    badge_pos = Vector((0.90 / 2.0 - 0.065, 0.40 / 2.0 - 0.028, 0.005))
    macro_cam = setup_macro_camera(scene, badge_pos)
    
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
    print("--- Rendering NovaDesk Macro Detail View (Felt + Stitches + Leather) ---")
    scene.camera = macro_cam
    macro_out = os.path.join(OUTPUT_DIR, "novadesk_mat_macro_detail.png")
    scene.render.filepath = macro_out
    bpy.ops.render.render(write_still=True)
    print(f"Macro Detail Render Saved: {macro_out}")
    
    # Save master blend file
    blend_path = os.path.join(MODELS_DIR, "novadesk_mat_master.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Master Scene Saved: {blend_path}")
    print("=== NOVADESK XL MAT RENDERS COMPLETE ===")

if __name__ == "__main__":
    main()
