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
	modules["rx"] = Module("", "rx", [])
	for name in modules:
		for destination in modules[name].destinations:
			if destination in modules:
				modules[destination].sources[name] = False

	## This solver makes the following assumptions:
	## - There only input to "rx" is a single conjunction module ("bb" in my input)
	## - All inputs to said conjunction modules are inverters, i.e. conjuction modules with a single input of their own ("kp", "ct", "xc", "ks" in my input)
	## - All inputs to said inverters are conjunction modules, and there are no other conjunction modules in the input ("xd", "gt", "zt", "ms" in my input)
	## - None of the conjunction modules above connect to any of the other conjunction modules
	## - All loops in the input contain exactly one conjunction module
	## - When a loopback conjunction module (i.e. all but the one connected to "rx") outputs a low pulse, the flip-flop modules in its loops are always in the same states
	##			
	## From these assumptions, it's possible to calculate a stable cycle count for each separate loopback conjunction module, and by extension, calculate the first time when all four output a low pulse at the same time
	##
	## Test these assumptions:
	if len(modules["rx"].sources) != 1:
		print("Invalid assumption! Expected exactly one conjunction module connected to 'rx', found {}".format(modules["rx"].sources))
	rx_source, = modules["rx"].sources
	if modules[rx_source].module_type != "&":
		print("Invalid assumption! Expected conjunction module connected to 'rx', found {}{}".format(modules[rx_source].module_type), rx_source)
		return
	inverter_modules = modules[rx_source].sources
	loopback_conjunction_modules = []
	for inverter in inverter_modules:
		if modules[inverter].module_type != "&" or len(modules[inverter].sources) != 1:
			print("Invalid assumption! Expected inverter module connected to source of 'rx', found {}{} with sources {}".format(modules[inverter].module_type), inverter, modules[inverter].sources)
			return
		if len(modules[inverter].destinations) != 1:
			print("Invalid assumption! Expected inverter module to only connect to 'rx', found {}{} with destinations {}".format(modules[inverter].module_type), inverter, modules[inverter].destinations)
			return
		inverter_source, = modules[inverter].sources
		if modules[inverter_source].module_type != "&":
			print("Invalid assumption! Expected conjunction module connected to source of inverter, found {}{}".format(modules[inverter_source].module_type), inverter_source)
			return
		loopback_conjunction_modules.append(inverter_source)
	counted_conjunction_modules = 1 + len(inverter_modules) + len(loopback_conjunction_modules)
	num_conjunction_modules = sum(module.module_type == "&" for module in modules.values())
	if counted_conjunction_modules != num_conjunction_modules:
		print("Invalid assumption! Expected no additional conjunction modules, found {}".format(counted_conjunction_modules - num_conjunction_modules))
		return
	tracer = collections.deque()
	tracer.append(([], "broadcaster"))
	while tracer:
		visited, name = tracer.popleft()
		if name in visited:
			loop = visited[visited.index(name):]
			conjugations_in_loop = [module for module in loop if modules[module].module_type == "&"]
			if len(conjugations_in_loop) != 1:
				print("Invalid assumption! Expected exactly one conjunction module in loop, found {}".format(conjugations_in_loop))
				return
		elif name in modules:
			module = modules[name]
			for destination in module.destinations:
				tracer.append((visited + [name], destination))

	## Now we can solve the problem. "rx" will receive a low pulse when all loopback conjunction modules output low pulses at the same time
	## This doesn't assume that the first low pulse happens exactly after cycle_length number of cycles (but it does for my input)
	pulses = collections.deque()
	cycle_start = {module: 0 for module in loopback_conjunction_modules}
	cycle_length = {module: 0 for module in loopback_conjunction_modules}
	num_pulses = 0
	while not all(cycle_length.values()):
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
				if name in cycle_length and output == False:
					if not cycle_start[name]:
						cycle_start[name] = num_pulses
					elif not cycle_length[name]:
						cycle_length[name] = num_pulses
	combined_cycle_start = []
	combined_cycle_length = []
	for module in loopback_conjunction_modules:
		combined_cycle_start.append(cycle_start[module])
		combined_cycle_length.append(cycle_length[module])
	while (num_unique := len(collections.Counter(combined_cycle_start))) != 1:
		if num_unique != len(combined_cycle_start):
			visited = dict()
			i = 0
			while i < len(combined_cycle_start):
				node = combined_cycle_start[i]
				if node in visited:
					other_i = visited[node]
					combined_cycle_length[other_i] *= combined_cycle_length[i] // math.gcd(combined_cycle_length[other_i], combined_cycle_length[i])
					combined_cycle_start[i:i+1] = []
					combined_cycle_length[i:i+1] = []
				else:
					visited[node] = i
					i += 1
		most_steps = max(combined_cycle_start)
		for i in range(len(combined_cycle_start)):
			if combined_cycle_start[i] != most_steps:
				combined_cycle_start[i] += ((most_steps - combined_cycle_start[i] - 1) // combined_cycle_length[i] + 1) * combined_cycle_length[i]
	print("Part 2: {}".format(combined_cycle_start[0]))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
