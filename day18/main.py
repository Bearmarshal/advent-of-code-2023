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
	
	@staticmethod
	def from_letter(letter):
		match letter:
			case "U":
				return UP
			case "D":
				return DOWN
			case "L":
				return LEFT
			case "R":
				return RIGHT
	
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
		dig_instructions = [(Direction.from_letter(direction), int(distance), colour) for direction, distance, colour in re.findall(r"([UDLR]) (\d+) \(#([0-9a-f]{6})\)", file.read())]
	max_y = 0
	max_x = 0
	for direction, distance, _ in dig_instructions:
		match direction:
			case Direction.DOWN:
				max_y += distance
			case Direction.RIGHT:
				max_x += distance
			case _:
				pass
	width = 2 * max_x + 1
	height = 2 * max_y + 1
	dig_map = [[" "] * width for _ in range(height)]
	turns = 0
	start = Position(max_x, max_y)
	start.set_item(dig_map, "S")
	position = start
	previous_direction = dig_instructions[-1][0]
	open_set = collections.deque()
	for direction, distance, _ in dig_instructions:
		if direction == previous_direction.right():
			turns += 1
		else:
			turns -= 1
		
		for _ in range(distance):
			position += direction
			position.set_item(dig_map, "#")
			right_side = position + direction.right()
			if right_side.get_item(dig_map) == " ":
				right_side.set_item(dig_map, "R")
				open_set.append(right_side)
			left_side = position + direction.left()
			if left_side.get_item(dig_map) == " ":
				left_side.set_item(dig_map, "L")
				open_set.append(left_side)
		previous_direction = direction
	while len(open_set):
		position = open_set.popleft()
		glyph = position.get_item(dig_map)
		for direction in Direction:
			neighbour = position + direction
			if neighbour.get_item(dig_map) == " ":
				neighbour.set_item(dig_map, glyph)
				open_set.append(neighbour)
	if turns > 0:
		volume = sum(row.count("#") + row.count("R") for row in dig_map)
	else:
		volume = sum(row.count("#") + row.count("L") for row in dig_map)
	print("Part 1: {}".format(volume))

def part2(filename):
	pass

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	# part2(filename)
