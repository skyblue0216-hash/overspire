#!/usr/bin/env python3
"""
Generate 64x64 Master Color Palette for Overspire Low-Poly Visuals
"""
import struct
import zlib
import os

def create_png(width, height, rgb_colors, filename):
    # rgb_colors is a list of (r, g, b) tuples or a grid
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0) # filter byte 0 (None)
        for x in range(width):
            color = rgb_colors[y * width + x]
            raw_data.extend(color)
            raw_data.append(255) # alpha
            
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw_data)))
    png += chunk(b'IEND', b'')

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(png)
    print(f"Created {filename} ({width}x{height})")

# Palette colors defined in visual-style-guide.md
PALETTE = [
    # Hero colors
    (194, 198, 207), # 0: Silver Hair
    (150, 155, 166), # 1: Hair Shadow
    (255, 210, 178), # 2: Skin
    (230, 180, 150), # 3: Skin Shadow
    (0, 208, 224),   # 4: Cyan Eyes
    (217, 207, 184), # 5: Beige Shirt
    (185, 175, 150), # 6: Shirt Shadow
    (91, 59, 40),    # 7: Dark Belt
    (229, 168, 35),  # 8: Brass Buckle
    (72, 75, 49),    # 9: Olive Pants
    (52, 55, 35),    # 10: Pants Shadow
    (102, 65, 38),   # 11: Brown Boots
    (75, 45, 25),    # 12: Boots Shadow
    # Gear
    (210, 215, 225), # 13: Steel Blade
    (140, 95, 60),   # 14: Wood Shield
    # Dungeon & Slime
    (90, 190, 70),   # 15: Slime Lime Green
    (50, 140, 40),   # 16: Slime Shadow
    (240, 190, 40),  # 17: Key Gold
    (120, 115, 110), # 18: Dungeon Stone Floor
    (70, 65, 75),    # 19: Dungeon Stone Wall
]

# Create a 64x64 grid of colors
width, height = 64, 64
pixels = []
for y in range(height):
    for x in range(width):
        idx = ((y // 8) * 8 + (x // 8)) % len(PALETTE)
        pixels.append(PALETTE[idx])

create_png(width, height, pixels, "assets/textures/palette_master.png")
