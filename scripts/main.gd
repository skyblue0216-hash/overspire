extends Node3D

## Overspire Layer 2: Micro Bump Test Arena Controller
## 카메라 추적 및 조이스틱 연동, 실시간 범프 전투 정보 HUD 표기

@onready var hero: Hero = $Hero
@onready var dummy: TrainingDummy = $TrainingDummy
@onready var camera: Camera3D = $Camera3D
@onready var joystick: VirtualJoystick = $UI/VirtualJoystick
@onready var hud_label: Label = $UI/HUD/InfoLabel

# 카메라 오프셋 (Orthogonal 탑다운 틸트)
const CAMERA_OFFSET := Vector3(0.0, 8.5, 5.2)
const CAMERA_LERP_SPEED := 6.5

var last_bump_info: String = "더미 인형(목표)을 향해 들이받아 보세요!"

func _ready() -> void:
	if joystick != null and hero != null:
		joystick.input_vector_changed.connect(func(v: Vector2): hero.external_input = v)
	
	if hero != null:
		hero.bumped.connect(_on_hero_bumped)

	# 카메라 초기 위치
	if camera != null and hero != null:
		camera.global_position = hero.global_position + CAMERA_OFFSET

func _on_hero_bumped(res: BumpResolver.BumpResult) -> void:
	if res.is_frontal:
		last_bump_info = "💥 [정면 충돌(상호 피해)] 영웅 -%d HP | 더미 -%d HP" % [res.damage_to_attacker, res.damage_to_defender]
	else:
		last_bump_info = "⚡ [측/후면 일방 타격(유리)] 영웅 0 HP (방어) | 더미 -%d HP" % [res.damage_to_defender]

func _process(delta: float) -> void:
	# 1. 직교 카메라 부드러운 플레이어 추적
	if camera != null and hero != null:
		var target_pos := hero.global_position + CAMERA_OFFSET
		camera.global_position = camera.global_position.lerp(target_pos, CAMERA_LERP_SPEED * delta)

	# 2. 실시간 조작 정보 HUD 갱신
	if hud_label != null and hero != null:
		var cd_str: String = "준비완료" if hero.attack_cooldown <= 0.0 else "쿨다운: %.2fs" % hero.attack_cooldown
		var dummy_hp: int = dummy.stat_hp if dummy != null else 0
		hud_label.text = "영웅 HP: %d/%d | 더미 HP: %d/100 | %s\n%s" % [
			hero.stat_hp,
			hero.stat_max_hp,
			dummy_hp,
			cd_str,
			last_bump_info
		]
