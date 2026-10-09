"""
Generates high-precision laser-etched typography and graphic textures
for the NOVA Flux 100W GaN Fast Charger 3D model.
Calibrated for exact sub-pixel alignment above port apertures.
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

    # High-precision typography
    font_brand = ImageFont.truetype(FONT_BOLD, 48)
    font_brand_sub = ImageFont.truetype(FONT_BOLD, 32)
    font_port_id = ImageFont.truetype(FONT_BOLD, 36)
    font_port_spec = ImageFont.truetype(FONT_REG, 26)
    font_status = ImageFont.truetype(FONT_BOLD, 24)

    # 1. Header Row (Y ~ 280)
    # Brand Logotype top-left:
    draw.text((340, 270), "NOVA", fill=(245, 247, 250, 255), font=font_brand)
    draw.text((490, 282), "// FLUX 100W GaN III", fill=(199, 255, 61, 255), font=font_brand_sub)

    # Status LED label top-right:
    # LED is at X = 0.18, Z = 0.38 -> pixel (1638, 303)
    draw.text((1638, 245), "STATUS", fill=(200, 205, 215, 220), font=font_status, anchor="mm")

    # 2. USB-C 1 Label (C1 aperture center is Y = 606; top rim is Y = 522)
    # Position text cleanly above at Y = 450
    draw.text((1024, 435), "C1  •  100W MAX", fill=(240, 243, 250, 255), font=font_port_id, anchor="mm")
    draw.text((1024, 480), "PD 3.0 • PPS • QC 5.0", fill=(170, 175, 185, 210), font=font_port_spec, anchor="mm")

    # 3. USB-C 2 Label (C2 aperture center is Y = 1100; top rim is Y = 1016)
    # Position text cleanly above at Y = 945
    draw.text((1024, 930), "C2  •  100W MAX", fill=(240, 243, 250, 255), font=font_port_id, anchor="mm")
    draw.text((1024, 975), "PD 3.0 • PPS • QC 5.0", fill=(170, 175, 185, 210), font=font_port_spec, anchor="mm")

    # 4. USB-A Label (A aperture center is Y = 1630; top rim is Y = 1506)
    # Position text cleanly above at Y = 1435
    draw.text((1024, 1420), "USB-A  •  22.5W FAST", fill=(240, 243, 250, 255), font=font_port_id, anchor="mm")
    draw.text((1024, 1465), "FCP • SCP • AFC 12V", fill=(170, 175, 185, 210), font=font_port_spec, anchor="mm")

    # 5. Technical baseline footer
    draw.line([(550, 1820), (1498, 1820)], fill=(140, 145, 155, 90), width=2)
    draw.text((1024, 1850), "DYNAMIC POWER ALLOCATION MATRIX", fill=(150, 155, 165, 180), font=font_port_spec, anchor="mm")

    out_path = os.path.join(TEXTURES_DIR, "charger_faceplate_labels.png")
    img.save(out_path, "PNG")
    print(f"Saved calibrated faceplate texture: {out_path}")

def create_side_graphic_texture():
    size = (2048, 2048)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_huge = ImageFont.truetype(FONT_BOLD, 220)
    font_sub = ImageFont.truetype(FONT_BOLD, 54)
    font_spec = ImageFont.truetype(FONT_REG, 34)

    draw.text((320, 850), "NOVA", fill=(255, 255, 255, 255), font=font_huge)
    draw.text((330, 1100), "FLUX // 100W GaN III", fill=(255, 255, 255, 220), font=font_sub)
    draw.text((330, 1180), "GALLIUM NITRIDE HIGH FREQUENCY POWER", fill=(255, 255, 255, 160), font=font_spec)

    out_path = os.path.join(TEXTURES_DIR, "charger_side_graphic.png")
    img.save(out_path, "PNG")
    print(f"Saved side graphic texture: {out_path}")

if __name__ == "__main__":
    create_faceplate_texture()
    create_side_graphic_texture()
