class_name SessionManager
extends Node

## Layer 4 Session Loop: Session State, Key Economy, and Zero-Risk Pause Management
## Enforces Rule 5: 100% Frozen Simulation during equipment comparison

signal key_collected()
signal stairs_unlocked()
signal floor_cleared(floor_num: int)
signal equipment_inspected(new_item: EquipmentItem, current_equipped: EquipmentItem)
signal pause_state_changed(is_paused: bool)

@export var current_floor: int = 1
@export var has_key: bool = false
@export var is_paused: bool = false

var dungeon_layout: DungeonGenerator.DungeonLayout = null
var equipped_slots: Dictionary = {
	EquipmentItem.SlotType.WEAPON: null,
	EquipmentItem.SlotType.ARMOR: null,
	EquipmentItem.SlotType.HELMET: null,
	EquipmentItem.SlotType.BOOTS: null,
	EquipmentItem.SlotType.RING: null,
	EquipmentItem.SlotType.SHIELD: null
}

func _ready() -> void:
	# Add to group for global access if needed
	add_to_group("session_manager")

## Starts a new floor session
func start_floor(floor_num: int, seed_val: int = 0) -> void:
	current_floor = floor_num
	has_key = false
	is_paused = false
	dungeon_layout = DungeonGenerator.generate_dungeon(seed_val, 6)

## Collects the single key on this floor (1/1 Single Key Economy)
func collect_key() -> void:
	if not has_key:
		has_key = true
		key_collected.emit()
		stairs_unlocked.emit()

## Attempts to exit stairs
func attempt_exit() -> bool:
	if has_key:
		floor_cleared.emit(current_floor)
		return true
	return false

## Rule 5: Zero-Risk Pause Invariant
## Freezes all physics, monster AI, and timers while UI is open
func set_zero_risk_pause(paused: bool) -> void:
	is_paused = paused
	get_tree().paused = paused
	pause_state_changed.emit(paused)

## Equips an item and returns the previously equipped item (or null)
func equip_item(new_item: EquipmentItem) -> EquipmentItem:
	if new_item == null:
		return null
	var prev_item: EquipmentItem = equipped_slots.get(new_item.slot, null)
	equipped_slots[new_item.slot] = new_item
	return prev_item

func get_equipped_item(slot: EquipmentItem.SlotType) -> EquipmentItem:
	return equipped_slots.get(slot, null)

func calculate_stat_bonus() -> Dictionary:
	var total_atk: float = 0.0
	var total_def: float = 0.0
	var total_hp: int = 0
	var total_atk_spd: float = 0.0

	for item in equipped_slots.values():
		if item is EquipmentItem:
			total_atk += item.bonus_atk
			total_def += item.bonus_def
			total_hp += item.bonus_hp
			total_atk_spd += item.bonus_atk_spd

	return {
		"bonus_atk": total_atk,
		"bonus_def": total_def,
		"bonus_hp": total_hp,
		"bonus_atk_spd": total_atk_spd
	}
