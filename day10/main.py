import collections
import enum
import io
import itertools
import math
import os
import re
import sys

class Direction(tuple, enum.Enum):
	def __init__(self, delta):
		self.dx, self.dy = delta

	def __neg__(self):
		return Direction((-self.dx, -self.dy))
	
	def opposite(self):
		return -self
	
	def right(self):
		return Direction((-self.dy, self.dx))
	
	def left(self):
		return Direction((self.dy, -self.dx))
	
	UP = (0, -1)
	DOWN = (0, 1)
	LEFT = (-1, 0)
	RIGHT = (1, 0)

class Position(tuple):
	def __new__(cls, x, y):
		self = tuple.__new__(cls, (x, y))
		self.x = x
		self.y = y
		return self

	def __add__(self, direction: Direction):
		return Position(self.x + direction.dx, self.y + direction.dy)
	
	def get_item(self, item_map):
		if self.y in range(len(item_map)) and self.x in range(len(item_map[self.y])):
			return item_map[self.y][self.x]
		else:
			return None
	
	def set_item(self, item_map, item):
		if self.y in range(len(item_map)) and self.x in range(len(item_map[self.y])):
			item_map[self.y][self.x] = item

UP = Direction.UP
DOWN = Direction.DOWN
LEFT = Direction.LEFT
RIGHT = Direction.RIGHT

class EnumContainsValueMeta(enum.EnumMeta):
	def __contains__(cls, value):
		return value in cls.__members__.values()
	
class Bend(enum.Enum):
	LEFT = enum.auto()
	NONE = enum.auto()
	RIGHT = enum.auto()

class Pipe(enum.StrEnum, metaclass = EnumContainsValueMeta):
	def __new__(cls, glyph: str, first_exit: Direction, second_exit: Direction, first_side: list, second_side: list):
		obj = str.__new__(cls, glyph)
		obj._value_ = glyph
		obj.first_exit = first_exit
		obj.second_exit = second_exit
		obj.first_side = first_side # If you exit through the second exit, these are on the right side
		obj.second_side = second_side
		return obj
	
	@classmethod
	def from_directions(cls, first_exit: Direction, second_exit: Direction):
		for pipe in Pipe:
			if pipe.first_exit in (first_exit, second_exit) and pipe.second_exit in (first_exit, second_exit):
				return pipe

	def is_enter_direction(self, direction: Direction):
		return direction.opposite() in (self.first_exit, self.second_exit)

	def get_exit_direction(self, enter_direction: Direction):
		if enter_direction.opposite() != self.first_exit:
			return self.first_exit
		else:
			return self.second_exit

	def get_right_side(self, exit_direction: Direction):
		if exit_direction == self.first_exit:
			return self.second_side
		else:
			return self.first_side

	def get_left_side(self, exit_direction: Direction):
		if exit_direction == self.first_exit:
			return self.first_side
		else:
			return self.second_side
		
	def get_bend(self, exit_direction: Direction):
		if self in (Pipe.UP_DOWN, Pipe.LEFT_RIGHT):
			return Bend.NONE
		elif exit_direction == self.first_exit:
			return Bend.LEFT
		else:
			return Bend.RIGHT

	UP_DOWN = "|", UP, DOWN, [LEFT], [RIGHT]
	LEFT_RIGHT = "-", LEFT, RIGHT, [DOWN], [UP]
	RIGHT_UP = "L", RIGHT, UP, [], [LEFT, DOWN]
	UP_LEFT = "J", UP, LEFT, [], [RIGHT, DOWN]
	LEFT_DOWN = "7", LEFT, DOWN, [], [UP, RIGHT]
	DOWN_RIGHT = "F", DOWN, RIGHT, [], [UP, LEFT]

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		pipe_map = [line.strip() for line in file]
	for y, row in enumerate(pipe_map):
		if "S" in row:
			start = Position(row.index("S"), y)
			break
	for direction in Direction:
		neighbour = start + direction
		tile = neighbour.get_item(pipe_map)
		if tile in Pipe and Pipe(tile).is_enter_direction(direction):
			position = neighbour
			break
	length = 1
	while (tile := position.get_item(pipe_map)) != "S":
		direction = Pipe(tile).get_exit_direction(direction)
		position += direction
		length += 1
	print("Part 1: {}".format(length // 2))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		pipe_map = [line.strip() for line in file if not line.isspace()]
	width = len(pipe_map[0])
	loop_map = [[" "] * width for _ in pipe_map]
	open_set = set()
	for y, row in enumerate(pipe_map):
		for x in range(len(row)):
			open_set.add(Position(x, y))
		if "S" in row:
			start = Position(row.index("S"), y)

	start_exits = []
	for direction in Direction:
		neighbour = start + direction
		tile = neighbour.get_item(pipe_map)
		if tile in Pipe and Pipe(tile).is_enter_direction(direction):
			start_exits.append(direction)

	start.set_item(loop_map, ".")
	open_set.remove(start)
	right_turns = 0
	left_turns = 0
	## Find what type of pipe is on the starting tile
	start_pipe = Pipe.from_directions(*start_exits)
	direction = start_pipe.first_exit
	for left_direction in start_pipe.get_left_side(direction):
		if (left_side := start + left_direction).get_item(loop_map) == " ":
			left_side.set_item(loop_map, "L")
			open_set.remove(left_side)
	for right_direction in start_pipe.get_right_side(direction):
		if (right_side := start + right_direction).get_item(loop_map) == " ":
			right_side.set_item(loop_map, "R")
			open_set.remove(right_side)
	match(start_pipe.get_bend(direction)):
		case Bend.RIGHT:
			right_turns += 1
		case Bend.LEFT:
			left_turns += 1
	position = start + direction

	while (tile := position.get_item(pipe_map)) != "S":
		position.set_item(loop_map, ".")
		if position in open_set: open_set.remove(position)
		pipe = Pipe(tile)
		direction = pipe.get_exit_direction(direction)
		for left_direction in pipe.get_left_side(direction):
			if (left_side := position + left_direction).get_item(loop_map) == " ":
				left_side.set_item(loop_map, "L")
				open_set.remove(left_side)
		for right_direction in pipe.get_right_side(direction):
			if (right_side := position + right_direction).get_item(loop_map) == " ":
				right_side.set_item(loop_map, "R")
				open_set.remove(right_side)
		match(pipe.get_bend(direction)):
			case Bend.RIGHT:
				right_turns += 1
			case Bend.LEFT:
				left_turns += 1
		position += direction
	unresolved = collections.deque(open_set)
	while len(unresolved):
		position = unresolved.popleft()
		if any((position + direction).get_item(loop_map) == "R" for direction in Direction):
			position.set_item(loop_map, "R")
		elif any((position + direction).get_item(loop_map) == "L" for direction in Direction):
			position.set_item(loop_map, "L")
		else:
			unresolved.append(position)
	if right_turns > left_turns:
		num_enclosed = sum(row.count("R") for row in loop_map)
	else:
		num_enclosed = sum(row.count("L") for row in loop_map)
	print("Part 2: {}".format(num_enclosed))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
