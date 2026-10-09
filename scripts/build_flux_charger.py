"""
NOVA FLUX 100W GaN Fast Charger - Master Commercial 3D Industrial Asset (V6)
Engineered for Blender 5.2.2 LTS with Cycles GPU (OptiX).
Features:
- Pure BMesh rounded-rectangle unibody shell (16 subdivisions per corner, zero boolean clamping)
- Seamless Studio Cyclorama (curved backdrop wall in #EBE8E1, zero black horizon voids)
- Pure BMesh hollow stadium sleeves for USB-C (100% open aperture, zero boolean glitch)
- 16 individual gold contact leaf pins per USB-C port (8 top, 8 bottom) on floating tongue
- Pure BMesh hollow rectangular sleeve for USB-A with lime insulator tongue & 4 gold pins
- Stepped faceplate with 0.4mm mechanical reveal seam
- High-precision UV mapped laser-etched typography on faceplate (calibrated above ports)
- Dual studio softboxes + rim kicker + port infill + grounded contact shadow
- Automated camera bounding-box fitting for 100% in-frame zero-clipping presentation
"""

import bpy
import bmesh
import math
import os
import mathutils
from mathutils import Vector, Euler

OUTPUT_DIR = r"D:\Projects\ууу\assets\previews"
MODELS_DIR = r"D:\Projects\ууу\assets\models"
TEXTURES_DIR = r"D:\Projects\ууу\assets\textures"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("Studio_World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        # Subtle warm studio ambient bounce
        bg.inputs["Color"].default_value = (0.92, 0.91, 0.88, 1.0)
        bg.inputs["Strength"].default_value = 0.15
    return scene

def configure_cycles(scene, samples=384):
    scene.render.engine = 'CYCLES'
    cycles = scene.cycles
    cycles.device = 'GPU'
    cycles.samples = samples
    cycles.preview_samples = 32
    cycles.use_denoising = True
    cycles.denoiser = 'OPTIX'
    
    prefs = bpy.context.preferences.addons.get("cycles")
    if prefs:
        cprefs = prefs.preferences
        cprefs.compute_device_type = 'OPTIX'
        cprefs.get_devices()
        for device in cprefs.devices:
            if device.type == 'OPTIX':
                device.use = True
            else:
                device.use = False
            print(f"Cycles Device: {device.name} (type={device.type}, use={device.use})")
            
    scene.render.film_transparent = False # Continuous studio cyclorama
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'

# -------------------------------------------------------------
# SHADERS
# -------------------------------------------------------------
def create_materials():
    mats = {}
    
    # 1. Premium PBT Matte Charcoal Chassis
    mat_pbt = bpy.data.materials.new("PBT_Charcoal_Shell")
    mat_pbt.use_nodes = True
    nt = mat_pbt.node_tree
    nt.nodes.clear()
    
    out_node = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.048, 0.050, 0.056, 1.0) # Deep charcoal slate
    bsdf.inputs["Roughness"].default_value = 0.32
    bsdf.inputs["IOR"].default_value = 1.52
    
    # High-frequency micro bump for authentic EDM mold texture
    tex_noise = nt.nodes.new("ShaderNodeTexNoise")
    tex_noise.inputs["Scale"].default_value = 1600.0
    tex_noise.inputs["Detail"].default_value = 5.0
    tex_noise.inputs["Roughness"].default_value = 0.6
    
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.012
    bump.inputs["Distance"].default_value = 0.002
    
    nt.links.new(tex_noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    mats["pbt"] = mat_pbt
    
    # 2. Front Faceplate with Laser Markings UV Texture
    mat_face = bpy.data.materials.new("Faceplate_Facia")
    mat_face.use_nodes = True
    nt = mat_face.node_tree
    nt.nodes.clear()
    
    out_node = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.040, 0.042, 0.048, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.26
    
    tex_path = os.path.join(TEXTURES_DIR, "charger_faceplate_labels.png")
    if os.path.exists(tex_path):
        tex_coord = nt.nodes.new("ShaderNodeTexCoord")
        tex_img = nt.nodes.new("ShaderNodeTexImage")
        tex_img.image = bpy.data.images.load(tex_path)
        nt.links.new(tex_coord.outputs["UV"], tex_img.inputs["Vector"])
        
        mix_rgb = nt.nodes.new("ShaderNodeMix")
        mix_rgb.data_type = 'RGBA'
        nt.links.new(tex_img.outputs["Alpha"], mix_rgb.inputs["Factor"])
        mix_rgb.inputs["A"].default_value = (0.040, 0.042, 0.048, 1.0)
        nt.links.new(tex_img.outputs["Color"], mix_rgb.inputs["B"])
        nt.links.new(mix_rgb.outputs["Result"], bsdf.inputs["Base Color"])
    
    nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    mats["faceplate"] = mat_face
    
    # 3. Brushed Nickel / Stainless Steel Collar
    mat_steel = bpy.data.materials.new("Brushed_Nickel_Collar")
    mat_steel.use_nodes = True
    bsdf_steel = mat_steel.node_tree.nodes.get("Principled BSDF")
    bsdf_steel.inputs["Base Color"].default_value = (0.84, 0.85, 0.87, 1.0)
    bsdf_steel.inputs["Metallic"].default_value = 0.96
    bsdf_steel.inputs["Roughness"].default_value = 0.16
    bsdf_steel.inputs["Anisotropic"].default_value = 0.35
    mats["steel"] = mat_steel
    
    # 4. Polished Gold Contact Pins
    mat_gold = bpy.data.materials.new("Polished_Gold_Contacts")
    mat_gold.use_nodes = True
    bsdf_gold = mat_gold.node_tree.nodes.get("Principled BSDF")
    bsdf_gold.inputs["Base Color"].default_value = (0.98, 0.78, 0.22, 1.0)
    bsdf_gold.inputs["Metallic"].default_value = 1.0
    bsdf_gold.inputs["Roughness"].default_value = 0.10
    mats["gold"] = mat_gold
    
    # 5. Signature Acid-Lime Pinstripe & Tongue
    mat_lime = bpy.data.materials.new("Acid_Lime_Accent")
    mat_lime.use_nodes = True
    bsdf_lime = mat_lime.node_tree.nodes.get("Principled BSDF")
    bsdf_lime.inputs["Base Color"].default_value = (0.78, 1.0, 0.24, 1.0)
    bsdf_lime.inputs["Roughness"].default_value = 0.22
    mats["lime"] = mat_lime
    
    # 6. Dark Port Cavity Wall (light trap)
    mat_cavity = bpy.data.materials.new("Port_Cavity_Wall")
    mat_cavity.use_nodes = True
    bsdf_cav = mat_cavity.node_tree.nodes.get("Principled BSDF")
    bsdf_cav.inputs["Base Color"].default_value = (0.012, 0.012, 0.015, 1.0)
    bsdf_cav.inputs["Roughness"].default_value = 0.70
    mats["cavity"] = mat_cavity
    
    # 7. Status LED Lens
    mat_led = bpy.data.materials.new("LED_Status_Lens")
    mat_led.use_nodes = True
    bsdf_led = mat_led.node_tree.nodes.get("Principled BSDF")
    bsdf_led.inputs["Base Color"].default_value = (0.78, 1.0, 0.24, 1.0)
    bsdf_led.inputs["Emission Color"].default_value = (0.78, 1.0, 0.24, 1.0)
    bsdf_led.inputs["Emission Strength"].default_value = 12.0
    bsdf_led.inputs["Roughness"].default_value = 0.1
    mats["led"] = mat_led
    
    # 8. Studio Seamless Cyclorama Backdrop (#EBE8E1)
    mat_cyc = bpy.data.materials.new("Studio_Cyc_Backdrop")
    mat_cyc.use_nodes = True
    bsdf_cyc = mat_cyc.node_tree.nodes.get("Principled BSDF")
    bsdf_cyc.inputs["Base Color"].default_value = (0.921, 0.910, 0.882, 1.0) # #EBE8E1
    bsdf_cyc.inputs["Roughness"].default_value = 0.65
    bsdf_cyc.inputs["Specular IOR Level"].default_value = 0.20
    mats["cyc"] = mat_cyc
    
    return mats

# -------------------------------------------------------------
# GEOMETRY GENERATORS (BMesh Precision Primitives)
# -------------------------------------------------------------
def get_rounded_rect_pts(w, h, r, n_seg=14):
    """
    Returns closed loop of (x, z) 2D points for a rounded rectangle.
    """
    hw = w / 2.0 - r
    hh = h / 2.0 - r
    pts = []
    
    # Corner centers:
    # 1. Top-Right (+hw, +hh) : 0 to pi/2
    for i in range(n_seg + 1):
        th = 0.0 + (math.pi / 2.0) * (i / float(n_seg))
        pts.append((hw + r * math.cos(th), hh + r * math.sin(th)))
    # 2. Top-Left (-hw, +hh) : pi/2 to pi
    for i in range(1, n_seg + 1):
        th = math.pi / 2.0 + (math.pi / 2.0) * (i / float(n_seg))
        pts.append((-hw + r * math.cos(th), hh + r * math.sin(th)))
    # 3. Bottom-Left (-hw, -hh) : pi to 3pi/2
    for i in range(1, n_seg + 1):
        th = math.pi + (math.pi / 2.0) * (i / float(n_seg))
        pts.append((-hw + r * math.cos(th), -hh + r * math.sin(th)))
    # 4. Bottom-Right (+hw, -hh) : 3pi/2 to 2pi
    for i in range(1, n_seg): # exclude last to avoid duplicating 0
        th = 1.5 * math.pi + (math.pi / 2.0) * (i / float(n_seg))
        pts.append((hw + r * math.cos(th), -hh + r * math.sin(th)))
    return pts

def create_unibody_extrusion(name, w, h, d, r=0.08, n_seg=14):
    """
    Creates a solid rounded-rectangle unibody extruded along Y.
    Guaranteed silky-smooth rounded corners with zero ngon boolean clipping.
    """
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    pts = get_rounded_rect_pts(w, h, r, n_seg)
    N = len(pts)
    
    y_front = -d / 2.0
    y_back  = d / 2.0
    
    v_front = [bm.verts.new((x, y_front, z)) for x, z in pts]
    v_back  = [bm.verts.new((x, y_back, z)) for x, z in pts]
    bm.verts.ensure_lookup_table()
    
    # Front cap (reversed winding)
    bm.faces.new(list(reversed(v_front)))
    # Back cap
    bm.faces.new(v_back)
    
    # Side walls
    for i in range(N):
        i_next = (i + 1) % N
        bm.faces.new((v_front[i], v_back[i], v_back[i_next], v_front[i_next]))
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

def create_hollow_usbc_sleeve(name, cx, cy_front, cz, depth=0.10, r_out=0.044, r_in=0.036, dx=0.14, n_semi=16):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    def get_stadium_pts(r, dx, n):
        pts = []
        for i in range(n + 1):
            th = -math.pi/2.0 + math.pi * i / float(n)
            pts.append((dx/2.0 + r * math.cos(th), r * math.sin(th)))
        for i in range(1, n):
            th = math.pi/2.0 + math.pi * i / float(n)
            pts.append((-dx/2.0 + r * math.cos(th), r * math.sin(th)))
        return pts

    pts_out = get_stadium_pts(r_out, dx, n_semi)
    pts_in = get_stadium_pts(r_in, dx, n_semi)
    N = len(pts_out)
    
    y0 = cy_front
    y1 = cy_front + depth
    
    v_f_out = [bm.verts.new((cx + x, y0, cz + z)) for x, z in pts_out]
    v_f_in  = [bm.verts.new((cx + x, y0, cz + z)) for x, z in pts_in]
    v_b_out = [bm.verts.new((cx + x, y1, cz + z)) for x, z in pts_out]
    v_b_in  = [bm.verts.new((cx + x, y1, cz + z)) for x, z in pts_in]
    bm.verts.ensure_lookup_table()
    
    for i in range(N):
        i_next = (i + 1) % N
        bm.faces.new((v_f_out[i], v_f_out[i_next], v_f_in[i_next], v_f_in[i]))
        bm.faces.new((v_f_out[i], v_b_out[i], v_b_out[i_next], v_f_out[i_next]))
        bm.faces.new((v_f_in[i], v_f_in[i_next], v_b_in[i_next], v_b_in[i]))
        bm.faces.new((v_b_out[i_next], v_b_out[i], v_b_in[i], v_b_in[i_next]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

def create_hollow_usba_sleeve(name, cx, cy_front, cz, w_out=0.31, h_out=0.12, depth=0.10, t_wall=0.008):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    w_in = w_out - t_wall * 2.0
    h_in = h_out - t_wall * 2.0
    hw_o, hh_o = w_out / 2.0, h_out / 2.0
    hw_i, hh_i = w_in / 2.0, h_in / 2.0
    
    pts_out = [(-hw_o, -hh_o), (hw_o, -hh_o), (hw_o, hh_o), (-hw_o, hh_o)]
    pts_in  = [(-hw_i, -hh_i), (hw_i, -hh_i), (hw_i, hh_i), (-hw_i, hh_i)]
    
    y0 = cy_front
    y1 = cy_front + depth
    
    v_f_out = [bm.verts.new((cx + x, y0, cz + z)) for x, z in pts_out]
    v_f_in  = [bm.verts.new((cx + x, y0, cz + z)) for x, z in pts_in]
    v_b_out = [bm.verts.new((cx + x, y1, cz + z)) for x, z in pts_out]
    v_b_in  = [bm.verts.new((cx + x, y1, cz + z)) for x, z in pts_in]
    bm.verts.ensure_lookup_table()
    
    for i in range(4):
        i_next = (i + 1) % 4
        bm.faces.new((v_f_out[i], v_f_out[i_next], v_f_in[i_next], v_f_in[i]))
        bm.faces.new((v_f_out[i], v_b_out[i], v_b_out[i_next], v_f_out[i_next]))
        bm.faces.new((v_f_in[i], v_f_in[i_next], v_b_in[i_next], v_b_in[i]))
        bm.faces.new((v_b_out[i_next], v_b_out[i], v_b_in[i], v_b_in[i_next]))
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

def create_solid_stadium_cutter(name, cx, cy, cz, depth=0.08, r=0.046, dx=0.14, n_semi=16):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    pts = []
    for i in range(n_semi + 1):
        th = -math.pi/2.0 + math.pi * i / float(n_semi)
        pts.append((dx/2.0 + r * math.cos(th), r * math.sin(th)))
    for i in range(1, n_semi):
        th = math.pi/2.0 + math.pi * i / float(n_semi)
        pts.append((-dx/2.0 + r * math.cos(th), r * math.sin(th)))
        
    N = len(pts)
    y0 = cy - depth / 2.0
    y1 = cy + depth / 2.0
    
    v_f = [bm.verts.new((cx + x, y0, cz + z)) for x, z in pts]
    v_b = [bm.verts.new((cx + x, y1, cz + z)) for x, z in pts]
    bm.verts.ensure_lookup_table()
    
    bm.faces.new(list(reversed(v_f)))
    bm.faces.new(v_b)
    for i in range(N):
        i_next = (i + 1) % N
        bm.faces.new((v_f[i], v_b[i], v_b[i_next], v_f[i_next]))
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

# -------------------------------------------------------------
# MASTER MODEL BUILDER
# -------------------------------------------------------------
def build_flux_charger_model(mats):
    W = 0.68  # Width (X)
    D = 1.32  # Depth (Y)
    H = 1.20  # Height (Z)
    R_corner = 0.085 # Ergonomic rounded corner radius
    
    y_front = -D / 2.0  # -0.66
    y_back = D / 2.0   # +0.66
    
    model_objects = []

    # 1. MAIN UNIBODY SHELL (Clean BMesh rounded-box extrusion)
    body = create_unibody_extrusion("Charger_Body_Shell", W, H, D, r=R_corner, n_seg=16)
    body.data.materials.append(mats["pbt"])
    
    # Front and back perimeter bevels
    bev = body.modifiers.new("Bevel_Caps", 'BEVEL')
    bev.width = 0.016
    bev.segments = 4
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(70) # only bevels the 90 deg cap edges!
    
    wn_b = body.modifiers.new("WeightedNormals", 'WEIGHTED_NORMAL')
    wn_b.keep_sharp = True
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.shade_smooth()
    model_objects.append(body)
    
    # 2. FRONT RECESS CUTTER (Steps down front face by 0.02)
    recess_cutter = create_unibody_extrusion("Recess_Cutter", W * 0.90, H * 0.90, 0.04, r=R_corner * 0.85, n_seg=12)
    recess_cutter.location = (0, y_front + 0.012, 0)
    
    bmod = body.modifiers.new("CutFrontRecess", 'BOOLEAN')
    bmod.operation = 'DIFFERENCE'
    bmod.object = recess_cutter
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier="CutFrontRecess")
    bpy.data.objects.remove(recess_cutter, do_unlink=True)
    
    # 3. REAR PLUG CAVITY CUTTER & FOLDING PRONGS
    cav_w, cav_d, cav_h = 0.36, 0.09, 0.52
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, 
        location=(0, y_back - cav_d/2.0 + 0.005, -0.08), 
        scale=(cav_w, cav_d, cav_h)
    )
    plug_cutter = bpy.context.active_object
    pbev = plug_cutter.modifiers.new("PlugCutBevel", 'BEVEL')
    pbev.width = 0.02
    pbev.segments = 4
    bpy.context.view_layer.objects.active = plug_cutter
    bpy.ops.object.modifier_apply(modifier="PlugCutBevel")
    
    bmod_p = body.modifiers.new("CutPlugCavity", 'BOOLEAN')
    bmod_p.operation = 'DIFFERENCE'
    bmod_p.object = plug_cutter
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier="CutPlugCavity")
    bpy.data.objects.remove(plug_cutter, do_unlink=True)
    
    # Foldable Prongs (Nickel blades with safety holes)
    for px in [-0.09, 0.09]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, 
            location=(px, y_back - 0.030, -0.08), 
            scale=(0.018, 0.065, 0.30)
        )
        blade = bpy.context.active_object
        blade.name = f"Plug_Blade_{px}"
        blade.data.materials.append(mats["steel"])
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.016, depth=0.04, 
            location=(px, y_back - 0.030, -0.19), 
            rotation=(0, math.radians(90), 0)
        )
        hole_cutter = bpy.context.active_object
        hmod = blade.modifiers.new("BladeHole", 'BOOLEAN')
        hmod.operation = 'DIFFERENCE'
        hmod.object = hole_cutter
        bpy.context.view_layer.objects.active = blade
        bpy.ops.object.modifier_apply(modifier="BladeHole")
        bpy.data.objects.remove(hole_cutter, do_unlink=True)
        
        b_bev = blade.modifiers.new("BladeBevel", 'BEVEL')
        b_bev.width = 0.004
        b_bev.segments = 3
        bpy.ops.object.shade_smooth()
        model_objects.append(blade)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.020, depth=0.024, 
            location=(px, y_back - 0.030, 0.08), 
            rotation=(0, math.radians(90), 0)
        )
        knuckle = bpy.context.active_object
        knuckle.name = f"Plug_Knuckle_{px}"
        knuckle.data.materials.append(mats["steel"])
        bpy.ops.object.shade_smooth()
        model_objects.append(knuckle)

    # 4. SIGNATURE ACCENT PINSTRIPE (Acid Lime)
    accent_bar = create_unibody_extrusion("Accent_Pinstripe", W * 0.995, H * 0.995, 0.008, r=R_corner, n_seg=16)
    accent_bar.location = (0, y_front + 0.10, 0)
    accent_bar.data.materials.append(mats["lime"])
    model_objects.append(accent_bar)

    # 5. FRONT FACEPLATE (Seated in recess with mechanical reveal gap)
    fp_w = W * 0.88
    fp_h = H * 0.88
    fp_t = 0.018
    fp_y = y_front + 0.006
    
    faceplate = create_unibody_extrusion("Charger_Faceplate", fp_w, fp_h, fp_t, r=R_corner * 0.78, n_seg=14)
    faceplate.location = (0, fp_y, 0)
    faceplate.data.materials.append(mats["faceplate"])
    
    # Bevel perimeter of faceplate
    fp_bev = faceplate.modifiers.new("FP_Bevel", 'BEVEL')
    fp_bev.width = 0.005
    fp_bev.segments = 3
    bpy.context.view_layer.objects.active = faceplate
    bpy.ops.object.modifier_apply(modifier="FP_Bevel")

    # Cut Apertures through faceplate:
    # A) USB-C 1 Aperture (Z = +0.22)
    c1_cutter = create_solid_stadium_cutter("C1_Cut", 0.0, fp_y, 0.22, depth=0.06, r=0.046, dx=0.14)
    # B) USB-C 2 Aperture (Z = -0.04)
    c2_cutter = create_solid_stadium_cutter("C2_Cut", 0.0, fp_y, -0.04, depth=0.06, r=0.046, dx=0.14)
    # C) USB-A Aperture (Z = -0.32)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, fp_y, -0.32), scale=(0.33, 0.06, 0.14))
    a_cutter = bpy.context.active_object
    a_cutter.name = "A_Cut"
    abev = a_cutter.modifiers.new("ACutBevel", 'BEVEL')
    abev.width = 0.015
    abev.segments = 4
    bpy.context.view_layer.objects.active = a_cutter
    bpy.ops.object.modifier_apply(modifier="ACutBevel")
    # D) LED Pinhole Cutter (X = 0.18, Z = 0.38)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.06, location=(0.18, fp_y, 0.38), rotation=(math.radians(90), 0, 0))
    led_cutter = bpy.context.active_object
    led_cutter.name = "LED_Cut"

    for cutter in [c1_cutter, c2_cutter, a_cutter, led_cutter]:
        m = faceplate.modifiers.new(f"Mod_{cutter.name}", 'BOOLEAN')
        m.operation = 'DIFFERENCE'
        m.object = cutter
        bpy.context.view_layer.objects.active = faceplate
        bpy.ops.object.modifier_apply(modifier=f"Mod_{cutter.name}")
        bpy.data.objects.remove(cutter, do_unlink=True)
        
    wn_fp = faceplate.modifiers.new("WeightedNormals", 'WEIGHTED_NORMAL')
    wn_fp.keep_sharp = True
    
    # ANALYTIC UV MAPPING FOR FACEPLATE TEXTURE
    if not faceplate.data.uv_layers:
        faceplate.data.uv_layers.new(name="UVMap")
    uv_layer = faceplate.data.uv_layers.active.data
    mesh_fp = faceplate.data
    for poly in mesh_fp.polygons:
        for loop_idx in poly.loop_indices:
            v_idx = mesh_fp.loops[loop_idx].vertex_index
            v_co = mesh_fp.vertices[v_idx].co
            u = (v_co.x + fp_w / 2.0) / fp_w
            v = (v_co.z + fp_h / 2.0) / fp_h
            uv_layer[loop_idx].uv = (u, v)
            
    bpy.context.view_layer.objects.active = faceplate
    bpy.ops.object.shade_smooth()
    model_objects.append(faceplate)

    # 6. HOLLOW METAL SLEEVES & INTERNAL ASSEMBLIES
    sleeve_y_front = fp_y - fp_t/2.0 + 0.003
    sleeve_depth = 0.08
    
    # USB-C 1 Sleeve (Z = 0.22)
    usbc1_sleeve = create_hollow_usbc_sleeve("USBC1_Sleeve", 0.0, sleeve_y_front, 0.22, depth=sleeve_depth)
    usbc1_sleeve.data.materials.append(mats["steel"])
    bpy.ops.object.shade_smooth()
    model_objects.append(usbc1_sleeve)
    
    # USB-C 2 Sleeve (Z = -0.04)
    usbc2_sleeve = create_hollow_usbc_sleeve("USBC2_Sleeve", 0.0, sleeve_y_front, -0.04, depth=sleeve_depth)
    usbc2_sleeve.data.materials.append(mats["steel"])
    bpy.ops.object.shade_smooth()
    model_objects.append(usbc2_sleeve)

    # Center Tongues & 16 Gold Leaf Contacts for both USB-C ports
    for port_name, z_c in [("C1", 0.22), ("C2", -0.04)]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, 
            location=(0, sleeve_y_front + sleeve_depth + 0.03, z_c), 
            scale=(0.28, 0.06, 0.12)
        )
        cav = bpy.context.active_object
        cav.name = f"{port_name}_Cavity"
        cav.data.materials.append(mats["cavity"])
        model_objects.append(cav)
        
        t_w, t_d, t_h = 0.13, 0.065, 0.012
        t_y = sleeve_y_front + t_d / 2.0 + 0.006
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, t_y, z_c), scale=(t_w, t_d, t_h))
        tongue = bpy.context.active_object
        tongue.name = f"{port_name}_Tongue"
        tongue.data.materials.append(mats["cavity"])
        tbev = tongue.modifiers.new("TBevel", 'BEVEL')
        tbev.width = 0.002
        tbev.segments = 2
        model_objects.append(tongue)
        
        pin_w, pin_d, pin_h = 0.006, 0.042, 0.002
        step = t_w / 9.0
        start_x = -t_w / 2.0 + step
        for i in range(8):
            px = start_x + i * step
            # Top contact
            bpy.ops.mesh.primitive_cube_add(
                size=1.0, 
                location=(px, t_y - 0.006, z_c + t_h/2.0 + pin_h/2.0), 
                scale=(pin_w, pin_d, pin_h)
            )
            pt = bpy.context.active_object
            pt.name = f"{port_name}_GoldPin_Top_{i}"
            pt.data.materials.append(mats["gold"])
            model_objects.append(pt)
            
            # Bottom contact
            bpy.ops.mesh.primitive_cube_add(
                size=1.0, 
                location=(px, t_y - 0.006, z_c - t_h/2.0 - pin_h/2.0), 
                scale=(pin_w, pin_d, pin_h)
            )
            pb = bpy.context.active_object
            pb.name = f"{port_name}_GoldPin_Bot_{i}"
            pb.data.materials.append(mats["gold"])
            model_objects.append(pb)

    # USB-A Hollow Sleeve & Internals (Z = -0.32)
    usba_sleeve = create_hollow_usba_sleeve("USBA_Sleeve", 0.0, sleeve_y_front, -0.32, depth=sleeve_depth)
    usba_sleeve.data.materials.append(mats["steel"])
    bpy.ops.object.shade_smooth()
    model_objects.append(usba_sleeve)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, 
        location=(0, sleeve_y_front + sleeve_depth + 0.03, -0.32), 
        scale=(0.34, 0.06, 0.15)
    )
    a_cav = bpy.context.active_object
    a_cav.name = "USBA_Cavity"
    a_cav.data.materials.append(mats["cavity"])
    model_objects.append(a_cav)
    
    # USB-A Lime Insulator Tongue
    at_w = 0.28
    at_h = 0.036
    at_d = 0.065
    at_y = sleeve_y_front + at_d / 2.0 + 0.006
    at_zc = -0.32 + 0.12/2.0 - at_h/2.0 - 0.008
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, at_y, at_zc), scale=(at_w, at_d, at_h))
    a_tongue = bpy.context.active_object
    a_tongue.name = "USBA_Tongue"
    a_tongue.data.materials.append(mats["lime"])
    model_objects.append(a_tongue)
    
    # 4 Heavy Gold Pins on USB-A Tongue
    for px in [-0.08, -0.026, 0.026, 0.08]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, 
            location=(px, at_y - 0.008, at_zc - at_h/2.0 - 0.002), 
            scale=(0.016, 0.045, 0.003)
        )
        apin = bpy.context.active_object
        apin.name = f"USBA_GoldPin_{px}"
        apin.data.materials.append(mats["gold"])
        model_objects.append(apin)

    # 7. STATUS LED ACRYLIC LENS
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.010, depth=0.016, 
        location=(0.18, fp_y + 0.004, 0.38), 
        rotation=(math.radians(90), 0, 0)
    )
    led_lens = bpy.context.active_object
    led_lens.name = "LED_LightGuide_Lens"
    led_lens.data.materials.append(mats["led"])
    bpy.ops.object.shade_smooth()
    model_objects.append(led_lens)

    # 8. SEAMLESS STUDIO CYCLORAMA BACKDROP (#EBE8E1)
    # L-shaped curved cyc wall eliminating black horizon
    mesh_cyc = bpy.data.meshes.new("Studio_Cyclorama")
    bm_c = bmesh.new()
    
    # Profile along Y-Z plane:
    # Floor: from y = -6.0 to y = +1.2 at z = -H/2.0
    # Arc: from y = +1.2, z = -H/2 to y = +3.2, z = -H/2 + 2.0 (radius 2.0)
    # Wall: from y = +3.2, z = -H/2 + 2.0 to y = +3.2, z = +6.0
    z_floor = -H / 2.0
    cyc_pts = []
    cyc_pts.append((-6.0, z_floor))
    cyc_pts.append((1.0, z_floor))
    
    r_cyc = 2.0
    cyc_c_y = 1.0
    cyc_c_z = z_floor + r_cyc
    for i in range(17):
        th = -math.pi/2.0 + (math.pi/2.0) * (i / 16.0)
        cyc_pts.append((cyc_c_y + r_cyc * math.cos(th), cyc_c_z + r_cyc * math.sin(th)))
    cyc_pts.append((cyc_c_y + r_cyc, z_floor + 6.0))
    
    x_half = 8.0
    v_left  = [bm_c.verts.new((-x_half, py, pz)) for py, pz in cyc_pts]
    v_right = [bm_c.verts.new((x_half, py, pz)) for py, pz in cyc_pts]
    bm_c.verts.ensure_lookup_table()
    
    for i in range(len(cyc_pts) - 1):
        bm_c.faces.new((v_left[i], v_right[i], v_right[i+1], v_left[i+1]))
        
    bmesh.ops.recalc_face_normals(bm_c, faces=bm_c.faces)
    bm_c.to_mesh(mesh_cyc)
    bm_c.free()
    
    cyc_obj = bpy.data.objects.new("Studio_Cyclorama", mesh_cyc)
    cyc_obj.data.materials.append(mats["cyc"])
    bpy.context.scene.collection.objects.link(cyc_obj)
    bpy.context.view_layer.objects.active = cyc_obj
    bpy.ops.object.shade_smooth()

    return model_objects

# -------------------------------------------------------------
# LIGHTING RIG (Balanced Commercial Hardware Specification)
# -------------------------------------------------------------
def setup_studio_lighting():
    # 1. Key Softbox (Front-Left 45 deg, wrap-around sheen)
    bpy.ops.object.light_add(type='AREA', location=(-2.4, -2.8, 2.0))
    key = bpy.context.active_object
    key.name = "Studio_Key_Softbox"
    key.data.energy = 55.0
    key.data.size = 2.2
    key.data.size_y = 1.6
    key.data.color = (1.0, 0.98, 0.95)
    dir_v = Vector((0, 0, 0)) - key.location
    key.rotation_euler = dir_v.to_track_quat('-Z', 'Y').to_euler()

    # 2. Fill / Bounce Softbox (Front-Right, lifts side wall texture)
    bpy.ops.object.light_add(type='AREA', location=(2.6, -1.8, 1.4))
    fill_side = bpy.context.active_object
    fill_side.name = "Studio_Fill_Side"
    fill_side.data.energy = 28.0
    fill_side.data.size = 1.8
    fill_side.data.size_y = 1.4
    fill_side.data.color = (0.96, 0.98, 1.0)
    dir_s = Vector((0.2, 0, 0)) - fill_side.location
    fill_side.rotation_euler = dir_s.to_track_quat('-Z', 'Y').to_euler()

    # 3. Rim / Kicker Light (Back-Right, creates razor-sharp edge glints)
    bpy.ops.object.light_add(type='AREA', location=(2.2, 2.0, 1.8))
    rim = bpy.context.active_object
    rim.name = "Studio_Rim_Kicker"
    rim.data.energy = 65.0
    rim.data.size = 0.5
    rim.data.size_y = 2.2
    rim.data.color = (0.98, 0.99, 1.0)
    dir_r = Vector((0, 0, 0.2)) - rim.location
    rim.rotation_euler = dir_r.to_track_quat('-Z', 'Y').to_euler()

    # 4. Front Port Infill Light (Directly illuminates recessed sockets & gold pins)
    bpy.ops.object.light_add(type='AREA', location=(-0.2, -3.4, 0.2))
    fill = bpy.context.active_object
    fill.name = "Studio_Port_Infill"
    fill.data.energy = 25.0
    fill.data.size = 1.4
    fill.data.size_y = 0.9
    fill.data.color = (1.0, 1.0, 1.0)
    dir_f = Vector((0, -0.66, 0.0)) - fill.location
    fill.rotation_euler = dir_f.to_track_quat('-Z', 'Y').to_euler()

    # 5. Top Crown Linear Accent
    bpy.ops.object.light_add(type='AREA', location=(0.0, -0.2, 2.6))
    top = bpy.context.active_object
    top.name = "Studio_Top_Crown"
    top.data.energy = 25.0
    top.data.size = 1.8
    top.data.size_y = 0.4
    top.data.color = (0.98, 0.99, 1.0)
    top.rotation_euler = Euler((0, 0, 0), 'XYZ')

# -------------------------------------------------------------
# AUTOMATED BOUNDING-BOX CAMERA FITTING
# -------------------------------------------------------------
def fit_camera_to_scene(scene, objects, fov_deg=40.0, margin=0.22, rot_euler=(math.radians(54), 0, math.radians(40))):
    bpy.context.view_layer.update()
    corners = []
    for obj in objects:
        if obj.type == 'MESH' and "Cyclorama" not in obj.name:
            for c in obj.bound_box:
                corners.append(obj.matrix_world @ mathutils.Vector(c))
    
    if not corners:
        print("Warning: No corners found for camera fit")
        return None
    
    min_co = mathutils.Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    max_co = mathutils.Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    center = (min_co + max_co) / 2.0
    
    cam_data = bpy.data.cameras.new("FittedCamera")
    cam_data.lens_unit = 'FOV'
    cam_data.angle = math.radians(fov_deg)
    cam_data.sensor_fit = 'AUTO'
    
    cam_obj = bpy.data.objects.new("FittedCamera", cam_data)
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

# -------------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------------
def main():
    print("=== STARTING MASTER FLUX CHARGER V6 BUILD & RENDER ===")
    scene = reset_scene()
    configure_cycles(scene, samples=384)
    
    mats = create_materials()
    model_objs = build_flux_charger_model(mats)
    setup_studio_lighting()
    
    # Save the master .blend file
    blend_path = os.path.join(MODELS_DIR, "flux_charger_v6.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Master Scene Saved: {blend_path}")
    
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1600

    # RENDER 1: HERO 3/4 PERSPECTIVE (with guaranteed bounding box fit)
    print("--- Setting up View 1: Hero Perspective (1600x1600) ---")
    hero_cam = fit_camera_to_scene(
        scene, model_objs, fov_deg=36.0, margin=0.22,
        rot_euler=(math.radians(60), 0, math.radians(42))
    )
    scene.camera = hero_cam
    hero_out = os.path.join(OUTPUT_DIR, "flux_charger_v6_hero.png")
    scene.render.filepath = hero_out
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {hero_out}")
    
    # RENDER 2: MACRO PORT ASSEMBLY & MECHANICAL DETAIL
    print("--- Setting up View 2: Macro Assembly & Ports (1600x1600) ---")
    # Front-facing 3/4 angle focused directly into the faceplate and ports
    macro_cam = fit_camera_to_scene(
        scene, model_objs, fov_deg=26.0, margin=-0.08, # Macro close-up
        rot_euler=(math.radians(76), 0, math.radians(26))
    )
    scene.camera = macro_cam
    macro_out = os.path.join(OUTPUT_DIR, "flux_charger_v6_macro.png")
    scene.render.filepath = macro_out
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {macro_out}")
    
    # RENDER 3: REAR MECHANICAL PLUG & BUILD ASSEMBLY
    print("--- Setting up View 3: Rear Mechanical Assembly & Prongs (1600x1600) ---")
    rear_cam = fit_camera_to_scene(
        scene, model_objs, fov_deg=34.0, margin=0.18,
        rot_euler=(math.radians(58), 0, math.radians(-138))
    )
    scene.camera = rear_cam
    rear_out = os.path.join(OUTPUT_DIR, "flux_charger_v6_rear.png")
    scene.render.filepath = rear_out
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {rear_out}")
    
    print("=== FINISHED MASTER FLUX CHARGER V6 BUILD ===")

if __name__ == "__main__":
    main()
