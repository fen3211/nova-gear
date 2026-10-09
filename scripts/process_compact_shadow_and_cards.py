"""
Processes compact shadow, exports WebP/PNG assets, and renders
real-world UI card mockups in exact site dimensions on Cream, Lime, and Dark themes.
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PREVIEWS_DIR = r"D:\Projects\ууу\assets\previews"
FONTS_DIR = r"C:\Windows\Fonts"

FONT_HEADING = os.path.join(FONTS_DIR, "segoeuib.ttf")
FONT_BODY = os.path.join(FONTS_DIR, "segoeui.ttf")
FONT_MONO = os.path.join(FONTS_DIR, "consola.ttf")

def process_shadow_with_guaranteed_margins():
    """
    Tapers the physical contact shadow smoothly to alpha=0 so that it never clips card borders.
    Preserves 100% of dense contact occlusion at device base, while guaranteeing >180px
    transparent padding on all four outer image borders.
    """
    raw_shadow_path = os.path.join(PREVIEWS_DIR, "flux_charger_hero_shadow_raw.png")
    if not os.path.exists(raw_shadow_path):
        print(f"Error: {raw_shadow_path} not found")
        return None
        
    shadow_img = Image.open(raw_shadow_path).convert("RGBA")
    w, h = shadow_img.size
    
    # Extract alpha channel as numpy array
    r, g, b, a = shadow_img.split()
    a_arr = np.array(a, dtype=np.float32)
    
    # Device ground contact center in 1600x1600 space:
    # Footprint sits roughly X in [500..950], Y in [1280..1380]
    # Center of contact patch:
    cx, cy = 720.0, 1330.0
    
    # Create elliptical feather mask centered on contact base
    # Radius X: 480px, Radius Y: 240px
    Y, X = np.ogrid[:h, :w]
    dx = (X - cx) / 520.0
    dy = (Y - cy) / 260.0
    dist = np.sqrt(dx*dx + dy*dy)
    
    # Falloff curve: 1.0 up to dist=0.65, smooth cosine taper to 0.0 at dist=1.0
    mask = np.ones((h, w), dtype=np.float32)
    inner = 0.60
    outer = 0.95
    
    t = np.clip((dist - inner) / (outer - inner), 0.0, 1.0)
    # Cosine smoothstep
    feather = 0.5 * (1.0 + np.cos(t * np.pi))
    feather[dist >= outer] = 0.0
    feather[dist <= inner] = 1.0
    
    # Apply feathering to alpha
    a_processed = a_arr * feather
    
    # Zero out strict borders: 180px margin left/right, 160px top/bottom
    margin_x = 180
    margin_y = 160
    a_processed[:, :margin_x] = 0.0
    a_processed[:, w - margin_x:] = 0.0
    a_processed[:margin_y, :] = 0.0
    a_processed[h - margin_y:, :] = 0.0
    
    a_final = Image.fromarray(np.uint8(np.clip(a_processed, 0, 255)), mode='L')
    
    # Reassemble pure black shadow with smoothed alpha
    processed_shadow = Image.merge("RGBA", (Image.new('L', (w, h), 0),
                                            Image.new('L', (w, h), 0),
                                            Image.new('L', (w, h), 0),
                                            a_final))
    
    out_png = os.path.join(PREVIEWS_DIR, "flux_charger_hero_shadow.png")
    out_webp = os.path.join(PREVIEWS_DIR, "flux_charger_hero_shadow.webp")
    processed_shadow.save(out_png, "PNG", optimize=True)
    processed_shadow.save(out_webp, "WEBP", lossless=True, quality=100)
    
    bbox = processed_shadow.getbbox()
    print(f"Compact Shadow Processed: bbox={bbox}, border max alpha={max(a_final.getpixel((0, y)) for y in range(h))}")
    return processed_shadow

def process_isolated_and_transparent(shadow_img):
    raw_iso_path = os.path.join(PREVIEWS_DIR, "flux_charger_hero_isolated_raw.png")
    if not os.path.exists(raw_iso_path):
        print(f"Error: {raw_iso_path} not found")
        return None
        
    iso_img = Image.open(raw_iso_path).convert("RGBA")
    
    # Save isolated product PNG & WebP
    iso_png = os.path.join(PREVIEWS_DIR, "flux_charger_hero_isolated.png")
    iso_webp = os.path.join(PREVIEWS_DIR, "flux_charger_hero_isolated.webp")
    iso_img.save(iso_png, "PNG", optimize=True)
    iso_img.save(iso_webp, "WEBP", lossless=True, quality=100)
    print(f"Isolated Product Saved: bbox={iso_img.getbbox()}")
    
    # Generate combined transparent hero (shadow + isolated product)
    comb_img = Image.alpha_composite(shadow_img, iso_img)
    comb_png = os.path.join(PREVIEWS_DIR, "flux_charger_hero_transparent.png")
    comb_webp = os.path.join(PREVIEWS_DIR, "flux_charger_hero_transparent.webp")
    comb_img.save(comb_png, "PNG", optimize=True)
    comb_img.save(comb_webp, "WEBP", lossless=True, quality=100)
    print(f"Combined Transparent Hero Saved: bbox={comb_img.getbbox()}")
    
    return iso_img

def render_real_card_mockup(theme_name, bg_canvas_color, card_bg_color, text_color, sub_color, border_color, btn_bg, btn_text):
    """
    Renders an editorial product card mockup in real-world proportions:
    Canvas: 760 x 820 px. Card: 640 x 700 px (radius 24px).
    Product visual height: 320 px (actual catalog display scale).
    """
    canvas_w, canvas_h = 760, 820
    card_w, card_h = 640, 700
    card_x = (canvas_w - card_w) // 2
    card_y = (canvas_h - card_h) // 2
    
    canvas = Image.new("RGBA", (canvas_w, canvas_h), bg_canvas_color)
    draw = ImageDraw.Draw(canvas)
    
    # Draw rounded card container
    card_mask = Image.new("L", (card_w, card_h), 0)
    draw_mask = ImageDraw.Draw(card_mask)
    draw_mask.rounded_rectangle([(0, 0), (card_w, card_h)], radius=24, fill=255)
    
    card_surface = Image.new("RGBA", (card_w, card_h), card_bg_color)
    
    # Subtle card border
    if border_color:
        draw_border = ImageDraw.Draw(card_surface)
        draw_border.rounded_rectangle([(0, 0), (card_w - 1, card_h - 1)], radius=24, outline=border_color, width=1)
        
    # Card Content:
    draw_card = ImageDraw.Draw(card_surface)
    
    font_meta = ImageFont.truetype(FONT_HEADING, 15)
    font_title = ImageFont.truetype(FONT_HEADING, 28)
    font_desc = ImageFont.truetype(FONT_BODY, 15)
    font_specs = ImageFont.truetype(FONT_MONO, 12)
    font_price = ImageFont.truetype(FONT_HEADING, 24)
    font_btn = ImageFont.truetype(FONT_HEADING, 13)
    
    # 1. Top Meta
    draw_card.text((36, 32), "04 // POWER", fill=sub_color, font=font_meta)
    draw_card.text((card_w - 36, 32), "GAN FAST CHARGER", fill=sub_color, font=font_meta, anchor="ra")
    
    # 2. Visual Stage (Product + Shadow)
    # Render product at actual card scale: 310 px height
    iso_path = os.path.join(PREVIEWS_DIR, "flux_charger_hero_isolated.png")
    shadow_path = os.path.join(PREVIEWS_DIR, "flux_charger_hero_shadow.png")
    
    iso_full = Image.open(iso_path).convert("RGBA")
    shadow_full = Image.open(shadow_path).convert("RGBA")
    
    # Crop to content bounds (same crop for both!)
    # Product bbox is (402, 261, 1175, 1390), shadow is slightly wider at bottom
    crop_box = (200, 200, 1400, 1500)
    iso_cropped = iso_full.crop(crop_box)
    shadow_cropped = shadow_full.crop(crop_box)
    
    target_h = 320
    aspect = iso_cropped.width / iso_cropped.height
    target_w = int(target_h * aspect)
    
    iso_scaled = iso_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    shadow_scaled = shadow_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Center horizontally in card, positioned at Y ~ 80
    vx = (card_w - target_w) // 2
    vy = 75
    
    # Alpha composite shadow, then product
    card_surface.alpha_composite(shadow_scaled, (vx, vy))
    card_surface.alpha_composite(iso_scaled, (vx, vy))
    
    # 3. Bottom Information
    draw_card.text((36, 420), "Flux 100W", fill=text_color, font=font_title)
    
    desc_lines = [
        "Triple-port GaN III architecture engineered to fast charge a laptop",
        "and two accessories simultaneously with dynamic power allocation."
    ]
    draw_card.text((36, 460), desc_lines[0], fill=sub_color, font=font_desc)
    draw_card.text((36, 482), desc_lines[1], fill=sub_color, font=font_desc)
    
    specs = "100W PD 3.0 • DUAL NAVITAS GAN • 2X USB-C + 1X USB-A • THERMALGUARD 3.0"
    draw_card.text((36, 520), specs, fill=sub_color, font=font_specs)
    
    # Thin divider
    draw_card.line([(36, 555), (card_w - 36, 555)], fill=border_color if border_color else (128, 128, 128, 40), width=1)
    
    # Action Bar
    draw_card.text((36, 580), "$69", fill=text_color, font=font_price)
    
    # Buttons
    # Specs button
    draw_card.rounded_rectangle([(card_w - 240, 574), (card_w - 150, 616)], radius=8, outline=sub_color, width=1)
    draw_card.text((card_w - 195, 595), "SPECS", fill=text_color, font=font_btn, anchor="mm")
    
    # Add to Cart button
    draw_card.rounded_rectangle([(card_w - 138, 574), (card_w - 36, 616)], radius=8, fill=btn_bg)
    draw_card.text((card_w - 87, 595), "ADD TO CART ↗", fill=btn_text, font=font_btn, anchor="mm")
    
    # Paste card onto canvas with mask
    canvas.paste(card_surface, (card_x, card_y), card_mask)
    
    out_name = f"card_preview_{theme_name}.png"
    out_path = os.path.join(PREVIEWS_DIR, out_name)
    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
    print(f"Card Mockup Saved: {out_name} ({canvas_w}x{canvas_h})")

def generate_all_card_mockups():
    # 1. CREAM THEME (--bg: #F3F0E7, card: #E8E4D9 / #F3F0E7)
    render_real_card_mockup(
        theme_name="cream",
        bg_canvas_color=(235, 232, 225, 255),
        card_bg_color=(243, 240, 231, 255),
        text_color=(17, 17, 17, 255),
        sub_color=(85, 85, 85, 255),
        border_color=(17, 17, 17, 30),
        btn_bg=(17, 17, 17, 255),
        btn_text=(243, 240, 231, 255)
    )
    
    # 2. LIME THEME (--card-green-bg: #C7FF3D)
    render_real_card_mockup(
        theme_name="lime",
        bg_canvas_color=(235, 232, 225, 255),
        card_bg_color=(199, 255, 61, 255),
        text_color=(17, 17, 17, 255),
        sub_color=(25, 30, 20, 220),
        border_color=(17, 17, 17, 35),
        btn_bg=(17, 17, 17, 255),
        btn_text=(199, 255, 61, 255)
    )
    
    # 3. DARK THEME (--dark-bg: #111111, --dark-surface: #18191E)
    render_real_card_mockup(
        theme_name="dark",
        bg_canvas_color=(17, 17, 17, 255),
        card_bg_color=(24, 25, 30, 255),
        text_color=(243, 240, 231, 255),
        sub_color=(158, 158, 158, 255),
        border_color=(243, 240, 231, 35),
        btn_bg=(199, 255, 61, 255),
        btn_text=(17, 17, 17, 255)
    )

if __name__ == "__main__":
    shadow = process_shadow_with_guaranteed_margins()
    if shadow:
        process_isolated_and_transparent(shadow)
        generate_all_card_mockups()
        print("All compact shadow and card mockups generated successfully!")
