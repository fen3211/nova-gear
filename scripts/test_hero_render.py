import bpy
import math
import os
import time
from mathutils import Vector

SCENE_PATH = r"D:\Projects\ууу\assets\scenes\assembled_k75.blend"
OUT_DIR = r"D:\Projects\ууу\assets\staging\hero_test"
os.makedirs(OUT_DIR, exist_ok=True)

print(">>> Loading assembled_k75.blend...")
bpy.ops.wm.open_mainfile(filepath=SCENE_PATH)
scene = bpy.context.scene

# Configure Cycles GPU OptiX
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
for dev in prefs.devices:
    dev.use = (dev.type == 'OPTIX')
scene.cycles.device = 'GPU'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.render.film_transparent = True
scene.render.resolution_x = 1200
scene.render.resolution_y = 800

# Remove ground floor object if it blocks transparency
for obj in bpy.data.objects:
    if "Floor" in obj.name or "Plane" in obj.name or "Studio_Editorial_Floor" in obj.name:
        obj.hide_render = True

# Add or setup Hero Camera
cam = scene.camera
if not cam:
    cam_data = bpy.data.cameras.new("Hero_Camera")
    cam = bpy.data.objects.new("Hero_Camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

cam.data.lens = 75.0 # 75mm lens for editorial product compression

# Test frame 0 camera
target = Vector((0.015, -0.005, 0.018))
dist = 0.58
elev = math.radians(26.0)
azim = math.radians(22.0)

cx = target.x + dist * math.cos(elev) * math.sin(azim)
cy = target.y - dist * math.cos(elev) * math.cos(azim)
cz = target.z + dist * math.sin(elev)
cam.location = Vector((cx, cy, cz))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

out_path = os.path.join(OUT_DIR, "hero_test_frame_0.png")
scene.render.filepath = out_path

t0 = time.time()
bpy.ops.render.render(write_still=True)
print(f">>> Rendered test frame in {time.time() - t0:.2f}s to {out_path}")
