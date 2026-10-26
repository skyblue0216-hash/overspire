extends CharacterBody3D
class_name Hero

## Overspire Layer 1 & 2: Hero Locomotion & Micro Bump Combat Controller
## 8방향 이동, 넉백, 각도별 범프 판정, 쿨다운, 히트스탑, 피격 플래시

signal moved(position: Vector3, facing: Vector2)
signal bumped(result: BumpResolver.BumpResult)

@export var max_speed: float = 5.2
@export var acceleration: float = 42.0
@export var friction: float = 48.0
@export var rotation_speed: float = 18.0

# 전투 스탯 (Layer 2)
@export var stat_hp: int = 100
@export var stat_max_hp: int = 100
@export var stat_atk: float = 12.0
@export var stat_def: float = 4.0
@export var stat_atk_spd_boost: float = 0.0
@export var stat_crit_rate: float = 0.15
@export var stat_crit_mult: float = 1.5

# 전투 런타임 상태
var attack_cooldown: float = 0.0
var hitstop_timer: float = 0.0
var flash_timer: float = 0.0
var knockback_velocity: Vector3 = Vector3.ZERO
var knockback_friction: float = 30.0

# 외부(가상 조이스틱) 입력 벡터 (-1.0 ~ 1.0)
var external_input: Vector2 = Vector2.ZERO

# 현재 시선 단위 벡터 (XZ 수평면 2D 투영: x=X, y=Z)
var facing_direction: Vector2 = Vector2(0, 1)

@onready var visual_pivot: Node3D = $VisualPivot
var _bump_resolver: BumpResolver = BumpResolver.new()

# 스텝 애니메이션용 변수 (12 FPS 리듬감)
var _anim_time: float = 0.0
var _step_timer: float = 0.0
const STEP_RATE: float = 1.0 / 12.0

func _ready() -> void:
	position.y = 0.0
	_update_visual_rotation(0.0)

func get_facing_direction_2d() -> Vector2:
	return facing_direction

func _physics_process(delta: float) -> void:
	# 0. 히트스탑 (Micro-freeze 0.04s) 처리
	if hitstop_timer > 0.0:
		hitstop_timer -= delta
		return

	# 쿨다운 및 피격 플래시 타이머
	if attack_cooldown > 0.0:
		attack_cooldown = maxf(0.0, attack_cooldown - delta)
	if flash_timer > 0.0:
		flash_timer -= delta
		if flash_timer <= 0.0:
			_reset_flash()

	# 1. 입력 벡터 수집
	var input_dir := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if external_input.length_squared() > 0.01:
		input_dir = external_input

	# 2. XZ 수평 평면 방향 변환
	var target_dir := Vector3(input_dir.x, 0.0, input_dir.y)
	if target_dir.length_squared() > 1.0:
		target_dir = target_dir.normalized()

	# 3. 넉백 물리 감쇄
	if knockback_velocity.length_squared() > 0.001:
		knockback_velocity = knockback_velocity.move_toward(Vector3.ZERO, knockback_friction * delta)

	# 4. 가속 및 감속 계산
	if target_dir.length_squared() > 0.001:
		velocity.x = move_toward(velocity.x, target_dir.x * max_speed, acceleration * delta)
		velocity.z = move_toward(velocity.z, target_dir.z * max_speed, acceleration * delta)
		
		facing_direction = Vector2(target_dir.x, target_dir.z).normalized()
		_update_visual_rotation(delta)
		
		# 12 FPS Bobbing
		_step_timer += delta
		if _step_timer >= STEP_RATE:
			_step_timer = 0.0
			_anim_time += STEP_RATE * 8.0
			_apply_stepped_walk_motion()
	else:
		velocity.x = move_toward(velocity.x, 0.0, friction * delta)
		velocity.z = move_toward(velocity.z, 0.0, friction * delta)
		_reset_walk_motion(delta)

	# 넉백 합성 & Y축 고정
	velocity += knockback_velocity
	velocity.y = 0.0
	
	# 5. 이동 및 충돌
	move_and_slide()
	position.y = 0.0

	# 6. 충돌 분석 (Micro Bump Resolution)
	_handle_bump_collisions()

	moved.emit(global_position, facing_direction)

func _handle_bump_collisions() -> void:
	var col_count: int = get_slide_collision_count()
	for i in range(col_count):
		var col: KinematicCollision3D = get_slide_collision(i)
		var collider: Object = col.get_collider()
		if collider and collider is Node3D and (collider.has_method("apply_bump_impact") or "stat_hp" in collider):
			var res: BumpResolver.BumpResult = _bump_resolver.resolve_bump(self, collider as Node3D)
			if res.valid_hit:
				# 유효 타격 발생
				attack_cooldown = BumpMath.calculate_cooldown(0.35, stat_atk_spd_boost)
				hitstop_timer = res.hitstop_duration
				knockback_velocity = res.knockback_attacker
				
				# 영웅 피해 및 피격 플래시
				if res.damage_to_attacker > 0:
					stat_hp = maxi(0, stat_hp - res.damage_to_attacker)
					_trigger_flash(Color(1.0, 0.25, 0.25, 1.0))
				else:
					# 일방 타격 성공 반동 효과
					_trigger_flash(Color(0.25, 1.0, 0.9, 1.0))

				# 상대방에게 충격 전달
				if collider.has_method("apply_bump_impact"):
					collider.apply_bump_impact(res.damage_to_defender, res.knockback_defender, res.is_frontal)

				bumped.emit(res)
			elif res.knockback_attacker.length_squared() > 0.0:
				# 쿨다운 중 단순 탄성 분리 반발력
				knockback_velocity = res.knockback_attacker
			break

func _trigger_flash(_color: Color) -> void:
	flash_timer = 0.06

func _reset_flash() -> void:
	pass

func _update_visual_rotation(delta: float) -> void:
	if visual_pivot == null:
		return
	var target_angle := atan2(facing_direction.x, facing_direction.y)
	if delta > 0.0:
		visual_pivot.rotation.y = lerp_angle(visual_pivot.rotation.y, target_angle, rotation_speed * delta)
	else:
		visual_pivot.rotation.y = target_angle

func get_facing_direction_key() -> String:
	var deg := rad_to_deg(atan2(facing_direction.x, facing_direction.y))
	if deg >= -22.5 and deg < 22.5:
		return "south"
	elif deg >= 22.5 and deg < 67.5:
		return "south-east"
	elif deg >= 67.5 and deg < 112.5:
		return "east"
	elif deg >= 112.5 and deg < 157.5:
		return "north-east"
	elif deg >= 157.5 or deg < -157.5:
		return "north"
	elif deg >= -157.5 and deg < -112.5:
		return "north-west"
	elif deg >= -112.5 and deg < -67.5:
		return "west"
	else:
		return "south-west"

func _apply_stepped_walk_motion() -> void:
	if visual_pivot == null:
		return
	var bob := abs(sin(_anim_time)) * 0.06
	var tilt := sin(_anim_time) * 0.08
	visual_pivot.position.y = bob
	visual_pivot.rotation.z = tilt

func _reset_walk_motion(delta: float) -> void:
	if visual_pivot == null:
		return
	visual_pivot.position.y = move_toward(visual_pivot.position.y, 0.0, delta * 2.0)
	visual_pivot.rotation.z = move_toward(visual_pivot.rotation.z, 0.0, delta * 3.0)
	_anim_time = 0.0
