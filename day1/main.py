import io
import os
import re
import sys

def part1(filename):
	print("Part 1: {}".format(sum((int(digits[0] + digits[-1]) for digits in (re.findall(r"(\d)", line) for line in io.open(filename, mode = 'r'))))))

def part2(filename):
	print("Part 2: {}".format(sum((int(digits[0] + digits[-1]) for digits in (re.findall(r"(\d)", re.sub(r"(o)(?=ne)|(t)(?=wo)|(t)(?=hree)|(f)(?=our)|(f)(?=ive)|(s)(?=ix)|(s)(?=even)|(e)(?=ight)|(n)(?=ine)", lambda m: "1" if m[1] else "2" if m[2] else "3" if m[3] else "4" if m[4] else "5" if m[5] else "6" if m[6] else "7" if m[7] else "8" if m[8] else "9", line)) for line in io.open(filename, mode = 'r'))))))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
