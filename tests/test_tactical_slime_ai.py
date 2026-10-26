#!/usr/bin/env python3
"""
Overspire - Layer 3: Tactical Loop Independent Test Harness
Validates Slime AI Finite State Machine, Turn Rate (omega = 120 deg/s) flanking window,
Telegraph direction lock-in, and Recovery counter window invariants.
"""

import math
import unittest


class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def length(self):
        return math.hypot(self.x, self.y)

    def normalized(self):
        l = self.length()
        if l < 1e-6:
            return Vector2(0, 0)
        return Vector2(self.x / l, self.y / l)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)


class SlimeAIState:
    IDLE = 0
    CHASE = 1
    TELEGRAPH = 2
    DASH = 3
    RECOVERY = 4
    DEAD = 5


class SlimeBrainPy:
    def __init__(self, pos=Vector2(0, 0), facing_deg=0.0):
        self.pos = pos
        # facing_rad: 0 is South (+Y in 2D), pi/2 is East (+X)
        self.facing_rad = math.radians(facing_deg)
        self.turn_speed_deg = 120.0  # omega = 120 deg/s
        self.aggro_radius = 6.5
        self.attack_range = 2.4
        self.chase_speed = 2.2
        self.dash_speed = 7.5

        self.telegraph_duration = 0.5
        self.dash_duration = 0.35
        self.recovery_duration = 0.4

        self.state = SlimeAIState.IDLE
        self.timer = 0.0
        self.locked_dash_dir = Vector2(0, 1)
        self.hp = 30
        self.max_hp = 30

    def get_facing_vec(self):
        # angle to (sin(a), cos(a)) where 0 is (0, 1)
        return Vector2(math.sin(self.facing_rad), math.cos(self.facing_rad)).normalized()

    def update(self, player_pos: Vector2, dt: float):
        if self.state == SlimeAIState.DEAD:
            return

        self.timer += dt
        diff = player_pos - self.pos
        dist = diff.length()
        to_player_dir = diff.normalized() if dist > 1e-6 else Vector2(0, 1)

        if self.state == SlimeAIState.IDLE:
            if dist <= self.aggro_radius:
                self.state = SlimeAIState.CHASE
                self.timer = 0.0

        elif self.state == SlimeAIState.CHASE:
            # Turn Rate Constraint: Rotate towards player at max 120 deg/s
            target_angle = math.atan2(to_player_dir.x, to_player_dir.y)
            # Angular diff with wrap-around
            diff_angle = (target_angle - self.facing_rad + math.pi) % (2 * math.pi) - math.pi
            max_turn = math.radians(self.turn_speed_deg) * dt

            if abs(diff_angle) <= max_turn:
                self.facing_rad = target_angle
            else:
                self.facing_rad += math.copysign(max_turn, diff_angle)

            facing_vec = self.get_facing_vec()
            self.pos = self.pos + facing_vec * (self.chase_speed * dt)

            if dist <= self.attack_range:
                self.state = SlimeAIState.TELEGRAPH
                self.timer = 0.0
                self.locked_dash_dir = facing_vec

        elif self.state == SlimeAIState.TELEGRAPH:
            # Direction is frozen/locked!
            if self.timer >= self.telegraph_duration:
                self.state = SlimeAIState.DASH
                self.timer = 0.0

        elif self.state == SlimeAIState.DASH:
            self.pos = self.pos + self.locked_dash_dir * (self.dash_speed * dt)
            if self.timer >= self.dash_duration:
                self.state = SlimeAIState.RECOVERY
                self.timer = 0.0

        elif self.state == SlimeAIState.RECOVERY:
            # Stationary and completely vulnerable!
            if self.timer >= self.recovery_duration:
                self.state = SlimeAIState.CHASE
                self.timer = 0.0


class TestTacticalSlimeAI(unittest.TestCase):
    def test_turn_rate_omega_limit_and_flanking_window(self):
        """Validates omega = 120 deg/s turn rate constraint: Slime cannot instantaneously track player"""
        # Slime at (0, 0) facing South (angle = 0 deg, vector = (0, 1))
        slime = SlimeBrainPy(pos=Vector2(0, 0), facing_deg=0.0)
        slime.state = SlimeAIState.CHASE

        # Player is placed directly East (+X, angle = 90 deg) at distance 4.0m
        player_pos = Vector2(4.0, 0.0)

        # 0.25 seconds update: Slime can turn at most 120 * 0.25 = 30 degrees
        slime.update(player_pos, dt=0.25)
        current_deg = math.degrees(slime.facing_rad)
        self.assertAlmostEqual(current_deg, 30.0, delta=0.5,
                               msg=f"Slime turned {current_deg}°, should be strictly capped at 30° in 0.25s")

        # Flanking window invariant: During first 0.375s (45 deg / 120 deg/s),
        # slime cannot turn 45 deg, so player at 90 deg is strictly in unilateral flank zone (cos < 0.7071)!
        facing = slime.get_facing_vec()
        contact = (player_pos - slime.pos).normalized()
        cos_theta = facing.dot(contact)
        self.assertLess(cos_theta, 0.7071,
                        f"At t=0.25s, cos_theta={cos_theta:.3f} must be < 0.7071 (Flanking Window active!)")

        # By 0.50 seconds (total 0.5s from start): turned 60 degrees (strictly capped)
        slime.update(player_pos, dt=0.25)
        current_deg = math.degrees(slime.facing_rad)
        self.assertAlmostEqual(current_deg, 60.0, delta=0.5,
                               msg=f"Slime turned {current_deg}°, should be strictly capped at 60° in 0.5s")

    def test_fsm_telegraph_dash_recovery_cycle(self):
        """Validates FSM transitions: Aggro -> Chase -> Telegraph (0.5s) -> Dash (0.35s) -> Recovery (0.4s)"""
        slime = SlimeBrainPy(pos=Vector2(0, 0), facing_deg=0.0)
        self.assertEqual(slime.state, SlimeAIState.IDLE)

        # Player at 5.0m (within aggro radius 6.5m)
        slime.update(Vector2(0, 5.0), dt=0.05)
        self.assertEqual(slime.state, SlimeAIState.CHASE, "Enters CHASE within aggro radius")

        # Advance player into attack range (2.0m <= 2.4m)
        slime.update(Vector2(0, 2.0), dt=0.05)
        self.assertEqual(slime.state, SlimeAIState.TELEGRAPH, "Enters TELEGRAPH when reaching attack range")

        # 0.3s into Telegraph: Still in Telegraph
        slime.update(Vector2(0, 2.0), dt=0.3)
        self.assertEqual(slime.state, SlimeAIState.TELEGRAPH)

        # 0.25s more (total 0.55s > 0.5s): Must transition to DASH
        slime.update(Vector2(0, 2.0), dt=0.25)
        self.assertEqual(slime.state, SlimeAIState.DASH, "Transitions to DASH after 0.5s telegraph")

        # 0.36s into Dash (> 0.35s): Must transition to RECOVERY
        slime.update(Vector2(0, 2.0), dt=0.36)
        self.assertEqual(slime.state, SlimeAIState.RECOVERY, "Transitions to RECOVERY after 0.35s dash")

        # 0.42s into Recovery (> 0.4s): Must return to CHASE
        slime.update(Vector2(0, 2.0), dt=0.42)
        self.assertEqual(slime.state, SlimeAIState.CHASE, "Re-enters CHASE after 0.4s recovery")

    def test_telegraph_direction_lockin_and_evasion(self):
        """Validates that Telegraph locks attack vector, allowing player sidestep dodge"""
        # Slime at (0, 0) starts telegraph facing South (0, 1)
        slime = SlimeBrainPy(pos=Vector2(0, 0), facing_deg=0.0)
        slime.state = SlimeAIState.TELEGRAPH
        slime.locked_dash_dir = Vector2(0, 1)

        # Player dodges sideways to (+3.0, 1.0)
        player_evaded_pos = Vector2(3.0, 1.0)

        # Slime finishes telegraph and dashes
        slime.update(player_evaded_pos, dt=0.55)
        self.assertEqual(slime.state, SlimeAIState.DASH)

        # Slime continues along locked South direction (0, 1), not following player!
        self.assertAlmostEqual(slime.locked_dash_dir.x, 0.0, places=3)
        self.assertAlmostEqual(slime.locked_dash_dir.y, 1.0, places=3)

    def test_recovery_counter_window(self):
        """Validates Recovery state: 0.4s stationary window where flank bump yields 100% unilateral advantage"""
        slime = SlimeBrainPy(pos=Vector2(0, 2.5), facing_deg=0.0)
        slime.state = SlimeAIState.RECOVERY
        slime.locked_dash_dir = Vector2(0, 1)  # Facing South

        # Player approaches from rear/side (0, 1.0) -> attacks slime at (0, 2.5)
        # Contact vector from Slime to Hero: (0, 1.0) - (0, 2.5) = (0, -1.5) -> normalized (0, -1)
        contact_from_slime_to_hero = Vector2(0, -1)
        slime_facing = slime.locked_dash_dir  # (0, 1)

        # Angle cos = facing . contact = 0*0 + 1*(-1) = -1.0 (Rear Backstab)
        cos_theta = slime_facing.dot(contact_from_slime_to_hero)
        self.assertAlmostEqual(cos_theta, -1.0, places=3)
        self.assertLess(cos_theta, 0.7071, "During recovery, rear attack produces unilateral counter strike")


if __name__ == "__main__":
    unittest.main()
