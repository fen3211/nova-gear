"""
Encode transparent animation frames into web-ready formats:
1. k75_assembly.webm (VP9 with yuva420p alpha channel)
2. k75_assembly.webp (Animated WebP with alpha channel)
"""
import glob
import os
import subprocess
import sys

FRAMES_DIR = r"D:\Projects\ууу\assets\frames_k75"
IMAGES_DIR = r"D:\Projects\ууу\assets\images"

def encode():
    frames = sorted(glob.glob(os.path.join(FRAMES_DIR, "frame_*.png")))
    print(f"Total rendered frames detected: {len(frames)}")
    if len(frames) < 144:
        print(f"ERROR: Expected 144 frames, found {len(frames)}")
        sys.exit(1)
        
    webm_out = os.path.join(IMAGES_DIR, "k75_assembly.webm")
    webp_out = os.path.join(IMAGES_DIR, "k75_assembly.webp")
    
    # 1. Encode WebM VP9 with native alpha (yuva420p)
    print(">>> Encoding transparent WebM (VP9 + yuva420p)...")
    cmd_webm = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p",
        "-b:v", "2200k",
        "-crf", "28",
        "-auto-alt-ref", "0",
        webm_out
    ]
    subprocess.run(cmd_webm, check=True)
    webm_size = os.path.getsize(webm_out) / (1024 * 1024)
    print(f"WebM encoded successfully: {webm_out} ({webm_size:.2f} MB)")
    
    # 2. Encode Animated WebP with native alpha
    print(">>> Encoding Animated WebP (yuva420p)...")
    cmd_webp = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
        "-loop", "0",
        "-c:v", "libwebp",
        "-pix_fmt", "yuva420p",
        "-quality", "80",
        "-compression_level", "4",
        webp_out
    ]
    subprocess.run(cmd_webp, check=True)
    webp_size = os.path.getsize(webp_out) / (1024 * 1024)
    print(f"WebP encoded successfully: {webp_out} ({webp_size:.2f} MB)")

if __name__ == "__main__":
    encode()
