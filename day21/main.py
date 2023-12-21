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
	print("Part 2: {}".format(2))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	# part2(filename)
