"""
Composites V8 raw renders over calibrated editorial canvas #EBE8E1
and generates 300x300 catalog thumbnail with Lanczos resampling.
"""
import os
from PIL import Image

PREVIEWS_DIR = r"D:\Projects\ууу\assets\previews"
BG_COLOR = (235, 232, 225, 255) # Exact #EBE8E1

def composite_image(raw_name, out_name):
    raw_path = os.path.join(PREVIEWS_DIR, raw_name)
    out_path = os.path.join(PREVIEWS_DIR, out_name)
    
    if not os.path.exists(raw_path):
        print(f"Error: {raw_path} not found")
        return
        
    img = Image.open(raw_path).convert("RGBA")
    bg = Image.new("RGBA", img.size, BG_COLOR)
    final = Image.alpha_composite(bg, img).convert("RGB")
    final.save(out_path, "PNG", optimize=True)
    print(f"Composited & Saved: {out_path} ({final.size[0]}x{final.size[1]})")

def make_thumbnail(hero_name, thumb_name, size=(300, 300)):
    hero_path = os.path.join(PREVIEWS_DIR, hero_name)
    thumb_path = os.path.join(PREVIEWS_DIR, thumb_name)
    
    if not os.path.exists(hero_path):
        print(f"Error: {hero_path} not found")
        return
        
    hero = Image.open(hero_path)
    thumb = hero.resize(size, Image.Resampling.LANCZOS)
    thumb.save(thumb_path, "PNG", optimize=True)
    print(f"Generated Thumbnail: {thumb_path} ({size[0]}x{size[1]})")

if __name__ == "__main__":
    composite_image("flux_charger_v8_hero_raw.png", "flux_charger_v8_hero.png")
    composite_image("flux_charger_v8_macro_raw.png", "flux_charger_v8_macro_usbc.png")
    make_thumbnail("flux_charger_v8_hero.png", "flux_charger_v8_hero_300x300.png")
    print("All V8 exports complete!")
