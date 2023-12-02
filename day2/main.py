import io
import math
import os
import re
import sys

def part1(filename):
	num_cubes = {"red": 12, "green": 13, "blue": 14}
	id_sum = 0
	game_regex = re.compile(r"Game (?P<id>\d+)")
	colour_regex = re.compile(r"(\d+) (red|green|blue)")

	with io.open(filename, mode = 'r') as infile:
		indata = [line.strip() for line in infile]

	for line in indata:
		prefix, draws = line.split(": ")
		possible = True
		for draw in draws.split("; "):
			for number, colour in colour_regex.findall(draw):
				if int(number) > num_cubes[colour]:
					possible = False
		if possible:
			id_sum += int(game_regex.match(prefix)["id"])

	print(f"Part 1: {id_sum}")

def part2(filename):
	power_sum = 0
	game_regex = re.compile(r"Game (?P<id>\d+)")
	colour_regex = re.compile(r"(\d+) (red|green|blue)")

	with io.open(filename, mode = 'r') as infile:
		indata = [line.strip() for line in infile]

	for line in indata:
		prefix, draws = line.split(": ")
		min_cubes = {"red": 0, "green": 0, "blue": 0}
		for draw in draws.split("; "):
			for number, colour in colour_regex.findall(draw):
				min_cubes[colour] = max(min_cubes[colour], int(number))
		power_sum += math.prod(min_cubes.values())

	print(f"Part 2: {power_sum}")

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
