"""
glTF 2.0 Binary (.glb) Exporter with Hidden-Face Culling and Modular Node Hierarchy
"""
import struct
import json
from typing import Dict, List, Tuple, Optional
from .voxel_grid import VoxelGrid, Part
from .palette import Palette

# glTF constants
GLTF_MAGIC = 0x46546C67 # 'glTF'
GLTF_VERSION = 2
CHUNK_JSON = 0x4E4F534A # 'JSON'
CHUNK_BIN = 0x004E4942  # 'BIN\x00'

TYPE_SCALAR = "SCALAR"
TYPE_VEC3 = "VEC3"
TYPE_VEC4 = "VEC4"

COMP_UBYTE = 5121
COMP_USHORT = 5123
COMP_UINT = 5125
COMP_FLOAT = 5126

TARGET_ARRAY_BUFFER = 34962
TARGET_ELEMENT_ARRAY_BUFFER = 34963

class GLBBuilder:
    def __init__(self):
        self.bin_data = bytearray()
        self.buffer_views: List[dict] = []
        self.accessors: List[dict] = []
        self.meshes: List[dict] = []
        self.nodes: List[dict] = []
        self.scenes: List[dict] = []

    def _pad_bin(self, alignment: int = 4):
        pad = (alignment - (len(self.bin_data) % alignment)) % alignment
        if pad > 0:
            self.bin_data.extend(b'\x00' * pad)

    def add_buffer_view(self, data: bytes, target: Optional[int] = None) -> int:
        self._pad_bin(4)
        offset = len(self.bin_data)
        length = len(data)
        self.bin_data.extend(data)
        self._pad_bin(4)

        bv = {
            "buffer": 0,
            "byteOffset": offset,
            "byteLength": length
        }
        if target is not None:
            bv["target"] = target
        self.buffer_views.append(bv)
        return len(self.buffer_views) - 1

    def add_accessor(self, buffer_view_idx: int, byte_offset: int, comp_type: int,
                     count: int, type_str: str, min_val: Optional[list] = None,
                     max_val: Optional[list] = None, normalized: bool = False) -> int:
        acc = {
            "bufferView": buffer_view_idx,
            "byteOffset": byte_offset,
            "componentType": comp_type,
            "count": count,
            "type": type_str
        }
        if min_val is not None:
            acc["min"] = min_val
        if max_val is not None:
            acc["max"] = max_val
        if normalized:
            acc["normalized"] = True
        self.accessors.append(acc)
        return len(self.accessors) - 1

    def build_glb(self) -> bytes:
        self._pad_bin(4)
        
        json_dict = {
            "asset": {"version": "2.0", "generator": "Overspire Voxel glTF Exporter"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": self.nodes,
            "meshes": self.meshes,
            "accessors": self.accessors,
            "bufferViews": self.buffer_views,
            "buffers": [{"byteLength": len(self.bin_data)}]
        }

        json_bytes = json.dumps(json_dict, separators=(',', ':')).encode('utf-8')
        json_pad = (4 - (len(json_bytes) % 4)) % 4
        if json_pad > 0:
            json_bytes += b' ' * json_pad

        bin_pad = (4 - (len(self.bin_data) % 4)) % 4
        if bin_pad > 0:
            self.bin_data.extend(b'\x00' * bin_pad)

        total_length = 12 + 8 + len(json_bytes) + 8 + len(self.bin_data)

        header = struct.pack('<3I', GLTF_MAGIC, GLTF_VERSION, total_length)
        chunk0_header = struct.pack('<2I', len(json_bytes), CHUNK_JSON)
        chunk1_header = struct.pack('<2I', len(self.bin_data), CHUNK_BIN)

        return header + chunk0_header + json_bytes + chunk1_header + bytes(self.bin_data)


# Face definitions: (normal_tuple, [v0, v1, v2, v3] relative to voxel corner)
FACE_DEFS = [
    # +Z (Front)
    ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
    # -Z (Back)
    ((0, 0, -1), [(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)]),
    # +Y (Top)
    ((0, 1, 0), [(0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)]),
    # -Y (Bottom)
    ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
    # +X (Right)
    ((1, 0, 0), [(1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)]),
    # -X (Left)
    ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
]

def mesh_voxel_set(voxels: Dict[Tuple[int, int, int], int],
                   palette: Palette,
                   scale: float = 0.05,
                   pivot: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> Tuple[bytes, bytes, bytes, bytes, int, list, list]:
    """
    Meshes a set of voxels with hidden-face culling.
    Returns: (positions_bytes, normals_bytes, colors_bytes, indices_bytes, vertex_count, min_pos, max_pos)
    """
    pos_bytes = bytearray()
    norm_bytes = bytearray()
    col_bytes = bytearray()
    idx_bytes = bytearray()

    v_count = 0
    min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

    # Neighbor check offsets
    neighbor_offsets = [
        (0, 0, 1),  # +Z
        (0, 0, -1), # -Z
        (0, 1, 0),  # +Y
        (0, -1, 0), # -Y
        (1, 0, 0),  # +X
        (-1, 0, 0), # -X
    ]

    for (vx, vy, vz), color_idx in voxels.items():
        r, g, b, a = palette.get_rgba(color_idx)

        for face_idx, (nx, ny, nz) in enumerate(neighbor_offsets):
            neighbor = (vx + nx, vy + ny, vz + nz)
            # Hidden-face culling: omit face if neighbor voxel is solid
            if neighbor in voxels:
                continue

            normal, vert_offsets = FACE_DEFS[face_idx]
            base_idx = v_count

            for dx, dy, dz in vert_offsets:
                # Local coordinates relative to pivot
                px = (vx + dx) * scale - pivot[0]
                py = (vy + dy) * scale - pivot[1]
                pz = (vz + dz) * scale - pivot[2]

                pos_bytes.extend(struct.pack('<3f', px, py, pz))
                norm_bytes.extend(struct.pack('<3f', float(normal[0]), float(normal[1]), float(normal[2])))
                col_bytes.extend(struct.pack('4B', r, g, b, 255))

                min_x = min(min_x, px)
                min_y = min(min_y, py)
                min_z = min(min_z, pz)
                max_x = max(max_x, px)
                max_y = max(max_y, py)
                max_z = max(max_z, pz)

                v_count += 1

            # Two triangles (0, 1, 2) and (0, 2, 3)
            idx_bytes.extend(struct.pack('<6H',
                base_idx + 0, base_idx + 1, base_idx + 2,
                base_idx + 0, base_idx + 2, base_idx + 3
            ))

    if v_count == 0:
        min_pos = [0.0, 0.0, 0.0]
        max_pos = [0.0, 0.0, 0.0]
    else:
        min_pos = [min_x, min_y, min_z]
        max_pos = [max_x, max_y, max_z]

    return bytes(pos_bytes), bytes(norm_bytes), bytes(col_bytes), bytes(idx_bytes), v_count, min_pos, max_pos


def export_glb_modular(grid: VoxelGrid, palette: Palette, filepath: str,
                       scale: float = 0.05, center_world: bool = True):
    """
    Exports a rigged, modular glTF binary (.glb) with anatomical pivots:
    - Root (Hero)
      - BodyPivot
        - TorsoMesh
        - HeadPivot -> HeadMesh
        - LeftArmPivot -> LeftArmMesh, ShieldSocket
        - RightArmPivot -> RightArmMesh, WeaponSocket
        - LeftLegPivot -> LeftLegMesh
        - RightLegPivot -> RightLegMesh
    """
    builder = GLBBuilder()

    # Calculate anatomical pivots
    min_x, min_y, min_z, max_x, max_y, max_z = grid.get_bounds()
    center_x = (min_x + max_x + 1) * 0.5 * scale if center_world else 0.0
    center_z = (min_z + max_z + 1) * 0.5 * scale if center_world else 0.0

    # Part bounding boxes for pivots
    def get_part_bounds(p):
        return grid.get_bounds(part_id=p)

    torso_b = get_part_bounds(Part.TORSO)
    head_b = get_part_bounds(Part.HEAD)
    larm_b = get_part_bounds(Part.LEFT_ARM)
    rarm_b = get_part_bounds(Part.RIGHT_ARM)
    lleg_b = get_part_bounds(Part.LEFT_LEG)
    rleg_b = get_part_bounds(Part.RIGHT_LEG)

    # World pivot coordinates (in meters)
    body_pivot_y = torso_b[1] * scale
    head_pivot = (center_x, (head_b[1]) * scale, center_z)
    larm_pivot = ((larm_b[0] + larm_b[3] + 1) * 0.5 * scale, (larm_b[4]) * scale, center_z)
    rarm_pivot = ((rarm_b[0] + rarm_b[3] + 1) * 0.5 * scale, (rarm_b[4]) * scale, center_z)
    lleg_pivot = ((lleg_b[0] + lleg_b[3] + 1) * 0.5 * scale, (lleg_b[4] + 1) * scale, center_z)
    rleg_pivot = ((rleg_b[0] + rleg_b[3] + 1) * 0.5 * scale, (rleg_b[4] + 1) * scale, center_z)

    # Sub-meshes creation helper
    def create_mesh_for_part(part_id: str, pivot: Tuple[float, float, float]) -> Optional[int]:
        vox_dict = {(x, y, z): c for x, y, z, c, p in grid.iter_voxels(part_id=part_id)}
        if not vox_dict:
            return None

        p_bytes, n_bytes, c_bytes, i_bytes, v_count, min_p, max_p = mesh_voxel_set(
            vox_dict, palette, scale=scale, pivot=pivot
        )
        if v_count == 0:
            return None

        bv_pos = builder.add_buffer_view(p_bytes, TARGET_ARRAY_BUFFER)
        bv_norm = builder.add_buffer_view(n_bytes, TARGET_ARRAY_BUFFER)
        bv_col = builder.add_buffer_view(c_bytes, TARGET_ARRAY_BUFFER)
        bv_idx = builder.add_buffer_view(i_bytes, TARGET_ELEMENT_ARRAY_BUFFER)

        acc_pos = builder.add_accessor(bv_pos, 0, COMP_FLOAT, v_count, TYPE_VEC3, min_p, max_p)
        acc_norm = builder.add_accessor(bv_norm, 0, COMP_FLOAT, v_count, TYPE_VEC3)
        acc_col = builder.add_accessor(bv_col, 0, COMP_UBYTE, v_count, TYPE_VEC4, normalized=True)
        num_indices = len(i_bytes) // 2
        acc_idx = builder.add_accessor(bv_idx, 0, COMP_USHORT, num_indices, TYPE_SCALAR)

        mesh_dict = {
            "name": f"Mesh_{part_id}",
            "primitives": [{
                "attributes": {
                    "POSITION": acc_pos,
                    "NORMAL": acc_norm,
                    "COLOR_0": acc_col
                },
                "indices": acc_idx
            }]
        }
        builder.meshes.append(mesh_dict)
        return len(builder.meshes) - 1

    # Create meshes for parts with their local pivots
    torso_mesh = create_mesh_for_part(Part.TORSO, (center_x, 0.0, center_z))
    head_mesh = create_mesh_for_part(Part.HEAD, head_pivot)
    larm_mesh = create_mesh_for_part(Part.LEFT_ARM, larm_pivot)
    rarm_mesh = create_mesh_for_part(Part.RIGHT_ARM, rarm_pivot)
    lleg_mesh = create_mesh_for_part(Part.LEFT_LEG, lleg_pivot)
    rleg_mesh = create_mesh_for_part(Part.RIGHT_LEG, rleg_pivot)

    # Also check props (sword, shield)
    sword_mesh = create_mesh_for_part(Part.SWORD, rarm_pivot)
    shield_mesh = create_mesh_for_part(Part.SHIELD, larm_pivot)

    # Build Node Hierarchy
    # Node indices will be allocated sequentially
    nodes = builder.nodes

    def add_node(name: str, mesh: Optional[int] = None, translation: Optional[list] = None,
                 children: Optional[list] = None) -> int:
        n = {"name": name}
        if mesh is not None:
            n["mesh"] = mesh
        if translation is not None and any(abs(t) > 1e-6 for t in translation):
            n["translation"] = translation
        if children:
            n["children"] = children
        nodes.append(n)
        return len(nodes) - 1

    # Leaf mesh nodes
    head_mesh_node = add_node("HeadMesh", mesh=head_mesh)
    larm_mesh_node = add_node("LeftArmMesh", mesh=larm_mesh)
    rarm_mesh_node = add_node("RightArmMesh", mesh=rarm_mesh)
    lleg_mesh_node = add_node("LeftLegMesh", mesh=lleg_mesh)
    rleg_mesh_node = add_node("RightLegMesh", mesh=rleg_mesh)

    # Accessory / Socket nodes
    shield_socket_node = add_node("ShieldSocket", mesh=shield_mesh, translation=[0.0, -0.15, 0.10])
    weapon_socket_node = add_node("WeaponSocket", mesh=sword_mesh, translation=[0.0, -0.15, 0.10])

    # Pivot nodes with local translation offsets
    head_pivot_node = add_node("HeadPivot", translation=[0.0, head_pivot[1], 0.0], children=[head_mesh_node])
    larm_pivot_node = add_node("LeftArmPivot", translation=[larm_pivot[0] - center_x, larm_pivot[1], larm_pivot[2] - center_z],
                               children=[larm_mesh_node, shield_socket_node])
    rarm_pivot_node = add_node("RightArmPivot", translation=[rarm_pivot[0] - center_x, rarm_pivot[1], rarm_pivot[2] - center_z],
                               children=[rarm_mesh_node, weapon_socket_node])
    lleg_pivot_node = add_node("LeftLegPivot", translation=[lleg_pivot[0] - center_x, lleg_pivot[1], lleg_pivot[2] - center_z],
                               children=[lleg_mesh_node])
    rleg_pivot_node = add_node("RightLegPivot", translation=[rleg_pivot[0] - center_x, rleg_pivot[1], rleg_pivot[2] - center_z],
                               children=[rleg_mesh_node])

    torso_mesh_node = add_node("TorsoMesh", mesh=torso_mesh)

    body_children = [
        torso_mesh_node,
        head_pivot_node,
        larm_pivot_node,
        rarm_pivot_node,
        lleg_pivot_node,
        rleg_pivot_node
    ]
    body_pivot_node = add_node("BodyPivot", children=body_children)

    # Root Node
    root_node = add_node("Hero", children=[body_pivot_node])

    glb_bytes = builder.build_glb()
    with open(filepath, 'wb') as f:
        f.write(glb_bytes)


def export_glb_static(grid: VoxelGrid, palette: Palette, filepath: str,
                      scale: float = 0.05, center_world: bool = True):
    """
    Exports a single unified static mesh glTF binary (.glb).
    """
    builder = GLBBuilder()
    min_x, min_y, min_z, max_x, max_y, max_z = grid.get_bounds()
    center_x = (min_x + max_x + 1) * 0.5 * scale if center_world else 0.0
    center_z = (min_z + max_z + 1) * 0.5 * scale if center_world else 0.0

    vox_dict = {(x, y, z): c for x, y, z, c, _ in grid.iter_voxels()}
    p_bytes, n_bytes, c_bytes, i_bytes, v_count, min_p, max_p = mesh_voxel_set(
        vox_dict, palette, scale=scale, pivot=(center_x, 0.0, center_z)
    )

    bv_pos = builder.add_buffer_view(p_bytes, TARGET_ARRAY_BUFFER)
    bv_norm = builder.add_buffer_view(n_bytes, TARGET_ARRAY_BUFFER)
    bv_col = builder.add_buffer_view(c_bytes, TARGET_ARRAY_BUFFER)
    bv_idx = builder.add_buffer_view(i_bytes, TARGET_ELEMENT_ARRAY_BUFFER)

    acc_pos = builder.add_accessor(bv_pos, 0, COMP_FLOAT, v_count, TYPE_VEC3, min_p, max_p)
    acc_norm = builder.add_accessor(bv_norm, 0, COMP_FLOAT, v_count, TYPE_VEC3)
    acc_col = builder.add_accessor(bv_col, 0, COMP_UBYTE, v_count, TYPE_VEC4, normalized=True)
    acc_idx = builder.add_accessor(bv_idx, 0, COMP_USHORT, len(i_bytes) // 2, TYPE_SCALAR)

    builder.meshes.append({
        "name": "Mesh_HeroStatic",
        "primitives": [{
            "attributes": {
                "POSITION": acc_pos,
                "NORMAL": acc_norm,
                "COLOR_0": acc_col
            },
            "indices": acc_idx
        }]
    })

    builder.nodes.append({"name": "HeroStatic", "mesh": 0})

    glb_bytes = builder.build_glb()
    with open(filepath, 'wb') as f:
        f.write(glb_bytes)
