import io
import itertools
import math
import os
import re
import sys

def part1(filename):
	print("Part 1: {}".format(sum(1 << (num_winning - 1) for num_winning in (len(re.findall(r"\b(\d+)\b(?=.+\b\1\b"), line.split(":")[1].strip()) for line in io.open(filename, mode = 'r')) if num_winning > 0)))

def part2(filename):
	print("Part 2: {}".format(sum(sum(math.prod(adjacent_numbers) for adjacent_numbers in ([int(number_match[0]) for line in (previous, current, next) if line for number_match in re.finditer(r"\d+", line) if match.start() in range(number_match.start() - 1, number_match.end() + 1)] for match in re.finditer(r"\*", current)) if len(adjacent_numbers) == 2) for previous, current, next in zip(*(itertools.islice(lines, n, None) for lines, n in zip(itertools.tee([None] + [line.strip() for line in io.open(filename, mode = 'r')] + [None], 3), itertools.count()))))))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	# part2(filename)
