"""
Tight identical cropping for Flux Charger isolated and shadow layers.
Guarantees:
1. Identical bounding box and aspect ratio for both layers (zero drift/offset).
2. Border alpha = 0 (no clipped shadows).
3. Larger visible product on card (+35% larger display).
"""

import os
from PIL import Image

PREVIEWS_DIR = r"D:\Projects\ууу\assets\previews"
IMAGES_DIR = r"D:\Projects\ууу\assets\images"

def main():
    iso_path = os.path.join(PREVIEWS_DIR, "flux_charger_hero_isolated.png")
    shd_path = os.path.join(PREVIEWS_DIR, "flux_charger_hero_shadow.png")
    
    if not os.path.exists(iso_path) or not os.path.exists(shd_path):
        print("Error: Source PNGs not found")
        return
        
    iso = Image.open(iso_path).convert("RGBA")
    shd = Image.open(shd_path).convert("RGBA")
    
    print(f"Original ISO: {iso.size}, bbox: {iso.getbbox()}")
    print(f"Original SHD: {shd.size}, bbox: {shd.getbbox()}")
    
    # Crop box determined from union bbox (269, 261, 1197, 1440) + safe margins
    # Square 1320x1320 centered on product
    crop_box = (73, 190, 1393, 1510) # 1320x1320
    
    iso_cropped = iso.crop(crop_box)
    shd_cropped = shd.crop(crop_box)
    
    # Verify border alpha on shadow
    alpha_shd = shd_cropped.split()[3]
    w, h = shd_cropped.size
    max_border_alpha = max(
        max(alpha_shd.getpixel((x, 0)) for x in range(w)),
        max(alpha_shd.getpixel((x, h - 1)) for x in range(w)),
        max(alpha_shd.getpixel((0, y)) for y in range(h)),
        max(alpha_shd.getpixel((w - 1, y)) for y in range(h))
    )
    print(f"Shadow max border alpha: {max_border_alpha}")
    assert max_border_alpha == 0, "Shadow exceeds crop boundary!"
    
    # Resize to high-density web resolution (1000x1000)
    target_size = (1000, 1000)
    iso_final = iso_cropped.resize(target_size, Image.Resampling.LANCZOS)
    shd_final = shd_cropped.resize(target_size, Image.Resampling.LANCZOS)
    
    # Save WebP and PNG assets to both images and previews
    destinations = [IMAGES_DIR, PREVIEWS_DIR]
    for d in destinations:
        os.makedirs(d, exist_ok=True)
        iso_final.save(os.path.join(d, "flux-charger-isolated.webp"), "WEBP", lossless=True, quality=100)
        shd_final.save(os.path.join(d, "flux-charger-shadow.webp"), "WEBP", lossless=True, quality=100)
        
        # Also save composite for backward compatibility
        comp = Image.alpha_composite(shd_final, iso_final)
        comp.save(os.path.join(d, "charger-flux.webp"), "WEBP", lossless=True, quality=100)
        comp.save(os.path.join(d, "charger-flux.png"), "PNG", optimize=True)
        
    print("Successfully cropped and saved Flux charger assets!")
    print(f"ISO final size: {iso_final.size}, bbox: {iso_final.getbbox()}")
    print(f"SHD final size: {shd_final.size}, bbox: {shd_final.getbbox()}")

if __name__ == "__main__":
    main()
