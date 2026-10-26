class_name Slime
extends CharacterBody3D

## Layer 3 Tactical Loop: Poring-style Slime Entity Controller
## Manages Ragnarok Poring-style squishy hop kinematics, telegraph, and bump handling

signal slime_died(slime: Slime)

@export var stat_hp: int = 30
@export var stat_max_hp: int = 30
@export var stat_atk: float = 10.0
@export var stat_def: float = 1.0

var brain: SlimeBrain = SlimeBrain.new()
var target_hero: Node3D = null

var knockback_velocity: Vector3 = Vector3.ZERO
var knockback_friction: float = 26.0

var flash_timer: float = 0.0
var _anim_time: float = 0.0

@onready var visual_pivot: Node3D = $VisualPivot
@onready var body_mesh: MeshInstance3D = $VisualPivot/BodyMesh
@onready var telegraph_indicator: MeshInstance3D = $VisualPivot/TelegraphIndicator

func _ready() -> void:
	if telegraph_indicator:
		telegraph_indicator.visible = false

func set_target(hero: Node3D) -> void:
	target_hero = hero

func get_facing_direction_2d() -> Vector2:
	if brain != null:
		return Vector2(sin(brain.current_facing_angle), cos(brain.current_facing_angle)).normalized()
	return Vector2.DOWN

func _physics_process(delta: float) -> void:
	if stat_hp <= 0:
		return

	_anim_time += delta

	# 1. AI Update
	var cmd := brain.update_ai(self, target_hero, delta)

	# 2. Knockback Damping
	if knockback_velocity.length_squared() > 0.001:
		knockback_velocity = knockback_velocity.move_toward(Vector3.ZERO, knockback_friction * delta)

	# 3. Apply Velocity
	velocity = cmd.move_velocity + knockback_velocity
	velocity.y = 0.0
	move_and_slide()
	global_position.y = 0.0

	# 4. Update Visual Facing & Poring Squash & Stretch
	_update_visuals(cmd, delta)

	# 5. Flash Timer
	if flash_timer > 0.0:
		flash_timer -= delta
		if flash_timer <= 0.0 and body_mesh:
			body_mesh.material_override = null

func _update_visuals(cmd: ArchetypeBrain.AICommand, delta: float) -> void:
	if visual_pivot == null:
		return

	# Yaw rotation
	var facing_angle := atan2(cmd.facing_direction.x, cmd.facing_direction.y)
	visual_pivot.rotation.y = lerp_angle(visual_pivot.rotation.y, facing_angle, 16.0 * delta)

	# Poring State-driven Squash & Stretch
	match cmd.state:
		ArchetypeBrain.AIState.IDLE:
			# Plump mochi breathing
			var breath := sin(_anim_time * 3.5) * 0.06
			visual_pivot.scale = Vector3(1.0 + breath, 1.0 - breath * 1.6, 1.0 + breath)
			visual_pivot.position.y = 0.0

		ArchetypeBrain.AIState.CHASE:
			if telegraph_indicator:
				telegraph_indicator.visible = false
			# Ragnarok Poring signature "Boing! Boing!" hop
			var hop := abs(sin(_anim_time * 7.5))
			visual_pivot.position.y = hop * 0.28
			# Stretch tall at peak, squash wide on ground impact
			visual_pivot.scale = Vector3(1.12 - hop * 0.22, 0.88 + hop * 0.38, 1.12 - hop * 0.22)

		ArchetypeBrain.AIState.TELEGRAPH:
			# Puffs up like a cute pink balloon before launching
			var vibrate := sin(_anim_time * 36.0) * 0.05
			visual_pivot.position.y = 0.0
			visual_pivot.scale = Vector3(1.30 + vibrate, 0.65, 1.30 + vibrate)
			if telegraph_indicator:
				telegraph_indicator.visible = true
				telegraph_indicator.scale.z = lerpf(0.2, 1.0, cmd.telegraph_ratio)

		ArchetypeBrain.AIState.DASH:
			if telegraph_indicator:
				telegraph_indicator.visible = false
			# Aerodynamic horizontal torpedo mochi stretch
			visual_pivot.scale = Vector3(0.78, 1.32, 0.78)
			visual_pivot.position.y = 0.10

		ArchetypeBrain.AIState.RECOVERY:
			if telegraph_indicator:
				telegraph_indicator.visible = false
			# Completely flattened delicious pink mochi puddle on floor
			visual_pivot.position.y = 0.0
			visual_pivot.scale = Vector3(1.50, 0.36, 1.50)

func apply_bump_impact(damage: int, knockback: Vector3, is_frontal: bool) -> void:
	stat_hp = maxi(0, stat_hp - damage)
	knockback_velocity = knockback

	# Flash feedback
	flash_timer = 0.10
	if body_mesh:
		var flash_mat := StandardMaterial3D.new()
		flash_mat.albedo_color = Color(1.0, 0.9, 0.3) if not is_frontal else Color(1.0, 0.3, 0.3)
		flash_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		body_mesh.material_override = flash_mat

	if stat_hp <= 0:
		die()

func die() -> void:
	stat_hp = 0
	brain.current_state = ArchetypeBrain.AIState.DEAD
	slime_died.emit(self)
	queue_free()
