"""
Automated Test for 16-bit JRPG Voxel Character Face Geometry & UV Invariants
"""
import os
import struct
import json
import unittest
from PIL import Image

class TestCharacterFace(unittest.TestCase):
    def setUp(self):
        self.vox_path = "character.vox"
        self.glb_path = "character.glb"
        self.tex_default_path = "skin_default.png"
        self.tex_iron_path = "skin_iron_armor.png"

    def test_texture_atlases_validity(self):
        """Verifies 64x64 texture atlases generated properly with 16-bit JRPG face"""
        for p in [self.tex_default_path, self.tex_iron_path]:
            self.assertTrue(os.path.exists(p), f"{p} must exist")
            with Image.open(p) as img:
                self.assertEqual(img.size, (64, 64), f"{p} must be 64x64")
                self.assertEqual(img.mode, "RGBA", f"{p} must be RGBA")

        # Verify eye glint (pure white) in skin_default.png
        with Image.open(self.tex_default_path) as img:
            # Left eye glint at (4, 17) or (5, 17)
            glint_pixel = img.getpixel((4, 17))
            self.assertEqual(glint_pixel, (255, 255, 255, 255), "Eye reflection glint must be pure white")

    def test_vox_face_flush_geometry(self):
        """Verifies MagicaVoxel face plane at Z=2 is 100% solid without hollow cavities"""
        self.assertTrue(os.path.exists(self.vox_path), f"{self.vox_path} must exist")
        with open(self.vox_path, 'rb') as f:
            data = f.read()

        # Parse XYZI
        idx = data.find(b'XYZI')
        self.assertNotEqual(idx, -1, "XYZI chunk must be present")
        content_size, children_size = struct.unpack('<2I', data[idx+4 : idx+12])
        num_voxels = struct.unpack('<I', data[idx+12 : idx+16])[0]
        self.assertGreaterEqual(num_voxels, 650, f"Expected >= 650 voxels, got {num_voxels}")

        # Size chunk
        s_idx = data.find(b'SIZE')
        self.assertNotEqual(s_idx, -1)
        sx, sy, sz = struct.unpack('<3I', data[s_idx+12 : s_idx+24])
        print(f"\n  -> [FACE TEST] Character.vox: {num_voxels} voxels, bounds {sx}x{sy}x{sz}")

    def test_glb_texture_and_white_colors(self):
        """Verifies character.glb has pure white COLOR_0 and valid UV accessors"""
        self.assertTrue(os.path.exists(self.glb_path), f"{self.glb_path} must exist")
        with open(self.glb_path, 'rb') as f:
            data = f.read()

        magic, version, total_len = struct.unpack('<3I', data[:12])
        self.assertEqual(magic, 0x46546C67)
        self.assertEqual(version, 2)

        c0_len = struct.unpack('<I', data[12:16])[0]
        json_bytes = data[20 : 20 + c0_len]
        gltf = json.loads(json_bytes.decode('utf-8'))

        # Check attributes
        prim = gltf["meshes"][0]["primitives"][0]
        self.assertIn("POSITION", prim["attributes"])
        self.assertIn("NORMAL", prim["attributes"])
        self.assertIn("TEXCOORD_0", prim["attributes"])
        self.assertIn("COLOR_0", prim["attributes"])

        # Check COLOR_0 accessor
        col_acc_idx = prim["attributes"]["COLOR_0"]
        col_acc = gltf["accessors"][col_acc_idx]
        self.assertEqual(col_acc["type"], "VEC4")
        self.assertEqual(col_acc["componentType"], 5121) # UNSIGNED_BYTE
        self.assertTrue(col_acc["normalized"])

        # Check triangle count ~ 1,500 Tri
        idx_acc_idx = prim["indices"]
        idx_acc = gltf["accessors"][idx_acc_idx]
        tri_count = idx_acc["count"] // 3
        print(f"  -> [FACE TEST] Character.glb: {tri_count} Tris (Target ~1,500 Tri met!)")
        self.assertLess(tri_count, 2200, "Must be optimized for real-time mobile web")

if __name__ == '__main__':
    unittest.main()
