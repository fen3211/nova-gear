import bpy
import math
import os
import time
from mathutils import Vector

SCENE_PATH = r"D:\Projects\ууу\assets\scenes\assembled_k75.blend"
RAW_DIR = r"D:\Projects\ууу\assets\staging\hero_raw"
OUT_DIR = r"D:\Projects\ууу\assets\frames_hero"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

print(">>> Opening assembled_k75.blend...")
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
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.render.film_transparent = True
scene.render.resolution_x = 1200
scene.render.resolution_y = 800

# Hide ground planes if any
for obj in bpy.data.objects:
    if any(k in obj.name.lower() for k in ["floor", "plane", "ground", "backdrop"]):
        obj.hide_render = True

# Add or setup Hero Camera
cam = scene.camera
if not cam:
    cam_data = bpy.data.cameras.new("Hero_Camera")
    cam = bpy.data.objects.new("Hero_Camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

cam.data.lens = 75.0

# Interpolation helper (smooth cubic ease)
def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)

def lerp(a, b, t):
    return a + (b - a) * t

TOTAL_FRAMES = 56 # 0..55

def get_camera_params(alpha):
    # Phase 0..0.30: Focus on brass knob and function row
    # Phase 0.30..0.70: Sweep across keycap matrix & Esc cluster
    # Phase 0.70..1.00: Settle into majestic wide isometric hero pose
    if alpha < 0.35:
        sub = alpha / 0.35
        sub = smoothstep(sub)
        tx = lerp(0.08, 0.01, sub)
        ty = lerp(0.02, 0.00, sub)
        tz = 0.018
        azim = lerp(16.0, -8.0, sub)
        elev = lerp(21.0, 26.0, sub)
        dist = lerp(0.46, 0.50, sub)
    elif alpha < 0.70:
        sub = (alpha - 0.35) / 0.35
        sub = smoothstep(sub)
        tx = lerp(0.01, -0.05, sub)
        ty = lerp(0.00, -0.01, sub)
        tz = 0.018
        azim = lerp(-8.0, -18.0, sub)
        elev = lerp(26.0, 31.0, sub)
        dist = lerp(0.50, 0.54, sub)
    else:
        sub = (alpha - 0.70) / 0.30
        sub = smoothstep(sub)
        tx = lerp(-0.05, 0.015, sub)
        ty = lerp(-0.01, -0.005, sub)
        tz = 0.018
        azim = lerp(-18.0, 22.0, sub)
        elev = lerp(31.0, 28.0, sub)
        dist = lerp(0.54, 0.60, sub)

    target = Vector((tx, ty, tz))
    rad_elev = math.radians(elev)
    rad_azim = math.radians(azim)

    cx = target.x + dist * math.cos(rad_elev) * math.sin(rad_azim)
    cy = target.y - dist * math.cos(rad_elev) * math.cos(rad_azim)
    cz = target.z + dist * math.sin(rad_elev)
    
    return target, Vector((cx, cy, cz))

print(f">>> Commencing render of {TOTAL_FRAMES} Hero 3D frames...")
t_start = time.time()

for idx in range(TOTAL_FRAMES):
    alpha = idx / float(TOTAL_FRAMES - 1)
    target, cam_pos = get_camera_params(alpha)
    
    cam.location = cam_pos
    direction = target - cam_pos
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    raw_path = os.path.join(RAW_DIR, f"hero_raw_{idx:02d}.png")
    scene.render.filepath = raw_path
    
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t0
    
    if idx % 5 == 0 or idx == TOTAL_FRAMES - 1:
        print(f"[{idx+1}/{TOTAL_FRAMES}] frame alpha={alpha:.3f} rendered in {dt:.2f}s")

print(f">>> Done! Total render time: {time.time() - t_start:.1f}s")
