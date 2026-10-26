class_name BumpResolver
extends RefCounted

## Context data passed into interceptors and evaluation
class BumpContext:
	var attacker: Node3D
	var defender: Node3D
	var contact_vec: Vector2
	var angle_cos: float
	var is_frontal: bool
	var damage_to_defender: int = 0
	var damage_to_attacker: int = 0
	var knockback_defender: Vector3 = Vector3.ZERO
	var knockback_attacker: Vector3 = Vector3.ZERO
	var hitstop_duration: float = 0.04
	var is_crit: bool = false
	var cancel: bool = false

## Result returned after resolving bump physics and damages
class BumpResult:
	var valid_hit: bool = false
	var is_frontal: bool = false
	var damage_to_attacker: int = 0
	var damage_to_defender: int = 0
	var knockback_attacker: Vector3 = Vector3.ZERO
	var knockback_defender: Vector3 = Vector3.ZERO
	var hitstop_duration: float = 0.0
	var is_crit: bool = false

	static func create_cooldown_bounce(kb_atk: Vector3, kb_def: Vector3) -> BumpResult:
		var res: BumpResult = BumpResult.new()
		res.valid_hit = false
		res.knockback_attacker = kb_atk
		res.knockback_defender = kb_def
		return res

## Base class for OCP Bump Interceptors
class BumpInterceptor extends RefCounted:
	func on_pre_bump(_ctx: BumpContext) -> void:
		pass
	func on_post_bump(_result: BumpResult) -> void:
		pass

var _interceptors: Array[BumpInterceptor] = []

func register_interceptor(interceptor: BumpInterceptor) -> void:
	if not _interceptors.has(interceptor):
		_interceptors.append(interceptor)

func unregister_interceptor(interceptor: BumpInterceptor) -> void:
	_interceptors.erase(interceptor)

## Main resolution pipeline enforcing Layer 2 Micro Bump Loop invariants
func resolve_bump(attacker: Node3D, defender: Node3D, force_crit: bool = false) -> BumpResult:
	var atk_pos: Vector3 = attacker.global_position
	var def_pos: Vector3 = defender.global_position

	# Target facing direction on horizontal plane
	var def_facing: Vector2 = Vector2.DOWN
	if defender.has_method("get_facing_direction_2d"):
		def_facing = defender.get_facing_direction_2d()
	elif "facing_direction" in defender:
		def_facing = defender.facing_direction

	var contact_vec: Vector2 = BumpMath.calculate_contact_vector(atk_pos, def_pos)
	var angle_cos: float = BumpMath.calculate_angle_cos(def_facing, contact_vec)
	var is_frontal: bool = BumpMath.is_frontal_clash(angle_cos)

	# Separation impulse directions
	var sep_dir_atk: Vector3 = BumpMath.to_plane_3d(contact_vec) # Pushes attacker away (+contact_vec)
	var sep_dir_def: Vector3 = -sep_dir_atk                     # Pushes defender back (-contact_vec)

	# 1. Check Attacker Cooldown (No-iframe Multi-hit prevention)
	var atk_cd: float = 0.0
	if "attack_cooldown" in attacker:
		atk_cd = attacker.attack_cooldown

	if atk_cd > 0.0:
		# In cooldown: Skip damage, purely apply rigid separation bounce
		var bounce_impulse: float = 3.2
		return BumpResult.create_cooldown_bounce(sep_dir_atk * bounce_impulse, sep_dir_def * (bounce_impulse * 0.5))

	# 2. Prepare Context for Valid Hit
	var ctx: BumpContext = BumpContext.new()
	ctx.attacker = attacker
	ctx.defender = defender
	ctx.contact_vec = contact_vec
	ctx.angle_cos = angle_cos
	ctx.is_frontal = is_frontal

	# Retrieve Stats
	var atk_stat: float = attacker.get("stat_atk") if "stat_atk" in attacker else 10.0
	var atk_def_stat: float = attacker.get("stat_def") if "stat_def" in attacker else 2.0
	var def_stat: float = defender.get("stat_def") if "stat_def" in defender else 2.0
	var def_atk_stat: float = defender.get("stat_atk") if "stat_atk" in defender else 8.0

	var crit_rate: float = attacker.get("stat_crit_rate") if "stat_crit_rate" in attacker else 0.1
	var crit_mult: float = attacker.get("stat_crit_mult") if "stat_crit_mult" in attacker else 1.5
	var is_crit: bool = force_crit or (randf() < crit_rate)
	ctx.is_crit = is_crit

	# Damage to defender
	ctx.damage_to_defender = BumpMath.calculate_damage(atk_stat, def_stat, 1.0, is_crit, crit_mult)

	# Impulses & Damage to attacker
	var base_impulse: float = 5.5
	if is_frontal:
		# Frontal Clash: Mutual Damage
		ctx.damage_to_attacker = BumpMath.calculate_damage(def_atk_stat, atk_def_stat, 1.0, false, 1.0)
		ctx.knockback_attacker = sep_dir_atk * (base_impulse * 0.9)
		ctx.knockback_defender = sep_dir_def * (base_impulse * 0.9)
		ctx.hitstop_duration = 0.04
	else:
		# Advantageous Strike: Zero damage to hero, heavy knockback on defender
		ctx.damage_to_attacker = 0
		ctx.knockback_attacker = sep_dir_atk * (base_impulse * 0.25) # Minor recoil
		ctx.knockback_defender = sep_dir_def * (base_impulse * 1.3)  # Big knockback
		ctx.hitstop_duration = 0.04

	# 3. Interceptors Pipeline (OCP: IBumpInterceptor)
	for interceptor in _interceptors:
		interceptor.on_pre_bump(ctx)

	if ctx.cancel:
		return BumpResult.new()

	# 4. Construct Final BumpResult
	var result: BumpResult = BumpResult.new()
	result.valid_hit = true
	result.is_frontal = ctx.is_frontal
	result.damage_to_attacker = ctx.damage_to_attacker
	result.damage_to_defender = ctx.damage_to_defender
	result.knockback_attacker = ctx.knockback_attacker
	result.knockback_defender = ctx.knockback_defender
	result.hitstop_duration = ctx.hitstop_duration
	result.is_crit = ctx.is_crit

	for interceptor in _interceptors:
		interceptor.on_post_bump(result)

	return result
