"""
Generates high-precision textures, laser-etched typography, micro-prismatic optical bump,
and knurling maps for NOVA Beam Monitor Light Bar.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

TEXTURES_DIR = r"D:\Projects\ууу\assets\textures"
os.makedirs(TEXTURES_DIR, exist_ok=True)

FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"

def create_laser_typography():
    size = (2048, 512)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_brand = ImageFont.truetype(FONT_BOLD, 42)
    font_spec = ImageFont.truetype(FONT_REG, 26)
    font_micro = ImageFont.truetype(FONT_REG, 20)

    # Laser engraving on aluminum bar top-rear
    draw.text((120, 220), "NOVA", fill=(235, 238, 245, 240), font=font_brand)
    draw.text((270, 232), "// BEAM SCREEN LIGHTBAR", fill=(199, 255, 61, 240), font=font_spec)
    
    spec_text = "AUTO-DIMMING DUAL CCT 2700-6500K • CRI Ra>97 • ASYMMETRIC OPTICAL DESIGN • 5V 2A USB-C"
    draw.text((120, 290), spec_text, fill=(170, 178, 190, 210), font=font_micro)
    
    # Technical alignment marks
    draw.line([(100, 360), (1950, 360)], fill=(140, 148, 160, 110), width=2)
    for x in range(200, 1900, 300):
        draw.line([(x, 350), (x, 370)], fill=(140, 148, 160, 160), width=2)
        draw.text((x, 385), f"+{x//10}mm", fill=(130, 138, 150, 160), font=font_micro, anchor="mt")

    out_path = os.path.join(TEXTURES_DIR, "beam_laser_typography.png")
    img.save(out_path, "PNG")
    print(f"Generated laser typography: {out_path}")

def create_dial_endcap_textures():
    # 1. Circular touch faceplate with power & mode icons
    size = (1024, 1024)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = 512, 512

    # Concentric indicator ring
    draw.arc([160, 160, 864, 864], start=0, end=360, fill=(180, 190, 205, 120), width=4)
    
    # Tick marks around the perimeter
    for i in range(24):
        angle = math.radians(i * 15)
        r1 = 390
        r2 = 410 if (i % 6 == 0) else 400
        x1 = cx + r1 * math.cos(angle)
        y1 = cy + r1 * math.sin(angle)
        x2 = cx + r2 * math.cos(angle)
        y2 = cy + r2 * math.sin(angle)
        width = 4 if (i % 6 == 0) else 2
        draw.line([(x1, y1), (x2, y2)], fill=(220, 228, 240, 200 if i % 6 == 0 else 120), width=width)

    # Power symbol at center
    font_icon = ImageFont.truetype(FONT_BOLD, 72)
    # Draw classic power circle + line
    draw.arc([430, 430, 594, 594], start=300, end=240, fill=(245, 248, 255, 255), width=10)
    draw.line([(512, 400), (512, 480)], fill=(245, 248, 255, 255), width=10)

    # Sub-text
    font_touch = ImageFont.truetype(FONT_REG, 24)
    draw.text((512, 640), "TAP: MODE • ROTATE: BRIGHTNESS", fill=(175, 185, 200, 200), font=font_touch, anchor="mm")

    out_path = os.path.join(TEXTURES_DIR, "beam_dial_touch_face.png")
    img.save(out_path, "PNG")
    print(f"Generated dial touch face: {out_path}")

def create_knurling_normal_map():
    # Diamond knurling bump / normal map for rotary dial rim (1024x256 repeating seamlessly)
    w, h = 1024, 256
    img = Image.new("RGB", (w, h), (128, 128, 255)) # Tangent space neutral normal
    pixels = img.load()

    # Create 32 diamond repeating cells horizontally, 8 vertically
    cell_w = w / 32.0
    cell_h = h / 8.0

    for y in range(h):
        for x in range(w):
            u = (x % cell_w) / cell_w - 0.5
            v = (y % cell_h) / cell_h - 0.5
            # Pyramid profile: distance in diamond metric |u| + |v|
            d = 1.0 - 2.0 * (abs(u) + abs(v))
            d = max(0.0, min(1.0, d))
            # Normal gradients
            # sign of u and v gives slope
            nx = -math.copysign(1.0, u) * (0.8 if d > 0.05 else 0.0)
            ny = -math.copysign(1.0, v) * (0.8 if d > 0.05 else 0.0)
            nz = 1.0

            # Normalize vector
            length = math.sqrt(nx*nx + ny*ny + nz*nz)
            nx /= length
            ny /= length
            nz /= length

            r = int((nx * 0.5 + 0.5) * 255)
            g = int((ny * 0.5 + 0.5) * 255)
            b = int((nz * 0.5 + 0.5) * 255)
            pixels[x, y] = (r, g, b)

    out_path = os.path.join(TEXTURES_DIR, "beam_knurling_normal.png")
    img.save(out_path, "PNG")
    print(f"Generated knurling normal map: {out_path}")

def create_prismatic_diffuser_map():
    # High-precision micro-prismatic Fresnel linear grooves for diffuser lens
    w, h = 2048, 512
    img = Image.new("RGB", (w, h), (128, 128, 255))
    pixels = img.load()

    # Linear prismatic ridges along X with period ~ 16 pixels
    period = 16.0
    for y in range(h):
        for x in range(w):
            phase = (x % period) / period  # 0 to 1
            # Triangular prism cross section
            slope = (phase - 0.5) * 2.0 # -1 to +1
            nx = slope * 0.6
            ny = 0.0
            nz = 0.8
            length = math.sqrt(nx*nx + ny*ny + nz*nz)
            r = int((nx/length * 0.5 + 0.5) * 255)
            g = int((ny/length * 0.5 + 0.5) * 255)
            b = int((nz/length * 0.5 + 0.5) * 255)
            pixels[x, y] = (r, g, b)

    out_path = os.path.join(TEXTURES_DIR, "beam_prismatic_lens_normal.png")
    img.save(out_path, "PNG")
    print(f"Generated optical diffuser normal map: {out_path}")

def create_silicone_grip_pad_map():
    # Hexagonal ribbed silicone anti-slip pattern for clamp interior
    w, h = 1024, 1024
    img = Image.new("RGB", (w, h), (128, 128, 255))
    draw = ImageDraw.Draw(img)
    # Dark charcoal silicone height/normal representation
    # Draw ribbed horizontal bars
    for y in range(0, h, 32):
        draw.rectangle([0, y, w, y+18], fill=(128, 175, 220))
        draw.rectangle([0, y+19, w, y+31], fill=(128, 85, 240))

    out_path = os.path.join(TEXTURES_DIR, "beam_silicone_pad_normal.png")
    img.save(out_path, "PNG")
    print(f"Generated silicone pad normal map: {out_path}")

def create_usbc_rear_labels():
    size = (512, 512)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_spec = ImageFont.truetype(FONT_BOLD, 28)
    font_micro = ImageFont.truetype(FONT_REG, 20)
    
    draw.text((256, 120), "USB-C INPUT", fill=(210, 220, 235, 230), font=font_spec, anchor="mm")
    draw.text((256, 160), "5V = 2.0A MAX", fill=(160, 170, 185, 200), font=font_micro, anchor="mm")
    
    # Port alignment symbol
    draw.rounded_rectangle([180, 240, 332, 310], radius=16, outline=(180, 190, 210, 180), width=3)
    
    out_path = os.path.join(TEXTURES_DIR, "beam_usbc_labels.png")
    img.save(out_path, "PNG")
    print(f"Generated USB-C rear labels: {out_path}")

if __name__ == "__main__":
    create_laser_typography()
    create_dial_endcap_textures()
    create_knurling_normal_map()
    create_prismatic_diffuser_map()
    create_silicone_grip_pad_map()
    create_usbc_rear_labels()
    print("All NOVA Beam textures successfully generated.")
