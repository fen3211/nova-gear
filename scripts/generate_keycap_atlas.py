"""
Generate high-resolution texture atlas and coordinate map for NovaKeys K75 keycaps.
Authentic Cherry-profile layout and typography:
- Alphas (QWERTY, ZXCVBNM)
- Modifiers (ESC, TAB, CAPS, SHIFT, CTRL, OPT, CMD, RETURN, DELETE, PGUP, PGDN, HOME, END)
- Numerals and symbols
- Color themes: Cream Beige, Slate Graphite, Acid Lime Accent (#C7FF3D)
High-contrast bold grotesque lettering positioned at authentic Cherry top-left/center.
"""
import os
import json
from PIL import Image, ImageDraw, ImageFont

ATLAS_SIZE = 4096
COLS = 16
ROWS = 8
CELL_W = ATLAS_SIZE // COLS  # 256 px
CELL_H = ATLAS_SIZE // ROWS  # 512 px

THEMES = {
    'cream': {
        'bg': (236, 232, 222, 255),      # Warm cream beige #ECE8DE
        'text': (24, 26, 30, 255)         # Deep charcoal black
    },
    'slate': {
        'bg': (32, 34, 38, 255),          # Dark graphite #202226
        'text': (250, 250, 252, 255)      # Pure crisp white
    },
    'accent': {
        'bg': (199, 255, 61, 255),        # Electric Acid Lime #C7FF3D
        'text': (16, 18, 20, 255)         # Jet black
    }
}

KEY_DEFS = [
    # Row 0: Function & Top row
    ("ESC", "ESC", "accent"),
    ("F1", "F1", "slate"),
    ("F2", "F2", "slate"),
    ("F3", "F3", "slate"),
    ("F4", "F4", "slate"),
    ("F5", "F5", "slate"),
    ("F6", "F6", "slate"),
    ("F7", "F7", "slate"),
    ("F8", "F8", "slate"),
    ("F9", "F9", "slate"),
    ("F10", "F10", "slate"),
    ("F11", "F11", "slate"),
    ("F12", "F12", "slate"),
    ("DEL", "DEL", "slate"),
    ("HOME", "HOME", "slate"),
    ("END", "END", "slate"),

    # Row 1: Numbers & Navigation
    ("TILDE", "~ `", "slate"),
    ("1", "1 !", "cream"),
    ("2", "2 @", "cream"),
    ("3", "3 #", "cream"),
    ("4", "4 $", "cream"),
    ("5", "5 %", "cream"),
    ("6", "6 ^", "cream"),
    ("7", "7 &", "cream"),
    ("8", "8 *", "cream"),
    ("9", "9 (", "cream"),
    ("0", "0 )", "cream"),
    ("MINUS", "- _", "cream"),
    ("PLUS", "= +", "cream"),
    ("BACKSPACE", "DELETE", "slate"),
    ("PGUP", "PGUP", "slate"),
    ("PGDN", "PGDN", "slate"),

    # Row 2: QWERTY
    ("TAB", "TAB", "slate"),
    ("Q", "Q", "cream"),
    ("W", "W", "cream"),
    ("E", "E", "cream"),
    ("R", "R", "cream"),
    ("T", "T", "cream"),
    ("Y", "Y", "cream"),
    ("U", "U", "cream"),
    ("I", "I", "cream"),
    ("O", "O", "cream"),
    ("P", "P", "cream"),
    ("LBRACKET", "{ [", "cream"),
    ("RBRACKET", "} ]", "cream"),
    ("BACKSLASH", "| \\", "cream"),
    ("INSERT", "INS", "slate"),
    ("MUTE", "MUTE", "slate"),

    # Row 3: Home row (ASDF)
    ("CAPS", "CAPS", "slate"),
    ("A", "A", "cream"),
    ("S", "S", "cream"),
    ("D", "D", "cream"),
    ("F", "F", "cream"),
    ("G", "G", "cream"),
    ("H", "H", "cream"),
    ("J", "J", "cream"),
    ("K", "K", "cream"),
    ("L", "L", "cream"),
    ("COLON", ": ;", "cream"),
    ("QUOTE", "\" '", "cream"),
    ("ENTER", "RETURN", "accent"),
    ("PRTSC", "PRT", "slate"),
    ("PAUSE", "PAUSE", "slate"),
    ("BLANK_SLATE", "", "slate"),

    # Row 4: ZXCVBNM row
    ("LSHIFT", "SHIFT", "slate"),
    ("Z", "Z", "cream"),
    ("X", "X", "cream"),
    ("C", "C", "cream"),
    ("V", "V", "cream"),
    ("B", "B", "cream"),
    ("N", "N", "cream"),
    ("M", "M", "cream"),
    ("COMMA", "< ,", "cream"),
    ("PERIOD", "> .", "cream"),
    ("SLASH", "? /", "cream"),
    ("RSHIFT", "SHIFT", "slate"),
    ("UP", "▲", "slate"),
    ("NOVA_LOGO", "NOVA", "accent"),
    ("BLANK_CREAM", "", "cream"),
    ("BLANK_ACCENT", "", "accent"),

    # Row 5: Bottom row
    ("LCTRL", "CTRL", "slate"),
    ("LOPT", "OPT", "slate"),
    ("LCMD", "CMD", "slate"),
    ("SPACEBAR", "NOVA", "cream"),
    ("RCMD", "CMD", "slate"),
    ("ROPT", "OPT", "slate"),
    ("FN", "FN", "slate"),
    ("LEFT", "◄", "slate"),
    ("DOWN", "▼", "slate"),
    ("RIGHT", "►", "slate"),
]

def main():
    atlas = Image.new("RGBA", (ATLAS_SIZE, ATLAS_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)

    font_path = "C:/Windows/Fonts/arialbd.ttf"
    font_large = ImageFont.truetype(font_path, 96)
    font_med = ImageFont.truetype(font_path, 76)
    font_small = ImageFont.truetype(font_path, 60)
    font_dual = ImageFont.truetype(font_path, 52)

    coords_map = {}

    for idx, item in enumerate(KEY_DEFS):
        if idx >= COLS * ROWS:
            break
        key_id, text, theme_key = item
        theme = THEMES[theme_key]

        col = idx % COLS
        row = idx // COLS

        x0 = col * CELL_W
        y0 = row * CELL_H
        x1 = x0 + CELL_W
        y1 = y0 + CELL_H

        # Fill background
        draw.rectangle([x0, y0, x1, y1], fill=theme['bg'])

        # Draw text legend centered on the key
        if text:
            if len(text) == 1:
                font = font_large
            elif len(text) <= 3:
                font = font_med
            elif " " in text:
                font = font_dual
            else:
                font = font_small

            lines = text.split(' ') if (' ' in text and not text.startswith('PG')) else [text]
            total_h = 0
            line_boxes = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                lw = bbox[2] - bbox[0]
                lh = bbox[3] - bbox[1]
                line_boxes.append((line, lw, lh))
                total_h += lh + 8
            total_h -= 8

            cur_y = y0 + (CELL_H - total_h) / 2
            for line, lw, lh in line_boxes:
                tx = x0 + (CELL_W - lw) / 2
                draw.text((tx, cur_y), line, font=font, fill=theme['text'])
                cur_y += lh + 8

        # In Blender: u = x / ATLAS_SIZE, v = 1.0 - (y / ATLAS_SIZE)
        u_min = x0 / ATLAS_SIZE
        u_max = x1 / ATLAS_SIZE
        v_min = 1.0 - (y1 / ATLAS_SIZE)
        v_max = 1.0 - (y0 / ATLAS_SIZE)

        coords_map[key_id] = {
            'col': col,
            'row': row,
            'text': text,
            'theme': theme_key,
            'u_min': u_min,
            'u_max': u_max,
            'v_min': v_min,
            'v_max': v_max
        }

    output_dir = "D:/Projects/ууу/assets/textures"
    os.makedirs(output_dir, exist_ok=True)
    atlas_path = os.path.join(output_dir, "keycap_atlas.png")
    json_path = os.path.join(output_dir, "keycap_atlas.json")

    atlas.save(atlas_path, optimize=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(coords_map, f, indent=2)

    print(f"Keycap Atlas updated: {atlas_path} ({ATLAS_SIZE}x{ATLAS_SIZE})")

if __name__ == "__main__":
    main()
