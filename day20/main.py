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
		match self.module_type:
			case "%":
				self.state = False
			case "&":
				self.state = dict()
			case "":
				self.state = None

	def copy(self):
		copy = Module(self.module_type, self.name, self.destinations)
		copy.state = self.state
		return copy
	
	def pulse(self, pulse):
		match self.module_type:
			case "%":
				if not pulse:
					self.state = not self.state
					return self.state
				else:
					return None
			case "&":
				return not all(self.state.values())
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
			if destination in modules and modules[destination].module_type == "&":
				modules[destination].state[name] = False
	num_pulses = {True: 0, False: 0}
	for _ in range(1000):
		num_pulses[False] += 1
		next_state = {name: module.copy() for name, module in modules.items()}
		pulse_map = {"broadcaster": False}
		while pulse_map:
			next_pulse_map = dict()
			for name, pulse in pulse_map.items():
				module = modules[name]
				output = module.pulse(pulse)
				if module.module_type == "%":
					next_state[name].state = module.state
				if output != None:
					for destination in module.destinations:
						if destination in modules:
							next_pulse_map[destination] = output
							if modules[destination].module_type == "&":
								next_state[destination].state[name] = output
						num_pulses[output] += 1
			pulse_map = next_pulse_map
	print(f"low: {num_pulses[False]}, high: {num_pulses[True]}")
	print("Part 1: {}".format(num_pulses[True] * num_pulses[False]))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		input = [line.strip() for line in file if not line.isspace()]
	print("Part 2: {}".format(2))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	# part2(filename)
