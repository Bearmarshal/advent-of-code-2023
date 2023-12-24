import collections
import enum
import io
import itertools
import math
import os
import queue
import re
import sys

from dataclasses import dataclass, field
from typing import Any

class EnumContainsValueMeta(enum.EnumMeta):
	def __contains__(cls, value):
		return value in cls.__members__.values()

class Direction(tuple, enum.Enum):
	def __init__(self, delta):
		self.dy, self.dx = delta

	def __neg__(self):
		return Direction((-self.dy, -self.dx))

	def opposite(self):
		return -self

	def right(self):
		return Direction((-self.dy, self.dx))

	def left(self):
		return Direction((self.dy, -self.dx))

	@classmethod
	def from_glyph(cls, glyph):
		match glyph:
			case "^": return cls.UP
			case "v": return cls.DOWN
			case "<": return cls.LEFT
			case ">": return cls.RIGHT

	UP = (-1, 0)
	DOWN = (1, 0)
	LEFT = (0, -1)
	RIGHT = (0, 1)

UP = Direction.UP
DOWN = Direction.DOWN
LEFT = Direction.LEFT
RIGHT = Direction.RIGHT

class Position(tuple):
	def __new__(cls, y, x):
		self = tuple.__new__(cls, (y, x))
		self.y = y
		self.x = x
		return self

	def __add__(self, direction: Direction):
		return Position(self.y + direction.dy, self.x + direction.dx)

	def get_manhattan_distance(self, other):
		return abs(self.y - other.y) + abs(self.x - other.x)

	def get_item(self, item_map):
		if self.y in range(len(item_map)) and self.x in range(len(item_map[self.y])):
			return item_map[self.y][self.x]
		else:
			return None

	def set_item(self, item_map, item):
		if self.y in range(len(item_map)) and self.x in range(len(item_map[self.y])):
			item_map[self.y][self.x] = item

class Junction():
	def __init__(self, position, distance):
		self.position = position
		self.longest_distance = distance
		self.downstream = set()

	def __repr__(self):
		return f"{self.position}: {self.longest_distance}, {[(downstream.position, distance) for downstream, distance in self.downstream]}"

@dataclass(order=True)
class PrioritisedItem:
    priority: int
    item: Any=field(compare=False)

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		trail_map = [line.strip() for line in file if not line.isspace()]
	start = Position(0, trail_map[0].index("."))
	exit = Position(len(trail_map) - 1, trail_map[-1].index("."))
	open_set = collections.deque([(start, DOWN, 0, Junction(start, 0))])
	junctions = dict()
	while open_set:
		position, last_direction, distance, last_junction = open_set.pop()
		if position == exit:
			exit_junction = Junction(exit, distance)
			junctions[exit] = exit_junction
			last_junction.downstream.add((exit_junction, distance - last_junction.longest_distance))
			continue
		num_paths = 0
		out_directions = []
		for direction in Direction:
			if direction == last_direction.opposite():
				continue
			neighbour = position + direction
			tile = neighbour.get_item(trail_map)
			num_paths += tile != "#"
			if tile == "." or Direction.from_glyph(tile) == direction:
				out_directions.append(direction)
		if num_paths > 1:
			if position in junctions:
				junction = junctions[position]
				last_junction.downstream.add((junction, distance - last_junction.longest_distance))
				if distance > junction.longest_distance:
					junction.longest_distance = distance
					to_update = collections.deque((downstream, distance + distance_to) for (downstream, distance_to) in junction.downstream)
					updated = set()
					while to_update:
						downstream, distance = to_update.popleft()
						if downstream in updated:
							continue
						if distance > downstream.longest_distance:
							downstream.longest_distance = distance
							to_update.extend((downstream, distance + distance_to) for (downstream, distance_to) in downstream.downstream)
							updated.add(downstream)
			else:
				junction = Junction(position, distance)
				junctions[position] = junction
				last_junction.downstream.add((junction, distance - last_junction.longest_distance))
				for direction in out_directions:
					open_set.append((position + direction, direction, distance + 1, junction))
		else:
			open_set.append((position + out_directions[0], out_directions[0], distance + 1, last_junction))
	print("Part 1: {}".format(exit_junction.longest_distance))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		trail_map = [line.strip() for line in file if not line.isspace()]
	start = Position(0, trail_map[0].index("."))
	exit = Position(len(trail_map) - 1, trail_map[-1].index("."))
	start_junction = Junction(start, 0)
	open_set = collections.deque([(start, DOWN, 0, start_junction)])
	junctions = dict()
	total_path_length = 0
	while open_set:
		position, last_direction, distance_to_last, last_junction = open_set.pop()
		if position == exit:
			exit_junction = Junction(exit, 0)
			junctions[exit] = exit_junction
			last_junction.downstream.add((exit_junction, distance_to_last))
			total_path_length += distance_to_last - 1
			continue
		out_directions = []
		for direction in Direction:
			if direction == last_direction.opposite():
				continue
			neighbour = position + direction
			tile = neighbour.get_item(trail_map)
			if tile != "#":
				out_directions.append(direction)
		if len(out_directions) > 1:
			if position in junctions:
				junction = junctions[position]
				if (last_junction, distance_to_last) in junction.downstream:
					continue
				junction.downstream.add((last_junction, distance_to_last))
				last_junction.downstream.add((junction, distance_to_last))
				total_path_length += distance_to_last - 1
			else:
				junction = Junction(position, 0)
				junctions[position] = junction
				junction.downstream.add((last_junction, distance_to_last))
				last_junction.downstream.add((junction, distance_to_last))
				total_path_length += distance_to_last - 1
				for direction in out_directions:
					open_set.append((position + direction, direction, 1, junction))
		else:
			open_set.append((position + out_directions[0], out_directions[0], distance_to_last + 1, last_junction))
	total_path_length += len(junctions)
	open_set = queue.PriorityQueue()
	open_set.put(PrioritisedItem(-total_path_length, (start_junction, 0, set())))
	while open_set.qsize():
		prioritised_item = open_set.get()
		heuristic = prioritised_item.priority
		junction, distance, visited = prioritised_item.item
		if junction == exit_junction:
			longest_distance = distance
			break
		heuristic += sum(distance_to - 1 for downstream, distance_to in junction.downstream if downstream not in visited)
		downstream_visited = visited.copy()
		downstream_visited.add(junction)
		for downstream, distance_to in junction.downstream:
			if downstream in visited:
				continue
			downstream_distance = distance + distance_to
			if downstream == exit_junction:
				downstream_heuristic = -downstream_distance
			else:
				downstream_heuristic = heuristic - (distance_to - 1)
			open_set.put(PrioritisedItem(downstream_heuristic, (downstream, downstream_distance, downstream_visited)))
	print("Part 2: {}".format(longest_distance))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
