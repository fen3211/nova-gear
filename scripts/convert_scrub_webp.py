import os
import glob
from PIL import Image

RAW_DIR = r"D:\Projects\ууу\assets\staging\scrub_raw"
OUT_DIR = r"D:\Projects\ууу\assets\frames_scrub"

os.makedirs(OUT_DIR, exist_ok=True)

total_bytes = 0
for idx in range(57):
    src = os.path.join(RAW_DIR, f"scrub_raw_{idx:02d}.png")
    dst = os.path.join(OUT_DIR, f"k75_scrub_{idx:02d}.webp")
    if not os.path.exists(src):
        raise FileNotFoundError(f"Missing {src}")
    
    with Image.open(src) as im:
        im.save(dst, format="WEBP", quality=88, method=4)
        total_bytes += os.path.getsize(dst)

print(f"[OK] 57 scrub WebP frames converted to {OUT_DIR}")
print(f"[OK] Total size: {total_bytes / (1024*1024):.2f} MB (avg {total_bytes / 57 / 1024:.1f} KB/frame)")

# Validate frame 00 and frame 56
with Image.open(os.path.join(OUT_DIR, "k75_scrub_00.webp")) as f0:
    bbox0 = f0.getbbox()
    w0 = bbox0[2] - bbox0[0]
    h0 = bbox0[3] - bbox0[1]
    print(f"Frame 00 (Assembled): bbox={bbox0}, width={w0} ({w0/720*100:.1f}%), height={h0} ({h0/720*100:.1f}%)")

with Image.open(os.path.join(OUT_DIR, "k75_scrub_56.webp")) as f56:
    bbox56 = f56.getbbox()
    w56 = bbox56[2] - bbox56[0]
    h56 = bbox56[3] - bbox56[1]
    print(f"Frame 56 (Exploded):  bbox={bbox56}, width={w56} ({w56/720*100:.1f}%), height={h56} ({h56/720*100:.1f}%)")
