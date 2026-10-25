#!/usr/bin/env python3
"""
Generate high-fidelity North (Back) and East (Side) directional sprites for Overspire Hero.
Extracts exact palette from south.png and crafts pixel-level matching sprites.
"""

from PIL import Image

def generate_sprites():
    src_path = "img/south.png"
    im_south = Image.open(src_path).convert("RGBA")
    w, h = im_south.size
    
    # Exact colors from south.png
    BLACK = (0, 1, 5, 255)
    DARK_OUTLINE = (5, 5, 10, 255)
    
    HAIR_HL = (216, 209, 197, 255)
    HAIR_LGT = (148, 145, 140, 255)
    HAIR_MID = (118, 113, 113, 255)
    HAIR_SHD = (89, 79, 89, 255)
    HAIR_DRK = (45, 31, 38, 255)
    
    SKIN_HL = (250, 193, 158, 255)
    SKIN_BASE = (240, 161, 126, 255)
    SKIN_SHD = (210, 113, 82, 255)
    SKIN_DRK = (195, 102, 74, 255)
    
    EYE_CYAN = (52, 171, 184, 255)
    EYE_WHITE = (252, 255, 254, 255)
    
    SHIRT_HL = (234, 216, 180, 255)
    SHIRT_LGT = (208, 189, 149, 255)
    SHIRT_MID = (168, 142, 112, 255)
    SHIRT_SHD = (133, 108, 89, 255)
    SHIRT_DRK = (95, 74, 73, 255)
    
    BELT_LGT = (116, 88, 74, 255)
    BELT_MID = (91, 69, 53, 255)
    BELT_DRK = (45, 31, 38, 255)
    
    PANTS_HL = (56, 42, 36, 255)
    PANTS_MID = (40, 30, 31, 255)
    PANTS_DRK = (18, 15, 19, 255)
    PANTS_BLK = (2, 2, 9, 255)
    
    BOOT_HL = (165, 98, 58, 255)
    BOOT_LGT = (129, 65, 38, 255)
    BOOT_MID = (96, 47, 35, 255)
    BOOT_DRK = (73, 31, 27, 255)
    BOOT_SOLE = (47, 22, 19, 255)

    # ========================================================
    # 1. NORTH (BACK VIEW)
    # ========================================================
    im_north = im_south.copy()
    pix_n = im_north.load()
    
    # Replace face / eyes area with full back of hair & neck
    for y in range(13, 20):
        for x in range(16, 32):
            if pix_n[x, y][3] > 0:
                dist = abs(x - 24)
                if y == 13:
                    if dist <= 2: pix_n[x, y] = HAIR_HL
                    elif dist <= 4: pix_n[x, y] = HAIR_LGT
                    else: pix_n[x, y] = HAIR_MID
                elif y == 14:
                    if dist <= 1: pix_n[x, y] = HAIR_HL
                    elif dist <= 3: pix_n[x, y] = HAIR_LGT
                    elif dist <= 5: pix_n[x, y] = HAIR_MID
                    else: pix_n[x, y] = HAIR_SHD
                elif y == 15:
                    if dist <= 2: pix_n[x, y] = HAIR_LGT
                    elif dist <= 4: pix_n[x, y] = HAIR_MID
                    else: pix_n[x, y] = HAIR_SHD
                elif y == 16:
                    if dist <= 2: pix_n[x, y] = HAIR_MID
                    elif dist <= 4: pix_n[x, y] = HAIR_SHD
                    else: pix_n[x, y] = HAIR_DRK
                elif y == 17:
                    if dist <= 3: pix_n[x, y] = HAIR_SHD
                    else: pix_n[x, y] = HAIR_DRK
                elif y == 18:
                    if dist <= 2: pix_n[x, y] = HAIR_DRK
                    else: pix_n[x, y] = BLACK
                elif y == 19:
                    if 22 <= x <= 25: pix_n[x, y] = HAIR_DRK
                    else: pix_n[x, y] = BLACK

    # Back Collar (y: 20)
    for x in range(21, 27):
        pix_n[x, 20] = SHIRT_SHD if x in (21, 26) else SHIRT_MID

    # Back of Shirt (y: 21..29) - replace front open chest with solid beige
    for y in range(21, 30):
        for x in range(21, 27):
            if pix_n[x, y][3] > 0:
                if x == 24: # Spine fold
                    pix_n[x, y] = SHIRT_SHD if (y % 2 == 1) else SHIRT_MID
                elif x in (22, 23, 25):
                    pix_n[x, y] = SHIRT_LGT if (y in (22, 23, 24)) else SHIRT_MID
                else:
                    pix_n[x, y] = SHIRT_MID

    # Belt back (y: 30..34) - remove buckle
    for y in range(30, 35):
        for x in range(20, 28):
            if pix_n[x, y][3] > 0:
                pix_n[x, y] = BELT_DRK if y in (30, 34) else BELT_MID

    # ========================================================
    # 2. EAST (SIDE VIEW - FACING RIGHT)
    # ========================================================
    im_east = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    pix_e = im_east.load()
    
    # Crown & Hair Top (y: 1..5)
    for y in range(1, 6):
        for x in range(17, 30):
            if y == 1 and 20 <= x <= 25: pix_e[x, y] = BLACK
            elif y == 2 and 18 <= x <= 27:
                pix_e[x, y] = BLACK if x in (18, 27) else (HAIR_LGT if 21 <= x <= 24 else HAIR_MID)
            elif y == 3 and 17 <= x <= 28:
                if x in (17, 28): pix_e[x, y] = BLACK
                elif 21 <= x <= 25: pix_e[x, y] = HAIR_HL
                elif 19 <= x <= 26: pix_e[x, y] = HAIR_LGT
                else: pix_e[x, y] = HAIR_MID
            elif y >= 4 and 16 <= x <= 29:
                if x in (16, 29): pix_e[x, y] = BLACK
                elif 21 <= x <= 25: pix_e[x, y] = HAIR_HL
                elif 18 <= x <= 27: pix_e[x, y] = HAIR_LGT
                else: pix_e[x, y] = HAIR_MID

    # Mid Hair & Bangs (y: 6..12)
    for y in range(6, 13):
        pix_e[16, y] = BLACK # back contour
        # Back hair volume
        for x in range(17, 22):
            pix_e[x, y] = HAIR_MID if y < 9 else HAIR_SHD
        # Crown highlight
        for x in range(22, 27):
            if y in (6, 7) and 23 <= x <= 25: pix_e[x, y] = HAIR_HL
            else: pix_e[x, y] = HAIR_LGT
        # Bangs flowing forward
        pix_e[27, y] = HAIR_LGT
        pix_e[28, y] = HAIR_MID
        if y in (7, 8, 9, 10):
            pix_e[29, y] = HAIR_MID
            pix_e[30, y] = BLACK
        else:
            pix_e[29, y] = BLACK

    # Face Profile & Cyan Eye (y: 13..18)
    for y in range(13, 19):
        # Back of head hair
        pix_e[17, y] = BLACK
        pix_e[18, y] = HAIR_SHD
        pix_e[19, y] = HAIR_DRK
        pix_e[20, y] = HAIR_DRK if y >= 16 else HAIR_SHD
        
        # Skin base
        for x in range(21, 29):
            pix_e[x, y] = SKIN_BASE

        # Eye & Facial features
        if y == 13:
            pix_e[21, y] = HAIR_SHD
            for x in range(22, 28): pix_e[x, y] = SKIN_HL
            pix_e[28, y] = SKIN_BASE; pix_e[29, y] = BLACK
        elif y == 14:
            for x in range(22, 28): pix_e[x, y] = SKIN_HL
            pix_e[28, y] = SKIN_BASE; pix_e[29, y] = BLACK
        elif y == 15:
            # Cute big cyan eye
            pix_e[23, y] = SKIN_HL
            pix_e[24, y] = EYE_CYAN
            pix_e[25, y] = EYE_WHITE
            pix_e[26, y] = EYE_CYAN
            pix_e[27, y] = SKIN_HL
            pix_e[28, y] = SKIN_BASE
            pix_e[29, y] = BLACK # nose tip
        elif y == 16:
            pix_e[24, y] = EYE_CYAN
            pix_e[25, y] = EYE_CYAN
            pix_e[26, y] = SKIN_HL
            pix_e[27, y] = SKIN_BASE
            pix_e[28, y] = BLACK
        elif y == 17:
            for x in range(22, 26): pix_e[x, y] = SKIN_HL
            pix_e[26, y] = SKIN_BASE
            pix_e[27, y] = BLACK
        elif y == 18:
            for x in range(22, 25): pix_e[x, y] = SKIN_BASE
            pix_e[25, y] = BLACK # cute chin

    # Neck (y: 19..20)
    for x in range(20, 25):
        pix_e[x, 19] = BLACK if x in (20, 24) else SKIN_SHD
    for x in range(19, 26):
        pix_e[x, 20] = BLACK if x in (19, 25) else SHIRT_SHD

    # Torso & Arm (y: 21..29)
    for y in range(21, 30):
        # Back line
        pix_e[18, y] = BLACK
        pix_e[19, y] = SHIRT_SHD
        pix_e[20, y] = SHIRT_MID
        
        # Center: Rolled sleeve arm
        if y <= 24:
            pix_e[21, y] = SHIRT_LGT
            pix_e[22, y] = SHIRT_HL
            pix_e[23, y] = SHIRT_LGT
        elif y == 25:
            pix_e[21, y] = SHIRT_MID
            pix_e[22, y] = SHIRT_SHD # cuff shadow
            pix_e[23, y] = SHIRT_MID
        else: # Forearm & hand
            pix_e[21, y] = SKIN_HL
            pix_e[22, y] = SKIN_BASE
            pix_e[23, y] = SKIN_SHD
        
        # Front chest
        pix_e[24, y] = SHIRT_HL
        pix_e[25, y] = SHIRT_LGT
        pix_e[26, y] = SHIRT_MID
        pix_e[27, y] = BLACK

    # Belt (y: 30..34)
    for y in range(30, 35):
        pix_e[18, y] = BLACK
        pix_e[19, y] = BELT_DRK
        pix_e[20, y] = BELT_MID
        # Side pouch
        for x in range(21, 24):
            pix_e[x, y] = BELT_LGT if y in (31, 32) else BELT_MID
        pix_e[24, y] = BELT_MID
        pix_e[25, y] = BELT_MID
        pix_e[26, y] = BELT_DRK
        pix_e[27, y] = BLACK

    # Pants (y: 35..39)
    for y in range(35, 40):
        pix_e[19, y] = BLACK
        for x in range(20, 26):
            pix_e[x, y] = PANTS_HL if x in (22, 23) else PANTS_MID
        pix_e[26, y] = BLACK

    # Boots (y: 40..45)
    for y in range(40, 46):
        if y in (40, 41): # Ankle
            pix_e[19, y] = BLACK
            for x in range(20, 26): pix_e[x, y] = BOOT_LGT if x in (22, 23) else BOOT_MID
            pix_e[26, y] = BLACK
        elif y in (42, 43): # Foot profile (toe pointing right)
            pix_e[18, y] = BLACK # heel back
            pix_e[19, y] = BOOT_DRK
            for x in range(20, 27): pix_e[x, y] = BOOT_LGT if x in (23, 24) else BOOT_MID
            pix_e[27, y] = BOOT_MID; pix_e[28, y] = BLACK # toe
        elif y in (44, 45): # Sole
            pix_e[18, y] = BLACK
            for x in range(19, 29):
                pix_e[x, y] = BOOT_SOLE if y == 45 else BOOT_DRK
            pix_e[29, y] = BLACK

    # Save to img/ and web_build/
    im_north.save("img/north.png")
    im_north.save("web_build/north.png")
    
    im_east.save("img/east.png")
    im_east.save("web_build/east.png")
    
    print("Successfully generated img/north.png and img/east.png!")

if __name__ == "__main__":
    generate_sprites()
