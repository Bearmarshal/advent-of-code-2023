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
	print("Part 1: {}".format(sum(extrapolate(series)[1] for series in [list(map(int, line.strip().split())) for line in io.open(filename, mode = 'r') if not line.isspace()])))

def part2(filename):
	print("Part 1: {}".format(sum(extrapolate(series)[0] for series in [list(map(int, line.strip().split())) for line in io.open(filename, mode = 'r') if not line.isspace()])))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
