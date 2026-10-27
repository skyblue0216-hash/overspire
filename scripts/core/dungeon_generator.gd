class_name DungeonGenerator
extends RefCounted

## Layer 4 Session Loop: Procedural Room-Corridor Dungeon Generator
## Generates rooms, corridors, cycle paths, and validates A* reachability invariants

enum RoomType {
	START,
	KEY,
	EXIT,
	LOOT,
	NORMAL
}

class Room:
	var id: int
	var type: RoomType = RoomType.NORMAL
	var x: int # Grid coordinate
	var y: int
	var width: int = 6
	var height: int = 6
	var connected_rooms: Array[int] = []

	func _init(p_id: int, p_x: int, p_y: int, p_type: RoomType = RoomType.NORMAL) -> void:
		id = p_id
		x = p_x
		y = p_y
		type = p_type

	func get_center_world(grid_scale: float = 8.0) -> Vector3:
		return Vector3(x * grid_scale, 0.0, y * grid_scale)

class DungeonLayout:
	var rooms: Array[Room] = []
	var start_room_id: int = 0
	var key_room_id: int = 1
	var exit_room_id: int = 2
	var has_key: bool = false
	var key_collected: bool = false
	var stairs_unlocked: bool = false

	func get_room(room_id: int) -> Room:
		for r in rooms:
			if r.id == room_id:
				return r
		return null

	func is_path_reachable(from_id: int, to_id: int) -> bool:
		var visited: Array[int] = []
		var queue: Array[int] = [from_id]

		while queue.size() > 0:
			var curr: int = queue.pop_front()
			if curr == to_id:
				return true
			visited.append(curr)
			var r: Room = get_room(curr)
			if r != null:
				for next_id in r.connected_rooms:
					if not visited.has(next_id) and not queue.has(next_id):
						queue.append(next_id)
		return false

## Procedurally generates a fully connected dungeon layout with 1/1 Key and Exit Stairs
static func generate_dungeon(seed_val: int = 0, room_count: int = 5) -> DungeonLayout:
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	if seed_val != 0:
		rng.seed = seed_val
	else:
		rng.randomize()

	var layout: DungeonLayout = DungeonLayout.new()
	var coords: Array[Vector2i] = []

	# Grid random walk for organic room placement
	var curr_pos: Vector2i = Vector2i(0, 0)
	coords.append(curr_pos)

	var directions: Array[Vector2i] = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]

	while coords.size() < room_count:
		var dir: Vector2i = directions[rng.randi() % directions.size()]
		var next_pos: Vector2i = curr_pos + dir
		if not coords.has(next_pos):
			coords.append(next_pos)
		curr_pos = next_pos

	# Assign Room Types
	layout.start_room_id = 0
	layout.key_room_id = 1
	layout.exit_room_id = room_count - 1

	for i in range(room_count):
		var r_type: RoomType = RoomType.NORMAL
		if i == layout.start_room_id:
			r_type = RoomType.START
		elif i == layout.key_room_id:
			r_type = RoomType.KEY
		elif i == layout.exit_room_id:
			r_type = RoomType.EXIT
		else:
			r_type = RoomType.LOOT if (i % 2 == 1) else RoomType.NORMAL

		var room: Room = Room.new(i, coords[i].x, coords[i].y, r_type)
		layout.rooms.append(room)

	# Build MST (Spanning Tree) Connections
	for i in range(room_count - 1):
		_connect_rooms(layout, i, i + 1)

	# Add Cycle Edges for looping corridors (avoiding single linear hallway)
	for i in range(room_count):
		for j in range(i + 2, room_count):
			var r1: Room = layout.rooms[i]
			var r2: Room = layout.rooms[j]
			var manhattan_dist: int = abs(r1.x - r2.x) + abs(r1.y - r2.y)
			if manhattan_dist == 1 and rng.randf() < 0.45:
				_connect_rooms(layout, i, j)

	return layout

static func _connect_rooms(layout: DungeonLayout, id1: int, id2: int) -> void:
	var r1: Room = layout.get_room(id1)
	var r2: Room = layout.get_room(id2)
	if r1 and r2:
		if not r1.connected_rooms.has(id2):
			r1.connected_rooms.append(id2)
		if not r2.connected_rooms.has(id1):
			r2.connected_rooms.append(id1)
