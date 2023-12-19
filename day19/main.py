import collections
import functools
import io
import itertools
import math
import os
import re
import sys

accepted_parts = []

def accept(part):
	accepted_parts.append(part)

def reject(part):
	pass

class Part:
	def __init__(self, x, m, a, s):
		self.x = x
		self.m = m
		self.a = a
		self.s = s

	def rating(self):
		return self.x + self.m + self.a + self.s
	
	def __repr__(self):
		return "{x=" + str(self.x) + ",m=" + str(self.m) + ",a=" + str(self.a) + ",s=" + str(self.s) + "}"

def compare_attribute_to(attribute, operator, value, part):
	if operator == "<":
		return part.__dict__[attribute] < value
	else:
		return part.__dict__[attribute] > value

class Workflow:
	def __init__(self, name, rules):
		self.name = name
		self.rules = []
		for rule in rules:
			if comparison_match := re.match(r"(?P<attribute>\w+)(?P<operator>[<>])(?P<value>\d+):(?P<action>\w+)", rule):
				attribute = comparison_match["attribute"]
				operator = comparison_match["operator"]
				value = int(comparison_match["value"])
				matcher = functools.partial(compare_attribute_to, attribute, operator, value)
				match comparison_match["action"]:
					case "A":
						action = lambda part, workflows: True
					case "R":
						action = lambda part, workflows: False
					case workflow:
						action = functools.partial(lambda part, workflows, w: workflows[w].process(part, workflows), w=workflow)
				self.rules.append((matcher, action))
			else:
				match rule:
					case "A":
						self.default = lambda part, workflows: True
					case "R":
						self.default = lambda part, workflows: False
					case workflow:
						self.default = functools.partial(lambda part, workflows, w: workflows[w].process(part, workflows), w=workflow)

	def process(self, part, workflows):
		for matcher, action in self.rules:
			if matcher(part):
				return action(part, workflows)
		else:
			return self.default(part, workflows)
		
	def __repr__(self):
		return self.name

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		workflows_input, parts_input = file.read().strip().split("\n\n")
	workflows = {name: Workflow(name, rules.split(",")) for name, rules in re.findall(r"(\w+)\{([^}]+)\}", workflows_input)}
	workflow_in = workflows["in"]
	parts = [Part(int(x), int(m), int(a), int(s)) for x, m, a, s in re.findall(r"\{x=(\d+),m=(\d+),a=(\d+),s=(\d+)\}", parts_input)]
	accepted_parts = [part for part in parts if workflow_in.process(part, workflows)]
	print("Part 1: {}".format(sum(part.rating() for part in accepted_parts)))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		steps = file.read().replace("\n", "").split(",")
	print("Part 2: {}".format(2))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	# part2(filename)
