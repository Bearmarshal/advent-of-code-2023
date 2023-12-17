import collections
import enum
import io
import itertools
import math
import os
import queue
import re
import sys

class EnumContainsValueMeta(enum.EnumMeta):
	def __contains__(cls, value):
		return value in cls.__members__.values()

class Direction(tuple, enum.Enum):
	def __init__(self, delta):
		self.dy, self.dx = delta

	def __neg__(self):
		return Direction((-self.dy, -self.dx))
	
	def opposite(self):
		return -self
	
	def right(self):
		return Direction((-self.dy, self.dx))
	
	def left(self):
		return Direction((self.dy, -self.dx))
	
	UP = (-1, 0)
	DOWN = (1, 0)
	LEFT = (0, -1)
	RIGHT = (0, 1)

UP = Direction.UP
DOWN = Direction.DOWN
LEFT = Direction.LEFT
RIGHT = Direction.RIGHT

class Position(tuple):
	def __new__(cls, y, x):
		self = tuple.__new__(cls, (y, x))
		self.y = y
		self.x = x
		return self

	def __add__(self, direction: Direction):
		return Position(self.y + direction.dy, self.x + direction.dx)
	
	def get_manhattan_distance(self, other):
		return abs(self.y - other.y) + abs(self.x - other.x)
	
	def get_item(self, item_map):
		if self.y in range(len(item_map)) and self.x in range(len(item_map[self.y])):
			return item_map[self.y][self.x]
		else:
			return None
	
	def set_item(self, item_map, item):
		if self.y in range(len(item_map)) and self.x in range(len(item_map[self.y])):
			item_map[self.y][self.x] = item

def part1(filename):
	with io.open(filename, mode = 'r') as file:
		heat_map = [line.strip() for line in file if not line.isspace()]
	height = len(heat_map)
	width = len(heat_map[0])
	open_set = queue.PriorityQueue()
	closed_set = dict() # position: {direction: [accumulated_heat_loss] * 4}
	start = Position(0, 0)
	target = Position(height - 1, width - 1)
	for direction in Direction:
		neighbour = start + direction
		if heat_loss := neighbour.get_item(heat_map):
			open_set.put((neighbour.get_manhattan_distance(target) + int(heat_loss), int(heat_loss), neighbour, direction, 1))
	while not open_set.empty():
		_, accumulated_heat_loss, position, in_direction, steps = open_set.get()
		if position == target:
			break
		if position in closed_set:
			better_than_any = False
			for direction in Direction:
				step_start = steps if direction == in_direction else 0
				for i in range(step_start, 4):
					if accumulated_heat_loss < closed_set[position][direction][i]:
						closed_set[position][direction][i] = accumulated_heat_loss
						better_than_any = True
			if not better_than_any:
				continue
		else:
			closed_set[position] = {direction: [float("inf")] * (steps if direction == in_direction else 0) + [accumulated_heat_loss] * (4 - (steps if direction == in_direction else 0)) for direction in Direction}
		for direction in Direction:
			if direction == in_direction.opposite():
				continue
			if direction == in_direction and steps >= 3:
				continue
			neighbour = position + direction
			if heat_loss := neighbour.get_item(heat_map):
				neighbour_steps = steps + 1 if direction == in_direction else 1
				neighbour_accumulated_heat_loss = accumulated_heat_loss + int(heat_loss)
				heuristic = neighbour_accumulated_heat_loss + neighbour.get_manhattan_distance(target)
				open_set.put((heuristic, neighbour_accumulated_heat_loss, neighbour, direction, neighbour_steps))
	print("Part 1: {}".format(accumulated_heat_loss))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		heat_map = [line.strip() for line in file if not line.isspace()]
	height = len(heat_map)
	width = len(heat_map[0])
	min_steps = 4
	max_controlled_steps = 10 - min_steps
	open_set = queue.PriorityQueue()
	closed_set = dict() # position: {direction: [accumulated_heat_loss] * (max_steps + 1)}
	start = Position(0, 0)
	target = Position(height - 1, width - 1)
	for direction in Direction:
		forced_steps = min_steps
		neighbour = start
		neighbour_accumulated_heat_loss = 0
		for i in range(forced_steps):
			neighbour += direction
			if heat_loss := neighbour.get_item(heat_map):
				neighbour_accumulated_heat_loss += int(heat_loss)
			else:
				break
		if neighbour.get_item(heat_map):
			heuristic = neighbour_accumulated_heat_loss + neighbour.get_manhattan_distance(target)
			open_set.put((heuristic, neighbour_accumulated_heat_loss, neighbour, direction, 0))
	while not open_set.empty():
		_, accumulated_heat_loss, position, in_direction, steps = open_set.get()
		if position == target:
			break
		if position in closed_set and in_direction in closed_set[position]:
			better_than_any = False
			for i in range(steps, (max_controlled_steps + 1)):
				if accumulated_heat_loss < closed_set[position][in_direction][i]:
					closed_set[position][in_direction][i] = accumulated_heat_loss
					better_than_any = True
			if not better_than_any:
				continue
		else:
			if position not in closed_set:
				closed_set[position] = dict()
			closed_set[position][in_direction] = [float("inf")] * steps + [accumulated_heat_loss] * ((max_controlled_steps + 1) - steps)
		for direction in Direction:
			if direction == in_direction.opposite():
				continue
			if direction == in_direction:
				if steps >= max_controlled_steps:
					continue
				forced_steps = 1
				neighbour_steps = steps + 1
			else:
				forced_steps = min_steps
				neighbour_steps = 0
			neighbour = position
			neighbour_accumulated_heat_loss = accumulated_heat_loss
			for i in range(forced_steps):
				neighbour += direction
				if heat_loss := neighbour.get_item(heat_map):
					neighbour_accumulated_heat_loss += int(heat_loss)
				else:
					break
			if neighbour.get_item(heat_map):
				heuristic = neighbour_accumulated_heat_loss + neighbour.get_manhattan_distance(target)
				open_set.put((heuristic, neighbour_accumulated_heat_loss, neighbour, direction, neighbour_steps))
	print("Part 2: {}".format(accumulated_heat_loss))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
