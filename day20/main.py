import collections
import functools
import io
import itertools
import math
import os
import re
import sys

class Module:
	def __init__(self, module_type, name, destinations):
		self.module_type = module_type
		self.name = name
		self.destinations = destinations
		self.sources = dict()
		self.state = False
	
	def pulse(self, source, pulse):
		match self.module_type:
			case "%":
				if not pulse:
					self.state = not self.state
					return self.state
				else:
					return None
			case "&":
				self.sources[source] = pulse
				return not all(self.sources.values())
			case "":
				return pulse

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		input = file.read().strip()
	modules = dict()
	for module_type, name, destinations in re.findall(r"(?P<type>[%&]?)(?P<name>\w+) -> (\w+(?:, \w+)*)", input):
		modules[name] = Module(module_type, name, destinations.split(", "))
	for name in modules:
		for destination in modules[name].destinations:
			if destination in modules:
				modules[destination].sources[name] = False
	num_pulses = {True: 0, False: 0}
	pulses = collections.deque()
	for _ in range(1000):
		pulses.append(("button", "broadcaster", False))
		while pulses:
			source, name, pulse = pulses.popleft()
			num_pulses[pulse] += 1
			if name in modules:
				module = modules[name]
				output = module.pulse(source, pulse)
				if output != None:
					for destination in module.destinations:
						pulses.append((name, destination, output))
	print("Part 1: {}".format(num_pulses[True] * num_pulses[False]))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		input = file.read().strip()
	modules = dict()
	for module_type, name, destinations in re.findall(r"(?P<type>[%&]?)(?P<name>\w+) -> (\w+(?:, \w+)*)", input):
		modules[name] = Module(module_type, name, destinations.split(", "))
	for name in modules:
		for destination in modules[name].destinations:
			if destination in modules:
				modules[destination].sources[name] = False
	traces = collections.deque()
	traces.append(([], "broadcaster"))
	loops = dict()
	while traces:
		visited, name = traces.popleft()
		if name in visited:
			loop = visited[visited.index(name):]
			lowest_index = loop.index(min(loop))
			loops["->".join(loop[lowest_index:] + loop[:lowest_index] + loop[lowest_index:lowest_index + 1])] = loop[lowest_index:] + loop[:lowest_index]
		elif name in modules:
			module = modules[name]
			for destination in module.destinations:
				traces.append((visited + [name], destination))
	# print(len(loops))
	# for loop, contained_modules in loops.items():
	# 	print(sum(modules[module].module_type == "&" for module in contained_modules))
	pulses = collections.deque()
	cycle_length = {module: 0 for module in ["xd", "gt", "zt", "ms"]}
	num_pulses = 0
	while not all (cycle_length.values()):
		num_pulses += 1
		pulses.append(("button", "broadcaster", False))
		while pulses:
			source, name, pulse = pulses.popleft()
			if name in modules:
				module = modules[name]
				output = module.pulse(source, pulse)
				if output != None:
					for destination in module.destinations:
						pulses.append((name, destination, output))
				if name in cycle_length and output == False and not cycle_length[name]:
					cycle_length[name] = num_pulses
	accumulator = 1
	for cycle in cycle_length.values():
		divisor = math.gcd(accumulator, cycle)
		accumulator *= cycle // divisor
	print("Part 2: {}".format(accumulator))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
