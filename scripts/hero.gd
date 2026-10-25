extends CharacterBody3D
class_name Hero

## Overspire Layer 1: Hero Locomotion Controller
## 8방향 이동, 가속/감속, 시선 회전(Facing Direction), 12 FPS 스텝 애니메이션 및 Y=0 평면 구속

signal moved(position: Vector3, facing: Vector2)

@export var max_speed: float = 5.2
@export var acceleration: float = 42.0
@export var friction: float = 48.0
@export var rotation_speed: float = 18.0

# 외부(가상 조이스틱) 입력 벡터 (-1.0 ~ 1.0)
var external_input: Vector2 = Vector2.ZERO

# 현재 시선 단위 벡터 (XZ 수평면 2D 투영: x=X, y=Z)
# 기본값은 남쪽(South: Z+, 화면 아래쪽)
var facing_direction: Vector2 = Vector2(0, 1)

@onready var visual_pivot: Node3D = $VisualPivot

# 스텝 애니메이션용 변수 (12 FPS 리듬감)
var _anim_time: float = 0.0
var _step_timer: float = 0.0
const STEP_RATE: float = 1.0 / 12.0 # 12 FPS

func _ready() -> void:
    # Y축 수평 평면 고정
    position.y = 0.0
    _update_visual_rotation(0.0)

func _physics_process(delta: float) -> void:
    # 1. 입력 벡터 수집 (키보드 WASD + 가상 조이스틱)
    var input_dir := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    if external_input.length_squared() > 0.01:
        input_dir = external_input

    # 2. XZ 수평 평면 3D 방향 변환 (Y축은 0)
    var target_dir := Vector3(input_dir.x, 0.0, input_dir.y)
    if target_dir.length_squared() > 1.0:
        target_dir = target_dir.normalized()

    # 3. 가속 및 감속 (Responsive Top-Down Movement)
    if target_dir.length_squared() > 0.001:
        # 가속
        velocity.x = move_toward(velocity.x, target_dir.x * max_speed, acceleration * delta)
        velocity.z = move_toward(velocity.z, target_dir.z * max_speed, acceleration * delta)
        
        # 시선 벡터 갱신 및 회전
        facing_direction = Vector2(target_dir.x, target_dir.z).normalized()
        _update_visual_rotation(delta)
        
        # 4. 스텝 워킹 애니메이션 (12 FPS Bobbing & Tilt)
        _step_timer += delta
        if _step_timer >= STEP_RATE:
            _step_timer = 0.0
            _anim_time += STEP_RATE * 8.0
            _apply_stepped_walk_motion()
    else:
        # 감속 (즉각적인 마찰력)
        velocity.x = move_toward(velocity.x, 0.0, friction * delta)
        velocity.z = move_toward(velocity.z, 0.0, friction * delta)
        
        # 정지 시 점진적 원복
        _reset_walk_motion(delta)

    # 5. Y축 절대 평면 구속
    velocity.y = 0.0
    
    # 6. 이동 및 충돌 처리
    move_and_slide()
    position.y = 0.0 # 미세 오차 방지

    moved.emit(global_position, facing_direction)

func _update_visual_rotation(delta: float) -> void:
    if visual_pivot == null:
        return
    # facing_direction은 (x, z) 평면
    # 회전각: atan2(x, z)
    var target_angle := atan2(facing_direction.x, facing_direction.y)
    if delta > 0.0:
        visual_pivot.rotation.y = lerp_angle(visual_pivot.rotation.y, target_angle, rotation_speed * delta)
    else:
        visual_pivot.rotation.y = target_angle

## 8방향 스프라이트 텍스처 키 반환 (south, south-east, east, north-east, north, north-west, west, south-west)
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
    # 상하 밥빙(Bobbing) & 좌우 뒤뚱거림(Wobble)
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
