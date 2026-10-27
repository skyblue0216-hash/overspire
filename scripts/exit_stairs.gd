class_name ExitStairs
extends Area3D

## Layer 4 Session Loop: Exit Stairs
## Requires 1/1 Key to unlock. Interacts with SessionManager.

signal stairs_entered()

@onready var lock_indicator: Node3D = $LockIndicator
@onready var unlocked_portal: Node3D = $UnlockedPortal
@onready var collision_shape: CollisionShape3D = $CollisionShape3D

var is_unlocked: bool = false

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	update_visuals(false)

func set_unlocked(unlocked: bool) -> void:
	is_unlocked = unlocked
	update_visuals(unlocked)

func update_visuals(unlocked: bool) -> void:
	if lock_indicator:
		lock_indicator.visible = not unlocked
	if unlocked_portal:
		unlocked_portal.visible = unlocked

func _on_body_entered(body: Node3D) -> void:
	if body.is_in_group("player"):
		var session = get_tree().get_first_node_in_group("session_manager")
		if session and session is SessionManager:
			if session.has_key:
				stairs_entered.emit()
				session.attempt_exit()
			else:
				# Show Locked Notification
				print("[ExitStairs] Locked! Find the Key Slime first.")
