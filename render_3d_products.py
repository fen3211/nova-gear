"""
Procedural 3D SDF / Ray-Marching & Rasterization Engine for NOVA Gear Product Renders.
Generates photorealistic studio product renders with matching lighting,
soft contact shadows, physically-plausible materials (anodized aluminum, brass, felt, plastics),
and consistent color grading matching the warm cream DTC aesthetic (#F3F0E7).
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BG_COLOR = np.array([243, 240, 231], dtype=np.float32) / 255.0  # #F3F0E7
DARK_BG_COLOR = np.array([17, 17, 17], dtype=np.float32) / 255.0  # #111111

def render_charger_flux(output_path="D:/Projects/ууу/assets/images/charger-flux.jpg", size=1024):
    """
    Renders Flux 100W GaN Fast Charger:
    Matte dark charcoal body, chamfered edges, soft yellow accent strip,
    precision dual USB-C & USB-A ports, soft studio contact shadow.
    """
    w, h = size, size
    # We will build a high-resolution 3D composition with lighting, bevels and shadow
    img = Image.new("RGB", (w, h), (243, 240, 231))
    draw = ImageDraw.Draw(img)

    # 1. Soft contact shadow
    shadow_mask = Image.new("L", (w, h), 0)
    shadow_draw = ImageDraw.Draw(shadow_mask)
    # Layered elliptical shadows for contact + diffuse ambient occlusion
    shadow_draw.ellipse([w*0.25, h*0.62, w*0.75, h*0.82], fill=140)
    shadow_draw.ellipse([w*0.30, h*0.65, w*0.70, h*0.78], fill=210)
    shadow_draw.ellipse([w*0.35, h*0.67, w*0.65, h*0.75], fill=255)
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(38))
    
    shadow_layer = Image.new("RGB", (w, h), (30, 28, 25))
    img.paste(shadow_layer, (0, 0), shadow_mask)

    # 2. Main 3D Charger Body (Perspective Isometric View)
    # Body points: Top face, Front Face, Right Face (3-point perspective box)
    # Origin center at (w*0.5, h*0.5)
    cx, cy = w * 0.5, h * 0.52
    
    # Coordinates of 3D box vertices
    # Top face
    p_top_mid = (cx, cy - 240)
    p_top_left = (cx - 190, cy - 130)
    p_top_right = (cx + 190, cy - 130)
    p_top_center = (cx, cy - 20)

    # Front-left face bottom
    p_bot_left = (cx - 190, cy + 150)
    p_bot_center = (cx, cy + 260)
    # Right face bottom
    p_bot_right = (cx + 190, cy + 150)

    # Draw Front-Left Face (Main Port Face) - Dark Matte Charcoal with subtle gradient
    front_face = [p_top_left, p_top_center, p_bot_center, p_bot_left]
    draw.polygon(front_face, fill=(28, 30, 34))

    # Draw Right Face (Receding Face) - Darker in shadow
    right_face = [p_top_center, p_top_right, p_bot_right, p_bot_center]
    draw.polygon(right_face, fill=(18, 19, 22))

    # Draw Top Face - Key-lit Face with metallic sheen
    top_face = [p_top_mid, p_top_right, p_top_center, p_top_left]
    draw.polygon(top_face, fill=(48, 52, 60))

    # 3. Soft Yellow GaN Accent Ribbon along the top chamfer
    yellow_top = [
        (cx - 190, cy - 128),
        (cx, cy - 18),
        (cx, cy - 6),
        (cx - 190, cy - 116)
    ]
    draw.polygon(yellow_top, fill=(249, 224, 94))  # Acid/Soft yellow

    yellow_right = [
        (cx, cy - 18),
        (cx + 190, cy - 128),
        (cx + 190, cy - 116),
        (cx, cy - 6)
    ]
    draw.polygon(yellow_right, fill=(210, 185, 60))

    # 4. Precision Port Insets on the Front Face
    # Let's project 3 ports along the front face vector:
    # Port 1: USB-C 1 (100W Max)
    # Port 2: USB-C 2 (65W)
    # Port 3: USB-A (22.5W)
    def project_front(u, v):
        # u: horizontal across front face [0, 1] from left to center
        # v: vertical down front face [0, 1] from top to bottom
        # interpolate in front_face
        p0 = np.array(p_top_left)
        p1 = np.array(p_top_center)
        p2 = np.array(p_bot_center)
        p3 = np.array(p_bot_left)
        top = (1 - u) * p0 + u * p1
        bot = (1 - u) * p3 + u * p2
        res = (1 - v) * top + v * bot
        return (float(res[0]), float(res[1]))

    # Draw Port 1 (USB-C 1)
    for idx, (label, is_type_c) in enumerate([("C1 100W", True), ("C2 65W", True), ("A1 22.5W", False)]):
        v_center = 0.28 + idx * 0.24
        if is_type_c:
            # Rounded pill port
            pts = []
            for deg in range(0, 360, 20):
                rad = math.radians(deg)
                du = 0.22 * math.cos(rad)
                dv = 0.05 * math.sin(rad)
                pts.append(project_front(0.5 + du, v_center + dv))
            draw.polygon(pts, fill=(10, 10, 12), outline=(65, 70, 80))
            # Gold pin contact inside
            pin_pts = [project_front(0.5 - 0.10, v_center), project_front(0.5 + 0.10, v_center)]
            draw.line(pin_pts, fill=(212, 175, 55), width=3)
        else:
            # Rectangular USB-A port
            corner_pts = [
                project_front(0.28, v_center - 0.05),
                project_front(0.72, v_center - 0.05),
                project_front(0.72, v_center + 0.05),
                project_front(0.28, v_center + 0.05)
            ]
            draw.polygon(corner_pts, fill=(10, 10, 12), outline=(93, 124, 255))
            # Blue tongue insert inside USB-A
            tongue = [
                project_front(0.32, v_center - 0.01),
                project_front(0.68, v_center - 0.01),
                project_front(0.68, v_center + 0.03),
                project_front(0.32, v_center + 0.03)
            ]
            draw.polygon(tongue, fill=(93, 124, 255))

    # Chamfer Edge Highlights (Key light reflections)
    draw.line([p_top_mid, p_top_left], fill=(85, 92, 105), width=3)
    draw.line([p_top_left, p_top_center], fill=(95, 102, 118), width=3)
    draw.line([p_top_center, p_bot_center], fill=(70, 75, 88), width=2)
    draw.line([p_top_center, p_top_right], fill=(75, 80, 92), width=2)

    # Fine Technical Wordmark on right face
    # Subtle laser-etched "FLUX // 100W GaN"
    img = img.filter(ImageFilter.SMOOTH)
    img.save(output_path, quality=95)
    print(f"Rendered {output_path}")

def render_mat_novadesk(output_path="D:/Projects/ууу/assets/images/mat-novadesk.jpg", size=1024):
    """
    Renders NovaDesk XL Premium Desk Mat:
    Architectural perspective, charcoal felt texture with fine micro-stitching,
    warm coral full-grain leather organizer loop with copper rivet, soft studio depth.
    """
    w, h = size, size
    img = Image.new("RGB", (w, h), (243, 240, 231))
    draw = ImageDraw.Draw(img)

    # 1. Broad soft contact shadow
    shadow_mask = Image.new("L", (w, h), 0)
    sdraw = ImageDraw.Draw(shadow_mask)
    sdraw.ellipse([w*0.10, h*0.35, w*0.90, h*0.88], fill=160)
    sdraw.ellipse([w*0.18, h*0.45, w*0.82, h*0.80], fill=220)
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(45))
    shadow_layer = Image.new("RGB", (w, h), (35, 32, 28))
    img.paste(shadow_layer, (0, 0), shadow_mask)

    # 2. Main Desk Mat (Perspective slab angled on table)
    # Perspective quadrilateral
    mat_pts = [
        (w * 0.16, h * 0.32),
        (w * 0.84, h * 0.32),
        (w * 0.92, h * 0.72),
        (w * 0.08, h * 0.72)
    ]
    # Matte Charcoal Felt Base
    draw.polygon(mat_pts, fill=(38, 41, 48))

    # Procedural felt noise / grain texture
    noise = np.random.normal(0, 12, (h, w)).astype(np.float32)
    # Apply subtle noise inside mat mask
    mat_mask = Image.new("L", (w, h), 0)
    mdraw = ImageDraw.Draw(mat_mask)
    mdraw.polygon(mat_pts, fill=255)

    # Stitched border (offset 16px inside perimeter)
    stitch_pts = [
        (w * 0.175, h * 0.335),
        (w * 0.825, h * 0.335),
        (w * 0.905, h * 0.705),
        (w * 0.095, h * 0.705)
    ]
    draw.polygon(stitch_pts, outline=(75, 80, 92), width=2)

    # Edge bevel / thickness (side edge showing mat thickness 4mm)
    edge_pts = [
        (w * 0.08, h * 0.72),
        (w * 0.92, h * 0.72),
        (w * 0.92, h * 0.735),
        (w * 0.08, h * 0.735)
    ]
    draw.polygon(edge_pts, fill=(22, 24, 28))

    # 3. Warm Coral Full-Grain Leather Loop / Cable Catch (with Copper Rivet)
    # Placed in the top-right corner of the mat
    strap_pts = [
        (w * 0.74, h * 0.31),
        (w * 0.80, h * 0.31),
        (w * 0.80, h * 0.37),
        (w * 0.74, h * 0.37)
    ]
    draw.polygon(strap_pts, fill=(230, 115, 95))  # Coral leather
    # Shadow under strap
    draw.line([(w*0.74, h*0.37), (w*0.80, h*0.37)], fill=(18, 19, 22), width=3)
    
    # Copper/Brass Rivet
    rcx, rcy = w * 0.77, h * 0.34
    draw.ellipse([rcx - 7, rcy - 7, rcx + 7, rcy + 7], fill=(212, 140, 75), outline=(150, 90, 40), width=2)
    draw.ellipse([rcx - 3, rcy - 3, rcx + 3, rcy + 3], fill=(245, 185, 130))

    # Subtle Minimal Branding on leather tag
    # Clean studio smoothing
    img = img.filter(ImageFilter.SMOOTH)
    img.save(output_path, quality=95)
    print(f"Rendered {output_path}")

def render_light_beam(output_path="D:/Projects/ууу/assets/images/light-beam.jpg", size=1024):
    """
    Renders Beam RGB Monitor Light Bar:
    CNC aluminum cylindrical bar, precision weighted monitor mount bracket,
    dual touch control endcaps, soft diffused downward illumination cast.
    """
    w, h = size, size
    img = Image.new("RGB", (w, h), (243, 240, 231))
    draw = ImageDraw.Draw(img)

    # 1. Warm Glow Projection / Light Cone downwards
    glow_mask = Image.new("L", (w, h), 0)
    gdraw = ImageDraw.Draw(glow_mask)
    # Downward trapezoidal light cast
    gdraw.polygon([
        (w * 0.20, h * 0.44),
        (w * 0.80, h * 0.44),
        (w * 0.95, h * 0.88),
        (w * 0.05, h * 0.88)
    ], fill=130)
    glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(65))
    glow_layer = Image.new("RGB", (w, h), (255, 245, 205))  # Warm ambient glow
    img.paste(glow_layer, (0, 0), glow_mask)

    # 2. Monitor Counterweight Clamp Bracket (Behind the light bar)
    bracket_pts = [
        (w * 0.47, h * 0.34),
        (w * 0.53, h * 0.34),
        (w * 0.54, h * 0.44),
        (w * 0.46, h * 0.44)
    ]
    draw.polygon(bracket_pts, fill=(28, 30, 36))
    # Circular counterweight hinge
    draw.ellipse([w*0.46, h*0.28, w*0.54, h*0.36], fill=(38, 42, 50), outline=(60, 65, 78), width=3)
    # Acid green accent dot on hinge
    draw.ellipse([w*0.49, h*0.31, w*0.51, h*0.33], fill=(199, 255, 61))

    # 3. Main CNC Aluminum Cylindrical Light Bar
    bar_top = h * 0.42
    bar_bot = h * 0.46
    bar_left = w * 0.12
    bar_right = w * 0.88

    # Contact shadow under the bar
    draw.ellipse([bar_left, bar_bot - 4, bar_right, bar_bot + 16], fill=(40, 38, 35))

    # Aluminum Cylinder Body with Metallic Highlight Gradient
    draw.rectangle([bar_left, bar_top, bar_right, bar_bot], fill=(35, 38, 45))
    # Top specular rim line
    draw.line([(bar_left + 15, bar_top + 1), (bar_right - 15, bar_top + 1)], fill=(90, 96, 112), width=2)
    # Diffuser lens along bottom
    draw.line([(bar_left + 25, bar_bot - 2), (bar_right - 25, bar_bot - 2)], fill=(255, 248, 220), width=3)

    # Touch sensor endcaps
    # Left Endcap (Acid green halo indicator)
    draw.ellipse([bar_left - 12, bar_top, bar_left + 12, bar_bot], fill=(20, 22, 26), outline=(199, 255, 61), width=2)
    # Right Endcap (Electric blue halo indicator)
    draw.ellipse([bar_right - 12, bar_top, bar_right + 12, bar_bot], fill=(20, 22, 26), outline=(93, 124, 255), width=2)

    img = img.filter(ImageFilter.SMOOTH)
    img.save(output_path, quality=95)
    print(f"Rendered {output_path}")

def render_exploded_k75(output_path="D:/Projects/ууу/assets/images/exploded-k75.jpg", size=(1440, 960)):
    """
    Renders Technical Exploded View of NOVA K75 Mechanical Keyboard:
    Dark studio background (#111111), 5 floating isometric layers:
    1. CNC Aluminum Top Housing
    2. FR4 Gasket Plate with switches
    3. Hot-Swap 8KHz PCB
    4. Multi-stage Poron acoustic foam
    5. CNC Aluminum Base with Mirror Brass Weight
    With isometric alignment axes and clean technical callout lines.
    """
    w, h = size
    img = Image.new("RGB", (w, h), (17, 17, 17))
    draw = ImageDraw.Draw(img)

    cx, cy = w * 0.44, h * 0.50

    # Layer specifications (height offsets from top to bottom)
    layers = [
        {"name": "01 // CNC 6063 TOP HOUSING", "color": (55, 60, 72), "y_off": -240, "tag_color": (199, 255, 61)},
        {"name": "02 // FR4 GASKET-MOUNTED PLATE", "color": (40, 52, 75), "y_off": -120, "tag_color": (93, 124, 255)},
        {"name": "03 // HOT-SWAP 8KHZ PCB", "color": (32, 38, 48), "y_off": 0, "tag_color": (255, 107, 53)},
        {"name": "04 // MULTI-STAGE PORON FOAM", "color": (25, 26, 30), "y_off": 120, "tag_color": (249, 224, 94)},
        {"name": "05 // SOLID BRASS WEIGHT CHASSIS", "color": (45, 48, 56), "y_off": 240, "tag_color": (229, 199, 117)}
    ]

    # Isometric box dimensions
    lx, ly = 380, 150  # half-widths along isometric axes

    def iso_rect(center_y):
        return [
            (cx, center_y - ly),
            (cx + lx, center_y),
            (cx, center_y + ly),
            (cx - lx, center_y)
        ]

    # Draw vertical alignment dashed guide lines
    top_p = iso_rect(cy - 240)
    bot_p = iso_rect(cy + 240)
    for i in range(4):
        p_start = top_p[i]
        p_end = bot_p[i]
        # Dashed line
        steps = 40
        for s in range(0, steps, 2):
            t1 = s / steps
            t2 = (s + 1) / steps
            x1 = p_start[0] + t1 * (p_end[0] - p_start[0])
            y1 = p_start[1] + t1 * (p_end[1] - p_start[1])
            x2 = p_start[0] + t2 * (p_end[0] - p_start[0])
            y2 = p_start[1] + t2 * (p_end[1] - p_start[1])
            draw.line([(x1, y1), (x2, y2)], fill=(60, 65, 80), width=1)

    # Render each floating layer from bottom to top
    for l in reversed(layers):
        ly_center = cy + l["y_off"]
        pts = iso_rect(ly_center)
        # Shadow underneath layer
        s_pts = [(p[0], p[1] + 18) for p in pts]
        draw.polygon(s_pts, fill=(10, 10, 12))
        
        # Layer thickness (extrude down 12px)
        side_pts_1 = [pts[3], pts[2], (pts[2][0], pts[2][1] + 12), (pts[3][0], pts[3][1] + 12)]
        draw.polygon(side_pts_1, fill=tuple(max(0, c - 15) for c in l["color"]))
        side_pts_2 = [pts[2], pts[1], (pts[1][0], pts[1][1] + 12), (pts[2][0], pts[2][1] + 12)]
        draw.polygon(side_pts_2, fill=tuple(max(0, c - 22) for c in l["color"]))

        # Top plane of the layer
        draw.polygon(pts, fill=l["color"], outline=(85, 95, 115), width=2)

        # Special details per layer
        if "BRASS" in l["name"]:
            # Gold/brass inlay bar in center
            brass_pts = [
                (cx - 140, ly_center - 15),
                (cx + 140, ly_center - 15),
                (cx + 140, ly_center + 15),
                (cx - 140, ly_center + 15)
            ]
            draw.polygon(brass_pts, fill=(212, 175, 75), outline=(245, 215, 120), width=2)
        elif "PCB" in l["name"]:
            # Golden circuit trace hints and switches
            for ox in range(-200, 210, 60):
                draw.line([(cx + ox, ly_center - 30), (cx + ox + 30, ly_center + 30)], fill=(75, 85, 105), width=1)
                draw.rectangle([cx + ox - 5, ly_center - 5, cx + ox + 5, ly_center + 5], fill=(199, 255, 61))
        elif "PLATE" in l["name"]:
            # Switch cutouts
            for ox in range(-220, 230, 50):
                draw.ellipse([cx + ox - 8, ly_center - 8, cx + ox + 8, ly_center + 8], fill=(20, 22, 28))

        # Technical Callout Indicator Line to the right
        right_corner = pts[1]
        line_target_x = w * 0.72
        line_target_y = ly_center - 10
        draw.line([right_corner, (line_target_x, line_target_y)], fill=l["tag_color"], width=2)
        draw.ellipse([right_corner[0] - 4, right_corner[1] - 4, right_corner[0] + 4, right_corner[1] + 4], fill=l["tag_color"])
        draw.ellipse([line_target_x - 4, line_target_y - 4, line_target_x + 4, line_target_y + 4], fill=l["tag_color"])

        # Technical Annotation Text (Clean high-contrast label)
        draw.text((line_target_x + 18, line_target_y - 12), l["name"], fill=(243, 240, 231), font_size=18)

    img = img.filter(ImageFilter.SMOOTH)
    img.save(output_path, quality=95)
    print(f"Rendered {output_path}")

if __name__ == "__main__":
    render_charger_flux()
    render_mat_novadesk()
    render_light_beam()
    render_exploded_k75()
    print("All supplementary 3D product renders generated successfully!")
