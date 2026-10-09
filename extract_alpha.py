import os
from PIL import Image
from rembg import remove, new_session

img_dir = r"D:\Projects\ууу\assets\images"
session = new_session("u2net")

targets = ["keyboard-k75", "mouse-pulse", "headphones-orbit"]

for name in targets:
    src = os.path.join(img_dir, f"{name}.jpg")
    dst = os.path.join(img_dir, f"{name}.png")
    if os.path.exists(src):
        print(f"Processing {src} -> {dst}...")
        img = Image.open(src)
        # remove background with alpha matting
        out = remove(img, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10)
        out.save(dst, "PNG")
        print(f"Saved {dst} ({out.size}, mode={out.mode})")
    else:
        print(f"Not found: {src}")

print("Alpha extraction complete!")
