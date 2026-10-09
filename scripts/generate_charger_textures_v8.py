"""
Generates high-precision laser-etched typography and graphic textures
for NOVA Flux 100W GaN Fast Charger V8 (Calibrated Editorial Form Factor).
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

    font_brand = ImageFont.truetype(FONT_BOLD, 44)
    font_brand_sub = ImageFont.truetype(FONT_BOLD, 28)
    font_port_id = ImageFont.truetype(FONT_BOLD, 32)
    font_port_spec = ImageFont.truetype(FONT_REG, 22)
    font_status = ImageFont.truetype(FONT_BOLD, 20)
    font_micro = ImageFont.truetype(FONT_REG, 20)

    # 1. Header (Y ~ 220)
    draw.text((280, 210), "NOVA", fill=(245, 248, 252, 255), font=font_brand)
    draw.text((430, 222), "// FLUX 100W GaN", fill=(199, 255, 61, 255), font=font_brand_sub)

    # Status LED label at X=1620, Y=220
    draw.text((1620, 220), "STATUS", fill=(185, 192, 202, 220), font=font_status, anchor="mm")

    # 2. USB-C 1 Label (C1 aperture top is Y ~ 506)
    draw.text((1024, 420), "C1  •  100W MAX", fill=(242, 245, 252, 255), font=font_port_id, anchor="mm")
    draw.text((1024, 462), "PD 3.0 • PPS • QC 5.0", fill=(160, 168, 178, 210), font=font_port_spec, anchor="mm")

    # 3. USB-C 2 Label (C2 aperture top is Y ~ 1008)
    draw.text((1024, 920), "C2  •  100W MAX", fill=(242, 245, 252, 255), font=font_port_id, anchor="mm")
    draw.text((1024, 962), "PD 3.0 • PPS • QC 5.0", fill=(160, 168, 178, 210), font=font_port_spec, anchor="mm")

    # 4. USB-A Label (A aperture top is Y ~ 1464)
    draw.text((1024, 1380), "USB-A  •  22.5W FAST", fill=(242, 245, 252, 255), font=font_port_id, anchor="mm")
    draw.text((1024, 1422), "FCP • SCP • AFC 12V", fill=(160, 168, 178, 210), font=font_port_spec, anchor="mm")

    # 5. Bottom Matrix Line & Microtext
    draw.line([(420, 1840), (1628, 1840)], fill=(130, 136, 146, 90), width=2)
    draw.text((1024, 1870), "INTELLIGENT GaN POWER ALLOCATION", fill=(140, 146, 156, 180), font=font_micro, anchor="mm")

    out_path = os.path.join(TEXTURES_DIR, "charger_faceplate_labels_v8.png")
    img.save(out_path, "PNG")
    print(f"Saved V8 faceplate texture: {out_path}")

def create_side_graphic_texture():
    size = (2048, 2048)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_huge = ImageFont.truetype(FONT_BOLD, 150)
    font_sub = ImageFont.truetype(FONT_BOLD, 42)
    font_spec = ImageFont.truetype(FONT_REG, 26)

    # Sleek typographic side graphic
    draw.text((300, 920), "NOVA", fill=(255, 255, 255, 240), font=font_huge)
    draw.text((305, 1090), "FLUX // 100W GaN III", fill=(255, 255, 255, 210), font=font_sub)
    draw.text((305, 1150), "GALLIUM NITRIDE HIGH FREQUENCY POWER ARCHITECTURE", fill=(255, 255, 255, 150), font=font_spec)

    out_path = os.path.join(TEXTURES_DIR, "charger_side_graphic_v8.png")
    img.save(out_path, "PNG")
    print(f"Saved V8 side graphic texture: {out_path}")

if __name__ == "__main__":
    create_faceplate_texture()
    create_side_graphic_texture()
