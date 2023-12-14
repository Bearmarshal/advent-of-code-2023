import collections
import functools
import io
import itertools
import math
import os
import re
import sys

def find_mirror(pattern):
	for i in range(1, len(pattern)):
		before = pattern[:i]
		after = pattern[i:]
		if all(b == a for b, a in zip(reversed(before), after)):
			return len(before)
	return 0

def find_smudged_mirror(pattern):
	for i in range(1, len(pattern)):
		before = pattern[:i]
		after = pattern[i:]
		if sum(1 if b != a else 0 for line_pair in zip(reversed(before), after) for b, a in zip(*line_pair)) == 1:
			return len(before)
	return 0

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		input = file.read()
	patterns = [block.strip().split() for block in input.split("\n\n")]
	summarised = 0
	for pattern in patterns:
		pattern_transposed = list("".join(glyphs) for glyphs in zip(*pattern))
		mirror = 100 * find_mirror(pattern) + find_mirror(pattern_transposed)
		summarised += mirror
	print("Part 1: {}".format(summarised))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		input = file.read()
	patterns = [block.strip().split() for block in input.split("\n\n")]
	summarised = 0
	for pattern in patterns:
		pattern_transposed = list("".join(glyphs) for glyphs in zip(*pattern))
		mirror = 100 * find_smudged_mirror(pattern) + find_smudged_mirror(pattern_transposed)
		summarised += mirror
	print("Part 2: {}".format(summarised))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
