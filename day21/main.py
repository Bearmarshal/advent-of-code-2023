import collections
import enum
import io
import itertools
import math
import os
import re
import sys

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

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		field_map = [line.strip() for line in file if not line.isspace()]
	closed_set = dict()
	open_set = collections.deque()
	for y, row in enumerate(field_map):
		if "S" in row:
			start_position = Position(y, row.index("S"))
			open_set.append((start_position, 64))
			closed_set[start_position] = 64
	while open_set:
		position, remaining_steps = open_set.popleft()
		if not remaining_steps:
			continue
		remaining_steps -= 1
		for direction in Direction:
			neighbour = position + direction
			if neighbour not in closed_set and neighbour.get_item(field_map) == ".":
				open_set.append((neighbour, remaining_steps))
				closed_set[neighbour] = remaining_steps
	print("Part 1: {}".format(sum(1 - steps % 2 for steps in closed_set.values())))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		field_map = [line.strip() for line in file if not line.isspace()]
	height = len(field_map)
	width = len(field_map[0])
	for y, row in enumerate(field_map):
		if "S" in row:
			start = Position(y, row.index("S"))

	## This solver makes the following assumptions:
	## - The field is a square with odd-valued dimensions
	## - The row and column of the starting point and the outer edges are all empty, so the closest entry point in each repeated
	##   field is on the same row/column as the starting point (cardinal directions), or the closest corner (diagonal directions).
	##
	## From these assumptions we can deduce:
	## - The shortest distance from the starting point to each entry point in every field is just the Manhattan distance
	## - Each field in the same quadrant and at the same distance from the starting point has the same number of reachable points
	##
	## Test these assumptions:
	if height != width or height % 2 == 0:
		print("Invalid assumption! Expected the field to be a square with odd-valued dimensions, found {}x{}".format(height, width))
		return
	if "#" in field_map[0] + field_map[-1] or "#" in "".join([row[0] + row[-1] for row in field_map]):
		print("Invalid assumption! Expected outer edges of the field to be empty")
		return
	if "#" in field_map[start.y] or "#" in [row[start.x] for row in field_map]:
		print("Invalid assumption! Expected row and column of the starting point to be empty")
		return

	## Now we can solve the problem
	entry_points = dict()
	for y, dy in ((0, height - start.y), (start.y, 0), (height - 1, start.y + 1)):
		for x, dx in ((0, width - start.x), (start.x, 0), (width - 1, start.x + 1)):
			entry_points[Position(y, x)] = dy + dx
	steps_remaining = 26501365
	congruence = steps_remaining % 2
	num_reachable = 0
	for point, distance_from_start in entry_points.items():
		closed_set = {point: 0}
		open_set = collections.deque([(point, 0)])
		while open_set:
			position, steps = open_set.popleft()
			steps += 1
			for direction in Direction:
				neighbour = position + direction
				if neighbour not in closed_set and (neighbour.get_item(field_map) == "." or neighbour.get_item(field_map) == "S"):
					open_set.append((neighbour, steps))
					closed_set[neighbour] = steps
		distances_from_entry_point = {position: steps for position, steps in closed_set.items() if (steps + distance_from_start) % 2 == 0}, {position: steps for position, steps in closed_set.items() if (steps + distance_from_start) % 2 == 1}
		if point == start:
			num_reachable += len(distances_from_entry_point[congruence])
		else:
			## Abusing that width == height and that all entry points are congruent with start in neigbouring fields
			num_entered_fields = 1 + (steps_remaining - distance_from_start) // width
			max_distance_in_field = max(max(distances_from_entry_point[0].values()), max(distances_from_entry_point[1].values()))
			num_full_fields = 1 + (steps_remaining - distance_from_start - max_distance_in_field) // width
			if point.y != start.y and point.x != start.x:
				## Diagonals
				num_full_congruent = ((num_full_fields + 1) // 2) ** 2
				num_full_not_congruent = num_full_fields * (num_full_fields + 1) // 2 - num_full_congruent
				num_reachable += num_full_congruent * len(distances_from_entry_point[congruence]) + num_full_not_congruent * len(distances_from_entry_point[1 - congruence])
				for field in range(num_full_fields, num_entered_fields):
					steps_remaining_at_field = steps_remaining - distance_from_start - field * width
					congruence_index = congruence if field % 2 == 0 else 1 - congruence
					num_reachable += (field + 1) * len([steps for steps in distances_from_entry_point[congruence_index].values() if steps <= steps_remaining_at_field])
			else:
				## Cardinals
				num_full_congruent = (num_full_fields + 1) // 2
				num_full_not_congruent = num_full_fields // 2
				num_reachable += num_full_congruent * len(distances_from_entry_point[congruence]) + num_full_not_congruent * len(distances_from_entry_point[1 - congruence])
				for field in range(num_full_fields, num_entered_fields):
					steps_remaining_at_field = steps_remaining - distance_from_start - field * width
					congruence_index = congruence if field % 2 == 0 else 1 - congruence
					num_reachable += len([steps for steps in distances_from_entry_point[congruence_index].values() if steps <= steps_remaining_at_field])
	print("Part 2: {}".format(num_reachable))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
