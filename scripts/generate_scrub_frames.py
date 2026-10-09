"""
Generate optimized WebP frame sequence for ultra-smooth scroll-driven scrubbing.
Source: assets/frames_k75/frame_0068.png (Assembled, progress=0)
Down to: assets/frames_k75/frame_0012.png (Exploded, progress=1)
Total 57 frames.
"""
import os
import glob
from PIL import Image

FRAMES_DIR = r"D:\Projects\ууу\assets\frames_k75"
OUT_DIR = r"D:\Projects\ууу\assets\frames_scrub"

os.makedirs(OUT_DIR, exist_ok=True)

def generate_scrub_sequence():
    # Assembled frame is 68, exploded frame is 12
    # Scroll down progresses from 68 down to 12
    frame_indices = list(range(68, 11, -1)) # 68, 67, ..., 12 (57 frames)
    print(f">>> Converting {len(frame_indices)} frames from {FRAMES_DIR} to WebP in {OUT_DIR}...")
    
    total_bytes = 0
    for idx, fnum in enumerate(frame_indices):
        src_path = os.path.join(FRAMES_DIR, f"frame_{fnum:04d}.png")
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"Missing source frame: {src_path}")
            
        dst_path = os.path.join(OUT_DIR, f"k75_scrub_{idx:02d}.webp")
        with Image.open(src_path) as im:
            # Save as optimized RGBA WebP with alpha transparency
            im.save(dst_path, format="WEBP", quality=85, method=4)
            size = os.path.getsize(dst_path)
            total_bytes += size
            
    print(f">>> Successfully generated {len(frame_indices)} scrub frames!")
    print(f">>> Total sequence size: {total_bytes / (1024 * 1024):.2f} MB (avg {total_bytes / len(frame_indices) / 1024:.1f} KB/frame)")

if __name__ == "__main__":
    generate_scrub_sequence()
