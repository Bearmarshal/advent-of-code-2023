import collections
import functools
import io
import itertools
import math
import os
import re
import sys

def all_equals(value, iterable):
	return all(map(lambda item: item == value, iterable))

def record_matches(record, num_contiguous):
	num_combinations = len(record) - num_contiguous + 1
	for i in range(num_combinations):
		if all_equals("?", record[0:i]) and (i + 1 == num_combinations or record[i + num_contiguous] == "?"):
			return i
	return -1

def find_num_matches(condition_record, group_lengths, start_index, constraints):
	match condition_record, group_lengths:
		case records, []:
			if all(all_equals("?", record_group) for record_group, _ in records):
				return 1
			else:
				return 0
		case [], _:
			return 0
	if (len(group_lengths), start_index) in constraints:
		return constraints[len(group_lengths), start_index]
	group_length, *rest = group_lengths
	i = start_index
	num_matches = 0
	while condition_record:
		record_group, group_start = condition_record[0]
		i = max(group_start, i)
		if not all_equals("?", record_group[:i-group_start]):
			break
		match_offset = record_matches(record_group[i - group_start:], group_length)
		if match_offset == -1 and not all_equals("?", record_group):
			break
		elif match_offset == -1:
			condition_record = condition_record[1:]
		else:
			group_remainder_start = i + match_offset + group_length + 1
			if len(record_group) > group_remainder_start - group_start:
				continuation = [(record_group[group_remainder_start - group_start:], group_remainder_start)] + condition_record[1:]
			else:
				continuation = condition_record[1:]
			num_matches += find_num_matches(continuation, rest, group_remainder_start, constraints)
			i += match_offset + 1
	constraints[len(group_lengths), start_index] = num_matches
	return num_matches


def part1(filename):
	with io.open(filename, mode = 'r') as file:
		input = [line.strip() for line in file if not line.isspace()]
	records = (([(match[0], match.start()) for match in re.finditer(r"[#?]+", record)], [int(group) for group in groups.split(",")]) for record, groups in (line.split() for line in input))
	print("Part 1: {}".format(sum(find_num_matches(condition_record, group_lengths, 0, dict()) for condition_record, group_lengths in records)))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		input = [line.strip() for line in file if not line.isspace()]
	records = (([(match[0], match.start()) for match in re.finditer(r"[#?]+", "?".join(5 * [record]))], 5 * [int(group) for group in groups.split(",")]) for record, groups in (line.split() for line in input))
	print("Part 2: {}".format(sum(find_num_matches(condition_record, group_lengths, 0, dict()) for condition_record, group_lengths in records)))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
