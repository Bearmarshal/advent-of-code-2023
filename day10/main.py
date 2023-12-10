import collections
import enum
import io
import itertools
import math
import os
import re
import sys

class Direction(tuple, enum.Enum):
	UP = (0, -1)
	DOWN = (0, 1)
	LEFT = (-1, 0)
	RIGHT = (1, 0)

	def __neg__(self):
		return Direction((-self[0], -self[1]))
	
	def opposite(self):
		return -self

class Position(tuple):
	def __new__(self, x, y):
		return tuple.__new__(Position, (x, y))

	def __add__(self, direction: Direction):
		return Position(self[0] + direction[0], self[1] + direction[1])
	
	def get_tile(self, pipe_map):
		return pipe_map[self[1]][self[0]]

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
	for direction in LEFT, RIGHT, UP, DOWN:
		neighbour = start + direction
		tile = neighbour.get_tile(pipe_map)
		if tile in pipes and -direction in pipes[tile]:
			position = neighbour
			break
	length = 1
	while (tile := position.get_tile(pipe_map)) != "S":
		direction = pipes[tile][0] if pipes[tile][0] != -direction else pipes[tile][1]
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
			open_set.add((x, y))
		if "S" in row:
			start = (row.index("S"), y)

	start_dirs = []
	for dx, dy in LEFT, RIGHT, UP, DOWN:
		x, y = start
		x += dx
		y += dy
		neighbour = pipe_map[y][x]
		if neighbour in pipes and (-dx, -dy) in pipes[neighbour]:
			start_dirs.append((dx, dy))

	x, y = start
	loop_map[y][x] = "."
	open_set.remove((x, y))
	right_turns = 0
	left_turns = 0
	## Find what type of pipe is at the starting tile
	for tile, (first_dir, second_dir) in pipes.items():
		if start_dirs == [first_dir, second_dir] or start_dirs == [second_dir, first_dir]:
			if (ny := y - dx) in y_span and (nx := x + dy) in x_span and loop_map[ny][nx] == " ": 
				loop_map[ny][nx] = "L"
				if (nx, ny) in open_set: open_set.remove((nx, ny))
			if (ny := y + dx) in y_span and (nx := x - dy) in x_span and loop_map[ny][nx] == " ":
				loop_map[ny][nx] = "R"
				if (nx, ny) in open_set: open_set.remove((nx, ny))
			if tile in "LJ7F":
				## (dx, dy) is the exit direction, so the order of the pipe directions is (L, R)
				if pipes[tile][1] == (dx, dy):
					right_turns += 1
					if (ny := y - dy) in y_span and (nx := x - dx) in x_span and loop_map[ny][nx] == " ":
						loop_map[ny][nx] = "L"
						if (nx, ny) in open_set: open_set.remove((nx, ny))
				else:
					left_turns += 1
					if (ny := y - dy) in y_span and (nx := x - dx) in x_span and loop_map[ny][nx] == " ":
						loop_map[ny][nx] = "R"
						if (nx, ny) in open_set: open_set.remove((nx, ny))
	x += dx
	y += dy
	while (tile := pipe_map[y][x]) != "S":
		loop_map[y][x] = "."
		if (x, y) in open_set: open_set.remove((x, y))
		if (ny := y - dx) in y_span and (nx := x + dy) in x_span and loop_map[ny][nx] == " ": 
			loop_map[ny][nx] = "L"
			if (nx, ny) in open_set: open_set.remove((nx, ny))
		if (ny := y + dx) in y_span and (nx := x - dy) in x_span and loop_map[ny][nx] == " ":
			loop_map[ny][nx] = "R"
			if (nx, ny) in open_set: open_set.remove((nx, ny))
		if tile in "LJ7F":
			## (-dx, -dy) is the entrance direction, so the order of the pipe directions is (R, L)
			if pipes[tile][0] == (-dx, -dy):
				right_turns += 1
				if (ny := y + dy) in y_span and (nx := x + dx) in x_span and loop_map[ny][nx] == " ":
					loop_map[ny][nx] = "L"
					if (nx, ny) in open_set: open_set.remove((nx, ny))
			else:
				left_turns += 1
				if (ny := y + dy) in y_span and (nx := x + dx) in x_span and loop_map[ny][nx] == " ":
					loop_map[ny][nx] = "R"
					if (nx, ny) in open_set: open_set.remove((nx, ny))
		dx, dy = pipes[tile][0] if pipes[tile][0] != (-dx, -dy) else pipes[tile][1]
		x += dx
		y += dy
	unresolved = collections.deque(open_set)
	while len(unresolved):
		x, y = unresolved.popleft()
		if any(loop_map[ny][nx] == "R" for dx, dy in (LEFT, RIGHT, UP, DOWN) if (ny := y + dy) in y_span and (nx := x + dx) in x_span):
			loop_map[y][x] = "R"
		elif any(loop_map[ny][nx] == "L" for dx, dy in (LEFT, RIGHT, UP, DOWN) if (ny := y + dy) in y_span and (nx := x + dx) in x_span):
			loop_map[y][x] = "L"
		else:
			unresolved.append((x, y))
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
