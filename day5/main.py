import collections
import io
import itertools
import math
import os
import re
import sys

from collections import Counter

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		input = file.read()

	regex = re.compile(r"seeds: (?P<seeds>(\d+ ?)+)|(?P<header_from>\w+)-to-(?P<header_to>\w+) map:|(?P<to>\d+) (?P<from>\d+) (?P<length>\d+)|(?P<end_context>\n\n)")
	almanac = collections.defaultdict(list)
	from_context = None
	to_context = "seed"

	for input_match in regex.finditer(input):
		if seeds := input_match["seeds"]:
			almanac["seed"] = [int(seed) for seed in seeds.strip().split()]
		elif input_match["header_from"]:
			almanac[to_context] += almanac[from_context]
			from_context = input_match["header_from"]
			to_context = input_match["header_to"]
			pass
		elif (from_start := input_match["from"]) and (to_start := input_match["to"]) and (range_length := input_match["length"]):
			from_range = range(int(from_start), int(from_start) + int(range_length))
			to_offset = int(to_start) - int(from_start)
			from_items = almanac[from_context]
			i = 0
			while i < len(from_items):
				item = from_items[i]
				if item in from_range:
					almanac[to_context].append(item + to_offset)
					from_items[i:i+1] = []
				else:
					i += 1
	almanac[to_context] += almanac[from_context]

	print("Part 1: {}".format(min(almanac["location"])))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		input = file.read()

	regex = re.compile(r"seeds: (?P<seeds>(\d+ ?)+)|(?P<header_from>\w+)-to-(?P<header_to>\w+) map:|(?P<to>\d+) (?P<from>\d+) (?P<length>\d+)|(?P<end_context>\n\n)")
	almanac = collections.defaultdict(list)
	from_context = None
	to_context = "seed"

	for input_match in regex.finditer(input):
		if seeds := input_match["seeds"]:
			almanac["seed"] = [range(int(seed_start), int(seed_start) + int(seed_length)) for seed_start, seed_length in re.findall(r"(\d+) (\d+)", seeds)]
		elif input_match["header_from"]:
			almanac[to_context] += almanac[from_context]
			from_context = input_match["header_from"]
			to_context = input_match["header_to"]
			pass
		elif (from_start := input_match["from"]) and (to_start := input_match["to"]) and (range_length := input_match["length"]):
			from_range = range(int(from_start), int(from_start) + int(range_length))
			to_offset = int(to_start) - int(from_start)
			from_items = almanac[from_context]
			i = 0
			while i < len(from_items):
				item = from_items[i]
				if intersection := range(max(item.start, from_range.start), min(item.stop, from_range.stop)):
					from_items[i:i+1] = []
					if disjunction_before := range(item.start, intersection.start):
						almanac[from_context].append(disjunction_before)
					if disjunction_after := range(intersection.stop, item.stop):
						almanac[from_context].append(disjunction_after)
					almanac[to_context].append(range(intersection.start + to_offset, intersection.stop + to_offset))
				else:
					i += 1
	almanac[to_context] += almanac[from_context]

	print("Part 2: {}".format(min(location.start for location in almanac["location"])))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
