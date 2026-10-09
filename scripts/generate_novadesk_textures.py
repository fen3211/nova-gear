"""
High-Contrast Tactile 4K Texture Generator for NovaDesk XL
Generates:
1. novadesk_felt_albedo.png (4096x2048) - 120,000 discrete heathered wool fibers
2. novadesk_felt_normal.png (4096x2048) - High-relief tactile microfiber normal map
3. novadesk_felt_roughness.png (4096x2048)
4. novadesk_leather_albedo.png (2048x1024) - Rich Cognac leather with hot-stamped branding
5. novadesk_leather_normal.png (2048x1024) - Grain and crease normal map
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TEXTURES_DIR = r"D:\Projects\ууу\assets\textures"
FONTS_DIR = r"C:\Windows\Fonts"
FONT_HEADING = os.path.join(FONTS_DIR, "segoeuib.ttf")

os.makedirs(TEXTURES_DIR, exist_ok=True)

def generate_tactile_felt():
    print("Generating High-Contrast 4K Heathered Merino Wool Textures...")
    w, h = 4096, 2048
    np.random.seed(777)
    
    # 1. Base Wool Clump Noise (Macro clouds)
    low_w, low_h = 256, 128
    low = np.random.uniform(0.3, 0.7, (low_h, low_w)).astype(np.float32)
    low_full = np.array(Image.fromarray(np.uint8(low * 255)).resize((w, h), Image.Resampling.BICUBIC), dtype=np.float32) / 255.0
    
    # 2. Dense Wool Fibers Layer (120,000 distinct fiber hairs)
    fiber_img = Image.new("L", (w, h), 128)
    draw_f = ImageDraw.Draw(fiber_img)
    
    n_fibers = 120000
    xs = np.random.randint(0, w, n_fibers)
    ys = np.random.randint(0, h, n_fibers)
    lens = np.random.randint(12, 38, n_fibers)
    angles = np.random.uniform(0, 2 * math.pi, n_fibers)
    curvs = np.random.uniform(-0.8, 0.8, n_fibers)
    
    # 5 distinct heather fiber classes: deep charcoal, slate gray, ash gray, silver fleck, black
    shades = np.random.choice([25, 60, 95, 140, 185, 230], size=n_fibers, p=[0.25, 0.25, 0.20, 0.15, 0.10, 0.05])
    
    for i in range(n_fibers):
        x0, y0 = xs[i], ys[i]
        ln = lens[i]
        ang = angles[i]
        c = curvs[i]
        sh = int(shades[i])
        
        # Curved fiber strand
        x1 = x0 + ln * 0.5 * math.cos(ang)
        y1 = y0 + ln * 0.5 * math.sin(ang)
        x2 = x0 + ln * math.cos(ang + c)
        y2 = y0 + ln * math.sin(ang + c)
        
        draw_f.line([(x0, y0), (x1, y1), (x2, y2)], fill=sh, width=1)
        
    fiber_arr = np.array(fiber_img, dtype=np.float32) / 255.0
    
    # Micro noise
    micro = np.random.normal(0.5, 0.15, (h, w)).astype(np.float32)
    micro = np.clip(micro, 0.0, 1.0)
    
    # Heightmap
    height = low_full * 0.25 + fiber_arr * 0.55 + micro * 0.20
    height = np.clip(height, 0.0, 1.0)
    
    # Albedo Color Mapping (Punchy heathered anthracite wool)
    # Deepest base: #181A1E (24, 26, 30)
    # Mid-tone heather: #2E323A (46, 50, 58)
    # Highlight silver-ash: #5A6070 (90, 96, 112)
    r = (height * 66 + 24).astype(np.uint8)
    g = (height * 70 + 26).astype(np.uint8)
    b = (height * 82 + 30).astype(np.uint8)
    
    albedo = Image.merge("RGB", (Image.fromarray(r), Image.fromarray(g), Image.fromarray(b)))
    albedo_path = os.path.join(TEXTURES_DIR, "novadesk_felt_albedo.png")
    albedo.save(albedo_path, "PNG", optimize=True)
    print(f"Saved: {albedo_path}")
    
    # Tactile Normal Map (Enhanced gradient multiplier for tactile relief)
    gx = np.zeros_like(height)
    gy = np.zeros_like(height)
    gx[:, 1:-1] = (height[:, 2:] - height[:, :-2]) * 0.5
    gy[1:-1, :] = (height[2:, :] - height[:-2, :]) * 0.5
    
    bump_mult = 4.2
    nx = -gx * bump_mult
    ny = -gy * bump_mult
    nz = np.ones_like(height)
    norm = np.sqrt(nx*nx + ny*ny + nz*nz)
    nx /= norm
    ny /= norm
    nz /= norm
    
    norm_r = np.uint8(np.clip((nx * 0.5 + 0.5) * 255, 0, 255))
    norm_g = np.uint8(np.clip((ny * 0.5 + 0.5) * 255, 0, 255))
    norm_b = np.uint8(np.clip((nz * 0.5 + 0.5) * 255, 0, 255))
    normal_img = Image.merge("RGB", (Image.fromarray(norm_r), Image.fromarray(norm_g), Image.fromarray(norm_b)))
    normal_path = os.path.join(TEXTURES_DIR, "novadesk_felt_normal.png")
    normal_img.save(normal_path, "PNG", optimize=True)
    print(f"Saved: {normal_path}")
    
    # Roughness Map (0.86 - 0.98)
    rough = np.uint8(np.clip((0.86 + height * 0.12) * 255, 0, 255))
    rough_img = Image.fromarray(rough, mode='L')
    rough_path = os.path.join(TEXTURES_DIR, "novadesk_felt_roughness.png")
    rough_img.save(rough_path, "PNG", optimize=True)
    print(f"Saved: {rough_path}")

def generate_leather():
    print("Generating High-Res Leather Textures...")
    w, h = 2048, 1024
    np.random.seed(999)
    
    # Leather grain
    pore = np.random.uniform(0.4, 0.6, (256, 128)).astype(np.float32)
    pore_img = Image.fromarray(np.uint8(pore * 255)).resize((w, h), Image.Resampling.BICUBIC)
    pore_arr = np.array(pore_img, dtype=np.float32) / 255.0
    
    fine = np.random.normal(0.5, 0.10, (h, w)).astype(np.float32)
    grain = np.clip(pore_arr * 0.5 + fine * 0.5, 0.0, 1.0)
    
    # Rich deep Cognac / Whiskey leather
    r = (grain * 32 + 74).astype(np.uint8) # 74..106
    g = (grain * 20 + 36).astype(np.uint8) # 36..56
    b = (grain * 12 + 16).astype(np.uint8) # 16..28
    
    badge_albedo = Image.merge("RGB", (Image.fromarray(r), Image.fromarray(g), Image.fromarray(b)))
    draw = ImageDraw.Draw(badge_albedo)
    
    # Hot-stamped blind deboss branding: "NOVA // DESK XL"
    font_logo = ImageFont.truetype(FONT_HEADING, 54)
    font_sub = ImageFont.truetype(FONT_HEADING, 24)
    
    # Positioned nicely in the middle-right area
    text_cx = int(w * 0.56)
    text_cy = int(h * 0.44)
    
    burnish = (36, 14, 6) # Dark burnished brown
    draw.text((text_cx, text_cy), "NOVA", fill=burnish, font=font_logo, anchor="mm")
    draw.text((text_cx, text_cy + 42), "DESK XL // MERINO", fill=burnish, font=font_sub, anchor="mm")
    
    # Heat creasing line
    draw.rounded_rectangle([(35, 35), (w - 35, h - 35)], radius=50, outline=burnish, width=3)
    
    leather_albedo_path = os.path.join(TEXTURES_DIR, "novadesk_leather_albedo.png")
    badge_albedo.save(leather_albedo_path, "PNG", optimize=True)
    print(f"Saved: {leather_albedo_path}")
    
    # Leather Normal Map
    gx = np.zeros_like(grain)
    gy = np.zeros_like(grain)
    gx[:, 1:-1] = (grain[:, 2:] - grain[:, :-2]) * 0.5
    gy[1:-1, :] = (grain[2:, :] - grain[:-2, :]) * 0.5
    
    bump_mult = 2.0
    nx = -gx * bump_mult
    ny = -gy * bump_mult
    nz = np.ones_like(grain)
    norm = np.sqrt(nx*nx + ny*ny + nz*nz)
    nx /= norm
    ny /= norm
    nz /= norm
    
    norm_r = np.uint8(np.clip((nx * 0.5 + 0.5) * 255, 0, 255))
    norm_g = np.uint8(np.clip((ny * 0.5 + 0.5) * 255, 0, 255))
    norm_b = np.uint8(np.clip((nz * 0.5 + 0.5) * 255, 0, 255))
    leather_norm = Image.merge("RGB", (Image.fromarray(norm_r), Image.fromarray(norm_g), Image.fromarray(norm_b)))
    leather_norm_path = os.path.join(TEXTURES_DIR, "novadesk_leather_normal.png")
    leather_norm.save(leather_norm_path, "PNG", optimize=True)
    print(f"Saved: {leather_norm_path}")

if __name__ == "__main__":
    generate_tactile_felt()
    generate_leather()
    print("Tactile textures updated!")
