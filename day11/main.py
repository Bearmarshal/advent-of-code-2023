import collections
import functools
import io
import itertools
import math
import os
import re
import sys

def extrapolate(series):
	match series:
		case [n]:
			return n, n
		case _ if all(n == 0 for n in series):
			return 0, 0
		case _:
			b, a = extrapolate([n - m for m, n in zip(series, series[1:])])
			return series[0] - b, series[-1] + a

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		input = [line.strip() for line in file if not line.isspace()]
	partial_expanded = []
	for line in input:
		partial_expanded.append(list(line))
		if all(glyph == "." for glyph in line):
			partial_expanded.append(list(line))
	i = len(input[0]) - 1
	for i in range(len(partial_expanded[0])-1, 0, -1):
		if all(line[i] == "." for line in partial_expanded):
			for line in partial_expanded:
				line[i:i] = [line[i]]
	galaxies = []
	for y, row in enumerate(partial_expanded):
		for x, glyph in enumerate(row):
			if glyph == "#":
				galaxies.append((y, x))
	sum_distances = sum(abs(by - ay) + abs(bx - ax) for (ay, ax), (by, bx) in itertools.combinations(galaxies, 2))
	print("Part 1: {}".format(sum_distances))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		input = [line.strip() for line in file if not line.isspace()]
	expansion = 10**6 - 1
	y_expansion = []
	x_expansion = []
	current_expansion = 0
	for line in input:
		y_expansion.append(current_expansion)
		if all(glyph == "." for glyph in line):
			current_expansion += expansion
	current_expansion = 0
	for i in range(len(input[0])):
		x_expansion.append(current_expansion)
		if all(line[i] == "." for line in input):
			current_expansion += expansion
	galaxies = []
	for y, row in enumerate(input):
		for x, glyph in enumerate(row):
			if glyph == "#":
				galaxies.append((y + y_expansion[y], x + x_expansion[x]))
	sum_distances = sum(abs(by - ay) + abs(bx - ax) for (ay, ax), (by, bx) in itertools.combinations(galaxies, 2))
	print("Part 2: {}".format(sum_distances))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
