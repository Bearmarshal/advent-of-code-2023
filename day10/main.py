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

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		pipe_map = [line.strip() for line in file]
	pipes = {"|": (UP, DOWN), "-": (LEFT, RIGHT), "L": (RIGHT, UP), "J": (LEFT, UP), "7": (LEFT, DOWN), "F": (RIGHT, DOWN)}
	for y, row in enumerate(pipe_map):
		if "S" in row:
			start = Position(row.index("S"), y)
			break
	for direction in Direction:
		neighbour = start + direction
		tile = neighbour.get_item(pipe_map)
		if tile in pipes and direction.opposite() in pipes[tile]:
			position = neighbour
			break
	length = 1
	while (tile := position.get_item(pipe_map)) != "S":
		direction = pipes[tile][0] if pipes[tile][0] != direction.opposite() else pipes[tile][1]
		position += direction
		length += 1
	print("Part 1: {}".format(length // 2))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		pipe_map = [line.strip() for line in file if not line.isspace()]
	## If you enter a turn from the first direction or exit from the second, you're turning right
	pipes = {"|": (UP, DOWN), "-": (LEFT, RIGHT), "L": (RIGHT, UP), "J": (UP, LEFT), "7": (LEFT, DOWN), "F": (DOWN, RIGHT)}
	width = len(pipe_map[0])
	height = len(pipe_map)
	x_span = range(width)
	y_span = range(height)
	loop_map = [[" "] * width for _ in pipe_map]
	open_set = set()
	for y, row in enumerate(pipe_map):
		for x in range(len(row)):
			open_set.add(Position(x, y))
		if "S" in row:
			start = Position(row.index("S"), y)

	start_dirs = []
	for direction in Direction:
		neighbour = start + direction
		tile = neighbour.get_item(pipe_map)
		if tile in pipes and direction.opposite() in pipes[tile]:
			start_dirs.append((direction))

	x, y = start
	## We arbitrarily choose to move in the second direction out of the start tile
	direction = start_dirs[1]
	start.set_item(loop_map, ".")
	open_set.remove(start)
	right_turns = 0
	left_turns = 0
	## Find what type of pipe is on the starting tile
	for tile, (first_dir, second_dir) in pipes.items():
		if start_dirs == [first_dir, second_dir] or start_dirs == [second_dir, first_dir]:
			if (left_side := start + direction.left()).get_item(loop_map) == " ":
				left_side.set_item(loop_map, "L")
				open_set.remove(left_side)
			if (right_side := start + direction.right()).get_item(loop_map) == " ":
				right_side.set_item(loop_map, "R")
				open_set.remove(right_side)
			if tile in "LJ7F":
				behind = start + direction.opposite()
				## direction is the exit direction, so the order of the pipe directions is (L, R)
				if pipes[tile][1] == direction:
					right_turns += 1
					if behind.get_item(loop_map) == " ":
						behind.set_item(loop_map, "L")
						open_set.remove(behind)
				else:
					left_turns += 1
					if behind.get_item(loop_map) == " ":
						behind.set_item(loop_map, "R")
						open_set.remove(behind)
	position = start + direction
	while (tile := position.get_item(pipe_map)) != "S":
		position.set_item(loop_map, ".")
		if position in open_set: open_set.remove(position)
		if (left_side := position + direction.left()).get_item(loop_map) == " ":
			left_side.set_item(loop_map, "L")
			open_set.remove(left_side)
		if (right_side := position + direction.right()).get_item(loop_map) == " ":
			right_side.set_item(loop_map, "R")
			open_set.remove(right_side)
		if tile in "LJ7F":
			ahead = position + direction
			## direction.opposite() is the entrance direction, so the order of the pipe directions is (R, L)
			if pipes[tile][0] == direction.opposite():
				right_turns += 1
				if ahead.get_item(loop_map) == " ":
					ahead.set_item(loop_map, "L")
					open_set.remove(ahead)
			else:
				left_turns += 1
				if ahead.get_item(loop_map) == " ":
					ahead.set_item(loop_map, "R")
					open_set.remove(ahead)
		direction = pipes[tile][0] if pipes[tile][0] != direction.opposite() else pipes[tile][1]
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
