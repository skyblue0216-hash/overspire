class_name BumpMath
extends RefCounted

## Cosine threshold for frontal clash: cos(45 deg) ≈ 0.7071
const FRONTAL_THRESHOLD: float = 0.70710678

## 2D projection on XZ plane (ignoring Y)
static func to_plane_2d(v3: Vector3) -> Vector2:
	return Vector2(v3.x, v3.z)

## 2D plane vector back to 3D XZ (Y = 0)
static func to_plane_3d(v2: Vector2, y: float = 0.0) -> Vector3:
	return Vector3(v2.x, y, v2.y)

## Normalized contact vector from target towards attacker
## Contact Vector = normalize(Attacker.pos - Target.pos)
static func calculate_contact_vector(attacker_pos: Vector3, target_pos: Vector3) -> Vector2:
	var diff: Vector2 = to_plane_2d(attacker_pos) - to_plane_2d(target_pos)
	if diff.length_squared() < 0.00001:
		return Vector2.UP
	return diff.normalized()

## Cosine of angle between target facing direction and contact approach vector
## cos(theta) = F_target . V_contact
static func calculate_angle_cos(target_facing: Vector2, contact_vec: Vector2) -> float:
	var f: Vector2 = target_facing.normalized()
	var c: Vector2 = contact_vec.normalized()
	return clampf(f.dot(c), -1.0, 1.0)

## Check if collision is in the frontal 90 degree cone (cos >= 0.7071)
static func is_frontal_clash(angle_cos: float, threshold: float = FRONTAL_THRESHOLD) -> bool:
	return angle_cos >= threshold

## Damage Dynamics: max(1, (Atk * SkillMult - Def * 0.5) * CritMult)
static func calculate_damage(atk: float, def_val: float, skill_mult: float = 1.0, is_crit: bool = false, crit_mult: float = 1.5) -> int:
	var raw_dmg: float = (atk * skill_mult) - (def_val * 0.5)
	var final_dmg: float = maxf(1.0, raw_dmg)
	if is_crit:
		final_dmg *= crit_mult
	return int(round(final_dmg))

## Cooldown calculation: BaseCooldown(0.35s) / (1.0 + AtkSpdBoost)
static func calculate_cooldown(base_cd: float = 0.35, atk_spd_boost: float = 0.0) -> float:
	return maxf(0.05, base_cd / (1.0 + maxf(0.0, atk_spd_boost)))
