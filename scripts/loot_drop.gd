class_name LootDrop
extends Area3D

## Layer 4 Session Loop: Floor Loot Drop
## Triggers Zero-Risk Pause (Rule 5) upon player interaction/touch

@export var item_data: EquipmentItem = null
@export var float_speed: float = 2.5
@export var rotation_speed: float = 1.8

var _time: float = 0.0
var _base_y: float = 0.5
var _is_player_inside: bool = false
var _cooldown: float = 0.0

@onready var visual_pivot: Node3D = $VisualPivot

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	_base_y = position.y

func _process(delta: float) -> void:
	if _cooldown > 0.0:
		_cooldown -= delta

	# Floating & rotation animation
	_time += delta
	if visual_pivot:
		visual_pivot.position.y = sin(_time * float_speed) * 0.12
		visual_pivot.rotate_y(rotation_speed * delta)

func set_item(item: EquipmentItem) -> void:
	item_data = item

func reset_cooldown(cd: float = 1.2) -> void:
	_cooldown = cd

func _on_body_entered(body: Node3D) -> void:
	if body.is_in_group("player") and item_data != null and not _is_player_inside and _cooldown <= 0.0:
		_is_player_inside = true
		_cooldown = 1.2
		var session = get_tree().get_first_node_in_group("session_manager")
		if session and session is SessionManager:
			var current_equipped = session.get_equipped_item(item_data.slot)
			# Rule 5: Zero-Risk Pause immediately triggered
			session.set_zero_risk_pause(true)
			session.equipment_inspected.emit(item_data, current_equipped)

func _on_body_exited(body: Node3D) -> void:
	if body.is_in_group("player"):
		_is_player_inside = false
