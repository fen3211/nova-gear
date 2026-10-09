import os
import numpy as np
from PIL import Image

IMAGES_DIR = r"D:\Projects\ууу\assets\images"
PREVIEWS_DIR = r"D:\Projects\ууу\assets\previews"

products_to_tighten = {
    'k75': {
        'iso': 'keyboard-k75-isolated.webp',
        'shd': 'keyboard-k75-shadow.webp',
        'composite': 'keyboard-k75',
        'target_size': (1200, 800), # 3:2 aspect ratio for wide keyboard card
    },
    'pulse': {
        'iso': 'mouse-pulse-isolated.webp',
        'shd': 'mouse-pulse-shadow.webp',
        'composite': 'mouse-pulse',
        'target_size': (1000, 800), # 5:4 aspect ratio for vertical portrait card
    },
    'orbit': {
        'iso': 'headphones-orbit-isolated.webp',
        'shd': 'headphones-orbit-shadow.webp',
        'composite': 'headphones-orbit',
        'target_size': (1000, 900), # 10:9 aspect ratio for vertical portrait card
    },
    'beam': {
        'iso': 'light-beam-isolated.webp',
        'shd': 'light-beam-shadow.webp',
        'composite': 'light-beam',
        'target_size': (1200, 800), # 3:2 aspect ratio for panoramic card
    }
}

def tighten_product(name, cfg):
    iso_path = os.path.join(IMAGES_DIR, cfg['iso'])
    shd_path = os.path.join(IMAGES_DIR, cfg['shd'])
    
    if not os.path.exists(iso_path) or not os.path.exists(shd_path):
        print(f"Skipping {name}: files not found")
        return
        
    iso = Image.open(iso_path).convert("RGBA")
    shd = Image.open(shd_path).convert("RGBA")
    
    b_iso = iso.getbbox()
    b_shd = shd.getbbox()
    
    # Combined bbox
    b_union = (
        min(b_iso[0], b_shd[0]),
        min(b_iso[1], b_shd[1]),
        max(b_iso[2], b_shd[2]),
        max(b_iso[3], b_shd[3])
    )
    
    # Margin around union (tight ~24px for shadow breathing room)
    margin = 28
    w, h = iso.size
    
    crop_x1 = max(0, b_union[0] - margin)
    crop_y1 = max(0, b_union[1] - margin)
    crop_x2 = min(w, b_union[2] + margin)
    crop_y2 = min(h, b_union[3] + margin)
    
    crop_box = (crop_x1, crop_y1, crop_x2, crop_y2)
    print(f"\n[{name.upper()}] original size: {iso.size}, union: {b_union}, crop_box: {crop_box}")
    
    iso_c = iso.crop(crop_box)
    shd_c = shd.crop(crop_box)
    
    # Ensure zero alpha at the 4 borders for the shadow layer
    shd_arr = np.array(shd_c)
    # Cosine ramp feather at the very edges (12px) if any slight residual alpha touches border
    alpha = shd_arr[:, :, 3].astype(np.float32)
    cw, ch = shd_c.size
    ramp = 14
    for i in range(ramp):
        factor = 0.5 * (1.0 - np.cos(np.pi * (i + 1) / ramp))
        # top & bottom
        alpha[i, :] *= factor
        alpha[ch - 1 - i, :] *= factor
        # left & right
        alpha[:, i] *= factor
        alpha[:, cw - 1 - i] *= factor
        
    # Force exact 0 on outermost 1px perimeter
    alpha[0, :] = 0
    alpha[-1, :] = 0
    alpha[:, 0] = 0
    alpha[:, -1] = 0
    shd_arr[:, :, 3] = np.clip(alpha, 0, 255).astype(np.uint8)
    shd_c = Image.fromarray(shd_arr, "RGBA")
    
    # Resize to target web resolution
    target_w, target_h = cfg['target_size']
    iso_final = iso_c.resize((target_w, target_h), Image.Resampling.LANCZOS)
    shd_final = shd_c.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Verify border alpha
    shd_final_arr = np.array(shd_final)
    b_alpha = max(
        shd_final_arr[0, :, 3].max(),
        shd_final_arr[-1, :, 3].max(),
        shd_final_arr[:, 0, 3].max(),
        shd_final_arr[:, -1, 3].max()
    )
    print(f"[{name.upper()}] Final size: {iso_final.size}, Shadow border alpha: {b_alpha}")
    assert b_alpha == 0, f"Shadow border alpha is non-zero: {b_alpha}"
    
    # Calculate visible product fill ratio
    fb = iso_final.getbbox()
    fw = fb[2] - fb[0]
    fh = fb[3] - fb[1]
    fill_w = (fw / target_w) * 100
    fill_h = (fh / target_h) * 100
    max_fill = max(fill_w, fill_h)
    print(f"[{name.upper()}] Product bbox: {fb}, Width fill: {fill_w:.1f}%, Height fill: {fill_h:.1f}%, Dominant fill: {max_fill:.1f}%")
    
    # Save optimized WebP to IMAGES_DIR and PREVIEWS_DIR
    for d in [IMAGES_DIR, PREVIEWS_DIR]:
        iso_final.save(os.path.join(d, cfg['iso']), "WEBP", quality=90, method=4)
        shd_final.save(os.path.join(d, cfg['shd']), "WEBP", quality=90, method=4)
        
        comp = Image.alpha_composite(shd_final, iso_final)
        comp.save(os.path.join(d, f"{cfg['composite']}.webp"), "WEBP", quality=90, method=4)
        comp.save(os.path.join(d, f"{cfg['composite']}.png"), "PNG", optimize=True)

if __name__ == "__main__":
    for name, cfg in products_to_tighten.items():
        tighten_product(name, cfg)
    print("\n[OK] All product catalog assets successfully tightened with 0 border alpha and verified fill ratios!")
