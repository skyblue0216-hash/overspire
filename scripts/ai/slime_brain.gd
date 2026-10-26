class_name SlimeBrain
extends ArchetypeBrain

## Layer 3 Tactical Loop: Slime Archetype Brain
## Enforces turn rate limit (120 deg/s), telegraph-dash-recovery cycle, and orbital flanking window

@export var aggro_radius: float = 6.5
@export var attack_range: float = 2.4
@export var chase_speed: float = 2.2
@export var turn_speed_deg: float = 120.0 # omega = 120 deg/s

@export var telegraph_duration: float = 0.5
@export var dash_speed: float = 7.5
@export var dash_duration: float = 0.35
@export var recovery_duration: float = 0.4

var current_state: AIState = AIState.IDLE
var state_timer: float = 0.0

# Facing angle on XZ plane in radians (0 = Vector2(0, 1) South)
var current_facing_angle: float = 0.0
var locked_dash_dir: Vector3 = Vector3.ZERO

func get_state() -> AIState:
	return current_state

func update_ai(entity: Node3D, target: Node3D, delta: float) -> AICommand:
	var cmd := AICommand.new()
	if current_state == AIState.DEAD or target == null:
		cmd.state = current_state
		return cmd

	state_timer += delta

	var entity_pos := Vector2(entity.global_position.x, entity.global_position.z)
	var target_pos := Vector2(target.global_position.x, target.global_position.z)
	var diff := target_pos - entity_pos
	var dist := diff.length()
	var to_target_dir := diff.normalized() if dist > 0.001 else Vector2.DOWN

	match current_state:
		AIState.IDLE:
			cmd.move_velocity = Vector3.ZERO
			if dist <= aggro_radius:
				_transition_to(AIState.CHASE)

		AIState.CHASE:
			# 1. Turn Rate Constraint: Rotate towards player at max 120 deg/s
			var target_angle := atan2(to_target_dir.x, to_target_dir.y)
			var max_turn_rad := deg_to_rad(turn_speed_deg) * delta
			current_facing_angle = rotate_toward(current_facing_angle, target_angle, max_turn_rad)

			# Facing 2D vector
			var facing_vec := Vector2(sin(current_facing_angle), cos(current_facing_angle)).normalized()
			cmd.facing_direction = facing_vec

			# Move forward in facing direction
			cmd.move_velocity = Vector3(facing_vec.x * chase_speed, 0.0, facing_vec.y * chase_speed)

			# Check Attack Range
			if dist <= attack_range:
				_transition_to(AIState.TELEGRAPH)
			elif dist > aggro_radius * 1.5:
				_transition_to(AIState.IDLE)

		AIState.TELEGRAPH:
			# 2. Lock-in: Freeze rotation and lock dash direction
			var facing_vec := Vector2(sin(current_facing_angle), cos(current_facing_angle)).normalized()
			cmd.facing_direction = facing_vec
			cmd.move_velocity = Vector3.ZERO
			cmd.telegraph_ratio = clampf(state_timer / telegraph_duration, 0.0, 1.0)

			if state_timer >= telegraph_duration:
				locked_dash_dir = Vector3(facing_vec.x, 0.0, facing_vec.y)
				_transition_to(AIState.DASH)

		AIState.DASH:
			# 3. High-Speed Straight Dash along locked direction
			cmd.move_velocity = locked_dash_dir * dash_speed
			cmd.facing_direction = Vector2(locked_dash_dir.x, locked_dash_dir.z).normalized()

			if state_timer >= dash_duration:
				_transition_to(AIState.RECOVERY)

		AIState.RECOVERY:
			# 4. Vulnerable Counter Window: Completely motionless
			cmd.move_velocity = Vector3.ZERO
			cmd.facing_direction = Vector2(locked_dash_dir.x, locked_dash_dir.z).normalized()
			cmd.is_vulnerable = true

			if state_timer >= recovery_duration:
				_transition_to(AIState.CHASE)

	cmd.state = current_state
	return cmd

func _transition_to(new_state: AIState) -> void:
	current_state = new_state
	state_timer = 0.0
