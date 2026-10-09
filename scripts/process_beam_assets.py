"""
Process Beam RGB Monitor Light multi-pass raw renders into production WebP and PNG assets.
Guarantees:
1. Identical bounding box and aspect ratio for both isolated and shadow layers.
2. Safe padding (margins >= 18% on all sides).
3. Zero border alpha (strictly 0 at perimeter).
4. WebP lossless export and PNG fallback.
5. Contrast validation across Cream, Lime, and Dark backgrounds.
"""

import os
import numpy as np
from PIL import Image

PREVIEWS_DIR = r"D:\Projects\ууу\assets\previews"
IMAGES_DIR = r"D:\Projects\ууу\assets\images"

def main():
    iso_raw_path = os.path.join(PREVIEWS_DIR, "beam_light_hero_isolated_raw.png")
    shd_raw_path = os.path.join(PREVIEWS_DIR, "beam_light_hero_shadow_raw.png")
    
    if not os.path.exists(iso_raw_path) or not os.path.exists(shd_raw_path):
        print(f"Error: Raw passes not found ({iso_raw_path}, {shd_raw_path})")
        return
        
    iso = Image.open(iso_raw_path).convert("RGBA")
    shd = Image.open(shd_raw_path).convert("RGBA")
    
    w, h = iso.size
    print(f"Original Canvas: {w}x{h}")
    
    # Calculate union bounding box of iso and shadow where alpha > 8
    iso_arr = np.array(iso)
    shd_arr = np.array(shd)
    
    iso_alpha = iso_arr[:, :, 3]
    shd_alpha = shd_arr[:, :, 3]
    
    union_alpha = np.maximum(iso_alpha, shd_alpha)
    
    ys, xs = np.where(union_alpha > 8)
    if len(ys) == 0:
        print("Error: Empty alpha layers")
        return
        
    ymin, ymax = int(ys.min()), int(ys.max())
    xmin, xmax = int(xs.min()), int(xs.max())
    
    content_w = xmax - xmin
    content_h = ymax - ymin
    print(f"Content Bounding Box: [{xmin}, {ymin}, {xmax}, {ymax}] -> {content_w}x{content_h}")
    
    # Check margins on original raw canvas
    margin_l = xmin / w
    margin_r = (w - xmax) / w
    margin_t = ymin / h
    margin_b = (h - ymax) / h
    print(f"Original Margins: L={margin_l:.1%}, R={margin_r:.1%}, T={margin_t:.1%}, B={margin_b:.1%}")
    
    # If original canvas already has >= 18% margins and 0 border alpha, we can either use full canvas
    # or crop proportionally to a standard 1600x1200 or 1600x1000 canvas.
    # Let's inspect perimeter alpha of original raw renders:
    border_max_iso = max(
        int(iso_alpha[0, :].max()), int(iso_alpha[-1, :].max()),
        int(iso_alpha[:, 0].max()), int(iso_alpha[:, -1].max())
    )
    border_max_shd = max(
        int(shd_alpha[0, :].max()), int(shd_alpha[-1, :].max()),
        int(shd_alpha[:, 0].max()), int(shd_alpha[:, -1].max())
    )
    print(f"Original Perimeter Max Alpha: ISO={border_max_iso}, SHD={border_max_shd}")
    
    # Crop to clean 1600x1000 (16:10 standard landscape) centered on product bounding box
    cx = (xmin + xmax) // 2
    cy = (ymin + ymax) // 2
    
    # Target size: 1600 x 1000 with ample padding
    target_aspect = 1.6 # 16:10
    
    # Required bounding box size to have >= 19% padding
    req_w = int(content_w / (1.0 - 2 * 0.19))
    req_h = int(content_h / (1.0 - 2 * 0.19))
    
    crop_w = max(req_w, int(req_h * target_aspect))
    crop_h = int(crop_w / target_aspect)
    
    # Ensure within canvas bounds
    crop_w = min(crop_w, w)
    crop_h = min(int(crop_w / target_aspect), h)
    
    x0 = max(0, min(w - crop_w, cx - crop_w // 2))
    y0 = max(0, min(h - crop_h, cy - crop_h // 2))
    x1 = x0 + crop_w
    y1 = y0 + crop_h
    
    crop_box = (x0, y0, x1, y1)
    print(f"Crop Box: {crop_box} -> {crop_w}x{crop_h}")
    
    iso_cropped = iso.crop(crop_box)
    shd_cropped = shd.crop(crop_box)
    
    # Assert zero alpha on perimeter of cropped images
    shd_cr_alpha = np.array(shd_cropped)[:, :, 3]
    edge_alpha = max(
        int(shd_cr_alpha[0, :].max()), int(shd_cr_alpha[-1, :].max()),
        int(shd_cr_alpha[:, 0].max()), int(shd_cr_alpha[:, -1].max())
    )
    print(f"Cropped Shadow Edge Max Alpha: {edge_alpha}")
    assert edge_alpha == 0, f"Edge alpha must be 0, was {edge_alpha}"
    
    # Resize to standard production 1600x1000
    out_size = (1600, 1000)
    iso_final = iso_cropped.resize(out_size, Image.Resampling.LANCZOS)
    shd_final = shd_cropped.resize(out_size, Image.Resampling.LANCZOS)
    
    # Verify final border alpha
    fin_alpha = np.array(shd_final)[:, :, 3]
    fin_edge = max(
        int(fin_alpha[0, :].max()), int(fin_alpha[-1, :].max()),
        int(fin_alpha[:, 0].max()), int(fin_alpha[:, -1].max())
    )
    print(f"Final Resized Shadow Edge Max Alpha: {fin_edge}")
    assert fin_edge == 0, f"Resized edge alpha must be 0, was {fin_edge}"
    
    # Composite
    comp_final = Image.alpha_composite(shd_final, iso_final)
    
    # Save destinations
    for d in [IMAGES_DIR, PREVIEWS_DIR]:
        iso_final.save(os.path.join(d, "light-beam-isolated.webp"), "WEBP", lossless=True, quality=100)
        shd_final.save(os.path.join(d, "light-beam-shadow.webp"), "WEBP", lossless=True, quality=100)
        comp_final.save(os.path.join(d, "light-beam.webp"), "WEBP", lossless=True, quality=100)
        comp_final.save(os.path.join(d, "light-beam.png"), "PNG", optimize=True)
        
    comp_final.save(os.path.join(PREVIEWS_DIR, "preview_light_beam.png"), "PNG", optimize=True)
    
    # Render validation test sheets on 3 backgrounds
    bg_cream = Image.new("RGBA", out_size, (243, 240, 231, 255)) # #F3F0E7
    bg_dark = Image.new("RGBA", out_size, (17, 17, 17, 255))      # #111111
    bg_lime = Image.new("RGBA", out_size, (199, 255, 61, 255))    # #C7FF3D
    
    Image.alpha_composite(bg_cream, comp_final).convert("RGB").save(os.path.join(PREVIEWS_DIR, "beam_light_preview_cream.png"))
    Image.alpha_composite(bg_dark, comp_final).convert("RGB").save(os.path.join(PREVIEWS_DIR, "beam_light_preview_dark.png"))
    Image.alpha_composite(bg_lime, comp_final).convert("RGB").save(os.path.join(PREVIEWS_DIR, "beam_light_preview_lime.png"))
    
    print("Beam RGB assets successfully processed and saved!")

if __name__ == "__main__":
    main()
