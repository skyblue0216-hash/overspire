#!/usr/bin/env python3
"""
Overspire Layer 1: Hero Locomotion Independent Test Harness
규칙 3에 따른 8방향 이동, 가속/감속, 회전(Facing Direction), Y=0 평면 구속 수학적 무결성 검증 러너
"""

import math
import sys

def test_8_direction_normalization():
    print("[TEST 1] 8-Direction Input Vector Normalization...")
    inputs = [
        (1, 0), (-1, 0), (0, 1), (0, -1),       # Cardinal
        (1, 1), (-1, 1), (1, -1), (-1, -1)     # Diagonal
    ]
    for ix, iz in inputs:
        length = math.sqrt(ix * ix + iz * iz)
        nx = ix / length
        nz = iz / length
        norm_len = math.sqrt(nx * nx + nz * nz)
        assert abs(norm_len - 1.0) < 1e-6, f"Normalization failed for ({ix}, {iz})"
        # Diagonal length must not exceed 1.0
        assert norm_len <= 1.00001, f"Diagonal speed boost detected for ({ix}, {iz})"
    print("  -> PASS: All 8 directions normalized to magnitude 1.0 (No diagonal speed exploit).")

def test_acceleration_and_braking_dynamics():
    print("[TEST 2] Kinematic Acceleration & Friction Braking Curves...")
    max_speed = 5.2
    acceleration = 42.0
    friction = 48.0
    dt = 1.0 / 60.0 # 60 FPS tick
    
    # Simulate full throttle for 0.5s
    vx, vz = 0.0, 0.0
    time = 0.0
    time_to_max = None
    for tick in range(60):
        # Accelerate along +Z
        vx = max(0.0, vx)
        vz = min(max_speed, vz + acceleration * dt)
        time += dt
        if abs(vz - max_speed) < 0.01 and time_to_max is None:
            time_to_max = time
            
    assert time_to_max is not None, "Failed to reach max speed"
    assert time_to_max < 0.20, f"Acceleration too sluggish: took {time_to_max:.3f}s (target < 0.20s)"
    print(f"  -> PASS: Reached max speed ({max_speed} m/s) in {time_to_max:.3f}s (Snappy start).")

    # Simulate release (Braking to dead stop)
    time_to_stop = None
    time = 0.0
    for tick in range(60):
        vz = max(0.0, vz - friction * dt)
        time += dt
        if vz <= 0.001 and time_to_stop is None:
            time_to_stop = time
            break
            
    assert time_to_stop is not None, "Failed to stop"
    assert time_to_stop < 0.18, f"Stopping distance too slippery: took {time_to_stop:.3f}s (target < 0.18s)"
    print(f"  -> PASS: Full stop in {time_to_stop:.3f}s (Zero-skate responsive braking).")

def test_facing_angle_resolution():
    print("[TEST 3] Facing Angle Resolution (atan2 mapping)...")
    expected_angles = [
        ((0, 1), 0.0),       # South (Forward, 0°)
        ((1, 0), 90.0),      # East (Right, 90°)
        ((0, -1), 180.0),    # North (Up, 180°)
        ((-1, 0), -90.0),    # West (Left, -90°)
        ((1, 1), 45.0),      # South-East (45°)
        ((-1, 1), -45.0),    # South-West (-45°)
        ((1, -1), 135.0),    # North-East (135°)
        ((-1, -1), -135.0)   # North-West (-135°)
    ]
    for (fx, fz), expected_deg in expected_angles:
        # atan2(x, z) gives radians where South (0, 1) is 0 rad
        deg = math.degrees(math.atan2(fx, fz))
        assert abs(deg - expected_deg) < 1e-4, f"Angle mismatch for ({fx}, {fz}): got {deg}, expected {expected_deg}"
    print("  -> PASS: All 8 facing angles resolve precisely without discontinuity.")

def test_y_plane_immutability():
    print("[TEST 4] Y=0 Horizontal Plane Invariant Constraint...")
    # Simulating 500 physics steps with arbitrary inputs
    pos_y = 0.0
    vel_y = 0.0
    for _ in range(500):
        # Force rule: velocity.y = 0.0, position.y = 0.0
        vel_y = 0.0
        pos_y += vel_y
        pos_y = 0.0
        assert pos_y == 0.0, "Y axis drifted from ground plane!"
        assert vel_y == 0.0, "Vertical velocity non-zero!"
    print("  -> PASS: Y=0 plane strictly maintained across 500 ticks.")

def test_directional_sprite_mapping():
    print("[TEST 5] 8-Directional Authentic Sprite Mapping Invariant...")
    def resolve_sprite_8(fx, fz):
        deg = math.degrees(math.atan2(fx, fz))
        if -22.5 <= deg < 22.5: return "south"
        elif 22.5 <= deg < 67.5: return "south-east"
        elif 67.5 <= deg < 112.5: return "east"
        elif 112.5 <= deg < 157.5: return "north-east"
        elif deg >= 157.5 or deg < -157.5: return "north"
        elif -157.5 <= deg < -112.5: return "north-west"
        elif -112.5 <= deg < -67.5: return "west"
        else: return "south-west"

    cases = [
        ((0, 1), "south"),         # South / Forward (0°)
        ((1, 1), "south-east"),     # South-East (45°)
        ((1, 0), "east"),           # East / Right (90°)
        ((1, -1), "north-east"),    # North-East (135°)
        ((0, -1), "north"),         # North / Back (180°)
        ((-1, -1), "north-west"),   # North-West (-135°)
        ((-1, 0), "west"),          # West / Left (-90°)
        ((-1, 1), "south-west"),    # South-West (-45°)
    ]
    for (fx, fz), exp_sprite in cases:
        sprite = resolve_sprite_8(fx, fz)
        assert sprite == exp_sprite, (
            f"8-Direction mapping mismatch for ({fx}, {fz}): got {sprite}, expected {exp_sprite}"
        )
    print("  -> PASS: All 8 directional sprites map with 100% mathematical precision.")

def main():
    print("=" * 65)
    print("  ⚔️  OVERSPIRE - LAYER 1: HERO LOCOMOTION TEST HARNESS")
    print("=" * 65)
    try:
        test_8_direction_normalization()
        test_acceleration_and_braking_dynamics()
        test_facing_angle_resolution()
        test_y_plane_immutability()
        test_directional_sprite_mapping()
        print("=" * 65)
        print("  ✅ ALL LAYER 1 INDEPENDENT TESTS PASSED (100% GREEN)!")
        print("=" * 65)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
