import os
from PIL import Image, ImageDraw, ImageFont

REVIEW_DIR = r"D:\Projects\ууу\review"
OUT_PATH = os.path.join(REVIEW_DIR, "master_contact_sheet.png")

def make_contact_sheet():
    hero_p = os.path.join(REVIEW_DIR, "02_hero_desktop_1440.png")
    c1_p = os.path.join(REVIEW_DIR, "03_card_01_k75_desktop.png")
    c2_p = os.path.join(REVIEW_DIR, "04_card_02_pulse_desktop.png")
    c3_p = os.path.join(REVIEW_DIR, "05_card_03_orbit_desktop.png")
    c4_p = os.path.join(REVIEW_DIR, "06_card_04_flux_desktop.png")
    c5_p = os.path.join(REVIEW_DIR, "07_card_05_novadesk_desktop.png")
    c6_p = os.path.join(REVIEW_DIR, "08_card_06_beam_desktop.png")
    
    s1_p = os.path.join(REVIEW_DIR, "story_k75_01_assembled.png")
    s2_p = os.path.join(REVIEW_DIR, "story_k75_02_mid_breakdown.png")
    s3_p = os.path.join(REVIEW_DIR, "story_k75_03_exploded.png")
    
    mob_p = os.path.join(REVIEW_DIR, "10_hero_mobile_390.png")
    
    # Load and scale components for a clean 1800px wide sheet
    sheet_w = 1800
    bg_color = (18, 19, 22) # #121316 dark studio background
    
    # 1. Hero banner: scale to 1720px wide
    hero = Image.open(hero_p)
    hw = 1720
    hh = int(hero.height * (hw / hero.width))
    hero_scaled = hero.resize((hw, hh), Image.Resampling.LANCZOS)
    
    # 2. Cards Grid (3 rows)
    # Row 1: K75 (65%) + Pulse (35%) -> 1100px + 600px + 20px gap = 1720px
    c1 = Image.open(c1_p)
    c2 = Image.open(c2_p)
    r1_h = 440
    c1_w = int(c1.width * (r1_h / c1.height))
    c2_w = int(c2.width * (r1_h / c2.height))
    c1_scaled = c1.resize((1100, r1_h), Image.Resampling.LANCZOS)
    c2_scaled = c2.resize((600, r1_h), Image.Resampling.LANCZOS)
    
    # Row 2: Orbit (35%) + Flux (65%)
    c3 = Image.open(c3_p)
    c4 = Image.open(c4_p)
    r2_h = 440
    c3_scaled = c3.resize((600, r2_h), Image.Resampling.LANCZOS)
    c4_scaled = c4.resize((1100, r2_h), Image.Resampling.LANCZOS)
    
    # Row 3: NovaDesk (50%) + Beam (50%) -> 850px + 850px + 20px gap = 1720px
    c5 = Image.open(c5_p)
    c6 = Image.open(c6_p)
    r3_h = 420
    c5_scaled = c5.resize((850, r3_h), Image.Resampling.LANCZOS)
    c6_scaled = c6.resize((850, r3_h), Image.Resampling.LANCZOS)
    
    # 3. K75 Story Breakdown sequence: 3 square panels (each 560x560)
    s1 = Image.open(s1_p).resize((560, 560), Image.Resampling.LANCZOS)
    s2 = Image.open(s2_p).resize((560, 560), Image.Resampling.LANCZOS)
    s3 = Image.open(s3_p).resize((560, 560), Image.Resampling.LANCZOS)
    
    # Compute total height
    margin = 40
    gap = 20
    header_h = 100
    section_title_h = 60
    
    total_h = (
        margin + header_h + 
        hh + gap + 
        section_title_h +
        r1_h + gap + 
        r2_h + gap + 
        r3_h + gap + 
        section_title_h + 
        560 + margin
    )
    
    sheet = Image.new("RGB", (sheet_w, total_h), bg_color)
    draw = ImageDraw.Draw(sheet)
    
    # Draw Master Header
    y = margin
    draw.text((margin, y), "NOVA GEAR // MASTER PRODUCTION SHOWCASE", fill=(243, 240, 231))
    draw.text((margin, y + 36), "Cinematic E-Commerce DTC • Blender Cycles GPU • Interactive Scroll Architecture", fill=(154, 158, 168))
    y += header_h
    
    # Paste Hero
    sheet.paste(hero_scaled, (margin, y))
    y += hh + gap
    
    # Catalog Section Header
    draw.text((margin, y), "CURATED CATALOG // ASYMMETRIC BESPOKE GEOMETRY", fill=(199, 255, 61))
    y += section_title_h
    
    # Row 1
    sheet.paste(c1_scaled, (margin, y))
    sheet.paste(c2_scaled, (margin + 1100 + gap, y))
    y += r1_h + gap
    
    # Row 2
    sheet.paste(c3_scaled, (margin, y))
    sheet.paste(c4_scaled, (margin + 600 + gap, y))
    y += r2_h + gap
    
    # Row 3
    sheet.paste(c5_scaled, (margin, y))
    sheet.paste(c6_scaled, (margin + 850 + gap, y))
    y += r3_h + gap
    
    # Story Breakdown Header
    draw.text((margin, y), "NOVAKEYS K75 // 3D SCROLL-DRIVEN ARCHITECTURE BREAKDOWN (0% -> 50% -> 100%)", fill=(199, 255, 61))
    y += section_title_h
    
    # Row Story
    sheet.paste(s1, (margin, y))
    sheet.paste(s2, (margin + 560 + gap, y))
    sheet.paste(s3, (margin + 1120 + (gap * 2), y))
    
    sheet.save(OUT_PATH, quality=92)
    print(f"[OK] Master contact sheet saved to {OUT_PATH} ({sheet.size})")

if __name__ == "__main__":
    make_contact_sheet()
