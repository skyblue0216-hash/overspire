class_name TrainingDummy
extends CharacterBody3D

@export var stat_hp: int = 100
@export var stat_max_hp: int = 100
@export var stat_atk: float = 8.0
@export var stat_def: float = 2.0
@export var facing_direction: Vector2 = Vector2.DOWN # 기본적으로 +Z(화면 아래)를 응시

var knockback_velocity: Vector3 = Vector3.ZERO
var knockback_friction: float = 24.0
var flash_timer: float = 0.0

@onready var visual_pivot: Node3D = $VisualPivot
@onready var dummy_mesh: MeshInstance3D = $VisualPivot/BodyMesh

func _ready() -> void:
	update_facing_visual()

func get_facing_direction_2d() -> Vector2:
	return facing_direction

func update_facing_visual() -> void:
	if visual_pivot:
		# Facing on XZ plane: angle = atan2(x, z)
		var angle: float = atan2(facing_direction.x, facing_direction.y)
		visual_pivot.rotation.y = angle

func _physics_process(delta: float) -> void:
	# Damp knockback
	if knockback_velocity.length_squared() > 0.001:
		velocity = knockback_velocity
		knockback_velocity = knockback_velocity.move_toward(Vector3.ZERO, knockback_friction * delta)
		move_and_slide()
		global_position.y = 0.0
	else:
		velocity = Vector3.ZERO

	# Flash recovery
	if flash_timer > 0.0:
		flash_timer -= delta
		if flash_timer <= 0.0 and dummy_mesh:
			dummy_mesh.material_override = null

func apply_bump_impact(damage: int, knockback: Vector3, is_frontal: bool) -> void:
	stat_hp = maxi(0, stat_hp - damage)
	knockback_velocity = knockback

	# Flash feedback
	flash_timer = 0.08
	if dummy_mesh:
		var flash_mat: StandardMaterial3D = StandardMaterial3D.new()
		flash_mat.albedo_color = Color(1.0, 0.9, 0.2, 1.0) if not is_frontal else Color(1.0, 0.3, 0.3, 1.0)
		flash_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		dummy_mesh.material_override = flash_mat

	# HP recovery for continuous testing
	if stat_hp <= 0:
		stat_hp = stat_max_hp
