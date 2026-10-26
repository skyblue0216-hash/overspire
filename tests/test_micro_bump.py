#!/usr/bin/env python3
"""
Overspire - Layer 2: Micro Bump Loop Independent Test Harness
Tests collision angle resolution, mutual vs unilateral damage,
separation impulse, attack cooldown invariants, and OCP interceptors.
"""

import math
import unittest

# Pure Python replication of BumpMath & BumpResolver for headless verification
FRONTAL_THRESHOLD = 0.70710678  # cos(45 deg)


class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def length(self):
        return math.hypot(self.x, self.y)

    def normalized(self):
        l = self.length()
        if l < 1e-6:
            return Vector2(0, 0)
        return Vector2(self.x / l, self.y / l)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)


class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def to_2d(self):
        return Vector2(self.x, self.z)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)


class BumpMathPy:
    @staticmethod
    def calculate_contact_vector(attacker_pos: Vector3, target_pos: Vector3) -> Vector2:
        diff = attacker_pos.to_2d() - target_pos.to_2d()
        return diff.normalized()

    @staticmethod
    def calculate_angle_cos(target_facing: Vector2, contact_vec: Vector2) -> float:
        f = target_facing.normalized()
        c = contact_vec.normalized()
        val = f.dot(c)
        return max(-1.0, min(1.0, val))

    @staticmethod
    def is_frontal_clash(angle_cos: float, threshold: float = FRONTAL_THRESHOLD) -> bool:
        return angle_cos >= threshold

    @staticmethod
    def calculate_damage(atk: float, def_val: float, skill_mult: float = 1.0, is_crit: bool = False, crit_mult: float = 1.5) -> int:
        raw_dmg = (atk * skill_mult) - (def_val * 0.5)
        final_dmg = max(1.0, raw_dmg)
        if is_crit:
            final_dmg *= crit_mult
        return int(round(final_dmg))

    @staticmethod
    def calculate_cooldown(base_cd: float = 0.35, atk_spd_boost: float = 0.0) -> float:
        return max(0.05, base_cd / (1.0 + max(0.0, atk_spd_boost)))


class MockCombatEntity:
    def __init__(self, pos: Vector3, facing_2d: Vector2, atk=10.0, def_val=2.0, hp=50):
        self.position = pos
        self.facing_direction = facing_2d.normalized()
        self.stat_atk = atk
        self.stat_def = def_val
        self.hp = hp
        self.attack_cooldown = 0.0
        self.stat_crit_rate = 0.1
        self.stat_crit_mult = 1.5


class BumpResolverPy:
    def __init__(self):
        self.interceptors = []

    def register_interceptor(self, interceptor):
        if interceptor not in self.interceptors:
            self.interceptors.append(interceptor)

    def resolve_bump(self, attacker: MockCombatEntity, defender: MockCombatEntity, force_crit: bool = False):
        contact_vec = BumpMathPy.calculate_contact_vector(attacker.position, defender.position)
        angle_cos = BumpMathPy.calculate_angle_cos(defender.facing_direction, contact_vec)
        is_frontal = BumpMathPy.is_frontal_clash(angle_cos)

        # 1. Cooldown Check (No-iframe Multi-hit prevention)
        if attacker.attack_cooldown > 0.0:
            return {
                "valid_hit": False,
                "is_frontal": is_frontal,
                "damage_to_attacker": 0,
                "damage_to_defender": 0,
                "knockback_attacker_mag": 3.2,
                "knockback_defender_mag": 1.6,
                "hitstop_duration": 0.0,
                "is_crit": False
            }

        # 2. Damage & Impulse resolution
        is_crit = force_crit
        dmg_defender = BumpMathPy.calculate_damage(attacker.stat_atk, defender.stat_def, 1.0, is_crit, attacker.stat_crit_mult)

        base_impulse = 5.5
        if is_frontal:
            dmg_attacker = BumpMathPy.calculate_damage(defender.stat_atk, attacker.stat_def, 1.0, False, 1.0)
            kb_atk = base_impulse * 0.9
            kb_def = base_impulse * 0.9
        else:
            dmg_attacker = 0
            kb_atk = base_impulse * 0.25
            kb_def = base_impulse * 1.3

        ctx = {
            "attacker": attacker,
            "defender": defender,
            "is_frontal": is_frontal,
            "damage_to_defender": dmg_defender,
            "damage_to_attacker": dmg_attacker,
            "kb_atk": kb_atk,
            "kb_def": kb_def,
            "hitstop": 0.04,
            "is_crit": is_crit,
            "cancel": False
        }

        # Interceptors
        for it in self.interceptors:
            it(ctx)

        if ctx["cancel"]:
            return {"valid_hit": False}

        attacker.attack_cooldown = BumpMathPy.calculate_cooldown(0.35, 0.0)

        return {
            "valid_hit": True,
            "is_frontal": ctx["is_frontal"],
            "damage_to_attacker": ctx["damage_to_attacker"],
            "damage_to_defender": ctx["damage_to_defender"],
            "knockback_attacker_mag": ctx["kb_atk"],
            "knockback_defender_mag": ctx["kb_def"],
            "hitstop_duration": ctx["hitstop"],
            "is_crit": ctx["is_crit"],
            "angle_cos": angle_cos
        }


class TestMicroBumpLoop(unittest.TestCase):
    def setUp(self):
        self.resolver = BumpResolverPy()

    def test_angle_resolution_0_deg(self):
        """0 deg (Head-on frontal clash): Mutual damage, cos ≈ 1.0 >= 0.7071"""
        # Target at (0, 0, 0) facing +Z (0, 1)
        # Hero attacks from (0, 0, 2), contact vector = (0, 1) -> angle = 0 deg
        target = MockCombatEntity(Vector3(0, 0, 0), Vector2(0, 1), atk=8, def_val=2)
        hero = MockCombatEntity(Vector3(0, 0, 2), Vector2(0, -1), atk=12, def_val=4)

        res = self.resolver.resolve_bump(hero, target)
        self.assertTrue(res["valid_hit"])
        self.assertTrue(res["is_frontal"])
        self.assertAlmostEqual(res["angle_cos"], 1.0, places=4)
        self.assertGreater(res["damage_to_attacker"], 0, "Hero must take mutual damage in 0 deg frontal clash")
        self.assertGreater(res["damage_to_defender"], 0, "Defender must take damage")

    def test_angle_resolution_30_deg(self):
        """30 deg (Within 45 deg frontal cone): Mutual damage, cos(30) ≈ 0.8660 >= 0.7071"""
        target = MockCombatEntity(Vector3(0, 0, 0), Vector2(0, 1), atk=8, def_val=2)
        # 30 deg offset: x = sin(30)=0.5, z = cos(30)=0.866
        hero = MockCombatEntity(Vector3(0.5, 0, 0.866), Vector2(-0.5, -0.866), atk=12, def_val=4)

        res = self.resolver.resolve_bump(hero, target)
        self.assertTrue(res["valid_hit"])
        self.assertTrue(res["is_frontal"])
        self.assertAlmostEqual(res["angle_cos"], math.cos(math.radians(30)), places=3)
        self.assertGreater(res["damage_to_attacker"], 0, "Hero must take mutual damage in 30 deg frontal cone")

    def test_angle_resolution_45_deg_boundary(self):
        """45 deg (Frontal boundary): cos(45) ≈ 0.70710678 >= threshold"""
        target = MockCombatEntity(Vector3(0, 0, 0), Vector2(0, 1), atk=8, def_val=2)
        hero = MockCombatEntity(Vector3(1.0, 0, 1.0), Vector2(-1, -1), atk=12, def_val=4)

        res = self.resolver.resolve_bump(hero, target)
        self.assertTrue(res["valid_hit"])
        self.assertTrue(res["is_frontal"])
        self.assertAlmostEqual(res["angle_cos"], math.cos(math.radians(45)), places=4)

    def test_angle_resolution_90_deg_flank(self):
        """90 deg (Flank strike): Unilateral strike, cos(90) = 0.0 < 0.7071, zero damage to hero"""
        target = MockCombatEntity(Vector3(0, 0, 0), Vector2(0, 1), atk=8, def_val=2)
        hero = MockCombatEntity(Vector3(2, 0, 0), Vector2(-1, 0), atk=12, def_val=4)

        res = self.resolver.resolve_bump(hero, target)
        self.assertTrue(res["valid_hit"])
        self.assertFalse(res["is_frontal"], "90 deg flank must be unilateral advantage")
        self.assertAlmostEqual(res["angle_cos"], 0.0, places=4)
        self.assertEqual(res["damage_to_attacker"], 0, "Hero must take 0 damage on flank strike")
        self.assertGreater(res["damage_to_defender"], 0)
        self.assertGreater(res["knockback_defender_mag"], res["knockback_attacker_mag"])

    def test_angle_resolution_180_deg_rear(self):
        """180 deg (Backstab/rear): Unilateral strike, cos(180) = -1.0 < 0.7071, zero damage to hero"""
        target = MockCombatEntity(Vector3(0, 0, 0), Vector2(0, 1), atk=8, def_val=2)
        hero = MockCombatEntity(Vector3(0, 0, -2), Vector2(0, 1), atk=12, def_val=4)

        res = self.resolver.resolve_bump(hero, target)
        self.assertTrue(res["valid_hit"])
        self.assertFalse(res["is_frontal"])
        self.assertAlmostEqual(res["angle_cos"], -1.0, places=4)
        self.assertEqual(res["damage_to_attacker"], 0, "Hero takes zero damage on rear attack")
        self.assertGreater(res["damage_to_defender"], 0)

    def test_damage_formula_and_crit(self):
        """Validates damage formula: max(1, (Atk*SkillMult - Def*0.5) * CritMult)"""
        # Normal hit: Atk 10, Def 4 -> 10 - 2 = 8
        dmg_normal = BumpMathPy.calculate_damage(10, 4, 1.0, False)
        self.assertEqual(dmg_normal, 8)

        # Crit hit: 8 * 1.5 = 12
        dmg_crit = BumpMathPy.calculate_damage(10, 4, 1.0, True, 1.5)
        self.assertEqual(dmg_crit, 12)

        # Over-defense (Def 100 vs Atk 5): Raw = 5 - 50 = -45 -> Minimum 1 damage invariant
        dmg_min = BumpMathPy.calculate_damage(5, 100, 1.0, False)
        self.assertEqual(dmg_min, 1)

    def test_cooldown_and_no_iframe_separation(self):
        """Validates No-iframe single-hit invariant: repeated contacts during cooldown cause bounce, not damage"""
        target = MockCombatEntity(Vector3(0, 0, 0), Vector2(0, 1), atk=8, def_val=2)
        hero = MockCombatEntity(Vector3(0, 0, -2), Vector2(0, 1), atk=12, def_val=4)

        # 1st Hit: Successful hit, sets cooldown
        res1 = self.resolver.resolve_bump(hero, target)
        self.assertTrue(res1["valid_hit"])
        self.assertGreater(res1["damage_to_defender"], 0)
        self.assertAlmostEqual(hero.attack_cooldown, 0.35, places=2)

        # Immediate 2nd contact while cooldown is active: Must be rejected as damage, bounce only!
        res2 = self.resolver.resolve_bump(hero, target)
        self.assertFalse(res2["valid_hit"], "No multi-hit damage while in cooldown")
        self.assertEqual(res2["damage_to_defender"], 0)
        self.assertEqual(res2["damage_to_attacker"], 0)
        self.assertGreater(res2["knockback_attacker_mag"], 0, "Rigid bounce separation remains active")

        # Cooldown expires
        hero.attack_cooldown = 0.0

        # 3rd contact after cooldown: Valid hit again
        res3 = self.resolver.resolve_bump(hero, target)
        self.assertTrue(res3["valid_hit"])
        self.assertGreater(res3["damage_to_defender"], 0)

    def test_ocp_interceptor_extensibility(self):
        """Zero Core Switch: Interceptors can modify damage/decision without changing resolver core"""
        target = MockCombatEntity(Vector3(0, 0, 0), Vector2(0, 1), atk=8, def_val=2)
        hero = MockCombatEntity(Vector3(0, 0, 2), Vector2(0, -1), atk=12, def_val=4)

        # Shield block interceptor: turns frontal clash damage to 0
        def shield_parry_interceptor(ctx):
            if ctx["is_frontal"]:
                ctx["damage_to_attacker"] = 0  # Perfect parry

        self.resolver.register_interceptor(shield_parry_interceptor)
        res = self.resolver.resolve_bump(hero, target)
        self.assertTrue(res["valid_hit"])
        self.assertTrue(res["is_frontal"])
        self.assertEqual(res["damage_to_attacker"], 0, "Interceptor successfully modified frontal damage to 0")


if __name__ == "__main__":
    unittest.main()
