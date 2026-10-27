class_name EquipmentItem
extends RefCounted

## Layer 4 Session Loop: Modular Equipment Data
## Supports 6 slots: WEAPON, ARMOR, HELMET, BOOTS, RING, SHIELD

enum SlotType {
	WEAPON,
	ARMOR,
	HELMET,
	BOOTS,
	RING,
	SHIELD
}

@export var id: String = ""
@export var name: String = ""
@export var slot: SlotType = SlotType.WEAPON
@export var bonus_atk: float = 0.0
@export var bonus_def: float = 0.0
@export var bonus_hp: int = 0
@export var bonus_atk_spd: float = 0.0
@export var bonus_crit: float = 0.0
@export var icon_name: String = "⚔️"

static func create(item_id: String, item_name: String, item_slot: SlotType, atk: float, def_val: float, hp: int, icon: String = "⚔️") -> EquipmentItem:
	var item := EquipmentItem.new()
	item.id = item_id
	item.name = item_name
	item.slot = item_slot
	item.bonus_atk = atk
	item.bonus_def = def_val
	item.bonus_hp = hp
	item.icon_name = icon
	return item
