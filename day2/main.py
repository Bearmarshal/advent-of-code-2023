import functools
import io
import math
import os
import re
import sys

def part1(filename):
	print("Part 1: {}".format(sum(map(lambda line: int(re.match(r"Game (\d+)", line)[1]), filter(lambda line: all((int(number) <= {"red": 12, "green": 13, "blue": 14}[colour] for number, colour in re.findall(r"(\d+) (red|green|blue)", line))), io.open(filename, mode = 'r'))))))

def part2(filename):
	print("Part 2: {}".format(sum(map(lambda line: math.prod(functools.reduce(lambda colour_map, num_colour: {colour: max(colour_map[colour], {num_colour[1]: int(num_colour[0])}.get(colour, 0)) for colour in colour_map.keys()}, re.findall(r"(\d+) (red|green|blue)", line), {"red": 0, "green": 0, "blue": 0}).values()), io.open(filename, mode = 'r')))))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
