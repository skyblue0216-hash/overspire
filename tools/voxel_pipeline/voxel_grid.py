"""
VoxelGrid Data Structure for 3D Modular Character Generation
"""
from typing import Dict, Tuple, Optional, Set, Iterator

class Part:
    TORSO     = "torso"
    HEAD      = "head"
    LEFT_ARM  = "left_arm"
    RIGHT_ARM = "right_arm"
    LEFT_LEG  = "left_leg"
    RIGHT_LEG = "right_leg"
    SWORD     = "sword"
    SHIELD    = "shield"
    
    ALL = [TORSO, HEAD, LEFT_ARM, RIGHT_ARM, LEFT_LEG, RIGHT_LEG, SWORD, SHIELD]

class VoxelGrid:
    def __init__(self, size_x: int = 32, size_y: int = 40, size_z: int = 32):
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        # Maps (x, y, z) -> (color_index, part_id)
        self.voxels: Dict[Tuple[int, int, int], Tuple[int, str]] = {}

    def in_bounds(self, x: int, y: int, z: int) -> bool:
        return 0 <= x < self.size_x and 0 <= y < self.size_y and 0 <= z < self.size_z

    def set_voxel(self, x: int, y: int, z: int, color_idx: int, part_id: str = Part.TORSO) -> bool:
        if not self.in_bounds(x, y, z):
            return False
        self.voxels[(x, y, z)] = (color_idx, part_id)
        return True

    def remove_voxel(self, x: int, y: int, z: int):
        if (x, y, z) in self.voxels:
            del self.voxels[(x, y, z)]

    def get_voxel(self, x: int, y: int, z: int) -> Optional[Tuple[int, str]]:
        return self.voxels.get((x, y, z), None)

    def fill_box(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, 
                 color_idx: int, part_id: str = Part.TORSO):
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        min_z, max_z = min(z1, z2), max(z1, z2)
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                for z in range(min_z, max_z + 1):
                    self.set_voxel(x, y, z, color_idx, part_id)

    def fill_cylinder_y(self, cx: float, cy1: int, cy2: int, cz: float, radius: float,
                        color_idx: int, part_id: str = Part.TORSO):
        r_sq = radius * radius
        min_y, max_y = min(cy1, cy2), max(cy1, cy2)
        min_x = int(cx - radius - 1)
        max_x = int(cx + radius + 1)
        min_z = int(cz - radius - 1)
        max_z = int(cz + radius + 1)
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                for z in range(min_z, max_z + 1):
                    dx = (x + 0.5) - cx
                    dz = (z + 0.5) - cz
                    if (dx*dx + dz*dz) <= r_sq:
                        self.set_voxel(x, y, z, color_idx, part_id)

    def get_bounds(self, part_id: Optional[str] = None) -> Tuple[int, int, int, int, int, int]:
        """Returns (min_x, min_y, min_z, max_x, max_y, max_z)"""
        matched = [pos for pos, (_, p) in self.voxels.items() if part_id is None or p == part_id]
        if not matched:
            return (0, 0, 0, 0, 0, 0)
        xs = [p[0] for p in matched]
        ys = [p[1] for p in matched]
        zs = [p[2] for p in matched]
        return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))

    def count(self, part_id: Optional[str] = None) -> int:
        if part_id is None:
            return len(self.voxels)
        return sum(1 for _, p in self.voxels.values() if p == part_id)

    def iter_voxels(self, part_id: Optional[str] = None) -> Iterator[Tuple[int, int, int, int, str]]:
        for (x, y, z), (c, p) in self.voxels.items():
            if part_id is None or p == part_id:
                yield (x, y, z, c, p)
