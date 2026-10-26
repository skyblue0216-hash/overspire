class_name Slime
extends CharacterBody3D

## Layer 3 Tactical Loop: Slime Entity Controller
## Manages FSM state execution, visual squash/stretch, telegraphing, and bump impact handling

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
@onready var top_tip: MeshInstance3D = $VisualPivot/TopTip
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

	# 4. Update Visual Facing & Squash/Stretch
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

	# State-driven Squash & Stretch
	match cmd.state:
		ArchetypeBrain.AIState.IDLE:
			# Cute gentle jelly breathing
			var breath := sin(_anim_time * 3.5) * 0.05
			visual_pivot.scale = Vector3(1.0 + breath, 1.0 - breath * 1.5, 1.0 + breath)
			if top_tip:
				top_tip.rotation.z = sin(_anim_time * 3.5) * 0.12

		ArchetypeBrain.AIState.CHASE:
			if telegraph_indicator:
				telegraph_indicator.visible = false
			# Rhythmic cute slime hopping with jelly jiggle
			var hop := abs(sin(_anim_time * 8.0))
			visual_pivot.position.y = hop * 0.18
			visual_pivot.scale = Vector3(1.08 - hop * 0.15, 0.90 + hop * 0.28, 1.08 - hop * 0.15)
			if top_tip:
				top_tip.rotation.z = sin(_anim_time * 8.0) * 0.25

		ArchetypeBrain.AIState.TELEGRAPH:
			# Cheeks puffed, vibrating angrily but adorably!
			var vibrate := sin(_anim_time * 35.0) * 0.06
			visual_pivot.position.y = 0.0
			visual_pivot.scale = Vector3(1.28 + vibrate, 0.65, 1.28 + vibrate)
			if top_tip:
				top_tip.rotation.z = vibrate * 2.0
			if telegraph_indicator:
				telegraph_indicator.visible = true
				telegraph_indicator.scale.z = lerpf(0.2, 1.0, cmd.telegraph_ratio)

		ArchetypeBrain.AIState.DASH:
			if telegraph_indicator:
				telegraph_indicator.visible = false
			# Aerodynamic forward teardrop stretch
			visual_pivot.scale = Vector3(0.72, 1.35, 0.72)
			visual_pivot.position.y = 0.08
			if top_tip:
				top_tip.rotation.x = -0.35 # Blown backward by high speed

		ArchetypeBrain.AIState.RECOVERY:
			if telegraph_indicator:
				telegraph_indicator.visible = false
			# Dizzy cute flattened puddle
			visual_pivot.position.y = 0.0
			visual_pivot.scale = Vector3(1.42, 0.40, 1.42)
			if top_tip:
				top_tip.rotation.z = sin(_anim_time * 12.0) * 0.35

func apply_bump_impact(damage: int, knockback: Vector3, is_frontal: bool) -> void:
	stat_hp = maxi(0, stat_hp - damage)
	knockback_velocity = knockback

	# Flash feedback
	flash_timer = 0.10
	if body_mesh:
		var flash_mat := StandardMaterial3D.new()
		flash_mat.albedo_color = Color(1.0, 0.3, 0.3) if is_frontal else Color(1.0, 0.95, 0.2)
		flash_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		body_mesh.material_override = flash_mat

	if stat_hp <= 0:
		die()

func die() -> void:
	stat_hp = 0
	brain.current_state = ArchetypeBrain.AIState.DEAD
	slime_died.emit(self)
	queue_free()
