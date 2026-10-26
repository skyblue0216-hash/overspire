"""
MagicaVoxel (.vox) Binary Exporter
Conforms strictly to EphTracy MagicaVoxel file format specification (Version 150)
"""
import struct
from typing import Optional
from .voxel_grid import VoxelGrid
from .palette import Palette

def export_vox(grid: VoxelGrid, palette: Palette, filepath: str, part_id: Optional[str] = None):
    """
    Exports a VoxelGrid (or specific part) to a standard .vox file.
    Coordinate mapping:
      Grid (X: Width, Y: Height, Z: Depth) -> VOX (X: Width, Y: Depth, Z: Height)
    """
    voxels = list(grid.iter_voxels(part_id=part_id))
    if not voxels:
        raise ValueError("Cannot export empty voxel grid to .vox")

    # Calculate actual bounding box to optimize VOX canvas size
    min_x, min_y, min_z, max_x, max_y, max_z = grid.get_bounds(part_id=part_id)
    size_x = max(1, max_x - min_x + 1)
    size_y = max(1, max_z - min_z + 1) # VOX Y is depth (Grid Z)
    size_z = max(1, max_y - min_y + 1) # VOX Z is height (Grid Y)

    # 1. SIZE Chunk
    size_content = struct.pack('<3I', size_x, size_y, size_z)
    size_chunk = b'SIZE' + struct.pack('<2I', len(size_content), 0) + size_content

    # 2. XYZI Chunk
    xyzi_body = bytearray(4 + len(voxels) * 4)
    struct.pack_into('<I', xyzi_body, 0, len(voxels))
    offset = 4
    for gx, gy, gz, color_idx, _ in voxels:
        vx = gx - min_x
        vy = gz - min_z # Depth in MagicaVoxel is Y
        vz = gy - min_y # Height in MagicaVoxel is Z
        struct.pack_into('4B', xyzi_body, offset, vx, vy, vz, color_idx)
        offset += 4

    xyzi_chunk = b'XYZI' + struct.pack('<2I', len(xyzi_body), 0) + bytes(xyzi_body)

    # 3. RGBA Palette Chunk
    rgba_content = palette.get_rgba_bytes()
    rgba_chunk = b'RGBA' + struct.pack('<2I', len(rgba_content), 0) + rgba_content

    # 4. MAIN Chunk
    children_content = size_chunk + xyzi_chunk + rgba_chunk
    main_chunk = b'MAIN' + struct.pack('<2I', 0, len(children_content)) + children_content

    # 5. Header (VOX  + version 150)
    header = b'VOX ' + struct.pack('<I', 150)

    with open(filepath, 'wb') as f:
        f.write(header + main_chunk)
