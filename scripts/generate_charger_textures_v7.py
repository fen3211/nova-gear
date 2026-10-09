"""
Generates high-precision laser-etched typography and graphic textures
for NOVA Flux 100W GaN Fast Charger V7 (Compact Architectural Form Factor).
"""
import os
from PIL import Image, ImageDraw, ImageFont

TEXTURES_DIR = r"D:\Projects\ууу\assets\textures"
os.makedirs(TEXTURES_DIR, exist_ok=True)

FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"

def create_faceplate_texture():
    size = (2048, 2048)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_brand = ImageFont.truetype(FONT_BOLD, 46)
    font_brand_sub = ImageFont.truetype(FONT_BOLD, 30)
    font_port_id = ImageFont.truetype(FONT_BOLD, 34)
    font_port_spec = ImageFont.truetype(FONT_REG, 24)
    font_status = ImageFont.truetype(FONT_BOLD, 22)
    font_micro = ImageFont.truetype(FONT_REG, 22)

    # 1. Header (Y ~ 220)
    draw.text((320, 210), "NOVA", fill=(245, 248, 252, 255), font=font_brand)
    draw.text((470, 222), "// FLUX 100W GaN", fill=(199, 255, 61, 255), font=font_brand_sub)

    # Status LED at (1638, 244)
    draw.text((1638, 185), "STATUS", fill=(195, 200, 210, 220), font=font_status, anchor="mm")

    # 2. USB-C 1 Label (C1 aperture top is Y ~ 493)
    draw.text((1024, 405), "C1  •  100W MAX", fill=(242, 245, 252, 255), font=font_port_id, anchor="mm")
    draw.text((1024, 448), "PD 3.0 • PPS • QC 5.0", fill=(165, 172, 182, 210), font=font_port_spec, anchor="mm")

    # 3. USB-C 2 Label (C2 aperture top is Y ~ 1029)
    draw.text((1024, 945), "C2  •  100W MAX", fill=(242, 245, 252, 255), font=font_port_id, anchor="mm")
    draw.text((1024, 988), "PD 3.0 • PPS • QC 5.0", fill=(165, 172, 182, 210), font=font_port_spec, anchor="mm")

    # 4. USB-A Label (A aperture top is Y ~ 1524)
    draw.text((1024, 1435), "USB-A  •  22.5W FAST", fill=(242, 245, 252, 255), font=font_port_id, anchor="mm")
    draw.text((1024, 1478), "FCP • SCP • AFC 12V", fill=(165, 172, 182, 210), font=font_port_spec, anchor="mm")

    # 5. Bottom Matrix Line (Y ~ 1840)
    draw.line([(520, 1830), (1528, 1830)], fill=(130, 136, 146, 100), width=2)
    draw.text((1024, 1860), "INTELLIGENT GaN POWER ALLOCATION", fill=(145, 150, 160, 180), font=font_micro, anchor="mm")

    out_path = os.path.join(TEXTURES_DIR, "charger_faceplate_labels_v7.png")
    img.save(out_path, "PNG")
    print(f"Saved V7 faceplate texture: {out_path}")

def create_side_graphic_texture():
    size = (2048, 2048)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_huge = ImageFont.truetype(FONT_BOLD, 180)
    font_sub = ImageFont.truetype(FONT_BOLD, 46)
    font_spec = ImageFont.truetype(FONT_REG, 28)

    draw.text((320, 880), "NOVA", fill=(255, 255, 255, 255), font=font_huge)
    draw.text((325, 1080), "FLUX // 100W GaN III", fill=(255, 255, 255, 220), font=font_sub)
    draw.text((325, 1145), "GALLIUM NITRIDE HIGH FREQUENCY POWER ARCHITECTURE", fill=(255, 255, 255, 160), font=font_spec)

    out_path = os.path.join(TEXTURES_DIR, "charger_side_graphic_v7.png")
    img.save(out_path, "PNG")
    print(f"Saved V7 side graphic texture: {out_path}")

if __name__ == "__main__":
    create_faceplate_texture()
    create_side_graphic_texture()
