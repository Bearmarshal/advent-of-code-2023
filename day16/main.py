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
	
	def get_item(self, item_map):
		if self.y in range(len(item_map)) and self.x in range(len(item_map[self.y])):
			return item_map[self.y][self.x]
		else:
			return None
	
	def set_item(self, item_map, item):
		if self.y in range(len(item_map)) and self.x in range(len(item_map[self.y])):
			item_map[self.y][self.x] = item

class Tile(enum.StrEnum, metaclass = EnumContainsValueMeta):
	def __new__(cls, glyph: str, paths: dict):
		obj = str.__new__(cls, glyph)
		obj._value_ = glyph
		obj.paths = paths
		return obj

	def get_exit_directions(self, enter_direction: Direction):
		return self.paths[enter_direction.opposite()]

	EMPTY = ".", {UP: [DOWN], DOWN: [UP], LEFT: [RIGHT], RIGHT: [LEFT]}
	CISPOSITIONAL_MIRROR = "\\", {UP: [RIGHT], DOWN: [LEFT], LEFT: [DOWN], RIGHT: [UP]}
	TRANSPOSITIONAL_MIRROR = "/", {UP: [LEFT], DOWN: [RIGHT], LEFT: [UP], RIGHT: [DOWN]}
	HORISONTAL_SPLITTER = "|", {UP: [DOWN], DOWN: [UP], LEFT: [UP, DOWN], RIGHT: [UP, DOWN]}
	VERTICAL_SPLITTER = "-", {UP: [LEFT, RIGHT], DOWN: [LEFT, RIGHT], LEFT: [RIGHT], RIGHT: [LEFT]}

def evaluate_beam(tile_map, start_position, in_direction):
	energised = set()
	open_set = {(start_position, in_direction)}
	closed_set = set()
	while open_set:
		position, in_direction = open_set.pop()
		closed_set.add((position, in_direction))
		tile_glyph = position.get_item(tile_map)
		if tile_glyph in Tile:
			energised.add(position)
			for out_direction in Tile(tile_glyph).get_exit_directions(in_direction):
				next = position + out_direction, out_direction
				if not next in closed_set:
					open_set.add(next)
	return energised

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		tile_map = [line.strip() for line in file if not line.isspace()]
	energised = evaluate_beam(tile_map, Position(0, 0), RIGHT)
	print("Part 1: {}".format(len(energised)))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		tile_map = [line.strip() for line in file if not line.isspace()]
	height = len(tile_map)
	width = len(tile_map[0])
	most_energised = 0
	for y in range(height):
		most_energised = max(most_energised, len(evaluate_beam(tile_map, Position(y, 0), RIGHT)), len(evaluate_beam(tile_map, Position(y, width - 1), LEFT)))
	for x in range(width):
		most_energised = max(most_energised, len(evaluate_beam(tile_map, Position(0, x), DOWN)), len(evaluate_beam(tile_map, Position(height - 1, x), UP)))
	print("Part 2: {}".format(most_energised))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
