"""
Independent Automated Test Suite for Overspire 3D Voxel Pipeline (.vox & .glb)
"""
import os
import struct
import json
import unittest

class TestVoxelPipeline(unittest.TestCase):
    def setUp(self):
        self.vox_path = "assets/models/hero_retro_jrpg.vox"
        self.glb_path = "assets/models/hero_retro_jrpg.glb"
        self.glb_static_path = "assets/models/hero_static.glb"

    def test_vox_format_specification(self):
        """Verifies EphTracy MagicaVoxel format specification (v150)"""
        self.assertTrue(os.path.exists(self.vox_path), "hero_retro_jrpg.vox must exist")
        with open(self.vox_path, 'rb') as f:
            data = f.read()

        # Header: 'VOX ' + 150
        magic = data[:4]
        self.assertEqual(magic, b'VOX ', "Magic must be 'VOX '")
        version = struct.unpack('<I', data[4:8])[0]
        self.assertEqual(version, 150, "Version must be 150")

        # MAIN chunk
        main_id = data[8:12]
        self.assertEqual(main_id, b'MAIN', "First chunk must be MAIN")
        content_len, children_len = struct.unpack('<2I', data[12:20])
        self.assertEqual(content_len, 0, "MAIN content length must be 0")
        self.assertEqual(len(data), 20 + children_len, "File size must match header + children")

        # Parse children of MAIN
        offset = 20
        chunks = {}
        while offset < len(data):
            c_id = data[offset : offset + 4].decode('ascii', errors='ignore')
            c_size, c_children = struct.unpack('<2I', data[offset + 4 : offset + 12])
            c_data = data[offset + 12 : offset + 12 + c_size]
            chunks[c_id] = c_data
            offset += 12 + c_size + c_children

        self.assertIn('SIZE', chunks, "VOX must contain SIZE chunk")
        self.assertIn('XYZI', chunks, "VOX must contain XYZI chunk")
        self.assertIn('RGBA', chunks, "VOX must contain RGBA chunk")

        # Check SIZE
        sx, sy, sz = struct.unpack('<3I', chunks['SIZE'])
        self.assertGreater(sx, 0)
        self.assertGreater(sy, 0)
        self.assertGreater(sz, 0)

        # Check XYZI
        num_voxels = struct.unpack('<I', chunks['XYZI'][:4])[0]
        self.assertEqual(num_voxels, 1891, "Must contain exactly 1891 sculpted voxels")
        self.assertEqual(len(chunks['XYZI']), 4 + num_voxels * 4, "XYZI body size must match voxel count")

        # Check RGBA (256 colors * 4 bytes = 1024 bytes)
        self.assertEqual(len(chunks['RGBA']), 1024, "RGBA palette chunk must be exactly 1024 bytes")
        print(f"\n  -> [VOX TEST] Validated MagicaVoxel v150: {num_voxels} voxels, bounds ({sx}x{sy}x{sz}), 256-color palette OK!")

    def test_glb_format_specification(self):
        """Verifies glTF 2.0 Binary (.glb) format specification"""
        self.assertTrue(os.path.exists(self.glb_path), "hero_retro_jrpg.glb must exist")
        with open(self.glb_path, 'rb') as f:
            data = f.read()

        # Header: magic, version, total_length
        magic, version, total_len = struct.unpack('<3I', data[:12])
        self.assertEqual(magic, 0x46546C67, "glTF magic must be 0x46546C67 ('glTF')")
        self.assertEqual(version, 2, "glTF version must be 2")
        self.assertEqual(total_len, len(data), "glTF total length header must match file size")

        # Chunk 0: JSON
        c0_len, c0_type = struct.unpack('<2I', data[12:20])
        self.assertEqual(c0_type, 0x4E4F534A, "Chunk 0 must be JSON (0x4E4F534A)")
        json_bytes = data[20 : 20 + c0_len]
        gltf = json.loads(json_bytes.decode('utf-8').strip())

        # Chunk 1: BIN
        c1_offset = 20 + c0_len
        c1_len, c1_type = struct.unpack('<2I', data[c1_offset : c1_offset + 8])
        self.assertEqual(c1_type, 0x004E4942, "Chunk 1 must be BIN (0x004E4942)")
        bin_data = data[c1_offset + 8 : c1_offset + 8 + c1_len]
        self.assertGreater(len(bin_data), 0, "Binary data chunk must not be empty")

        # Node Hierarchy Integrity Check
        node_names = [n["name"] for n in gltf["nodes"]]
        self.assertIn("Hero", node_names)
        self.assertIn("BodyPivot", node_names)
        self.assertIn("HeadPivot", node_names)
        self.assertIn("LeftArmPivot", node_names)
        self.assertIn("RightArmPivot", node_names)
        self.assertIn("LeftLegPivot", node_names)
        self.assertIn("RightLegPivot", node_names)
        self.assertIn("WeaponSocket", node_names)
        self.assertIn("ShieldSocket", node_names)

        # Meshes & Attributes Check
        self.assertGreater(len(gltf["meshes"]), 0)
        for m in gltf["meshes"]:
            for prim in m["primitives"]:
                attrs = prim["attributes"]
                self.assertIn("POSITION", attrs, "Every primitive must have POSITION")
                self.assertIn("NORMAL", attrs, "Every primitive must have NORMAL")
                self.assertIn("COLOR_0", attrs, "Every primitive must have vertex COLOR_0")
                self.assertIn("indices", prim, "Every primitive must have indexed geometry")

        # Hidden-face culling efficiency
        # Total un-culled faces for 1891 voxels would be 1891 * 6 = 11346 faces (22692 tris)
        total_tris = sum(gltf["accessors"][prim["indices"]]["count"] // 3 for m in gltf["meshes"] for prim in m["primitives"])
        culling_ratio = 1.0 - (total_tris / 22692.0)
        self.assertGreater(culling_ratio, 0.65, f"Hidden-face culling must eliminate >65% of internal faces (culled: {culling_ratio*100:.1f}%)")
        print(f"  -> [GLB TEST] Validated glTF 2.0 Binary: {len(gltf['nodes'])} nodes, {len(gltf['meshes'])} submeshes, {total_tris} tris (culled {culling_ratio*100:.1f}% internal faces) OK!")

if __name__ == "__main__":
    unittest.main()
