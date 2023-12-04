import io
import itertools
import math
import os
import re
import sys

from collections import Counter

def part1(filename):
	print("Part 1: {}".format(sum(1 << (num_winning - 1) for num_winning in (len(re.findall(r"\b(\d+)\b(?=.+\b\1\b)", line.split(":")[1].strip())) for line in io.open(filename, mode = 'r')) if num_winning > 0)))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		lines = [line for line in file]
	num_scratchcards = Counter()
	for line in lines:
		current_scratchcard = int(re.match(r"Card\s+(\d+):", line)[1])
		num_scratchcards[current_scratchcard] += 1
		for won_scratchcard, _ in zip(itertools.count(current_scratchcard + 1), (re.findall(r"\b(\d+)\b(?=.+\b\1\b)", line.split(":")[1].strip()))):
			num_scratchcards[won_scratchcard] += num_scratchcards[current_scratchcard]
	print("Part 2: {}".format(num_scratchcards.total()))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
