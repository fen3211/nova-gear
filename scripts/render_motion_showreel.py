#!/usr/bin/env python3
"""
render_motion_showreel.py
=========================
NOVA GEAR — Dribbble / Creative Mints Style Motion Showcase
Isometric 3D Mockup · Exploded UI Layers · 60 FPS MP4

Duration: 24.0 seconds (1440 frames @ 60 FPS)
Resolution: 1920x1080 Full HD
Codec: H.264 High Profile, CRF 19, YUV420p, <40 MB

Storyline:
- 00:00 - 00:04: Intro & Fluid Assembly (stagger spring overshoot, K75 levitating)
- 00:04 - 00:09: 3D Orbit & Telemetry Pop-up (macro zoom, 45° rotation, leader lines)
- 00:09 - 00:15: Layer Explosion & Exploded View (chassis / PCB / keycaps split, specs sheet)
- 00:15 - 00:20: Keyboard Studio Morph (collapse layers, neon lime #C7FF3D wave, toggle click)
- 00:20 - 00:24: Outro & Final Brand Lockup (isometric settle, QUICK ADD, signature fade)
"""

import os
import sys
import math
import time
import subprocess
import argparse
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

# Explicit unicode-safe project root
ROOT_DIR = "D:/Projects/\u0443\u0443\u0443"
if not os.path.exists(ROOT_DIR):
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
HERO_FRAMES_DIR = os.path.join(ASSETS_DIR, "frames_hero")
SCRUB_FRAMES_DIR = os.path.join(ASSETS_DIR, "frames_scrub")
REVIEW_DIR = os.path.join(ROOT_DIR, "review")
FRAMES_OUT_DIR = os.path.join(REVIEW_DIR, "motion_frames")
OUTPUT_REVIEW = os.path.join(REVIEW_DIR, "motion_showcase.mp4")
OUTPUT_KWORK = os.path.join(ROOT_DIR, "kwork_portfolio", "work_1_hero_3d", "video.mp4")

# Video Constants
WIDTH = 1920
HEIGHT = 1080
FPS = 60.0
TOTAL_SECONDS = 24.0
TOTAL_FRAMES = int(TOTAL_SECONDS * FPS)  # 1440 frames

# Color Palette (Creative Mints warm architectural cream + Nova tech palette)
BG_CREAM_CENTER = (250, 248, 243)  # #FAF8F3
BG_CREAM_EDGE = (235, 230, 218)    # #EBE6DA
ACCENT_LIME = (61, 255, 199)       # #C7FF3D in BGR: (61, 255, 199)
ACCENT_CORAL = (37, 54, 191)       # #BF3625 in BGR: (37, 54, 191)

def safe_imwrite(path, img_bgr):
    """Encodes and writes an image safely even with non-ASCII Windows paths."""
    is_success, buf = cv2.imencode(".png", img_bgr)
    if is_success:
        with open(path, "wb") as f:
            f.write(buf)
        return True
    return False

# Fonts
def get_font(size, bold=False, mono=False):
    if mono:
        candidates = ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/lucon.ttf"]
    elif bold:
        candidates = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
    else:
        candidates = ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

# -----------------------------------------------------------------------------
# Easing & Math Utilities
# -----------------------------------------------------------------------------
def clamp(v, min_v=0.0, max_v=1.0):
    return max(min_v, min(max_v, float(v)))

def ease_out_cubic(t):
    t = clamp(t)
    return 1.0 - math.pow(1.0 - t, 3.0)

def ease_out_snappy(t):
    """Firm, velvet deceleration approximating cubic-bezier(0.16, 1, 0.3, 1)."""
    t = clamp(t)
    return 1.0 - math.pow(1.0 - t, 4.0)

def ease_in_out_cubic(t):
    t = clamp(t)
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - math.pow(-2.0 * t + 2.0, 3.0) / 2.0

def spring_overshoot(t, s=0.15):
    """Elastic spring with pleasant organic overshoot."""
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    return 1.0 - math.exp(-5.5 * t) * math.cos(t * math.pi * 3.0)

def lerp(a, b, t):
    return a + (b - a) * t

# -----------------------------------------------------------------------------
# 3D Geometry & Camera Projection
# -----------------------------------------------------------------------------
def project_points(pts_3d, pitch_deg, yaw_deg, roll_deg, cam_dist, f_len, pan=(0, 0)):
    """
    Project 3D vertices into 2D camera coordinates with perspective foreshortening.
    """
    p = math.radians(pitch_deg)
    y = math.radians(yaw_deg)
    r = math.radians(roll_deg)

    # Rotation matrix R = Rz * Rx * Ry
    Rx = np.array([
        [1.0, 0.0, 0.0],
        [0.0, math.cos(p), -math.sin(p)],
        [0.0, math.sin(p),  math.cos(p)]
    ], dtype=np.float32)

    Ry = np.array([
        [ math.cos(y), 0.0, math.sin(y)],
        [ 0.0,         1.0, 0.0],
        [-math.sin(y), 0.0, math.cos(y)]
    ], dtype=np.float32)

    Rz = np.array([
        [math.cos(r), -math.sin(r), 0.0],
        [math.sin(r),  math.cos(r), 0.0],
        [0.0,         0.0,         1.0]
    ], dtype=np.float32)

    R = Rz @ Rx @ Ry

    # Transform
    pts_rot = (R @ pts_3d.T).T
    pts_rot[:, 0] += pan[0]
    pts_rot[:, 1] += pan[1]
    pts_rot[:, 2] += cam_dist

    # Perspective divide
    z = np.maximum(pts_rot[:, 2], 10.0)
    u = 960.0 + (pts_rot[:, 0] * f_len) / z
    v = 540.0 + (pts_rot[:, 1] * f_len) / z

    return np.column_stack([u, v])

def get_layer_corners_3d(w, h, z_height, center_offset=(0, 0)):
    cx, cy = center_offset
    return np.array([
        [cx - w / 2.0, cy - h / 2.0, z_height],
        [cx + w / 2.0, cy - h / 2.0, z_height],
        [cx + w / 2.0, cy + h / 2.0, z_height],
        [cx - w / 2.0, cy + h / 2.0, z_height]
    ], dtype=np.float32)

def warp_layer_to_frame(frame_bgr, layer_rgba, proj_dst_pts, opacity=1.0):
    """
    Warps a layer with sub-pixel interpolation and alpha blends into frame_bgr.
    """
    if opacity <= 0.005:
        return frame_bgr
    
    h_l, w_l = layer_rgba.shape[:2]
    src_pts = np.float32([
        [0, 0],
        [w_l, 0],
        [w_l, h_l],
        [0, h_l]
    ])
    
    # Perspective homography matrix
    M = cv2.getPerspectiveTransform(src_pts, proj_dst_pts.astype(np.float32))
    
    # Warp RGBA layer
    warped_rgba = cv2.warpPerspective(
        layer_rgba, M, (WIDTH, HEIGHT),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)
    )
    
    # Extract warped color and alpha
    w_rgb = warped_rgba[:, :, :3]
    w_alpha = warped_rgba[:, :, 3].astype(np.float32) / 255.0
    if opacity < 0.999:
        w_alpha *= opacity
        
    mask = w_alpha > 0.002
    if not np.any(mask):
        return frame_bgr
        
    alpha_3d = w_alpha[:, :, np.newaxis]
    frame_bgr = (frame_bgr.astype(np.float32) * (1.0 - alpha_3d) + w_rgb.astype(np.float32) * alpha_3d).astype(np.uint8)
    return frame_bgr

def render_alpha_contact_shadow(frame_bgr, layer_alpha, proj_ground_pts, z_dist, base_opacity=0.42, blur_mult=0.45):
    """
    Physically grounded contact shadow warped from the ACTUAL layer alpha mask.
    Eliminates rectangular gray bounding boxes completely.
    """
    if base_opacity <= 0.01:
        return frame_bgr
        
    h_l, w_l = layer_alpha.shape[:2]
    src_pts = np.float32([
        [0, 0],
        [w_l, 0],
        [w_l, h_l],
        [0, h_l]
    ])
    
    M = cv2.getPerspectiveTransform(src_pts, proj_ground_pts.astype(np.float32))
    warped_alpha = cv2.warpPerspective(
        layer_alpha, M, (WIDTH, HEIGHT),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0
    )
    
    # Blur radius scales with elevation
    ksize = int(17 + z_dist * blur_mult)
    if ksize % 2 == 0:
        ksize += 1
    ksize = max(5, min(141, ksize))
    
    blurred = cv2.GaussianBlur(warped_alpha, (ksize, ksize), 0)
    
    # Falloff with elevation
    eff_opacity = base_opacity * max(0.18, 1.0 - z_dist * 0.0016)
    alpha_norm = (blurred.astype(np.float32) / 255.0) * eff_opacity
    
    darken = 1.0 - alpha_norm[:, :, np.newaxis]
    frame_bgr = (frame_bgr.astype(np.float32) * darken).astype(np.uint8)
    return frame_bgr

# -----------------------------------------------------------------------------
# Asset Generators (High-DPI PIL Canvases)
# -----------------------------------------------------------------------------
def create_light_canvas():
    """Generates the primary 1600x960 desktop browser canvas."""
    cw, ch = 1600, 960
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    card_bg = (250, 248, 245, 255)
    border_color = (0, 0, 0, 22)
    draw.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=32, fill=card_bg, outline=border_color, width=2)
    draw.line([32, 2, cw - 32, 2], fill=(255, 255, 255, 180), width=2)
    
    # Header Bar
    f_logo = get_font(22, bold=True)
    f_nav = get_font(13, bold=False)
    f_mono = get_font(11, mono=True)
    
    draw.text((64, 42), "NOVA GEAR", fill=(18, 18, 18), font=f_logo)
    draw.text((205, 47), "[ARCHIVE 2026]", fill=(120, 120, 120), font=f_mono)
    
    nav_items = ["K75 KEYBOARD", "KEYBOARD STUDIO", "EXPLODED ARCHITECTURE", "SPECIFICATIONS"]
    nx = 400
    for item in nav_items:
        draw.text((nx, 47), item, fill=(60, 60, 60), font=f_nav)
        nx += 175
        
    draw.rounded_rectangle([1220, 38, 1420, 68], radius=15, fill=(240, 238, 232), outline=(0, 0, 0, 15))
    draw.ellipse([1236, 50, 1244, 58], fill=(37, 191, 102))  # green live dot
    draw.text((1254, 46), "BATCH 04 // IN STOCK", fill=(40, 40, 40), font=f_mono)
    
    draw.rounded_rectangle([1440, 38, 1536, 68], radius=15, fill=(18, 18, 18))
    draw.text((1462, 46), "CART [1]", fill=(250, 250, 250), font=f_mono)
    
    draw.line([64, 88, cw - 64, 88], fill=(0, 0, 0, 16), width=1)
    
    # Hero Content
    f_h1 = get_font(70, bold=True)
    f_sub = get_font(17, bold=False)
    f_pill = get_font(12, bold=True)
    
    draw.text((64, 150), "BETTER GEAR.", fill=(18, 18, 18), font=f_h1)
    draw.text((64, 230), "BETTER DAYS.", fill=(18, 18, 18), font=f_h1)
    
    draw.text((64, 335), "Engineered for mechanical purists.", fill=(90, 90, 90), font=f_sub)
    draw.text((64, 365), "Solid 6063-T6 aluminum chassis with acoustic gasket isolation.", fill=(110, 110, 110), font=f_sub)
    
    tags = ["75% COMPACT LAYOUT", "1,850G SOLID BRASS WEIGHT", "TTC LINEAR 45G // LUBED", "QMK / VIA OPEN SOURCE"]
    tx = 64
    for tag in tags:
        tw = draw.textlength(tag, font=f_pill)
        draw.rounded_rectangle([tx, 420, tx + tw + 22, 452], radius=8, fill=(240, 237, 230), outline=(0, 0, 0, 12))
        draw.text((tx + 11, 429), tag, fill=(35, 35, 35), font=f_pill)
        tx += int(tw + 30)
        
    draw.line([64, 500, 400, 500], fill=(0, 0, 0, 14), width=1)
    draw.text((64, 525), "SERIES 01 // K75 PRO", fill=(120, 120, 120), font=f_mono)
    draw.text((64, 550), "$289.00 USD", fill=(18, 18, 18), font=get_font(28, bold=True))
    draw.text((64, 595), "SHIPS WITH METEORITE ANODIZED CHASSIS", fill=(100, 100, 100), font=f_mono)
    draw.text((64, 615), "FACTORY TUNED ACOUSTIC DAMPENING", fill=(100, 100, 100), font=f_mono)
    
    draw.rounded_rectangle([64, 655, 290, 705], radius=12, fill=(18, 18, 18))
    draw.text((92, 670), "ORDER NOW  →", fill=(255, 255, 255), font=get_font(14, bold=True))
    
    draw.line([1500, 450, 1540, 450], fill=(0, 0, 0, 16), width=1)
    draw.line([1520, 430, 1520, 470], fill=(0, 0, 0, 16), width=1)
    
    draw.line([64, 880, cw - 64, 880], fill=(0, 0, 0, 16), width=1)
    draw.text((64, 905), "NOVA GEAR ENGINEERING CORP. · SAN FRANCISCO / TOKYO · ALL RIGHTS RESERVED", fill=(140, 140, 140), font=f_mono)
    draw.text((1340, 905), "PRECISION CAD V4.2 [PASSED]", fill=(140, 140, 140), font=f_mono)
    
    arr = np.array(img)
    arr[:, :, [0, 2]] = arr[:, :, [2, 0]]
    return arr

def create_specs_mode_canvas():
    """Generates clean minimal canvas variant for Phase 3 (no headline clutter behind specs card)."""
    cw, ch = 1600, 960
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    card_bg = (250, 248, 245, 255)
    border_color = (0, 0, 0, 22)
    draw.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=32, fill=card_bg, outline=border_color, width=2)
    draw.line([32, 2, cw - 32, 2], fill=(255, 255, 255, 180), width=2)
    
    f_logo = get_font(22, bold=True)
    f_nav = get_font(13, bold=False)
    f_mono = get_font(11, mono=True)
    
    draw.text((64, 42), "NOVA GEAR", fill=(18, 18, 18), font=f_logo)
    draw.text((205, 47), "[ARCHIVE 2026]", fill=(120, 120, 120), font=f_mono)
    
    nav_items = ["K75 KEYBOARD", "KEYBOARD STUDIO", "EXPLODED ARCHITECTURE", "SPECIFICATIONS"]
    nx = 400
    for item in nav_items:
        draw.text((nx, 47), item, fill=(60, 60, 60), font=f_nav)
        nx += 175
        
    draw.rounded_rectangle([1220, 38, 1420, 68], radius=15, fill=(240, 238, 232), outline=(0, 0, 0, 15))
    draw.ellipse([1236, 50, 1244, 58], fill=(37, 191, 102))
    draw.text((1254, 46), "BATCH 04 // IN STOCK", fill=(40, 40, 40), font=f_mono)
    
    draw.rounded_rectangle([1440, 38, 1536, 68], radius=15, fill=(18, 18, 18))
    draw.text((1462, 46), "CART [1]", fill=(250, 250, 250), font=f_mono)
    
    draw.line([64, 88, cw - 64, 88], fill=(0, 0, 0, 16), width=1)
    
    # Bottom markings
    draw.line([64, 880, cw - 64, 880], fill=(0, 0, 0, 16), width=1)
    draw.text((64, 905), "NOVA GEAR ENGINEERING CORP. · SAN FRANCISCO / TOKYO · ALL RIGHTS RESERVED", fill=(140, 140, 140), font=f_mono)
    draw.text((1340, 905), "EXPLODED VIEW CAD // 6-STAGE ACOUSTIC RIG", fill=(140, 140, 140), font=f_mono)
    
    arr = np.array(img)
    arr[:, :, [0, 2]] = arr[:, :, [2, 0]]
    return arr

def create_dark_studio_canvas():
    """Generates the dark Studio Workstation canvas for Phase 4."""
    cw, ch = 1600, 960
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    card_bg = (20, 21, 26, 255)
    border_color = (61, 255, 199, 65)  # Neon lime subtle border
    draw.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=32, fill=card_bg, outline=border_color, width=2)
    
    f_logo = get_font(22, bold=True)
    f_mono = get_font(11, mono=True)
    f_title = get_font(38, bold=True)
    
    draw.text((64, 42), "NOVA GEAR", fill=(255, 255, 255), font=f_logo)
    draw.text((205, 47), "[KEYBOARD STUDIO v2.4]", fill=(61, 255, 199), font=f_mono)
    
    draw.line([64, 88, cw - 64, 88], fill=(255, 255, 255, 20), width=1)
    
    # Studio Headline
    draw.text((64, 130), "KEYBOARD STUDIO // ACTIVE REMAPPER", fill=(255, 255, 255), font=f_title)
    draw.text((64, 185), "REAL-TIME HARDWARE FIRMWARE · LOW-LATENCY LIGHTING MATRIX", fill=(160, 160, 160), font=f_mono)
    
    # Toggle switch background for macOS / WIN
    draw.rounded_rectangle([64, 230, 280, 275], radius=22, fill=(32, 34, 42), outline=(255, 255, 255, 25))
    # macOS active pill
    draw.rounded_rectangle([68, 234, 170, 271], radius=18, fill=(61, 255, 199))
    draw.text((95, 245), "macOS", fill=(18, 18, 18), font=get_font(13, bold=True))
    draw.text((205, 245), "WIN", fill=(180, 180, 180), font=get_font(13, bold=True))
    
    # Switch Profile Pills
    profiles = ["[ TTC LINEAR 45G ]", "[ SOUTH-FACING RGB ]", "[ LAYER 0: DEFAULT ]", "[ 1000 HZ POLLING ]"]
    px = 310
    for p in profiles:
        pw = draw.textlength(p, font=f_mono)
        draw.rounded_rectangle([px, 234, px + pw + 20, 271], radius=8, fill=(28, 30, 38), outline=(255, 255, 255, 15))
        draw.text((px + 10, 246), p, fill=(200, 200, 200), font=f_mono)
        px += int(pw + 30)
        
    arr = np.array(img)
    arr[:, :, [0, 2]] = arr[:, :, [2, 0]]
    return arr

def create_telemetry_badge(title, subtitle, chip_color_bgr, value_tag=None):
    """Creates a floating frosted glass telemetry badge."""
    w, h = 340, 96
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=18, fill=(255, 255, 255, 245), outline=(0, 0, 0, 28), width=1)
    draw.line([18, 2, w - 18, 2], fill=(255, 255, 255, 255), width=2)
    
    cr, cg, cb = chip_color_bgr[2], chip_color_bgr[1], chip_color_bgr[0]
    draw.rounded_rectangle([20, 22, 28, 74], radius=4, fill=(cr, cg, cb, 255))
    
    f_title = get_font(15, bold=True)
    f_sub = get_font(11, mono=True)
    
    draw.text((44, 24), title, fill=(18, 18, 18), font=f_title)
    draw.text((44, 48), subtitle, fill=(100, 100, 100), font=f_sub)
    if value_tag:
        draw.text((44, 68), value_tag, fill=(140, 140, 140), font=f_sub)
        
    arr = np.array(img)
    arr[:, :, [0, 2]] = arr[:, :, [2, 0]]
    return arr

def create_exploded_specs_sheet():
    """Creates the premium architectural layer specs card (Phase 3)."""
    w, h = 480, 580
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=24, fill=(255, 255, 255, 245), outline=(0, 0, 0, 30), width=2)
    draw.line([24, 2, w - 24, 2], fill=(255, 255, 255, 255), width=2)
    
    f_head = get_font(18, bold=True)
    f_mono = get_font(11, mono=True)
    f_item_num = get_font(13, bold=True, mono=True)
    f_item_title = get_font(14, bold=True)
    f_item_sub = get_font(11, bold=False)
    
    draw.text((32, 28), "LAYER ARCHITECTURE", fill=(18, 18, 18), font=f_head)
    draw.text((32, 54), "NOVA K75 // 6-STAGE ACOUSTIC STACK", fill=(110, 110, 110), font=f_mono)
    draw.line([32, 78, w - 32, 78], fill=(0, 0, 0, 16), width=1)
    
    layers = [
        ("01", "PBT DOUBLE-SHOT KEYCAPS", "1.5mm wall thickness, dye-sublimated legends"),
        ("02", "CNC 6063 TOP HOUSING", "Bead-blasted, meteorite anodized aluminum"),
        ("03", "TTC LINEAR 45G SWITCHES", "Factory lubricated POM stems with gold springs"),
        ("04", "FR4 FLEX-CUT MOUNT PLATE", "Precision laser-cut acoustic flex isolation"),
        ("05", "PORON GASKET DAMPENING", "Dual IXPE acoustic foam sound profile"),
        ("06", "1,850G SOLID BRASS WEIGHT", "Mirror polished PVD coated acoustic anchor")
    ]
    
    y = 96
    for num, title, sub in layers:
        draw.text((32, y), num, fill=(180, 50, 40), font=f_item_num)
        draw.text((68, y), title, fill=(20, 20, 20), font=f_item_title)
        draw.text((68, y + 20), sub, fill=(100, 100, 100), font=f_item_sub)
        y += 66
        draw.line([32, y - 10, w - 32, y - 10], fill=(0, 0, 0, 10), width=1)
        
    arr = np.array(img)
    arr[:, :, [0, 2]] = arr[:, :, [2, 0]]
    return arr

def create_outro_brand_card():
    """Creates the final Quick Add & Brand lockup card (Phase 5)."""
    w, h = 540, 150
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=28, fill=(18, 18, 20, 252), outline=(255, 255, 255, 24), width=2)
    
    # Quick Add CTA Button on right
    draw.rounded_rectangle([300, 32, 508, 92], radius=18, fill=(61, 255, 199))  # Neon lime
    draw.text((328, 48), "QUICK ADD — $289", fill=(18, 18, 18), font=get_font(13, bold=True))
    draw.text((478, 48), "→", fill=(18, 18, 18), font=get_font(14, bold=True))
    
    # Left Brand Lockup
    draw.text((36, 32), "NOVA GEAR", fill=(255, 255, 255), font=get_font(22, bold=True))
    draw.text((36, 62), "SERIES 01 // K75 PRO EDITION", fill=(180, 180, 180), font=get_font(11, mono=True))
    
    # 5 Vector Rating Stars
    sx = 36
    for _ in range(5):
        pts = []
        for i in range(10):
            r = 6 if i % 2 == 0 else 3
            ang = -math.pi / 2 + i * (math.pi / 5)
            pts.append((sx + 6 + r * math.cos(ang), 95 + r * math.sin(ang)))
        draw.polygon(pts, fill=(61, 255, 199))
        sx += 16
        
    draw.text((sx + 10, 88), "4.9 / 5.0 (428 REVIEWS)", fill=(61, 255, 199), font=get_font(10, mono=True))
    
    arr = np.array(img)
    arr[:, :, [0, 2]] = arr[:, :, [2, 0]]
    return arr

def create_signature_outro_layer():
    """Renders the final centered minimalist brand lockup for the last second."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    f_brand = get_font(42, bold=True)
    f_sub = get_font(14, mono=True)
    f_tag = get_font(12, mono=True)
    
    # Centered texts
    b_txt = "N O V A   G E A R"
    bw = draw.textlength(b_txt, font=f_brand)
    draw.text(((WIDTH - bw) / 2.0, 480), b_txt, fill=(18, 18, 18), font=f_brand)
    
    s_txt = "STUDIO GRADE MECHANICAL HARDWARE"
    sw = draw.textlength(s_txt, font=f_sub)
    draw.text(((WIDTH - sw) / 2.0, 545), s_txt, fill=(100, 100, 100), font=f_sub)
    
    t_txt = "SAN FRANCISCO · TOKYO · EST. 2026"
    tw = draw.textlength(t_txt, font=f_tag)
    draw.text(((WIDTH - tw) / 2.0, 580), t_txt, fill=(140, 140, 140), font=f_tag)
    
    arr = np.array(img)
    arr[:, :, [0, 2]] = arr[:, :, [2, 0]]
    return arr

# -----------------------------------------------------------------------------
# Background Environment Renderer
# -----------------------------------------------------------------------------
def generate_cream_background():
    """Generates the soft radial vignette architectural cream background."""
    bg = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    
    y, x = np.ogrid[:HEIGHT, :WIDTH]
    dist_sq = ((x - 960.0) / 1000.0) ** 2 + ((y - 540.0) / 600.0) ** 2
    dist_norm = np.clip(np.sqrt(dist_sq), 0.0, 1.0)
    
    c_center = np.array(BG_CREAM_CENTER[::-1], dtype=np.float32)  # BGR
    c_edge = np.array(BG_CREAM_EDGE[::-1], dtype=np.float32)      # BGR
    
    grad = c_center[None, None, :] * (1.0 - dist_norm[:, :, None]) + c_edge[None, None, :] * dist_norm[:, :, None]
    
    noise = np.random.normal(0, 1.0, (HEIGHT, WIDTH, 1))
    grad = np.clip(grad + noise, 0, 255).astype(np.uint8)
    return grad

# -----------------------------------------------------------------------------
# Frame Sequence Loader
# -----------------------------------------------------------------------------
def load_all_frames():
    print("[*] Loading high-resolution asset frames...")
    hero_frames = []
    for i in range(56):
        path = os.path.join(HERO_FRAMES_DIR, f"k75_hero_{i:02d}.webp")
        im = Image.open(path).convert("RGBA")
        arr = np.array(im)
        arr[:, :, [0, 2]] = arr[:, :, [2, 0]]  # RGBA to BGRA
        hero_frames.append(arr)
        
    scrub_frames = []
    for i in range(57):
        path = os.path.join(SCRUB_FRAMES_DIR, f"k75_scrub_{i:02d}.webp")
        im = Image.open(path).convert("RGBA")
        arr = np.array(im)
        arr[:, :, [0, 2]] = arr[:, :, [2, 0]]  # RGBA to BGRA
        scrub_frames.append(arr)
        
    print(f"    Loaded {len(hero_frames)} hero frames and {len(scrub_frames)} scrub frames.")
    return hero_frames, scrub_frames

# -----------------------------------------------------------------------------
# Main Video Choreography & Render Loop
# -----------------------------------------------------------------------------
def render_frame_pipeline(f_idx, bg_base, hero_frames, scrub_frames, ui_light, ui_specs, ui_dark, badges, card_specs, card_outro, signature_outro):
    """
    Renders a single 60 FPS frame for index f_idx (0 to 1439).
    """
    t_sec = f_idx / FPS
    frame = bg_base.copy()
    
    # -------------------------------------------------------------------------
    # Choreography & Camera Parameters across 5 Phases
    # -------------------------------------------------------------------------
    pitch = 28.0
    yaw = -18.0
    roll = 3.5
    cam_dist = 2200.0
    f_len = 2000.0
    pan_x = 0.0
    pan_y = 0.0
    
    canvas_z = 0.0
    canvas_scale = 1.0
    canvas_opacity = 1.0
    canvas_specs_blend = 0.0
    canvas_dark_blend = 0.0
    
    k75_z = 60.0
    k75_frame_type = "hero"
    k75_frame_idx = 0
    k75_scale = 0.94
    k75_offset_x = 360.0
    k75_offset_y = 40.0
    
    show_telemetry = False
    telemetry_spring = 0.0
    
    show_exploded_specs = False
    specs_progress = 0.0
    
    is_studio_phase = False
    studio_progress = 0.0
    keywave_pos = -999.0
    cursor_click_t = 0.0
    
    show_outro = False
    outro_progress = 0.0
    sig_outro_opacity = 0.0
    
    # --- PHASE 1: 00:00 - 00:04 (Frames 0 - 240) --- Intro & Fluid Assembly
    if f_idx < 240:
        p1_t = f_idx / 240.0
        canvas_in = spring_overshoot(p1_t * 1.15)
        pitch = lerp(35.0, 28.0, ease_out_snappy(p1_t))
        yaw = lerp(-26.0, -18.0, ease_out_snappy(p1_t))
        roll = lerp(6.0, 3.5, ease_out_snappy(p1_t))
        cam_dist = lerp(2650.0, 2200.0, ease_out_snappy(p1_t))
        
        canvas_scale = lerp(0.88, 1.0, canvas_in)
        canvas_opacity = ease_out_cubic(clamp(p1_t * 3.0))
        
        k_t = clamp((p1_t - 0.12) / 0.88)
        k_spring = spring_overshoot(k_t)
        k75_z = lerp(450.0, 60.0, k_spring)
        k75_scale = lerp(0.80, 0.94, k_spring)
        k75_frame_idx = 0
        
    # --- PHASE 2: 00:04 - 00:09 (Frames 240 - 540) --- Orbit & Telemetry Pop-up
    elif f_idx < 540:
        p2_t = (f_idx - 240) / 300.0
        ease_p2 = ease_in_out_cubic(p2_t)
        pitch = lerp(28.0, 24.5, ease_p2)
        yaw = lerp(-18.0, -12.0, ease_p2)
        roll = lerp(3.5, 2.0, ease_p2)
        cam_dist = lerp(2200.0, 1650.0, ease_p2)
        pan_x = lerp(0.0, -280.0, ease_p2)
        pan_y = lerp(0.0, 30.0, ease_p2)
        
        rot_progress = ease_in_out_cubic(clamp(p2_t * 1.1))
        k75_frame_idx = int(rot_progress * 18.0)
        k75_frame_idx = min(18, max(0, k75_frame_idx))
        
        k75_z = 65.0 + math.sin(p2_t * math.pi * 3.0) * 8.0
        
        if p2_t > 0.25:
            show_telemetry = True
            telemetry_t = clamp((p2_t - 0.25) / 0.6)
            telemetry_spring = spring_overshoot(telemetry_t)
            
    # --- PHASE 3: 00:09 - 00:15 (Frames 540 - 900) --- Layer Explosion & Exploded View
    elif f_idx < 900:
        p3_t = (f_idx - 540) / 360.0
        ease_p3 = ease_in_out_cubic(p3_t)
        
        pitch = lerp(24.5, 30.5, ease_p3)
        yaw = lerp(-12.0, -19.0, ease_p3)
        roll = lerp(2.0, 3.8, ease_p3)
        cam_dist = lerp(1650.0, 2380.0, ease_p3)
        pan_x = lerp(-280.0, 60.0, ease_p3)
        pan_y = lerp(30.0, -10.0, ease_p3)
        
        k75_frame_type = "scrub"
        scrub_t = ease_in_out_cubic(clamp(p3_t * 1.25))
        k75_frame_idx = int(scrub_t * 56.0)
        k75_frame_idx = min(56, max(0, k75_frame_idx))
        k75_z = lerp(65.0, 130.0, scrub_t)
        k75_scale = 1.22
        k75_offset_x = 350.0
        k75_offset_y = 65.0
        
        # Smoothly blend to specs minimal canvas so specs card doesn't collide with text
        canvas_specs_blend = ease_out_snappy(clamp(p3_t * 2.5))
        
        show_exploded_specs = True
        specs_t = clamp((p3_t - 0.15) / 0.7)
        specs_progress = spring_overshoot(specs_t)
        
    # --- PHASE 4: 00:15 - 00:20 (Frames 900 - 1200) --- Keyboard Studio Morph & Keywave
    elif f_idx < 1200:
        p4_t = (f_idx - 900) / 300.0
        is_studio_phase = True
        studio_progress = p4_t
        
        # Reverse scrub frames back to collapsed solid body (56 -> 0)
        collapse_t = clamp(p4_t * 2.2)
        scrub_rev = 1.0 - ease_in_out_cubic(collapse_t)
        if collapse_t < 1.0:
            k75_frame_type = "scrub"
            k75_frame_idx = int(scrub_rev * 56.0)
            k75_frame_idx = min(56, max(0, k75_frame_idx))
            k75_z = lerp(60.0, 130.0, scrub_rev)
            k75_scale = 1.22
            k75_offset_x = 350.0
            k75_offset_y = 65.0
            canvas_specs_blend = scrub_rev
        else:
            k75_frame_type = "hero"
            k75_frame_idx = 0
            k75_z = 60.0 + math.sin((p4_t - 0.45) * math.pi * 2.0) * 5.0
            k75_scale = 0.94
            k75_offset_x = 360.0
            k75_offset_y = 40.0
            canvas_specs_blend = 0.0
            
        canvas_dark_blend = ease_out_snappy(clamp((p4_t - 0.15) / 0.6))
        
        pitch = lerp(30.5, 27.5, ease_out_snappy(p4_t))
        yaw = lerp(-19.0, -16.0, ease_out_snappy(p4_t))
        cam_dist = lerp(2380.0, 2100.0, ease_out_snappy(p4_t))
        pan_x = lerp(60.0, -40.0, ease_out_snappy(p4_t))
        pan_y = lerp(-10.0, 0.0, ease_out_snappy(p4_t))
        
        if p4_t > 0.35:
            wave_t = clamp((p4_t - 0.35) / 0.55)
            keywave_pos = wave_t * 1800.0
            
        if p4_t > 0.40:
            cursor_click_t = clamp((p4_t - 0.40) / 0.55)
            
    # --- PHASE 5: 00:20 - 00:24 (Frames 1200 - 1440) --- Outro & Final Brand Lockup
    else:
        p5_t = (f_idx - 1200) / 240.0
        k75_frame_type = "hero"
        k75_frame_idx = 0
        k75_z = 60.0
        k75_scale = 0.94
        k75_offset_x = 360.0
        k75_offset_y = 40.0
        canvas_dark_blend = lerp(1.0, 0.0, ease_out_snappy(clamp(p5_t * 1.5)))
        
        pitch = lerp(27.5, 28.0, ease_out_snappy(p5_t))
        yaw = lerp(-16.0, -18.0, ease_out_snappy(p5_t))
        roll = lerp(3.8, 3.2, ease_out_snappy(p5_t))
        cam_dist = lerp(2100.0, 2180.0, ease_out_snappy(p5_t))
        pan_x = lerp(-40.0, 0.0, ease_out_snappy(p5_t))
        pan_y = lerp(0.0, 0.0, ease_out_snappy(p5_t))
        
        show_outro = True
        outro_progress = spring_overshoot(clamp(p5_t * 1.3))
        
        # Smooth fade-out of canvas and fade-in of signature centered outro at the end
        if p5_t > 0.78:
            end_t = clamp((p5_t - 0.78) / 0.22)
            canvas_opacity = 1.0 - ease_out_cubic(end_t)
            sig_outro_opacity = ease_out_cubic(clamp((p5_t - 0.82) / 0.18))
            
    # -------------------------------------------------------------------------
    # 3D Layer Rendering
    # -------------------------------------------------------------------------
    
    # 1. Base Canvas (Z = 0)
    canvas_w = int(1600 * canvas_scale)
    canvas_h = int(960 * canvas_scale)
    corners_canvas_3d = get_layer_corners_3d(canvas_w, canvas_h, z_height=canvas_z)
    proj_canvas = project_points(corners_canvas_3d, pitch, yaw, roll, cam_dist, f_len, pan=(pan_x, pan_y))
    
    frame = render_alpha_contact_shadow(frame, ui_light[:, :, 3], proj_canvas, z_dist=80.0, base_opacity=0.38 * canvas_opacity, blur_mult=0.5)
    
    # Canvas Blending (Light vs Specs Minimal vs Dark Studio)
    active_canvas = ui_light
    if canvas_specs_blend > 0.01:
        active_canvas = cv2.addWeighted(ui_light, 1.0 - canvas_specs_blend, ui_specs, canvas_specs_blend, 0)
    if canvas_dark_blend > 0.01:
        active_canvas = cv2.addWeighted(active_canvas, 1.0 - canvas_dark_blend, ui_dark, canvas_dark_blend, 0)
        
    frame = warp_layer_to_frame(frame, active_canvas, proj_canvas, opacity=canvas_opacity)
        
    # 2. 3D Keyboard Layer (Floating at k75_z)
    if k75_frame_type == "hero":
        k_img = hero_frames[k75_frame_idx].copy()
        kw, kh = int(1200 * k75_scale), int(800 * k75_scale)
    else:
        k_img = scrub_frames[k75_frame_idx].copy()
        kw, kh = int(720 * k75_scale), int(720 * k75_scale)
        
    # Neon Lime Keywave effect during Phase 4
    if keywave_pos > -100.0:
        kh_cur, kw_cur = k_img.shape[:2]
        y_g, x_g = np.ogrid[:kh_cur, :kw_cur]
        beam_dist = np.abs((x_g + y_g * 0.8) - keywave_pos)
        wave_mask = np.clip(1.0 - (beam_dist / 140.0), 0.0, 1.0) ** 2.0
        
        lime_bgr = np.array([61, 255, 199], dtype=np.float32)
        alpha_factor = (k_img[:, :, 3].astype(np.float32) / 255.0) * wave_mask
        
        glow = (lime_bgr[None, None, :] * alpha_factor[:, :, None] * 1.8).astype(np.uint8)
        k_rgb = cv2.add(k_img[:, :, :3], glow)
        k_img[:, :, :3] = k_rgb
        
    corners_k75_3d = get_layer_corners_3d(kw, kh, z_height=k75_z, center_offset=(k75_offset_x, k75_offset_y))
    proj_k75 = project_points(corners_k75_3d, pitch, yaw, roll, cam_dist, f_len, pan=(pan_x, pan_y))
    
    corners_k75_ground = get_layer_corners_3d(int(kw * 0.95), int(kh * 0.95), z_height=0.0, center_offset=(k75_offset_x + 12.0, k75_offset_y + 20.0))
    proj_k75_shadow = project_points(corners_k75_ground, pitch, yaw, roll, cam_dist, f_len, pan=(pan_x, pan_y))
    frame = render_alpha_contact_shadow(frame, k_img[:, :, 3], proj_k75_shadow, z_dist=k75_z, base_opacity=0.45 * canvas_opacity, blur_mult=0.4)
    
    frame = warp_layer_to_frame(frame, k_img, proj_k75, opacity=canvas_opacity)
    
    # 3. Telemetry Badges & Leader Lines (Phase 2)
    if show_telemetry and telemetry_spring > 0.01:
        encoder_3d = np.array([[k75_offset_x + kw * 0.30, k75_offset_y - kh * 0.20, k75_z + 20.0]], dtype=np.float32)
        proj_enc = project_points(encoder_3d, pitch, yaw, roll, cam_dist, f_len, pan=(pan_x, pan_y))[0]
        
        b1_w, b1_h = 340, 96
        b1_scale = telemetry_spring
        b1_3d = get_layer_corners_3d(int(b1_w * b1_scale), int(b1_h * b1_scale), z_height=k75_z + 140.0, center_offset=(k75_offset_x + 360.0, k75_offset_y - 170.0))
        proj_b1 = project_points(b1_3d, pitch, yaw, roll, cam_dist, f_len, pan=(pan_x, pan_y))
        
        frame = render_alpha_contact_shadow(frame, badges["encoder"][:, :, 3], proj_b1, z_dist=120.0, base_opacity=0.3, blur_mult=0.3)
        frame = warp_layer_to_frame(frame, badges["encoder"], proj_b1, opacity=clamp(telemetry_spring))
        
        b1_anchor = (int(proj_b1[3, 0]), int(proj_b1[3, 1]))
        p_enc = (int(proj_enc[0]), int(proj_enc[1]))
        mid_pt = (b1_anchor[0], p_enc[1])
        cv2.line(frame, p_enc, mid_pt, (18, 18, 18), 2, lineType=cv2.LINE_AA)
        cv2.line(frame, mid_pt, b1_anchor, (18, 18, 18), 2, lineType=cv2.LINE_AA)
        cv2.circle(frame, p_enc, 4, (37, 54, 191), -1, lineType=cv2.LINE_AA)
        cv2.circle(frame, p_enc, int(8 + math.sin(t_sec * 8.0) * 3), (37, 54, 191), 1, lineType=cv2.LINE_AA)
        
        sw_3d = np.array([[k75_offset_x - kw * 0.08, k75_offset_y - kh * 0.04, k75_z + 20.0]], dtype=np.float32)
        proj_sw = project_points(sw_3d, pitch, yaw, roll, cam_dist, f_len, pan=(pan_x, pan_y))[0]
        
        b2_3d = get_layer_corners_3d(int(b1_w * b1_scale), int(b1_h * b1_scale), z_height=k75_z + 160.0, center_offset=(k75_offset_x - 360.0, k75_offset_y - 210.0))
        proj_b2 = project_points(b2_3d, pitch, yaw, roll, cam_dist, f_len, pan=(pan_x, pan_y))
        
        frame = render_alpha_contact_shadow(frame, badges["switches"][:, :, 3], proj_b2, z_dist=140.0, base_opacity=0.3, blur_mult=0.3)
        frame = warp_layer_to_frame(frame, badges["switches"], proj_b2, opacity=clamp(telemetry_spring))
        
        b2_anchor = (int(proj_b2[2, 0]), int(proj_b2[2, 1]))
        p_sw = (int(proj_sw[0]), int(proj_sw[1]))
        mid_sw = (b2_anchor[0], p_sw[1])
        cv2.line(frame, p_sw, mid_sw, (18, 18, 18), 2, lineType=cv2.LINE_AA)
        cv2.line(frame, mid_sw, b2_anchor, (18, 18, 18), 2, lineType=cv2.LINE_AA)
        cv2.circle(frame, p_sw, 4, (61, 255, 199), -1, lineType=cv2.LINE_AA)
        cv2.circle(frame, p_sw, int(8 + math.sin(t_sec * 8.0 + 1.5) * 3), (61, 255, 199), 1, lineType=cv2.LINE_AA)
        
    # 4. Exploded Architecture Specs Card & Architecture Leader Lines (Phase 3)
    if show_exploded_specs and specs_progress > 0.01:
        cw_sp = int(480 * specs_progress)
        ch_sp = int(580 * specs_progress)
        sp_3d = get_layer_corners_3d(cw_sp, ch_sp, z_height=180.0, center_offset=(-380.0, 30.0))
        proj_sp = project_points(sp_3d, pitch, yaw, roll, cam_dist, f_len, pan=(pan_x, pan_y))
        
        frame = render_alpha_contact_shadow(frame, card_specs[:, :, 3], proj_sp, z_dist=180.0, base_opacity=0.35, blur_mult=0.45)
        frame = warp_layer_to_frame(frame, card_specs, proj_sp, opacity=clamp(specs_progress))
        
        # Subtle architectural leader lines to keycap and plate layers
        if specs_progress > 0.7:
            line_op = clamp((specs_progress - 0.7) / 0.3)
            # Anchor 1: Keycaps
            pt_sp_01 = (int(proj_sp[1, 0]), int(proj_sp[1, 1] + 105 * specs_progress))
            pt_target_01 = (int(proj_k75[0, 0] + kw * 0.15), int(proj_k75[0, 1] + 30))
            cv2.line(frame, pt_sp_01, pt_target_01, (180, 50, 40), 1, lineType=cv2.LINE_AA)
            cv2.circle(frame, pt_target_01, 3, (180, 50, 40), -1, lineType=cv2.LINE_AA)
            
            # Anchor 2: Gasket Plate
            pt_sp_04 = (int(proj_sp[1, 0]), int(proj_sp[1, 1] + 300 * specs_progress))
            pt_target_04 = (int(proj_k75[0, 0] + kw * 0.12), int(proj_k75[0, 1] + kh * 0.45))
            cv2.line(frame, pt_sp_04, pt_target_04, (37, 54, 191), 1, lineType=cv2.LINE_AA)
            cv2.circle(frame, pt_target_04, 3, (37, 54, 191), -1, lineType=cv2.LINE_AA)
        
    # Interactive Cursor and Click Ripple during Phase 4
    if cursor_click_t > 0.0:
        toggle_3d = np.array([[-1600.0 / 2.0 + 120.0, -960.0 / 2.0 + 252.0, 10.0]], dtype=np.float32)
        proj_toggle = project_points(toggle_3d, pitch, yaw, roll, cam_dist, f_len, pan=(pan_x, pan_y))[0]
        tx_cur, ty_cur = int(proj_toggle[0]), int(proj_toggle[1])
        
        c_move = ease_out_snappy(clamp(cursor_click_t * 1.8))
        cx = int(lerp(tx_cur + 90.0, tx_cur, c_move))
        cy = int(lerp(ty_cur + 110.0, ty_cur, c_move))
        
        cur_scale = 1.0
        if cursor_click_t > 0.55:
            click_sub = (cursor_click_t - 0.55) / 0.45
            cur_scale = 0.88 if click_sub < 0.3 else 1.0
            
            rip_r = int(lerp(6.0, 42.0, click_sub))
            cv2.circle(frame, (tx_cur, ty_cur), rip_r, (61, 255, 199), 2, lineType=cv2.LINE_AA)
            
        cursor_poly = np.array([
            [cx, cy],
            [cx, int(cy + 18 * cur_scale)],
            [int(cx + 5 * cur_scale), int(cy + 14 * cur_scale)],
            [int(cx + 10 * cur_scale), int(cy + 22 * cur_scale)],
            [int(cx + 13 * cur_scale), int(cy + 20 * cur_scale)],
            [int(cx + 8 * cur_scale), int(cy + 12 * cur_scale)],
            [int(cx + 14 * cur_scale), int(cy + 12 * cur_scale)]
        ], dtype=np.int32)
        
        cv2.fillPoly(frame, [cursor_poly], (255, 255, 255), lineType=cv2.LINE_AA)
        cv2.polylines(frame, [cursor_poly], True, (18, 18, 18), 1, lineType=cv2.LINE_AA)

    # 5. Outro Brand Lockup Card (Phase 5)
    if show_outro and outro_progress > 0.01:
        ow = int(540 * outro_progress)
        oh = int(150 * outro_progress)
        outro_3d = get_layer_corners_3d(ow, oh, z_height=160.0, center_offset=(0.0, 270.0))
        proj_outro = project_points(outro_3d, pitch, yaw, roll, cam_dist, f_len, pan=(pan_x, pan_y))
        
        frame = render_alpha_contact_shadow(frame, card_outro[:, :, 3], proj_outro, z_dist=160.0, base_opacity=0.4 * canvas_opacity, blur_mult=0.4)
        frame = warp_layer_to_frame(frame, card_outro, proj_outro, opacity=clamp(outro_progress * canvas_opacity))
        
    # Signature Outro fade-in at the very end
    if sig_outro_opacity > 0.01:
        alpha_sig = (signature_outro[:, :, 3].astype(np.float32) / 255.0) * sig_outro_opacity
        rgb_sig = signature_outro[:, :, :3].astype(np.float32)
        frame = (frame.astype(np.float32) * (1.0 - alpha_sig[:, :, np.newaxis]) + rgb_sig * alpha_sig[:, :, np.newaxis]).astype(np.uint8)

    return frame

# -----------------------------------------------------------------------------
# Main Execution Pipeline
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Render NOVA GEAR Dribbble Motion Showcase 60 FPS")
    parser.add_argument("--preview-frames", action="store_true", help="Only render key check frames and exit")
    parser.add_argument("--test-range", type=int, nargs=2, help="Render range of frames e.g. 0 120")
    args = parser.parse_args()

    os.makedirs(FRAMES_OUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_KWORK), exist_ok=True)
    
    print("=" * 70)
    print("NOVA GEAR — CREATIVE MINTS STYLE MOTION SHOWCASE (60 FPS)")
    print(f"Target Resolution : {WIDTH}x{HEIGHT} (Full HD)")
    print(f"Target Duration   : {TOTAL_SECONDS:.1f}s ({TOTAL_FRAMES} frames @ {FPS} FPS)")
    print(f"Target Review Path: {OUTPUT_REVIEW}")
    print(f"Target Kwork Path : {OUTPUT_KWORK}")
    print("=" * 70)

    # 1. Pre-generate all UI Canvases and Badges
    print("[*] Generating vector UI layouts & frosted badges...")
    bg_base = generate_cream_background()
    ui_light = create_light_canvas()
    ui_specs = create_specs_mode_canvas()
    ui_dark = create_dark_studio_canvas()
    
    badges = {
        "encoder": create_telemetry_badge("BRASS ROTARY ENCODER", "STEPLESS DAMPED ROTATION", ACCENT_CORAL, "CNC BEAD-BLASTED // METEORITE"),
        "switches": create_telemetry_badge("TTC LINEAR 45G", "FACTORY LUBED POM STEMS", ACCENT_LIME, "3.8MM TOTAL KEY TRAVEL"),
        "chassis": create_telemetry_badge("CNC 6063 ALUMINUM", "ACOUSTIC ISOLATION GASKET", (120, 120, 120), "1,850G SOLID BRASS WEIGHT")
    }
    card_specs = create_exploded_specs_sheet()
    card_outro = create_outro_brand_card()
    signature_outro = create_signature_outro_layer()

    # 2. Load animation sequence frames
    hero_frames, scrub_frames = load_all_frames()

    # 3. Preview Key Inspection Frames
    key_indices = [
        (120, "01_intro_assembly.png"),
        (390, "02_orbit_telemetry.png"),
        (720, "03_exploded_layers.png"),
        (1080, "04_studio_keywave.png"),
        (1320, "05_outro_brand_lockup.png")
    ]
    
    print("\n[*] Rendering key milestone frames for visual validation...")
    for f_idx, fname in key_indices:
        out_path = os.path.join(FRAMES_OUT_DIR, fname)
        frame = render_frame_pipeline(
            f_idx, bg_base, hero_frames, scrub_frames,
            ui_light, ui_specs, ui_dark, badges, card_specs, card_outro, signature_outro
        )
        safe_imwrite(out_path, frame)
        print(f"    [+] Saved frame {f_idx:4d} ({f_idx / FPS:4.1f}s) -> {fname}")

    if args.preview_frames:
        print("\n[OK] Preview frames generated successfully.")
        return

    # 4. Stream Render directly into FFmpeg Pipe
    print("\n[*] Initializing FFmpeg pipe for 60 FPS H.264 encode...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "bgr24",
        "-r", f"{int(FPS)}",
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "slow",
        "-crf", "19",
        "-movflags", "+faststart",
        OUTPUT_REVIEW
    ]

    pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    start_frame = 0
    end_frame = TOTAL_FRAMES
    if args.test_range:
        start_frame, end_frame = args.test_range

    t_start = time.time()
    rendered_count = 0
    
    print(f"[*] Rendering frames {start_frame} through {end_frame}...")
    try:
        for f_idx in range(start_frame, end_frame):
            frame = render_frame_pipeline(
                f_idx, bg_base, hero_frames, scrub_frames,
                ui_light, ui_specs, ui_dark, badges, card_specs, card_outro, signature_outro
            )
            pipe.stdin.write(frame.tobytes())
            rendered_count += 1
            
            if rendered_count % 60 == 0 or rendered_count == (end_frame - start_frame):
                elapsed = time.time() - t_start
                cur_fps = rendered_count / max(0.001, elapsed)
                pct = (rendered_count / (end_frame - start_frame)) * 100.0
                sys.stdout.write(f"\r    Progress: {rendered_count:4d}/{end_frame - start_frame} frames ({pct:5.1f}%) | Speed: {cur_fps:4.1f} FPS | Elapsed: {elapsed:4.1f}s")
                sys.stdout.flush()
                
    except Exception as e:
        print(f"\n[!] Error during render: {e}")
        pipe.kill()
        raise
    finally:
        pipe.stdin.close()
        stderr_output = pipe.stderr.read()
        pipe.wait()

    total_time = time.time() - t_start
    print(f"\n\n[OK] FFmpeg render finished in {total_time:.2f}s (Average {rendered_count / total_time:.1f} FPS).")

    # 5. Copy to Kwork Portfolio destination
    if os.path.exists(OUTPUT_REVIEW):
        file_size_mb = os.path.getsize(OUTPUT_REVIEW) / (1024 * 1024)
        print(f"[*] Review showcase size: {file_size_mb:.2f} MB -> {OUTPUT_REVIEW}")
        
        # Copy to work_1_hero_3d/video.mp4
        import shutil
        shutil.copy2(OUTPUT_REVIEW, OUTPUT_KWORK)
        print(f"[*] Copied to Kwork portfolio: {file_size_mb:.2f} MB -> {OUTPUT_KWORK}")
        
        # Validate with ffprobe
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,duration",
            "-of", "default=noprint_wrappers=1",
            OUTPUT_KWORK
        ]
        res = subprocess.run(probe_cmd, capture_output=True, text=True)
        print("\n[*] FFprobe stream validation:")
        print(res.stdout.strip())
        print(f"[*] File size check: {file_size_mb:.2f} MB (strictly below 40-50 MB limit: {file_size_mb < 40.0})")

if __name__ == "__main__":
    main()
