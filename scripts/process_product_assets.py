"""
NOVA Gear // Product Asset Post-Processing & Alpha Normalization Suite
Uses system Python (Pillow + numpy) for zero-border ramp, matching canvas crop,
dual-layer RGBA isolated + shadow catcher combination, and WebP lossless/high-Q export.
"""

import os
import sys
import math
import numpy as np
from PIL import Image

PROJECT_ROOT = r"D:\Projects\ууу"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "assets", "previews")
IMAGES_DIR = os.path.join(PROJECT_ROOT, "assets", "images")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def apply_zero_border_ramp(shd_img, border_fade_px=24):
    arr = np.array(shd_img).copy()
    h, w, c = arr.shape
    alpha = arr[:, :, 3].astype(np.float32)
    x_fade = np.ones(w, dtype=np.float32)
    y_fade = np.ones(h, dtype=np.float32)
    for i in range(border_fade_px):
        weight = 0.5 * (1.0 - math.cos(math.pi * (i / float(border_fade_px))))
        x_fade[i] = weight
        x_fade[w - 1 - i] = weight
    for i in range(border_fade_px):
        weight = 0.5 * (1.0 - math.cos(math.pi * (i / float(border_fade_px))))
        y_fade[i] = weight
        y_fade[h - 1 - i] = weight
    grid_fade = np.outer(y_fade, x_fade)
    alpha = alpha * grid_fade
    arr[:, :, 3] = np.clip(alpha, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def process_dual_layer(iso_raw_path, shd_raw_path, base_name, target_size=(1600, 1200), padding_margin=0.18):
    print(f"\n--- Processing Dual-Layer: {base_name} ---")
    if not os.path.exists(iso_raw_path) or not os.path.exists(shd_raw_path):
        raise FileNotFoundError(f"Missing raw passes: {iso_raw_path} or {shd_raw_path}")
        
    iso_raw = Image.open(iso_raw_path).convert("RGBA")
    shd_raw = Image.open(shd_raw_path).convert("RGBA")
    
    shd_clean = apply_zero_border_ramp(shd_raw, border_fade_px=28)
    
    iso_a = np.array(iso_raw)[:, :, 3]
    shd_a = np.array(shd_clean)[:, :, 3]
    union_a = np.maximum(iso_a, shd_a)
    
    ys, xs = np.where(union_a > 4)
    if len(ys) == 0:
        raise ValueError(f"Empty alpha for {base_name}")
        
    ymin, ymax = int(ys.min()), int(ys.max())
    xmin, xmax = int(xs.min()), int(xs.max())
    content_w = xmax - xmin
    content_h = ymax - ymin
    cx = (xmin + xmax) // 2
    cy = (ymin + ymax) // 2
    
    avail_w = int(target_size[0] * (1.0 - padding_margin * 2.0))
    avail_h = int(target_size[1] * (1.0 - padding_margin * 2.0))
    scale = min(avail_w / float(content_w), avail_h / float(content_h))
    
    crop_w = int(target_size[0] / scale)
    crop_h = int(target_size[1] / scale)
    
    box_x0 = cx - crop_w // 2
    box_y0 = cy - crop_h // 2
    box_x1 = box_x0 + crop_w
    box_y1 = box_y0 + crop_h
    
    pad_left = max(0, -box_x0)
    pad_top = max(0, -box_y0)
    pad_right = max(0, box_x1 - iso_raw.width)
    pad_bottom = max(0, box_y1 - iso_raw.height)
    
    if any([pad_left, pad_top, pad_right, pad_bottom]):
        new_w = iso_raw.width + pad_left + pad_right
        new_h = iso_raw.height + pad_top + pad_bottom
        
        iso_exp = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
        iso_exp.paste(iso_raw, (pad_left, pad_top))
        iso_raw = iso_exp
        
        shd_exp = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
        shd_exp.paste(shd_clean, (pad_left, pad_top))
        shd_clean = shd_exp
        
        box_x0 += pad_left
        box_x1 += pad_left
        box_y0 += pad_top
        box_y1 += pad_top
        
    iso_cropped = iso_raw.crop((box_x0, box_y0, box_x1, box_y1)).resize(target_size, Image.Resampling.LANCZOS)
    shd_cropped = shd_clean.crop((box_x0, box_y0, box_x1, box_y1)).resize(target_size, Image.Resampling.LANCZOS)
    
    iso_final = apply_zero_border_ramp(iso_cropped, border_fade_px=8)
    shd_final = apply_zero_border_ramp(shd_cropped, border_fade_px=24)
    
    comb = Image.new("RGBA", target_size, (0, 0, 0, 0))
    comb.alpha_composite(shd_final)
    comb.alpha_composite(iso_final)
    
    # Save outputs
    iso_webp = os.path.join(IMAGES_DIR, f"{base_name}-isolated.webp")
    shd_webp = os.path.join(IMAGES_DIR, f"{base_name}-shadow.webp")
    comb_png = os.path.join(IMAGES_DIR, f"{base_name}.png")
    comb_webp = os.path.join(IMAGES_DIR, f"{base_name}.webp")
    
    iso_final.save(iso_webp, "WEBP", quality=95, method=6)
    shd_final.save(shd_webp, "WEBP", quality=95, method=6)
    comb.save(comb_png, "PNG")
    comb.save(comb_webp, "WEBP", quality=95, method=6)
    
    # Preview with cream studio backdrop
    backdrop = Image.new("RGBA", target_size, (243, 240, 231, 255))
    backdrop.alpha_composite(comb)
    prev_path = os.path.join(OUTPUT_DIR, f"preview_{base_name}.png")
    backdrop.convert("RGB").save(prev_path, "PNG")
    
    print(f"[OK] Isolated layer: {iso_webp}")
    print(f"[OK] Shadow layer:   {shd_webp}")
    print(f"[OK] Combined asset: {comb_png}")
    print(f"[OK] Studio preview: {prev_path}")
    return comb

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        iso_p = sys.argv[1]
        shd_p = sys.argv[2]
        name = sys.argv[3]
        pad = float(sys.argv[4]) if len(sys.argv) > 4 else 0.18
        process_dual_layer(iso_p, shd_p, name, padding_margin=pad)
    else:
        print("Usage: python process_product_assets.py <iso_raw> <shd_raw> <base_name> [padding_margin]")
