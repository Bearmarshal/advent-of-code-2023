import collections
import io
import itertools
import math
import os
import re
import sys

from collections import Counter

def part1(filename):
	print("Part 1: {}".format(math.prod(list((2 * math.ceil(math.sqrt((int(time) / 2) ** 2 - int(distance)) - 1 + int(time) % 2 * 0.5) + 1 - int(time) % 2 for time, distance in zip(*[re.findall(r"(\d+)", line) for line in io.open(filename, mode = 'r')][0:2]))))))

def part2(filename):
	print("Part 2: {}".format(math.prod(list((2 * math.ceil(math.sqrt((int(time) / 2) ** 2 - int(distance)) - 1 + int(time) % 2 * 0.5) + 1 - int(time) % 2 for time, distance in zip(*[re.findall(r"(\d+)", line.replace(" ", "")) for line in io.open(filename, mode = 'r')][0:2]))))))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
