extends Node3D

## Overspire Layer 3: Tactical Loop Test Arena Controller
## 카메라 추적, 조이스틱 연동, 슬라임 AI 팩 전투 및 전술 상태 HUD 표기

@onready var hero: Hero = $Hero
@onready var dummy: TrainingDummy = $TrainingDummy
@onready var slime1: Slime = get_node_or_null("Slime1")
@onready var slime2: Slime = get_node_or_null("Slime2")
@onready var camera: Camera3D = $Camera3D
@onready var joystick: VirtualJoystick = $UI/VirtualJoystick
@onready var hud_label: Label = $UI/HUD/InfoLabel

const CAMERA_OFFSET := Vector3(0.0, 8.5, 5.2)
const CAMERA_LERP_SPEED := 6.5

var last_bump_info: String = "슬라임의 텔레그래프를 유도하고, 회피 후 무방비 상태(Recovery)의 측후면을 노리세요!"

func _ready() -> void:
	if joystick != null and hero != null:
		joystick.input_vector_changed.connect(func(v: Vector2): hero.external_input = v)
	
	if hero != null:
		hero.bumped.connect(_on_hero_bumped)

	if slime1 != null and hero != null:
		slime1.set_target(hero)
	if slime2 != null and hero != null:
		slime2.set_target(hero)

	if camera != null and hero != null:
		camera.global_position = hero.global_position + CAMERA_OFFSET

func _on_hero_bumped(res: BumpResolver.BumpResult) -> void:
	if res.is_frontal:
		last_bump_info = "💥 [정면 충돌(상호 피해)] 용사 -%d HP | 적 -%d HP" % [res.damage_to_attacker, res.damage_to_defender]
	else:
		last_bump_info = "⚡ [측/후면 카운터(일방 타격)] 용사 0 HP (완전 방어) | 적 -%d HP (치명)" % [res.damage_to_defender]

func _process(delta: float) -> void:
	if camera != null and hero != null:
		var target_pos := hero.global_position + CAMERA_OFFSET
		camera.global_position = camera.global_position.lerp(target_pos, CAMERA_LERP_SPEED * delta)

	if hud_label != null and hero != null:
		var cd_str: String = "준비완료" if hero.attack_cooldown <= 0.0 else "쿨다운: %.2fs" % hero.attack_cooldown
		var s1_hp: int = slime1.stat_hp if is_instance_valid(slime1) else 0
		var s2_hp: int = slime2.stat_hp if is_instance_valid(slime2) else 0
		
		hud_label.text = "용사 HP: %d/%d | 슬라임1: %d/30 | 슬라임2: %d/30 | %s\n%s" % [
			hero.stat_hp,
			hero.stat_max_hp,
			s1_hp,
			s2_hp,
			cd_str,
			last_bump_info
		]
