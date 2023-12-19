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
	
class PartRange(Part):
	def split(self, attribute, threshold):
		match attribute:
			case "x":
				return PartRange((self.x[0], threshold - 1), self.m, self.a, self.s), PartRange((threshold, self.x[1]), self.m, self.a, self.s)
			case "m":
				return PartRange(self.x, (self.m[0], threshold - 1), self.a, self.s), PartRange(self.x, (threshold, self.m[1]), self.a, self.s)
			case "a":
				return PartRange(self.x, self.m, (self.a[0], threshold - 1), self.s), PartRange(self.x, self.m, (threshold, self.a[1]), self.s)
			case "s":
				return PartRange(self.x, self.m, self.a, (self.s[0], threshold - 1)), PartRange(self.x, self.m, self.a, (threshold, self.s[1]))
			
	def count_parts(self):
		return max(0, self.x[1] - self.x[0] + 1) * max(0, self.m[1] - self.m[0] + 1) * max(0, self.a[1] - self.a[0] + 1) * max(0, self.s[1] - self.s[0] + 1)
	
	def __repr__(self):
		return "{" + f"x={self.x[0]}..{self.x[1]},m={self.m[0]}..{self.m[1]},a={self.a[0]}..{self.a[1]},s={self.s[0]}..{self.s[1]}" + "}"

class Workflow:
	def __init__(self, name, rules):
		self.name = name
		self.rules = rules

	def process(self, part, workflows):
		for rule in self.rules:
			if comparison_match := re.match(r"(?P<attribute>\w+)(?P<operator>[<>])(?P<threshold>\d+):(?P<action>\w+)", rule):
				attribute = comparison_match["attribute"]
				operator = comparison_match["operator"]
				threshold = int(comparison_match["threshold"])
				value = part.__dict__[attribute]
				matches = value < threshold if operator == "<" else value > threshold
				if matches:
					match comparison_match["action"]:
						case "A":
							return True
						case "R":
							return False
						case workflow:
							return workflows[workflow].process(part, workflows)
			else:
				match rule:
					case "A":
						return True
					case "R":
						return False
					case workflow:
						return workflows[workflow].process(part, workflows)
					
	def preprocess(self, part_range, workflows):
		accepted_ranges = []
		for rule in self.rules:
			if not part_range.count_parts():
				break
			if comparison_match := re.match(r"(?P<attribute>\w+)(?P<operator>[<>])(?P<threshold>\d+):(?P<action>\w+)", rule):
				attribute = comparison_match["attribute"]
				operator = comparison_match["operator"]
				threshold = int(comparison_match["threshold"]) + (1 if operator == ">" else 0)
				under, over = part_range.split(attribute, threshold)
				selected, part_range = (under, over) if operator == "<" else (over, under)
				if selected.count_parts():
					match comparison_match["action"]:
						case "A":
							accepted_ranges.append(selected)
						case "R":
							pass
						case workflow:
							accepted_ranges += workflows[workflow].preprocess(selected, workflows)
			else:
				match rule:
					case "A":
						accepted_ranges.append(part_range)
					case "R":
						pass
					case workflow:
						accepted_ranges += workflows[workflow].preprocess(part_range, workflows)
		return accepted_ranges
		
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
		workflows_input, parts_input = file.read().strip().split("\n\n")
	workflows = {name: Workflow(name, rules.split(",")) for name, rules in re.findall(r"(\w+)\{([^}]+)\}", workflows_input)}
	workflow_in = workflows["in"]
	allpart = PartRange((1, 4000), (1, 4000), (1, 4000), (1, 4000))
	accepted_part_ranges = [part_range for part_range in workflow_in.preprocess(allpart, workflows)]
	print("Part 2: {}".format(sum(part_range.count_parts() for part_range in accepted_part_ranges)))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
