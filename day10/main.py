import collections
import io
import itertools
import math
import os
import re
import sys

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		pipe_map = [line.strip() for line in file]
	pipes = {"|": ((0, -1), (0, 1)), "-": ((-1, 0), (1, 0)), "L": ((1, 0), (0, -1)), "J": ((-1, 0), (0, -1)), "7": ((-1, 0), (0, 1)), "F": ((1, 0), (0, 1))}
	for y, row in enumerate(pipe_map):
		if "S" in row:
			start = (row.index("S"), y)
			break
	for dx, dy in (-1, 0), (1, 0), (0, -1), (0, 1):
		x, y = start
		x += dx
		y += dy
		neighbour = pipe_map[y][x]
		if neighbour in pipes and (-dx, -dy) in pipes[neighbour]:
			break
	length = 1
	while (tile := pipe_map[y][x]) != "S":
		dx, dy = pipes[tile][0] if pipes[tile][0] != (-dx, -dy) else pipes[tile][1]
		x += dx
		y += dy
		length += 1
	print("Part 1: {}".format(length // 2))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		pipe_map = [line.strip() for line in file if not line.isspace()]
	# If you enter a turn from the first direction, you're turning right
	pipes = {"|": ((0, -1), (0, 1)), "-": ((-1, 0), (1, 0)), "L": ((1, 0), (0, -1)), "J": ((0, -1), (-1, 0)), "7": ((-1, 0), (0, 1)), "F": ((0, 1), (1, 0))}
	loop_map = [[" "] * len(row) for row in pipe_map]
	open_set = set()
	for y, row in enumerate(pipe_map):
		for x in range(len(row)):
			open_set.add((x, y))
		if "S" in row:
			start = (row.index("S"), y)

	start_dirs = []
	for dx, dy in (-1, 0), (1, 0), (0, -1), (0, 1):
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
	for tile, (first_dir, second_dir) in pipes.items():
		if start_dirs == [first_dir, second_dir] or start_dirs == [second_dir, first_dir]:
			if y - dx in range(len(loop_map)) and x + dy in range(len(loop_map[0])) and loop_map[y - dx][x + dy] == " ": 
				loop_map[y - dx][x + dy] = "L"
				if (x + dy, y - dx) in open_set: open_set.remove((x + dy, y - dx))
			if y + dx in range(len(loop_map)) and x - dy in range(len(loop_map[0])) and loop_map[y + dx][x - dy] == " ":
				loop_map[y + dx][x - dy] = "R"
				if (x - dy, y + dx) in open_set: open_set.remove((x - dy, y + dx))
			if tile in "LJ7F":
				if pipes[tile][1] == (dx, dy):
					right_turns += 1
					if y - dy in range(len(loop_map)) and x - dx in range(len(loop_map[0])) and loop_map[y - dy][x - dx] == " ":
						loop_map[y - dy][x - dx] = "L"
						if (x - dx, y - dy) in open_set: open_set.remove((x - dx, y - dy))
				else:
					left_turns += 1
					if y - dy in range(len(loop_map)) and x - dx in range(len(loop_map[0])) and loop_map[y - dy][x - dx] == " ":
						loop_map[y - dy][x - dx] = "R"
						if (x - dx, y - dy) in open_set: open_set.remove((x - dx, y - dy))
	x += dx
	y += dy
	while (tile := pipe_map[y][x]) != "S":
		loop_map[y][x] = "."
		if (x, y) in open_set: open_set.remove((x, y))
		if y - dx in range(len(loop_map)) and x + dy in range(len(loop_map[0])) and loop_map[y - dx][x + dy] == " ": 
			loop_map[y - dx][x + dy] = "L"
			if (x + dy, y - dx) in open_set: open_set.remove((x + dy, y - dx))
		if y + dx in range(len(loop_map)) and x - dy in range(len(loop_map[0])) and loop_map[y + dx][x - dy] == " ":
			loop_map[y + dx][x - dy] = "R"
			if (x - dy, y + dx) in open_set: open_set.remove((x - dy, y + dx))
		if tile in "LJ7F":
			if pipes[tile][0] == (-dx, -dy):
				right_turns += 1
				if y + dy in range(len(loop_map)) and x + dx in range(len(loop_map[0])) and loop_map[y + dy][x + dx] == " ":
					loop_map[y + dy][x + dx] = "L"
					if (x + dx, y + dy) in open_set: open_set.remove((x + dx, y + dy))
			else:
				left_turns += 1
				if y + dy in range(len(loop_map)) and x + dx in range(len(loop_map[0])) and loop_map[y + dy][x + dx] == " ":
					loop_map[y + dy][x + dx] = "R"
					if (x + dx, y + dy) in open_set: open_set.remove((x + dx, y + dy))
		dx, dy = pipes[tile][0] if pipes[tile][0] != (-dx, -dy) else pipes[tile][1]
		x += dx
		y += dy
	unresolved = collections.deque(open_set)
	while len(unresolved):
		x, y = unresolved.popleft()
		if any(loop_map[y + dy][x + dx] == "R" for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)) if y + dy in range(len(loop_map)) and x + dx in range(len(loop_map[0]))):
			loop_map[y][x] = "R"
		elif any(loop_map[y + dy][x + dx] == "L" for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)) if y + dy in range(len(loop_map)) and x + dx in range(len(loop_map[0]))):
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
