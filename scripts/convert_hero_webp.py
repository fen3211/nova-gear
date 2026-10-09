import os
import glob
from PIL import Image
import subprocess

RAW_DIR = r"D:\Projects\ууу\assets\staging\hero_raw"
OUT_DIR = r"D:\Projects\ууу\assets\frames_hero"
REVIEW_DIR = r"D:\Projects\ууу\review"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(REVIEW_DIR, exist_ok=True)

pngs = sorted(glob.glob(os.path.join(RAW_DIR, "hero_raw_*.png")))
print(f"Found {len(pngs)} raw hero frames.")

for i, p in enumerate(pngs):
    im = Image.open(p)
    # Ensure RGBA
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    
    out_name = f"k75_hero_{i:02d}.webp"
    out_path = os.path.join(OUT_DIR, out_name)
    im.save(out_path, format="WEBP", quality=90, method=6)
    
    if i % 10 == 0 or i == len(pngs) - 1:
        print(f"Saved {out_name} ({os.path.getsize(out_path)//1024} KB)")

# Also create a composite MP4 video on warm studio background for video demo
print("Generating hero_cinematic_demonstration.mp4...")
video_path = os.path.join(REVIEW_DIR, "hero_cinematic_demonstration.mp4")

# We can use ffmpeg with warm editorial background:
# ffmpeg -framerate 24 -i hero_raw_%02d.png -filter_complex "[0:v]format=rgba,pad=1200:800:color=#F4F1E9[v]" -c:v libx264 -pix_fmt yuv420p video.mp4
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-framerate", "20",
    "-i", os.path.join(RAW_DIR, "hero_raw_%02d.png"),
    "-filter_complex", "color=c=#F4F1E9:s=1200x800:d=2.8[bg];[bg][0:v]overlay=0:0:format=auto[v]",
    "-map", "[v]",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    video_path
]

try:
    res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"Created video demo: {video_path} ({os.path.getsize(video_path)//1024} KB)")
    else:
        print("FFmpeg warning:", res.stderr[-200:])
except Exception as e:
    print("FFmpeg error:", e)

print("Conversion complete!")
