import bpy
import math
import os
import time
from mathutils import Vector

SCENE_PATH = r"D:\Projects\ууу\assets\scenes\k75_animation.blend"
RAW_DIR = r"D:\Projects\ууу\assets\staging\scrub_raw"
OUT_DIR = r"D:\Projects\ууу\assets\frames_scrub"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

print(">>> Opening master animation blend file...")
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
scene.render.resolution_x = 720
scene.render.resolution_y = 720

scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'

cam = scene.camera

def set_camera(alpha):
    # Dynamic camera pullback:
    # alpha=0: dist=0.68, target_z=0.025 (tight frame on assembled keyboard: 73.2% width)
    # alpha=1: dist=0.98, target_z=0.165 (framing exploded vertical stack: 78.3% height)
    dist = 0.68 + alpha * (0.98 - 0.68)
    target_z = 0.025 + alpha * (0.165 - 0.025)
    target = Vector((0.005, 0.000, target_z))
    elev_rad = math.radians(36.0)
    azim_rad = math.radians(18.0)
    
    cam_x = target.x + dist * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target.y - dist * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target.z + dist * math.sin(elev_rad)
    cam.location = Vector((cam_x, cam_y, cam_z))
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

TOTAL_FRAMES = 57 # indices 0..56
# Frame 68 is fully assembled (idx=0)
# Frame 12 is fully exploded (idx=56)

print(f">>> Commencing render of {TOTAL_FRAMES} dynamic scrub frames...")
t_start = time.time()

for idx in range(TOTAL_FRAMES):
    alpha = idx / float(TOTAL_FRAMES - 1)
    blend_frame = 68 - idx
    
    set_camera(alpha)
    scene.frame_set(blend_frame)
    
    raw_path = os.path.join(RAW_DIR, f"scrub_raw_{idx:02d}.png")
    scene.render.filepath = raw_path
    
    f_t0 = time.time()
    bpy.ops.render.render(write_still=True)
    f_elapsed = time.time() - f_t0
    
    if idx % 5 == 0 or idx == TOTAL_FRAMES - 1:
        print(f"[{idx+1}/{TOTAL_FRAMES}] frame {blend_frame} (alpha={alpha:.3f}) rendered in {f_elapsed:.2f}s")

t_total = time.time() - t_start
print(f">>> All {TOTAL_FRAMES} frames rendered in {t_total:.1f}s (avg {t_total/TOTAL_FRAMES:.2f}s/frame)")
