extends Control
class_name VirtualJoystick

## Overspire Mobile & Web Touch Joystick
## 화면 좌측 터치/클릭을 감지하여 8방향 아날로그 입력 벡터를 생성합니다.

signal input_vector_changed(vector: Vector2)

@export var max_radius: float = 65.0
@export var deadzone: float = 0.15

var _is_active: bool = false
var _touch_index: int = -1
var _center_pos: Vector2 = Vector2.ZERO
var _current_pos: Vector2 = Vector2.ZERO
var _output_vector: Vector2 = Vector2.ZERO

func _ready() -> void:
    # 기본 위치 (화면 좌하단)
    _center_pos = Vector2(100.0, size.y - 100.0) if size.y > 200 else Vector2(100.0, 240.0)
    _current_pos = _center_pos
    queue_redraw()

func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        # 화면 좌측 절반만 처리
        var viewport_rect := get_viewport_rect()
        if event.position.x < viewport_rect.size.x * 0.55:
            if event.pressed and not _is_active:
                _is_active = true
                _touch_index = event.index
                _center_pos = event.position
                _current_pos = event.position
                _update_vector()
            elif not event.pressed and event.index == _touch_index:
                _reset_joystick()
                
    elif event is InputEventScreenDrag and _is_active:
        if event.index == _touch_index:
            _current_pos = event.position
            _update_vector()
            
    # 마우스 지원 (PC 웹 브라우저 테스트용)
    elif event is InputEventMouseButton:
        var viewport_rect := get_viewport_rect()
        if event.position.x < viewport_rect.size.x * 0.55:
            if event.button_index == MOUSE_BUTTON_LEFT:
                if event.pressed:
                    _is_active = true
                    _touch_index = 999
                    _center_pos = event.position
                    _current_pos = event.position
                    _update_vector()
                else:
                    _reset_joystick()
                    
    elif event is InputEventMouseMotion and _is_active and _touch_index == 999:
        _current_pos = event.position
        _update_vector()

func _update_vector() -> void:
    var diff := _current_pos - _center_pos
    var distance := diff.length()
    
    if distance > max_radius:
        diff = diff.normalized() * max_radius
        _current_pos = _center_pos + diff
        distance = max_radius

    var norm := distance / max_radius
    if norm < deadzone:
        _output_vector = Vector2.ZERO
    else:
        var remapped := (norm - deadzone) / (1.0 - deadzone)
        _output_vector = diff.normalized() * remapped
        
    input_vector_changed.emit(_output_vector)
    queue_redraw()

func _reset_joystick() -> void:
    _is_active = false
    _touch_index = -1
    _output_vector = Vector2.ZERO
    input_vector_changed.emit(_output_vector)
    queue_redraw()

func _draw() -> void:
    if _is_active:
        # 조이스틱 베이스 (원형 테두리)
        draw_circle(_center_pos, max_radius, Color(0.1, 0.15, 0.2, 0.4))
        draw_arc(_center_pos, max_radius, 0.0, TAU, 32, Color(0.7, 0.8, 0.9, 0.6), 2.5)
        # 조이스틱 놉 (중심 핸들)
        draw_circle(_current_pos, 24.0, Color(0.0, 0.8, 0.9, 0.75))
        draw_circle(_current_pos, 10.0, Color(1.0, 1.0, 1.0, 0.9))
    else:
        # 평상시 대기 안내 표시
        var hint_pos := Vector2(80.0, get_viewport_rect().size.y - 80.0) if get_viewport_rect().size.y > 0 else Vector2(80, 260)
        draw_circle(hint_pos, 45.0, Color(0.2, 0.25, 0.35, 0.2))
        draw_arc(hint_pos, 45.0, 0.0, TAU, 24, Color(0.7, 0.8, 0.9, 0.3), 1.5)
