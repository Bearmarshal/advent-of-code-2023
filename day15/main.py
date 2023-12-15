import collections
import functools
import io
import itertools
import math
import os
import re
import sys

def hash(string):
	hash = 0
	for character in string:
		hash += ord(character)
		hash *= 17
		hash %= 256
	return hash

class HashMap:
	def __init__(self):
		self.store = [[] for _ in range(256)]

	def put(self, key, value):
		bin = hash(key)
		for i in range(len(self.store[bin])):
			if self.store[bin][i][0] == key:
				self.store[bin][i][1] = value
				return
		else:
			self.store[bin].append([key, value])

	def remove(self, key):
		bin = hash(key)
		for i in range(len(self.store[bin])):
			if self.store[bin][i][0] == key:
				self.store[bin].pop(i)
				return
	
	def checksum(self):
		checksum = 0
		for i, bin in enumerate(self.store, 1):
			for j, (_, value) in enumerate(bin, 1):
				checksum += i * j * value
		return checksum
	
	def __str__(self):
		active_bins = []
		for i, bin in enumerate(self.store):
			if bin:
				active_bins.append(f"Box {i}: " + " ".join(f"[{key} {value}]" for key, value in bin))
		return "\n".join(active_bins)

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		steps = file.read().replace("\n", "").split(",")
	print("Part 1: {}".format(sum(hash(step) for step in steps)))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		steps = file.read().replace("\n", "").split(",")
	lenses = HashMap()
	for step in steps:
		if step[-2] == "=":
			lenses.put(step[:-2], int(step[-1]))
		else:
			lenses.remove(step[:-1])
	print("Part 2: {}".format(lenses.checksum()))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
