class_name ArchetypeBrain
extends RefCounted

## ALEP OCP Archetype Brain Specification
## Defines the contract for monster AI decision making

enum AIState {
	IDLE,
	CHASE,
	TELEGRAPH,
	DASH,
	RECOVERY,
	DEAD
}

class AICommand:
	var state: AIState = AIState.IDLE
	var move_velocity: Vector3 = Vector3.ZERO
	var facing_direction: Vector2 = Vector2.DOWN
	var telegraph_ratio: float = 0.0 # 0.0 to 1.0 during telegraph
	var is_vulnerable: bool = false   # True during recovery
	var custom_data: Dictionary = {}

func update_ai(_entity: Node3D, _target: Node3D, _delta: float) -> AICommand:
	return AICommand.new()

func get_state() -> AIState:
	return AIState.IDLE
