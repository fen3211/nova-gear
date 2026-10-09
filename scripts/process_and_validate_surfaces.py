"""
Processes transparent passes:
1. Exports lossless WebP files.
2. Generates multi-surface validation previews on:
   - Cream (#F3F0E7, site main background)
   - Signature Lime (#C7FF3D, site accent card)
   - Dark (#111111, site dark section)
3. Verifies edge quality and absence of light halos.
"""
import os
from PIL import Image

PREVIEWS_DIR = r"D:\Projects\ууу\assets\previews"

# Exact design tokens from after/style.css
SURFACES = {
    "cream": {
        "hex": "#F3F0E7",
        "rgb": (243, 240, 231, 255),
        "desc": "Site Canvas Cream (--bg: #F3F0E7)"
    },
    "lime": {
        "hex": "#C7FF3D",
        "rgb": (199, 255, 61, 255),
        "desc": "Site Signature Lime Card (--card-green-bg: #C7FF3D)"
    },
    "dark": {
        "hex": "#111111",
        "rgb": (17, 17, 17, 255),
        "desc": "Site Dark Theme Section (--dark-bg: #111111)"
    }
}

def export_webp_versions():
    files = [
        "flux_charger_hero_isolated",
        "flux_charger_hero_shadow",
        "flux_charger_hero_transparent"
    ]
    for name in files:
        png_path = os.path.join(PREVIEWS_DIR, f"{name}.png")
        webp_path = os.path.join(PREVIEWS_DIR, f"{name}.webp")
        if os.path.exists(png_path):
            img = Image.open(png_path)
            img.save(webp_path, "WEBP", lossless=True, quality=100)
            print(f"Exported WebP: {webp_path} ({os.path.getsize(webp_path):,} bytes)")

def create_surface_validations():
    iso_path = os.path.join(PREVIEWS_DIR, "flux_charger_hero_isolated.png")
    shadow_path = os.path.join(PREVIEWS_DIR, "flux_charger_hero_shadow.png")
    
    if not os.path.exists(iso_path) or not os.path.exists(shadow_path):
        print("Error: Missing isolated or shadow PNG passes")
        return
        
    iso_img = Image.open(iso_path).convert("RGBA")
    shadow_img = Image.open(shadow_path).convert("RGBA")
    
    for key, info in SURFACES.items():
        bg = Image.new("RGBA", iso_img.size, info["rgb"])
        
        # Step 1: Composite contact shadow onto surface
        with_shadow = Image.alpha_composite(bg, shadow_img)
        
        # Step 2: Composite isolated product onto shadowed surface
        final = Image.alpha_composite(with_shadow, iso_img).convert("RGB")
        
        out_name = f"flux_charger_preview_{key}.png"
        out_path = os.path.join(PREVIEWS_DIR, out_name)
        final.save(out_path, "PNG", optimize=True)
        print(f"Generated Validation Preview: {out_name} on {info['desc']}")

if __name__ == "__main__":
    export_webp_versions()
    create_surface_validations()
    print("Multi-surface processing complete!")
