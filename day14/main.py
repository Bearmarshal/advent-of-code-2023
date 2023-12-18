import collections
import functools
import io
import itertools
import math
import os
import re
import sys

def tilt_east_west(platform, tilt_west):
	tilted = []
	for row in platform:
		tilted_segments = []
		for free_segment in row.split("#"):
			tilted_segments.append("".join(sorted(free_segment, reverse=tilt_west)))
		tilted.append("#".join(tilted_segments))
	return tilted

def tilt_north(platform):
	platform_transposed = list("".join(glyphs) for glyphs in zip(*platform))
	tilted_transposed = tilt_east_west(platform_transposed, tilt_west=True)
	return list("".join(glyphs) for glyphs in zip(*tilted_transposed))

def perform_spin_cycle(platform):
	for _ in range(4):
		platform_rotated = list("".join(glyphs) for glyphs in zip(*reversed(platform)))
		platform = tilt_east_west(platform_rotated, tilt_west=False)
	return platform

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		platform = [line.strip() for line in file if not line.isspace()]
	tilted_platform = tilt_north(platform)
	print("Part 1: {}".format(sum((len(tilted_platform) - i) * row.count("O") for i, row in enumerate(tilted_platform))))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		platform = [line.strip() for line in file if not line.isspace()]
	history = {hash("\n".join(platform)): 0}
	equal_to_end = -1
	for i in range(1, 10**9 + 1):
	# for i in range(1, 4):
		platform = perform_spin_cycle(platform)
		if i == equal_to_end:
			break
		platform_hash = hash("\n".join(platform))
		if equal_to_end == -1:
			if platform_hash in history:
				loop_length = i - history[platform_hash]
				offset_to_end = (10**9 - i) % loop_length
				equal_to_end = i + offset_to_end
			else:
				history[platform_hash] = i
	print("Part 2: {}".format(sum((len(platform) - i) * row.count("O") for i, row in enumerate(platform))))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
