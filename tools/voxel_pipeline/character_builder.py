"""
Retro JRPG Chibi Adventurer Character Builder (2.5-Head Proportions)
Generates the complete voxel data for the silver-haired adventurer hero.
"""
from .voxel_grid import VoxelGrid, Part
from .palette import Palette

def build_hero_grid(palette: Palette, include_props: bool = True) -> VoxelGrid:
    grid = VoxelGrid(size_x=24, size_y=32, size_z=22)

    c_skin_base     = palette.get("SKIN_BASE")
    c_skin_shadow   = palette.get("SKIN_SHADOW")
    c_skin_hi       = palette.get("SKIN_HIGHLIGHT")
    c_blush         = palette.get("BLUSH")

    c_eye_cyan_br   = palette.get("EYE_CYAN_BRIGHT")
    c_eye_cyan_dp   = palette.get("EYE_CYAN_DEEP")
    c_eye_white     = palette.get("EYE_WHITE")
    c_eye_pupil     = palette.get("EYE_PUPIL_DARK")

    c_hair_hi       = palette.get("HAIR_HIGHLIGHT")
    c_hair_base     = palette.get("HAIR_BASE")
    c_hair_mid      = palette.get("HAIR_MID_SHADOW")
    c_hair_deep     = palette.get("HAIR_DEEP_SHADOW")

    c_shirt_base    = palette.get("SHIRT_BASE")
    c_shirt_collar  = palette.get("SHIRT_COLLAR")
    c_shirt_shadow  = palette.get("SHIRT_SHADOW")
    c_shirt_dark    = palette.get("SHIRT_DARK")

    c_belt_leather  = palette.get("BELT_LEATHER")
    c_belt_dark     = palette.get("BELT_DARK")
    c_buckle_gold   = palette.get("BUCKLE_GOLD")
    c_buckle_shadow = palette.get("BUCKLE_SHADOW")

    c_pants_base    = palette.get("PANTS_BASE")
    c_pants_shadow  = palette.get("PANTS_SHADOW")
    c_boots_leather = palette.get("BOOTS_LEATHER")
    c_boots_hi      = palette.get("BOOTS_HIGHLIGHT")
    c_boots_sole    = palette.get("BOOTS_SOLE")

    c_steel_blade   = palette.get("STEEL_BLADE")
    c_steel_shine   = palette.get("STEEL_SHINE")
    c_gold_hilt     = palette.get("GOLD_HILT")
    c_leather_grip  = palette.get("LEATHER_GRIP")
    c_shield_wood   = palette.get("SHIELD_WOOD")
    c_shield_rim    = palette.get("SHIELD_IRON_RIM")
    c_shield_emblem = palette.get("SHIELD_EMBLEM")

    # =========================================================================
    # 1. LEGS & BOOTS (Y = 0 .. 7)
    # =========================================================================
    # --- Left Leg (X: 8..10) ---
    # Outsole (Y=0)
    grid.fill_box(8, 0, 8, 10, 0, 12, c_boots_sole, Part.LEFT_LEG)
    # Boot Leather (Y=1..3)
    grid.fill_box(8, 1, 8, 10, 3, 12, c_boots_leather, Part.LEFT_LEG)
    grid.fill_box(8, 3, 11, 10, 3, 12, c_boots_hi, Part.LEFT_LEG) # Toe cap highlight
    # Pants (Y=4..6)
    grid.fill_box(8, 4, 8, 10, 6, 11, c_pants_base, Part.LEFT_LEG)
    grid.fill_box(8, 4, 8, 10, 6, 8, c_pants_shadow, Part.LEFT_LEG) # Back crease

    # --- Right Leg (X: 13..15) ---
    # Outsole (Y=0)
    grid.fill_box(13, 0, 8, 15, 0, 12, c_boots_sole, Part.RIGHT_LEG)
    # Boot Leather (Y=1..3)
    grid.fill_box(13, 1, 8, 15, 3, 12, c_boots_leather, Part.RIGHT_LEG)
    grid.fill_box(13, 3, 11, 15, 3, 12, c_boots_hi, Part.RIGHT_LEG)
    # Pants (Y=4..6)
    grid.fill_box(13, 4, 8, 15, 6, 11, c_pants_base, Part.RIGHT_LEG)
    grid.fill_box(13, 4, 8, 15, 6, 8, c_pants_shadow, Part.RIGHT_LEG)

    # =========================================================================
    # 2. TORSO & BELT (Y = 7 .. 16)
    # =========================================================================
    # Pelvis join (Y=7)
    grid.fill_box(7, 7, 8, 16, 7, 11, c_pants_base, Part.TORSO)

    # Leather Belt (Y=8..9)
    grid.fill_box(7, 8, 8, 16, 9, 11, c_belt_leather, Part.TORSO)
    grid.fill_box(7, 8, 7, 16, 9, 7, c_belt_dark, Part.TORSO) # back belt shadow
    # Golden Brass Buckle (Front center, protruding at Z=12)
    grid.fill_box(10, 8, 12, 13, 9, 12, c_buckle_gold, Part.TORSO)
    grid.set_voxel(11, 8, 12, c_buckle_shadow, Part.TORSO)
    grid.set_voxel(12, 8, 12, c_buckle_shadow, Part.TORSO)

    # Rolled-Sleeve Adventurer Shirt (Y=10..16)
    grid.fill_box(7, 10, 8, 16, 16, 11, c_shirt_base, Part.TORSO)
    grid.fill_box(7, 10, 7, 16, 16, 7, c_shirt_shadow, Part.TORSO) # back shirt shadow

    # V-Neck Collar & Chest Skin (Front at Z=12)
    grid.fill_box(9, 15, 12, 14, 16, 12, c_shirt_collar, Part.TORSO) # Folded collar
    grid.fill_box(11, 14, 12, 12, 15, 12, c_skin_base, Part.TORSO)   # Skin V-notch

    # =========================================================================
    # 3. ARMS (Y = 9 .. 16)
    # =========================================================================
    # --- Left Arm (X: 4..6) ---
    # Rolled sleeve puff (Y=14..16)
    grid.fill_box(4, 14, 8, 6, 16, 11, c_shirt_base, Part.LEFT_ARM)
    grid.fill_box(4, 14, 8, 6, 14, 11, c_shirt_collar, Part.LEFT_ARM) # rolled cuff
    # Forearm & Hand (Y=9..13)
    grid.fill_box(4, 9, 8, 6, 13, 10, c_skin_base, Part.LEFT_ARM)
    grid.fill_box(4, 9, 8, 6, 11, 8, c_skin_shadow, Part.LEFT_ARM)

    # --- Right Arm (X: 17..19) ---
    # Rolled sleeve puff (Y=14..16)
    grid.fill_box(17, 14, 8, 19, 16, 11, c_shirt_base, Part.RIGHT_ARM)
    grid.fill_box(17, 14, 8, 19, 14, 11, c_shirt_collar, Part.RIGHT_ARM) # rolled cuff
    # Forearm & Hand (Y=9..13)
    grid.fill_box(17, 9, 8, 19, 13, 10, c_skin_base, Part.RIGHT_ARM)
    grid.fill_box(17, 9, 8, 19, 11, 8, c_skin_shadow, Part.RIGHT_ARM)

    # =========================================================================
    # 4. CHIBI HEAD & MESSY SILVER HAIR (Y = 17 .. 28)
    # =========================================================================
    # Neck (Y=17)
    grid.fill_box(10, 17, 9, 13, 17, 10, c_skin_shadow, Part.HEAD)

    # Peach Skin Face Cube (Y=18..24, X=7..16, Z=8..12)
    grid.fill_box(7, 18, 8, 16, 24, 12, c_skin_base, Part.HEAD)

    # Cute Cheek Blush (Z=13)
    grid.set_voxel(8, 19, 13, c_blush, Part.HEAD)
    grid.set_voxel(15, 19, 13, c_blush, Part.HEAD)

    # Big Expressive Cyan Eyes (Front face at Z=13, Y=20..22)
    # Left Eye (X: 8..9)
    grid.set_voxel(8, 20, 13, c_eye_cyan_dp, Part.HEAD)
    grid.set_voxel(9, 20, 13, c_eye_cyan_dp, Part.HEAD)
    grid.set_voxel(8, 21, 13, c_eye_cyan_br, Part.HEAD)
    grid.set_voxel(9, 21, 13, c_eye_white,   Part.HEAD) # Cute Glint!
    grid.set_voxel(8, 22, 13, c_hair_deep,   Part.HEAD) # Eyelash / brow
    grid.set_voxel(9, 22, 13, c_hair_deep,   Part.HEAD)

    # Right Eye (X: 14..15)
    grid.set_voxel(14, 20, 13, c_eye_cyan_dp, Part.HEAD)
    grid.set_voxel(15, 20, 13, c_eye_cyan_dp, Part.HEAD)
    grid.set_voxel(14, 21, 13, c_eye_cyan_br, Part.HEAD)
    grid.set_voxel(15, 21, 13, c_eye_white,   Part.HEAD) # Cute Glint!
    grid.set_voxel(14, 22, 13, c_hair_deep,   Part.HEAD) # Eyelash / brow
    grid.set_voxel(15, 22, 13, c_hair_deep,   Part.HEAD)

    # --- Messy Layered Silver Hair ---
    # Crown Volume (Y=25..27, X=6..17, Z=7..13)
    grid.fill_box(6, 25, 7, 17, 27, 13, c_hair_base, Part.HEAD)

    # Top Tufts & Highlights (Y=28)
    grid.fill_box(9, 28, 8, 14, 28, 11, c_hair_hi, Part.HEAD)
    grid.fill_box(11, 29, 9, 13, 29, 10, c_hair_hi, Part.HEAD) # Cowlick spiky tuft!

    # Front Bangs Clumps (Layered over forehead at Z=13..14)
    grid.fill_box(7, 24, 13, 16, 25, 13, c_hair_base, Part.HEAD)
    # Bangs tufts reaching down
    grid.fill_box(8, 23, 14, 9, 24, 14, c_hair_hi, Part.HEAD)
    grid.fill_box(11, 23, 14, 13, 24, 14, c_hair_base, Part.HEAD)
    grid.fill_box(14, 23, 14, 15, 24, 14, c_hair_mid, Part.HEAD)
    # Bangs spike tip
    grid.set_voxel(12, 22, 14, c_hair_hi, Part.HEAD)

    # Side Hair Locks (Framing face, X=6 and X=17)
    grid.fill_box(6, 19, 8, 6, 24, 12, c_hair_base, Part.HEAD)
    grid.fill_box(17, 19, 8, 17, 24, 12, c_hair_base, Part.HEAD)
    grid.fill_box(6, 18, 10, 6, 20, 11, c_hair_mid, Part.HEAD) # sideburn tip
    grid.fill_box(17, 18, 10, 17, 20, 11, c_hair_mid, Part.HEAD)

    # Back Hair (Flowing down behind neck, Z=6..7)
    grid.fill_box(6, 18, 6, 17, 25, 7, c_hair_deep, Part.HEAD)
    grid.fill_box(7, 16, 6, 16, 17, 6, c_hair_deep, Part.HEAD) # nape touching collar

    # =========================================================================
    # 5. RETRO JRPG PROPS (SWORD & SHIELD)
    # =========================================================================
    if include_props:
        # --- Steel Short Sword (Attached to Right Arm Hand) ---
        # Pommel & Grip (Y=7..9, X=18, Z=12)
        grid.set_voxel(18, 7, 12, c_gold_hilt, Part.SWORD)
        grid.fill_box(18, 8, 12, 18, 9, 12, c_leather_grip, Part.SWORD)
        # Crossguard (Y=10)
        grid.fill_box(17, 10, 11, 19, 10, 13, c_gold_hilt, Part.SWORD)
        # Blade (Y=11..19)
        grid.fill_box(18, 11, 12, 18, 18, 12, c_steel_blade, Part.SWORD)
        grid.fill_box(18, 11, 13, 18, 17, 13, c_steel_shine, Part.SWORD) # sharp edge
        grid.set_voxel(18, 19, 12, c_steel_shine, Part.SWORD) # pointed tip

        # --- Round Wooden Buckler Shield (Attached to Left Arm) ---
        # Outer Iron Rim (X=3, Y=10..16, Z=7..13)
        grid.fill_box(3, 11, 7, 3, 15, 13, c_shield_rim, Part.SHIELD)
        grid.fill_box(3, 10, 8, 3, 16, 12, c_shield_rim, Part.SHIELD)
        # Wooden Inlay
        grid.fill_box(3, 11, 8, 3, 15, 12, c_shield_wood, Part.SHIELD)
        # Center Cyan Boss / Emblem
        grid.fill_box(2, 12, 9, 2, 14, 11, c_shield_emblem, Part.SHIELD)
        grid.set_voxel(2, 13, 10, c_eye_white, Part.SHIELD) # center metal rivet

    return grid
