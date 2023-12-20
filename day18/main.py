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

	@staticmethod
	def from_digit(digit):
		match digit:
			case "3":
				return UP
			case "1":
				return DOWN
			case "2":
				return LEFT
			case "0":
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

def dig(dig_instructions):
	x_stack = [] # Negative values go left, positive go right
	y_stack = [] # Negative values go up, positive go down
	dangling_x = 0
	dangling_y = 0
	resolved_area = 0
	total_distance = 0
	for direction, absolute_distance in dig_instructions:
		total_distance += absolute_distance
		match direction:
			case 0, dy:
				distance = absolute_distance * dy # Direction aware distance
				distance += dangling_y
				dangling_y = 0
				if y_stack and y_stack[-1] * distance < 0:
					# if negative, the stack is going oposite direction to the current instruction (after adding dangling distance)
					while y_stack and distance:
						other_distance = y_stack.pop()
						combined_distance = other_distance + distance
						if combined_distance * dy <= 0:
							x_distance = x_stack.pop()
							resolved_area += -distance * x_distance
							dangling_x = x_distance
							if combined_distance:
								y_stack.append(combined_distance)
							elif x_stack:
								dangling_x += x_stack.pop()
							distance = 0
							break
						else:
							x_distance = x_stack.pop()
							resolved_area += other_distance * x_distance
							x_stack.append(x_distance + (x_stack.pop() if x_stack else 0))
							distance = combined_distance
					if distance:
						y_stack.append(distance)
				else:
					y_stack.append(distance)
			case dx, 0:
				distance = absolute_distance * dx # Direction aware distance
				distance += dangling_x
				dangling_x = 0
				if x_stack and x_stack[-1] * distance < 0:
					# if negative, the stack is going oposite direction to the current instruction (after adding dangling distance)
					while x_stack and distance:
						other_distance = x_stack.pop()
						combined_distance = other_distance + distance
						if combined_distance * dx <= 0:
							y_distance = y_stack.pop()
							resolved_area += distance * y_distance
							dangling_y = y_distance
							if combined_distance:
								x_stack.append(combined_distance)
							elif y_stack:
								dangling_y += y_stack.pop()
							distance = 0
							break
						else:
							y_distance = y_stack.pop()
							resolved_area += -other_distance * y_distance
							y_stack.append(y_distance + (y_stack.pop() if y_stack else 0))
							distance = combined_distance
					if distance:
						x_stack.append(distance)
				else:
					x_stack.append(distance)
	return abs(resolved_area) + total_distance // 2 + 1

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		dig_instructions = [(Direction.from_letter(direction), int(distance)) for direction, distance, hex_distance, hex_direction in re.findall(r"([UDLR]) (\d+) \(#([0-9a-f]{5})([0-3])\)", file.read())]
	print("Part 1: {}".format(dig(dig_instructions)))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		dig_instructions = [(Direction.from_digit(hex_direction), int(hex_distance, 16)) for direction, distance, hex_distance, hex_direction in re.findall(r"([UDLR]) (\d+) \(#([0-9a-f]{5})([0-3])\)", file.read())]
	print("Part 2: {}".format(dig(dig_instructions)))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
