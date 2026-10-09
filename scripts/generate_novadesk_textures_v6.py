"""
NovaDesk XL - Ultra-Detailed Tactile Texture Generator V6
Produces:
1. novadesk_leather_albedo.png (2200x650) - Rich vegetable-tanned cognac leather with hot-stamped deboss and heat crease
2. novadesk_leather_normal.png (2200x650) - Pore grain, sharp debossed typography, and heat crease relief
3. novadesk_leather_roughness.png (2200x650) - Satin leather with burnished deboss
4. novadesk_felt_albedo.png (4096x2048) - Rich dark anthracite heathered merino wool (150,000 distinct fibers)
5. novadesk_felt_normal.png (4096x2048) - High-relief tactile microfiber normal map
6. novadesk_felt_roughness.png (4096x2048)
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TEXTURES_DIR = r"D:\Projects\ууу\assets\textures"
FONTS_DIR = r"C:\Windows\Fonts"
FONT_HEADING = os.path.join(FONTS_DIR, "segoeuib.ttf")
FONT_REGULAR = os.path.join(FONTS_DIR, "segoeui.ttf")

os.makedirs(TEXTURES_DIR, exist_ok=True)

def generate_leather_v6():
    print("Generating NovaDesk Leather Textures V6 (2200x650)...")
    # Badge physical size: 88mm x 26mm -> 2200 x 650 (25 px / mm)
    w, h = 2200, 650
    np.random.seed(888)
    
    # 1. Base Full-Grain Leather Micro-Pores & Marbling
    # Low-frequency pull-up color variation
    low_w, low_h = 220, 65
    low_noise = np.random.uniform(0.35, 0.65, (low_h, low_w)).astype(np.float32)
    low_img = Image.fromarray(np.uint8(low_noise * 255)).resize((w, h), Image.Resampling.BICUBIC)
    low_arr = np.array(low_img, dtype=np.float32) / 255.0
    
    # High-frequency leather pore grain
    grain_raw = np.random.normal(0.5, 0.12, (h, w)).astype(np.float32)
    grain = np.clip(low_arr * 0.4 + grain_raw * 0.6, 0.0, 1.0)
    
    # Rich Cognac / English Saddle Tan Leather Palette:
    # Deep warm chestnut in pores, warm amber/cognac on raised grain
    # Dark tone: #4A2210 (74, 34, 16)
    # Mid tone: #8C4820 (140, 72, 32)
    # Highlight: #AD622D (173, 98, 45)
    r = (grain * 60 + 82).astype(np.uint8)
    g = (grain * 38 + 38).astype(np.uint8)
    b = (grain * 20 + 16).astype(np.uint8)
    
    leather_img = Image.merge("RGB", (Image.fromarray(r), Image.fromarray(g), Image.fromarray(b)))
    
    # 2. Draw Vector Branding & Heat Crease Lines
    # Scale: 25 px / mm
    # Inset heat crease line: 1.6 mm = 40 px from outer edge
    # Outer corner radius: 4.5 mm = 112 px -> crease corner radius = 72 px
    draw = ImageDraw.Draw(leather_img)
    
    burnish_color = (42, 18, 8) # Deep burnished dark espresso
    burnish_crease = (52, 22, 10)
    
    crease_margin = 40
    draw.rounded_rectangle(
        [(crease_margin, crease_margin), (w - crease_margin, h - crease_margin)],
        radius=72,
        outline=burnish_crease,
        width=5
    )
    
    # Slot position: Physical slot is 24mm x 6mm centered at X = 24mm (from left edge: 12..36mm)
    # In pixels: X center = 25 * 24 = 600 px. Slot width = 600 px, height = 150 px.
    slot_cx = 580
    slot_cy = h // 2
    slot_w_px = 580
    slot_h_px = 145
    slot_r_px = slot_h_px // 2 # Pill shape
    
    # Crease line around slot: 1.5mm offset = 38 px
    slot_crease_pad = 32
    draw.rounded_rectangle(
        [(slot_cx - slot_w_px//2 - slot_crease_pad, slot_cy - slot_h_px//2 - slot_crease_pad),
         (slot_cx + slot_w_px//2 + slot_crease_pad, slot_cy + slot_h_px//2 + slot_crease_pad)],
        radius=slot_r_px + slot_crease_pad,
        outline=burnish_crease,
        width=4
    )
    
    # Debossed Branding in Center-Right Area (between slot and brass rivet):
    # Rivet is centered at X = w - 25*14 = 2200 - 350 = 1850 px
    # Logo center around X = 1260 px
    logo_cx = 1260
    logo_cy = h // 2 - 20
    
    font_nova = ImageFont.truetype(FONT_HEADING, 76)
    font_sub = ImageFont.truetype(FONT_HEADING, 30)
    
    # 2b. Generate Deboss Mask first to burnish/flatten pores inside lettering
    mask_deboss = Image.new("L", (w, h), 0)
    draw_mask = ImageDraw.Draw(mask_deboss)
    
    # Heat crease lines in mask
    draw_mask.rounded_rectangle(
        [(crease_margin, crease_margin), (w - crease_margin, h - crease_margin)],
        radius=72,
        outline=180,
        width=5
    )
    draw_mask.rounded_rectangle(
        [(slot_cx - slot_w_px//2 - slot_crease_pad, slot_cy - slot_h_px//2 - slot_crease_pad),
         (slot_cx + slot_w_px//2 + slot_crease_pad, slot_cy + slot_h_px//2 + slot_crease_pad)],
        radius=slot_r_px + slot_crease_pad,
        outline=180,
        width=4
    )
    # Deep sharp typography deboss
    draw_mask.text((logo_cx, logo_cy), "NOVA", fill=255, font=font_nova, anchor="mm")
    draw_mask.text((logo_cx, logo_cy + 62), "DESK XL // MERINO WOOL", fill=240, font=font_sub, anchor="mm")
    
    # Rivet coordinates
    rivet_cx = 1860
    rivet_cy = h // 2
    rivet_rad = int(25 * 5.0) # 125 px
    
    # Rivet depression
    draw_mask.ellipse(
        [(rivet_cx - rivet_rad - 6, rivet_cy - rivet_rad - 6),
         (rivet_cx + rivet_rad + 6, rivet_cy + rivet_rad + 6)],
        outline=160,
        width=3
    )
    
    mask_deboss_blurred = mask_deboss.filter(ImageFilter.GaussianBlur(radius=1.5))
    deboss_arr = np.array(mask_deboss_blurred, dtype=np.float32) / 255.0
    
    # Flatten pores inside debossed impression (hot metal stamp compression)
    grain_compressed = grain * (1.0 - deboss_arr * 0.85)
    
    # Rich Cognac Palette with dark compressed burnish
    # Unpressed leather: warm amber cognac (r: 82..142, g: 38..76, b: 16..36)
    # Debossed area: dark polished burnish (r: 34, g: 14, b: 6)
    r = ((grain_compressed * 60 + 82) * (1.0 - deboss_arr * 0.72) + 28 * deboss_arr * 0.72).astype(np.uint8)
    g = ((grain_compressed * 38 + 38) * (1.0 - deboss_arr * 0.75) + 12 * deboss_arr * 0.75).astype(np.uint8)
    b = ((grain_compressed * 20 + 16) * (1.0 - deboss_arr * 0.75) + 6 * deboss_arr * 0.75).astype(np.uint8)
    
    leather_img = Image.merge("RGB", (Image.fromarray(r), Image.fromarray(g), Image.fromarray(b)))
    
    albedo_path = os.path.join(TEXTURES_DIR, "novadesk_leather_albedo.png")
    leather_img.save(albedo_path, "PNG", optimize=True)
    print(f"Saved: {albedo_path}")
    
    # 3. Height Map for Normal & Roughness Generation
    height = grain.copy() - deboss_arr * 0.55
    
    # Normal Map
    gx = np.zeros_like(height)
    gy = np.zeros_like(height)
    gx[:, 1:-1] = (height[:, 2:] - height[:, :-2]) * 0.5
    gy[1:-1, :] = (height[2:, :] - height[:-2, :]) * 0.5
    
    bump_mult = 3.5
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
    normal_path = os.path.join(TEXTURES_DIR, "novadesk_leather_normal.png")
    normal_img.save(normal_path, "PNG", optimize=True)
    print(f"Saved: {normal_path}")
    
    # Roughness Map: Satin leather (0.36), debossed areas are smoother/burnished (0.24)
    rough = np.clip(0.38 - deboss_arr * 0.14 + (grain - 0.5) * 0.08, 0.15, 0.60)
    rough_img = Image.fromarray(np.uint8(rough * 255), mode='L')
    rough_path = os.path.join(TEXTURES_DIR, "novadesk_leather_roughness.png")
    rough_img.save(rough_path, "PNG", optimize=True)
    print(f"Saved: {rough_path}")

def generate_felt_v6():
    print("Generating NovaDesk 4K Merino Felt Textures V6 (4096x2048)...")
    w, h = 4096, 2048
    np.random.seed(666)
    
    # 1. Base Heather Clump Noise (Macro mottle)
    low_w, low_h = 256, 128
    low = np.random.uniform(0.35, 0.65, (low_h, low_w)).astype(np.float32)
    low_full = np.array(Image.fromarray(np.uint8(low * 255)).resize((w, h), Image.Resampling.BICUBIC), dtype=np.float32) / 255.0
    
    # 2. Dense Wool Fibers Layer (150,000 distinct fiber hairs)
    fiber_img = Image.new("L", (w, h), 128)
    draw_f = ImageDraw.Draw(fiber_img)
    
    n_fibers = 150000
    xs = np.random.randint(0, w, n_fibers)
    ys = np.random.randint(0, h, n_fibers)
    lens = np.random.randint(14, 42, n_fibers)
    angles = np.random.uniform(0, 2 * math.pi, n_fibers)
    curvs = np.random.uniform(-0.9, 0.9, n_fibers)
    
    # Discrete heather fiber shades: deep charcoal, slate, ash, silver fleck, deep jet
    shades = np.random.choice([20, 50, 85, 130, 180, 230], size=n_fibers, p=[0.30, 0.28, 0.20, 0.12, 0.07, 0.03])
    
    for i in range(n_fibers):
        x0, y0 = xs[i], ys[i]
        ln = lens[i]
        ang = angles[i]
        c = curvs[i]
        sh = int(shades[i])
        
        x1 = x0 + ln * 0.5 * math.cos(ang)
        y1 = y0 + ln * 0.5 * math.sin(ang)
        x2 = x0 + ln * math.cos(ang + c)
        y2 = y0 + ln * math.sin(ang + c)
        
        draw_f.line([(x0, y0), (x1, y1), (x2, y2)], fill=sh, width=1)
        
    fiber_arr = np.array(fiber_img, dtype=np.float32) / 255.0
    
    # Micro tactile noise
    micro = np.random.normal(0.5, 0.14, (h, w)).astype(np.float32)
    micro = np.clip(micro, 0.0, 1.0)
    
    # Height map
    height = low_full * 0.22 + fiber_arr * 0.58 + micro * 0.20
    height = np.clip(height, 0.0, 1.0)
    
    # Rich Dark Charcoal / Anthracite Heather Albedo:
    # Deep base: #18191D (24, 25, 29)
    # Mid-tone heather: #282A31 (40, 42, 49)
    # Subtle silver-ash flecks: #484C58 (72, 76, 88)
    r = (height * 48 + 24).astype(np.uint8)
    g = (height * 51 + 25).astype(np.uint8)
    b = (height * 59 + 29).astype(np.uint8)
    
    albedo = Image.merge("RGB", (Image.fromarray(r), Image.fromarray(g), Image.fromarray(b)))
    albedo_path = os.path.join(TEXTURES_DIR, "novadesk_felt_albedo.png")
    albedo.save(albedo_path, "PNG", optimize=True)
    print(f"Saved: {albedo_path}")
    
    # Tactile Normal Map
    gx = np.zeros_like(height)
    gy = np.zeros_like(height)
    gx[:, 1:-1] = (height[:, 2:] - height[:, :-2]) * 0.5
    gy[1:-1, :] = (height[2:, :] - height[:-2, :]) * 0.5
    
    bump_mult = 4.8
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
    
    # Roughness Map (0.88 - 0.98)
    rough = np.uint8(np.clip((0.88 + height * 0.10) * 255, 0, 255))
    rough_img = Image.fromarray(rough, mode='L')
    rough_path = os.path.join(TEXTURES_DIR, "novadesk_felt_roughness.png")
    rough_img.save(rough_path, "PNG", optimize=True)
    print(f"Saved: {rough_path}")

if __name__ == "__main__":
    generate_leather_v6()
    generate_felt_v6()
    print("Texture generation V6 completed successfully!")
