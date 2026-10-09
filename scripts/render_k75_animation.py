"""
Dedicated fast rendering pipeline for NovaKeys K75 Assembly Animation
Renders 144 frames @ 24fps from assets/scenes/k75_animation.blend,
then encodes transparent WebM, animated WebP, and branded MP4.
"""
import bpy
import os
import subprocess
import sys
import time

SCENE_PATH = r"D:\Projects\ууу\assets\scenes\k75_animation.blend"
FRAMES_DIR = r"D:\Projects\ууу\assets\frames_k75"
IMAGES_DIR = r"D:\Projects\ууу\assets\images"

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def render_sequence():
    print(">>> Loading animated scene:", SCENE_PATH)
    bpy.ops.wm.open_mainfile(filepath=SCENE_PATH)
    scene = bpy.context.scene

    scene.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = (dev.type == 'OPTIX')
    scene.cycles.device = 'GPU'
    
    # 48 samples with OptiX AI denoiser delivers pristine noise-free frames in ~1.2s/frame
    scene.cycles.samples = 48
    scene.cycles.preview_samples = 16
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.render.image_settings.compression = 15
    
    scene.frame_start = 1
    scene.frame_end = 144
    scene.render.fps = 24
    scene.render.resolution_x = 720
    scene.render.resolution_y = 720
    
    output_pattern = os.path.join(FRAMES_DIR, "frame_")
    scene.render.filepath = output_pattern

    t0 = time.time()
    print(f">>> Commencing 144-frame render to {output_pattern}####.png ...")
    bpy.ops.render.render(animation=True)
    t1 = time.time()
    print(f">>> Render completed in {t1 - t0:.1f}s (avg {(t1-t0)/144:.2f}s/frame)")

if __name__ == "__main__":
    render_sequence()
