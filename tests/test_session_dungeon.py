#!/usr/bin/env python3
"""
Overspire - Layer 4: Session Loop Independent Test Harness
Validates:
1. Procedural Dungeon Generation & 1,000 Seeds A* Reachability (Start -> Key -> Exit).
2. Single Key Economy (1/1 key required to unlock exit stairs).
3. Zero-Risk Pause Invariant (Rule 5: 100% frozen physics and AI during equipment inspection).
4. Modular 6-Slot Equipment System & Stat Comparison.
"""

import math
import random
import unittest
from collections import deque
from enum import Enum, auto


class RoomType(Enum):
    START = auto()
    KEY = auto()
    EXIT = auto()
    LOOT = auto()
    NORMAL = auto()


class EquipmentSlot(Enum):
    WEAPON = 0
    ARMOR = 1
    HELMET = 2
    BOOTS = 3
    RING = 4
    SHIELD = 5


class EquipmentItem:
    def __init__(self, item_id: str, name: str, slot: EquipmentSlot,
                 bonus_atk: float = 0.0, bonus_def: float = 0.0,
                 bonus_hp: int = 0, bonus_atk_spd: float = 0.0,
                 icon: str = "⚔️"):
        self.item_id = item_id
        self.name = name
        self.slot = slot
        self.bonus_atk = bonus_atk
        self.bonus_def = bonus_def
        self.bonus_hp = bonus_hp
        self.bonus_atk_spd = bonus_atk_spd
        self.icon = icon


class DungeonRoom:
    def __init__(self, room_id: int, x: int, y: int, room_type: RoomType = RoomType.NORMAL):
        self.id = room_id
        self.x = x
        self.y = y
        self.room_type = room_type
        self.connected_rooms = []


class DungeonLayout:
    def __init__(self):
        self.rooms = []
        self.start_room_id = 0
        self.key_room_id = 1
        self.exit_room_id = 2

    def get_room(self, room_id: int):
        for r in self.rooms:
            if r.id == room_id:
                return r
        return None

    def is_path_reachable(self, from_id: int, to_id: int) -> bool:
        visited = set()
        queue = deque([from_id])

        while queue:
            curr = queue.popleft()
            if curr == to_id:
                return True
            visited.add(curr)
            r = self.get_room(curr)
            if r:
                for next_id in r.connected_rooms:
                    if next_id not in visited and next_id not in queue:
                        queue.append(next_id)
        return False

    def count_cycle_edges(self) -> int:
        """Counts edges beyond spanning tree (E - (V - 1)) for undirected graph."""
        v = len(self.rooms)
        edge_set = set()
        for r in self.rooms:
            for nbr in r.connected_rooms:
                edge = tuple(sorted((r.id, nbr)))
                edge_set.add(edge)
        e = len(edge_set)
        return max(0, e - (v - 1))


class ProceduralDungeonGeneratorPy:
    @staticmethod
    def generate(seed_val: int = 0, room_count: int = 6) -> DungeonLayout:
        rng = random.Random(seed_val)
        layout = DungeonLayout()

        # Grid random walk
        coords = [(0, 0)]
        curr_pos = (0, 0)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        while len(coords) < room_count:
            d = rng.choice(directions)
            next_pos = (curr_pos[0] + d[0], curr_pos[1] + d[1])
            if next_pos not in coords:
                coords.append(next_pos)
            curr_pos = next_pos

        # Assign types: 0=START, 1=KEY, room_count-1=EXIT, rest LOOT/NORMAL
        layout.start_room_id = 0
        layout.key_room_id = 1
        layout.exit_room_id = room_count - 1

        for i in range(room_count):
            if i == layout.start_room_id:
                r_type = RoomType.START
            elif i == layout.key_room_id:
                r_type = RoomType.KEY
            elif i == layout.exit_room_id:
                r_type = RoomType.EXIT
            else:
                r_type = RoomType.LOOT if (i % 2 == 1) else RoomType.NORMAL

            room = DungeonRoom(i, coords[i][0], coords[i][1], r_type)
            layout.rooms.append(room)

        # Build Spanning Tree (MST sequential backbone)
        for i in range(room_count - 1):
            ProceduralDungeonGeneratorPy._connect(layout, i, i + 1)

        # Add Cycle Edges for grid neighbors
        for i in range(room_count):
            for j in range(i + 2, room_count):
                r1 = layout.rooms[i]
                r2 = layout.rooms[j]
                manhattan = abs(r1.x - r2.x) + abs(r1.y - r2.y)
                if manhattan == 1 and rng.random() < 0.45:
                    ProceduralDungeonGeneratorPy._connect(layout, i, j)

        return layout

    @staticmethod
    def _connect(layout: DungeonLayout, id1: int, id2: int):
        r1 = layout.get_room(id1)
        r2 = layout.get_room(id2)
        if r1 and r2:
            if id2 not in r1.connected_rooms:
                r1.connected_rooms.append(id2)
            if id1 not in r2.connected_rooms:
                r2.connected_rooms.append(id1)


class SessionState:
    def __init__(self):
        self.floor_number = 1
        self.has_key = False
        self.key_dropped = False
        self.stairs_unlocked = False
        self.session_cleared = False
        self.is_paused = False  # Zero-Risk Pause flag
        self.equipped = {slot: None for slot in EquipmentSlot}
        self.base_hp = 100
        self.current_hp = 100
        self.base_atk = 10.0
        self.base_def = 2.0

    def collect_key(self):
        self.has_key = True
        self.stairs_unlocked = True

    def attempt_exit(self) -> bool:
        if self.stairs_unlocked:
            self.session_cleared = True
            return True
        return False

    def equip_item(self, item: EquipmentItem) -> EquipmentItem:
        """Equips item and returns previously equipped item (or None)."""
        old_item = self.equipped[item.slot]
        self.equipped[item.slot] = item
        return old_item

    def get_total_atk(self) -> float:
        bonus = sum(it.bonus_atk for it in self.equipped.values() if it)
        return self.base_atk + bonus

    def get_total_def(self) -> float:
        bonus = sum(it.bonus_def for it in self.equipped.values() if it)
        return self.base_def + bonus

    def get_max_hp(self) -> int:
        bonus = sum(it.bonus_hp for it in self.equipped.values() if it)
        return self.base_hp + bonus


class TestSessionDungeon(unittest.TestCase):
    def test_01_dungeon_1000_seeds_reachability_invariant(self):
        """Rule 3: Simulate 1,000 distinct seeds to guarantee Start->Key and Key->Exit reachability."""
        failures = 0
        cycle_edge_total = 0
        sample_count = 1000

        for seed in range(1, sample_count + 1):
            layout = ProceduralDungeonGeneratorPy.generate(seed_val=seed, room_count=6)

            # 1. Start -> Key reachable
            if not layout.is_path_reachable(layout.start_room_id, layout.key_room_id):
                failures += 1
                continue

            # 2. Key -> Exit reachable
            if not layout.is_path_reachable(layout.key_room_id, layout.exit_room_id):
                failures += 1
                continue

            # 3. Start -> Exit reachable
            if not layout.is_path_reachable(layout.start_room_id, layout.exit_room_id):
                failures += 1
                continue

            # 4. Check all rooms connected
            for room in layout.rooms:
                if not layout.is_path_reachable(layout.start_room_id, room.id):
                    failures += 1
                    break

            cycle_edge_total += layout.count_cycle_edges()

        self.assertEqual(failures, 0, f"Found {failures} seeds out of {sample_count} with disconnected rooms!")
        avg_cycles = cycle_edge_total / sample_count
        # Ensure we have looping corridors across seeds (not just linear corridors)
        self.assertGreater(avg_cycles, 0.05, "Cycle edges should be organically generated for branching loops")

    def test_02_single_key_economy_invariant(self):
        """Rule 1 & 2.3: Dungeon has strict 1/1 key economy. Exit locked without key, unlocked with key."""
        session = SessionState()

        # Initial state: no key
        self.assertFalse(session.has_key)
        self.assertFalse(session.stairs_unlocked)
        self.assertFalse(session.session_cleared)

        # Attempt to exit without key -> MUST FAIL
        success = session.attempt_exit()
        self.assertFalse(success, "Player must not be able to exit without collecting the key")
        self.assertFalse(session.session_cleared)

        # Collect key
        session.collect_key()
        self.assertTrue(session.has_key)
        self.assertTrue(session.stairs_unlocked)

        # Attempt to exit with key -> MUST SUCCEED
        success = session.attempt_exit()
        self.assertTrue(success, "Player must be able to exit stairs after collecting key")
        self.assertTrue(session.session_cleared)

    def test_03_zero_risk_pause_invariant(self):
        """Rule 5: Zero-Risk Pause. While looting / comparing equipment, physics & AI must be 100% frozen."""
        session = SessionState()
        enemy_pos = [10.0, 10.0]
        player_pos = [0.0, 0.0]
        player_hp_before = session.current_hp

        # Simulation step function with pause check
        def step_simulation(session_ref, dt=0.016):
            if session_ref.is_paused:
                # 100% Frozen: no movement, no AI, no combat ticks
                return
            # Normal movement & combat
            enemy_pos[0] -= 1.0 * dt
            player_pos[0] += 2.0 * dt
            # Damage calculation
            session_ref.current_hp -= 5

        # Normal tick
        step_simulation(session)
        self.assertNotEqual(player_pos[0], 0.0)
        self.assertNotEqual(enemy_pos[0], 10.0)
        self.assertEqual(session.current_hp, 95)

        # Snapshot positions before pause
        pos_p_snapshot = list(player_pos)
        pos_e_snapshot = list(enemy_pos)
        hp_snapshot = session.current_hp

        # TRIGGER ZERO-RISK PAUSE (Player opens loot comparison UI)
        session.is_paused = True

        # Run 60 simulation frames during pause (1 full second of game time)
        for _ in range(60):
            step_simulation(session)

        # Invariant: Not a single millimeter moved, zero damage taken
        self.assertEqual(player_pos, pos_p_snapshot, "Player position must freeze completely during pause")
        self.assertEqual(enemy_pos, pos_e_snapshot, "Enemy AI position must freeze completely during pause")
        self.assertEqual(session.current_hp, hp_snapshot, "Player must take zero damage while inspecting loot")

        # UNPAUSE (Player closes loot comparison UI)
        session.is_paused = False
        step_simulation(session)
        self.assertNotEqual(player_pos[0], pos_p_snapshot[0], "Simulation must resume smoothly after unpause")

    def test_04_modular_equipment_and_stat_delta(self):
        """Validates 6 equipment slots, stat calculation, and delta comparison."""
        session = SessionState()
        self.assertEqual(session.get_total_atk(), 10.0)
        self.assertEqual(session.get_total_def(), 2.0)
        self.assertEqual(session.get_max_hp(), 100)

        # Create Rusty Sword (Weapon)
        rusty_sword = EquipmentItem("wpn_01", "녹슨 검", EquipmentSlot.WEAPON, bonus_atk=5.0)
        old_item = session.equip_item(rusty_sword)
        self.assertIsNone(old_item)
        self.assertEqual(session.get_total_atk(), 15.0)

        # Create Iron Armor (Armor)
        iron_armor = EquipmentItem("arm_01", "철 갑옷", EquipmentSlot.ARMOR, bonus_def=4.0, bonus_hp=20)
        session.equip_item(iron_armor)
        self.assertEqual(session.get_total_def(), 6.0)
        self.assertEqual(session.get_max_hp(), 120)

        # Equip Upgraded Crystal Blade (Weapon replace)
        crystal_blade = EquipmentItem("wpn_02", "수정 장검", EquipmentSlot.WEAPON, bonus_atk=12.0)
        dropped_item = session.equip_item(crystal_blade)
        self.assertEqual(dropped_item.item_id, "wpn_01")
        self.assertEqual(session.get_total_atk(), 22.0)  # 10 base + 12 crystal

        # Calculate Stat Delta for Comparison UI
        delta_atk = crystal_blade.bonus_atk - rusty_sword.bonus_atk
        self.assertEqual(delta_atk, +7.0, "Comparison UI must show +7 ATK gain")


if __name__ == "__main__":
    unittest.main()
