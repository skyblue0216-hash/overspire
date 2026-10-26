"""
Voxel Character Pipeline CLI Runner
Builds the 2.5-Head Retro JRPG Adventurer in .vox and .glb formats.
"""
import os
import sys
from .palette import Palette
from .voxel_grid import Part
from .character_builder import build_hero_grid
from .vox_writer import export_vox
from .glb_writer import export_glb_modular, export_glb_static

def run_pipeline(output_dir: str = "assets/models"):
    os.makedirs(output_dir, exist_ok=True)
    palette = Palette()

    print("=================================================================")
    print("  ⚔️  OVERSPIRE - 2.5-HEAD RETRO JRPG VOXEL PIPELINE")
    print("=================================================================")

    # 1. Build Grid
    print("[1/4] Sculpting 2.5-head Chibi Adventurer Voxel Grid...")
    grid = build_hero_grid(palette, include_props=True)
    total_voxels = grid.count()
    print(f"  -> Total voxels sculpted: {total_voxels}")
    for p in Part.ALL:
        c = grid.count(p)
        if c > 0:
            print(f"     - {p.ljust(10)}: {c} voxels")

    # 2. Export .VOX (MagicaVoxel)
    vox_path = os.path.join(output_dir, "hero_retro_jrpg.vox")
    print(f"[2/4] Generating MagicaVoxel file: {vox_path}...")
    export_vox(grid, palette, vox_path)
    vox_size = os.path.getsize(vox_path)
    print(f"  -> SUCCESS: {vox_path} ({vox_size} bytes, MagicaVoxel v150)")

    # Also export individual props as .vox
    sword_vox_path = os.path.join(output_dir, "sword.vox")
    export_vox(grid, palette, sword_vox_path, part_id=Part.SWORD)
    print(f"  -> SUCCESS: {sword_vox_path} ({os.path.getsize(sword_vox_path)} bytes)")

    shield_vox_path = os.path.join(output_dir, "shield.vox")
    export_vox(grid, palette, shield_vox_path, part_id=Part.SHIELD)
    print(f"  -> SUCCESS: {shield_vox_path} ({os.path.getsize(shield_vox_path)} bytes)")

    # 3. Export Modular .GLB (Rigged with Anatomical Pivots & Sockets)
    glb_modular_path = os.path.join(output_dir, "hero_retro_jrpg.glb")
    print(f"[3/4] Generating Rigged Modular glTF: {glb_modular_path}...")
    export_glb_modular(grid, palette, glb_modular_path, scale=0.05)
    glb_modular_size = os.path.getsize(glb_modular_path)
    print(f"  -> SUCCESS: {glb_modular_path} ({glb_modular_size} bytes)")
    print(f"     * Rig Hierarchy: BodyPivot -> [Torso, HeadPivot, LeftArmPivot, RightArmPivot, LeftLegPivot, RightLegPivot]")
    print(f"     * Equipment Sockets: WeaponSocket (Right Hand), ShieldSocket (Left Hand)")

    # 4. Export Static .GLB (Unified single-mesh)
    glb_static_path = os.path.join(output_dir, "hero_static.glb")
    print(f"[4/4] Generating Unified Static glTF: {glb_static_path}...")
    export_glb_static(grid, palette, glb_static_path, scale=0.05)
    glb_static_size = os.path.getsize(glb_static_path)
    print(f"  -> SUCCESS: {glb_static_path} ({glb_static_size} bytes)")

    print("=================================================================")
    print("  ✅ 3D VOXEL PIPELINE COMPLETED SUCCESSFULLY!")
    print("=================================================================")

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "assets/models"
    run_pipeline(out_dir)
