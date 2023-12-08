import collections
import io
import itertools
import math
import os
import re
import sys

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		lines = [line.strip() for line in file]

	directions = itertools.cycle(lines[0])
	nodes = {node: (left, right) for matching in (re.findall(r"(\w+) = \((\w+), (\w+)\)", line.strip()) for line in lines) for node, left, right in matching if matching}
	current_node = "AAA"
	target_node = "ZZZ"
	num_steps = 0
	while current_node != target_node:
		left, right = nodes[current_node]
		current_node = left if next(directions) == "L" else right
		num_steps += 1
	print("Part 1: {}".format(num_steps))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		lines = [line.strip() for line in file]

	directions = itertools.cycle(lines[0])
	nodes = {node: (left, right) for matching in (re.findall(r"(\w+) = \((\w+), (\w+)\)", line.strip()) for line in lines) for node, left, right in matching if matching}
	current_nodes = [node for node in nodes if node[-1] == "A"]
	num_steps = 0
	target_nodes = [0 for _ in current_nodes]
	loop_length = [0 for _ in current_nodes]
	while not all(loop_length):
		direction = next(directions)
		num_steps += 1
		for i in range(len(current_nodes)):
			left, right = nodes[current_nodes[i]]
			node = left if direction == "L" else right
			current_nodes[i] = node
			if node[-1] == "Z":
				if not target_nodes[i]:
					target_nodes[i] = num_steps
				elif not loop_length[i]:
					loop_length[i] = num_steps - target_nodes[i]
	while (num_unique := len(collections.Counter(target_nodes))) != 1:
		if num_unique != len(target_nodes):
			visited = dict()
			i = 0
			while i < len(target_nodes):
				node = target_nodes[i]
				if node in visited:
					other_i = visited[node]
					loop_length[other_i] *= loop_length[i] // math.gcd(loop_length[other_i], loop_length[i])
					target_nodes[i:i+1] = []
					loop_length[i:i+1] = []
				else:
					visited[node] = i
					i += 1
		most_steps = max(target_nodes)
		for i in range(len(target_nodes)):
			if target_nodes[i] != most_steps:
				target_nodes[i] += ((most_steps - target_nodes[i] - 1) // loop_length[i] + 1) * loop_length[i]
	print("Part 2: {}".format(target_nodes[0]))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
