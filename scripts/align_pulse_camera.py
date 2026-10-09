"""
NOVA PULSE PRO // Camera & Orientation Alignment
Finds the exact camera coordinates and mouse rotation to match media_1791575583430_5b6e195d.jpg
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

PROJECT_ROOT = r"D:\Projects\ууу"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "assets", "previews")

import sys
sys.path.append(os.path.dirname(__file__))
import test_pulse_cage

def align_and_render():
    scene = test_pulse_cage.reset_scene()
    test_pulse_cage.configure_cycles(scene, samples=32)
    m_clay = test_pulse_cage.setup_studio_environment()
    mouse = test_pulse_cage.build_mouse_control_cage()
    mouse.data.materials.append(m_clay)

    # Let's orient the mouse so that:
    # Nose is pointing towards (-0.7, -0.7, 0)
    # Thumb wing is facing the camera
    # We can keep mouse unrotated and position camera:
    # Camera in photo: looking at the left-front flank of the mouse
    # If Nose = -Y, Tail = +Y, Thumb = -X (Left), Right side = +X
    # Let's place camera at (X, Y, Z) and check what angle shows:
    # Nose at screen bottom-left, thumb wing at screen bottom-right, palm at screen top-right.
    
    # Try mouse rotation: Z rotation = -35 degrees
    mouse.rotation_euler = Euler((0.0, 0.0, math.radians(-32.0)), 'XYZ')

    cam_data = bpy.data.cameras.new("Aligned_Camera")
    cam_data.lens = 75.0
    cam_obj = bpy.data.objects.new("Aligned_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Position camera in front and slightly to the left
    cam_obj.location = Vector((-0.12, -0.26, 0.22))
    
    target = bpy.data.objects.new("Cam_Target", None)
    bpy.context.scene.collection.objects.link(target)
    target.location = Vector((-0.005, 0.005, 0.020))

    track = cam_obj.constraints.new('TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Studio light
    bpy.ops.object.light_add(type='AREA', location=(-0.25, -0.25, 0.40))
    key = bpy.context.active_object
    key.data.energy = 90.0
    key.data.size = 0.5

    out_file = os.path.join(OUTPUT_DIR, "pulse_pro_aligned_test.png")
    scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered test to: {out_file}")

if __name__ == "__main__":
    align_and_render()
