extends Node3D

## Overspire Layer 1 Test Arena Controller
## 카메라 추적 및 조이스틱 연동, 실시간 조작 정보 HUD 표기

@onready var hero: Hero = $Hero
@onready var camera: Camera3D = $Camera3D
@onready var joystick: VirtualJoystick = $UI/VirtualJoystick
@onready var hud_label: Label = $UI/HUD/InfoLabel

# 카메라 오프셋 (Orthogonal 탑다운 틸트)
const CAMERA_OFFSET := Vector3(0.0, 8.5, 5.2)
const CAMERA_LERP_SPEED := 6.5

func _ready() -> void:
    if joystick != null and hero != null:
        joystick.input_vector_changed.connect(func(v: Vector2): hero.external_input = v)
    
    # 카메라 초기 위치
    if camera != null and hero != null:
        camera.global_position = hero.global_position + CAMERA_OFFSET

func _process(delta: float) -> void:
    # 1. 직교 카메라 부드러운 플레이어 추적
    if camera != null and hero != null:
        var target_pos := hero.global_position + CAMERA_OFFSET
        camera.global_position = camera.global_position.lerp(target_pos, CAMERA_LERP_SPEED * delta)

    # 2. 실시간 조작 정보 HUD 갱신
    if hud_label != null and hero != null:
        var angle_deg := rad_to_deg(atan2(hero.facing_direction.x, hero.facing_direction.y))
        hud_label.text = "위치: (%.1f, %.1f) | 속도: %.1f m/s\n시선 각도: %.0f° | 8방향 이동 정상" % [
            hero.global_position.x,
            hero.global_position.z,
            hero.velocity.length(),
            angle_deg
        ]
