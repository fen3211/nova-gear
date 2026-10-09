"""
NOVA PULSE PRO // Clean SubD Quad Cage Builder & Clay Silhouette Verification
Matches authentic reference photo: media_1791575583430_5b6e195d.jpg
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"D:\Projects\ууу"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "assets", "previews")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Clay_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.92, 0.90, 0.86, 1.0)
        bg.inputs['Strength'].default_value = 0.85
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
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Base Contrast'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024

def build_mouse_control_cage():
    """
    Constructs a closed, manifold, quad-dominant ergonomic mouse mesh.
    Cross sections along Y:
    Y from -0.060 (front nose) to +0.060 (rear tail).
    Rings around Z axis:
    8 points per ring from bottom floor, left thumb rest, left upper flank,
    crest ridge, right upper flank, right waist, right base, to bottom center.
    """
    mesh = bpy.data.meshes.new("Mouse_Chassis_Cage")
    bm = bmesh.new()

    # 11 longitudinal stations along Y
    # y_stations from front to back
    stations = [
        # y, base_z, nose/tail_taper
        -0.062, # 0: Front bumper lip
        -0.052, # 1: Front clicks tip
        -0.038, # 2: Main clicks slope
        -0.022, # 3: Wheel well center
        -0.006, # 4: Wheel rear / palm transition
         0.010, # 5: Peak palm hump & widest thumb wing
         0.025, # 6: Palm crest
         0.038, # 7: Rear slope
         0.048, # 8: Lower tail
         0.056, # 9: Tail base
         0.060  # 10: Tail tip
    ]

    # At each station, define 10 profile points in a loop:
    # 0: bottom center
    # 1: bottom left
    # 2: thumb wing tip / left lower flank
    # 3: left upper waist / thumb groove
    # 4: left crest / LMB ridge
    # 5: top center ridge
    # 6: right crest / RMB ridge
    # 7: right upper flank
    # 8: right lower waist
    # 9: bottom right

    # Coordinate table: (x, y, z) for all 10 rings
    # Widths and heights are carefully tuned to match the reference photo:
    # Length: ~122mm (-62 to +60)
    # Total width with thumb wing: ~82mm (-46mm to +36mm)
    # Peak height: ~43mm (Z=0.043 at y=0.010, biased left at x=-0.006)
    ring_specs = [
        # Station 0: Front bumper lip (Y = -0.062)
        [
            ( 0.000, 0.003), (-0.012, 0.003), (-0.018, 0.005), (-0.016, 0.010), (-0.008, 0.013),
            ( 0.000, 0.014), ( 0.008, 0.013), ( 0.016, 0.010), ( 0.018, 0.005), ( 0.012, 0.003)
        ],
        # Station 1: Front clicks tip (Y = -0.052)
        [
            ( 0.000, 0.002), (-0.016, 0.002), (-0.024, 0.005), (-0.022, 0.014), (-0.012, 0.019),
            ( 0.000, 0.020), ( 0.012, 0.019), ( 0.022, 0.014), ( 0.024, 0.005), ( 0.016, 0.002)
        ],
        # Station 2: Main clicks slope (Y = -0.038)
        [
            ( 0.000, 0.002), (-0.020, 0.002), (-0.032, 0.005), (-0.027, 0.020), (-0.015, 0.026),
            ( 0.000, 0.027), ( 0.014, 0.026), ( 0.026, 0.019), ( 0.029, 0.005), ( 0.019, 0.002)
        ],
        # Station 3: Wheel well center (Y = -0.022)
        [
            ( 0.000, 0.002), (-0.022, 0.002), (-0.040, 0.004), (-0.029, 0.025), (-0.016, 0.033),
            ( 0.000, 0.034), ( 0.015, 0.033), ( 0.028, 0.024), ( 0.032, 0.005), ( 0.021, 0.002)
        ],
        # Station 4: Wheel rear / palm transition (Y = -0.006)
        [
            ( 0.000, 0.002), (-0.024, 0.002), (-0.045, 0.004), (-0.030, 0.029), (-0.016, 0.038),
            (-0.002, 0.039), ( 0.015, 0.037), ( 0.029, 0.027), ( 0.034, 0.005), ( 0.022, 0.002)
        ],
        # Station 5: Peak palm hump & widest thumb wing (Y = +0.010)
        [
            ( 0.000, 0.002), (-0.025, 0.002), (-0.046, 0.004), (-0.031, 0.031), (-0.017, 0.042),
            (-0.005, 0.043), ( 0.015, 0.040), ( 0.029, 0.028), ( 0.034, 0.005), ( 0.022, 0.002)
        ],
        # Station 6: Palm crest (Y = +0.025)
        [
            ( 0.000, 0.002), (-0.024, 0.002), (-0.042, 0.004), (-0.029, 0.030), (-0.016, 0.040),
            (-0.004, 0.041), ( 0.014, 0.037), ( 0.027, 0.026), ( 0.032, 0.005), ( 0.020, 0.002)
        ],
        # Station 7: Rear slope (Y = +0.038)
        [
            ( 0.000, 0.002), (-0.020, 0.002), (-0.032, 0.004), (-0.025, 0.025), (-0.013, 0.033),
            (-0.003, 0.034), ( 0.012, 0.031), ( 0.023, 0.022), ( 0.027, 0.004), ( 0.017, 0.002)
        ],
        # Station 8: Lower tail (Y = +0.048)
        [
            ( 0.000, 0.002), (-0.015, 0.002), (-0.023, 0.003), (-0.018, 0.018), (-0.010, 0.024),
            (-0.002, 0.025), ( 0.009, 0.023), ( 0.017, 0.016), ( 0.020, 0.003), ( 0.013, 0.002)
        ],
        # Station 9: Tail base (Y = +0.056)
        [
            ( 0.000, 0.002), (-0.010, 0.002), (-0.014, 0.003), (-0.012, 0.011), (-0.006, 0.015),
            (-0.001, 0.016), ( 0.006, 0.015), ( 0.011, 0.010), ( 0.013, 0.003), ( 0.008, 0.002)
        ],
        # Station 10: Tail tip (Y = +0.060)
        [
            ( 0.000, 0.002), (-0.005, 0.002), (-0.007, 0.003), (-0.006, 0.007), (-0.003, 0.009),
            ( 0.000, 0.010), ( 0.003, 0.009), ( 0.006, 0.007), ( 0.007, 0.003), ( 0.004, 0.002)
        ]
    ]

    rings = []
    for s_idx, y in enumerate(stations):
        spec = ring_specs[s_idx]
        ring_v = []
        for p_idx, (x, z) in enumerate(spec):
            v = bm.verts.new((x, y, z))
            ring_v.append(v)
        rings.append(ring_v)

    n_pts = 10
    # Create quad faces bridging each ring
    for s_idx in range(len(stations) - 1):
        for p_idx in range(n_pts):
            p_next = (p_idx + 1) % n_pts
            v0 = rings[s_idx][p_idx]
            v1 = rings[s_idx][p_next]
            v2 = rings[s_idx + 1][p_next]
            v3 = rings[s_idx + 1][p_idx]
            bm.faces.new((v0, v1, v2, v3))

    # Cap front pole
    v_front_pole = bm.verts.new((0.0, stations[0] - 0.002, 0.008))
    for p_idx in range(n_pts):
        p_next = (p_idx + 1) % n_pts
        bm.faces.new((v_front_pole, rings[0][p_next], rings[0][p_idx]))

    # Cap back pole
    v_back_pole = bm.verts.new((0.0, stations[-1] + 0.002, 0.005))
    for p_idx in range(n_pts):
        p_next = (p_idx + 1) % n_pts
        bm.faces.new((v_back_pole, rings[-1][p_idx], rings[-1][p_next]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Mouse_Chassis", mesh)
    bpy.context.scene.collection.objects.link(obj)

    # Smooth shading
    for poly in obj.data.polygons:
        poly.use_smooth = True

    # Subdivision surface level 2 for silky smooth organic curve
    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 3

    return obj

def setup_studio_environment():
    # Warm cream studio floor matching reference photo #EAE6DF
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0.0, 0.0, 0.0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    
    m_floor = bpy.data.materials.new("Studio_Floor_Mat")
    m_floor.use_nodes = True
    bsdf_f = m_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        # Off-white warm studio tone
        bsdf_f.inputs['Base Color'].default_value = (0.86, 0.83, 0.77, 1.0)
        bsdf_f.inputs['Roughness'].default_value = 0.55
    floor.data.materials.append(m_floor)

    # Clay material for mouse chassis
    m_clay = bpy.data.materials.new("Clay_Mouse_Mat")
    m_clay.use_nodes = True
    bsdf_c = m_clay.node_tree.nodes.get("Principled BSDF")
    if bsdf_c:
        # Neutral dark matte graphite
        bsdf_c.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1.0)
        bsdf_c.inputs['Roughness'].default_value = 0.40
    return m_clay

def setup_camera_matching_reference():
    """
    Calibrate camera to exactly match media_1791575583430_5b6e195d.jpg:
    - 3/4 beauty angle looking down from left-front
    - Lens: 85mm
    """
    cam_data = bpy.data.cameras.new("Hero_Camera")
    cam_data.lens = 85.0
    cam_obj = bpy.data.objects.new("Hero_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Position camera
    cam_obj.location = Vector((-0.18, -0.22, 0.17))
    
    # Track target
    target = bpy.data.objects.new("Cam_Target", None)
    bpy.context.scene.collection.objects.link(target)
    target.location = Vector((-0.005, 0.000, 0.018))

    track = cam_obj.constraints.new('TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Lighting setup matching photo
    # Key light: soft warm overhead left
    bpy.ops.object.light_add(type='AREA', location=(-0.25, -0.20, 0.35))
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 85.0
    key.data.size = 0.4
    key.data.color = (1.0, 0.98, 0.95)

    # Fill light: soft right
    bpy.ops.object.light_add(type='AREA', location=(0.28, -0.15, 0.25))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 35.0
    fill.data.size = 0.5
    fill.data.color = (0.95, 0.96, 1.0)

    # Rim light: from behind right
    bpy.ops.object.light_add(type='AREA', location=(0.15, 0.25, 0.20))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 45.0
    rim.data.size = 0.3

def main():
    print(">>> Testing Pulse Pro Base SubD Cage...")
    scene = reset_scene()
    configure_cycles(scene, samples=48)
    m_clay = setup_studio_environment()
    mouse = build_mouse_control_cage()
    mouse.data.materials.append(m_clay)
    setup_camera_matching_reference()

    out_file = os.path.join(OUTPUT_DIR, "pulse_pro_clay_silhouette.png")
    scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Clay silhouette saved to: {out_file}")

if __name__ == "__main__":
    main()
