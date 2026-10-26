"""
Retro JRPG Voxel Color Palette Specification
"""

class Palette:
    def __init__(self):
        # 256 RGBA slots (MagicaVoxel format: indices 1..255 are active, 0 is unused)
        # Each entry is (R, G, B, A) with 0..255
        self.colors = [(0, 0, 0, 0)] * 256
        self.named_indices = {}
        self._next_idx = 1
        
        self._init_default_colors()

    def _init_default_colors(self):
        # 1. Skin Tones
        self.register("SKIN_BASE",      (250, 193, 158, 255)) # #FAC19E
        self.register("SKIN_SHADOW",    (225, 165, 132, 255)) # #E1A584
        self.register("SKIN_HIGHLIGHT", (255, 212, 185, 255)) # #FFD4B9
        self.register("BLUSH",          (242, 148, 142, 255)) # #F2948E
        
        # 2. Cyan Eyes
        self.register("EYE_CYAN_BRIGHT",(0,   216, 232, 255)) # #00D8E8
        self.register("EYE_CYAN_DEEP",  (0,   154, 172, 255)) # #009AAC
        self.register("EYE_WHITE",      (255, 255, 255, 255)) # #FFFFFF
        self.register("EYE_PUPIL_DARK", (10,  40,  55,  255)) # #0A2837
        
        # 3. Messy Silver / Ash-Gray Hair
        self.register("HAIR_HIGHLIGHT", (228, 224, 228, 255)) # #E4E0E4
        self.register("HAIR_BASE",      (196, 192, 196, 255)) # #C4C0C4
        self.register("HAIR_MID_SHADOW",(156, 152, 156, 255)) # #9C989C
        self.register("HAIR_DEEP_SHADOW",(118, 113, 113, 255)) # #767171
        
        # 4. Adventurer Beige/Sand Rolled-sleeve Shirt
        self.register("SHIRT_BASE",     (208, 189, 149, 255)) # #D0BD95
        self.register("SHIRT_COLLAR",   (228, 214, 182, 255)) # #E4D6B6
        self.register("SHIRT_SHADOW",   (168, 152, 116, 255)) # #A89874
        self.register("SHIRT_DARK",     (135, 120, 90,  255)) # #87785A
        
        # 5. Leather Belt & Brass Gold Buckle
        self.register("BELT_LEATHER",   (91,  69,  53,  255)) # #5B4535
        self.register("BELT_DARK",      (60,  44,  32,  255)) # #3C2C20
        self.register("BUCKLE_GOLD",    (245, 197, 66,  255)) # #F5C542
        self.register("BUCKLE_SHADOW",  (196, 155, 37,  255)) # #C49B25
        
        # 6. Trousers & Leather Boots
        self.register("PANTS_BASE",     (34,  30,  32,  255)) # #221E20
        self.register("PANTS_SHADOW",   (24,  20,  22,  255)) # #181416
        self.register("BOOTS_LEATHER",  (129, 65,  38,  255)) # #814126
        self.register("BOOTS_HIGHLIGHT",(160, 85,  50,  255)) # #A05532
        self.register("BOOTS_SOLE",     (47,  22,  19,  255)) # #2F1613
        
        # 7. Sword & Shield
        self.register("STEEL_BLADE",    (216, 223, 232, 255)) # #D8DFE8
        self.register("STEEL_SHINE",    (245, 248, 252, 255)) # #F5F8FC
        self.register("STEEL_SHADOW",   (140, 155, 172, 255)) # #8C9BAC
        self.register("GOLD_HILT",      (210, 160, 48,  255)) # #D2A030
        self.register("LEATHER_GRIP",   (75,  52,  38,  255)) # #4B3426
        self.register("SHIELD_WOOD",    (106, 74,  50,  255)) # #6A4A32
        self.register("SHIELD_IRON_RIM",(120, 130, 142, 255)) # #78828E
        self.register("SHIELD_EMBLEM",  (0,   180, 205, 255)) # #00B4CD

    def register(self, name: str, rgba: tuple) -> int:
        idx = self._next_idx
        if idx >= 256:
            raise ValueError("Palette limit of 255 active colors exceeded")
        self.colors[idx] = rgba
        self.named_indices[name] = idx
        self._next_idx += 1
        return idx

    def get(self, name: str) -> int:
        if name not in self.named_indices:
            raise KeyError(f"Color '{name}' not found in palette")
        return self.named_indices[name]

    def get_rgba(self, idx: int) -> tuple:
        return self.colors[idx]

    def get_rgb_float(self, idx: int) -> tuple:
        r, g, b, _ = self.colors[idx]
        return (r / 255.0, g / 255.0, b / 255.0)

    def get_rgba_bytes(self) -> bytes:
        # Standard MagicaVoxel RGBA chunk: 256 * 4 bytes
        # Note: In MagicaVoxel, color index i (1..255) maps to palette entry (i - 1).
        # Entry 255 is palette[254], and palette[255] is slot 0.
        out = bytearray(1024)
        for i in range(1, 256):
            r, g, b, a = self.colors[i]
            offset = (i - 1) * 4
            out[offset] = r
            out[offset + 1] = g
            out[offset + 2] = b
            out[offset + 3] = a
        # 256th slot
        r, g, b, a = self.colors[0]
        out[255 * 4 : 256 * 4] = bytes([r, g, b, a])
        return bytes(out)
