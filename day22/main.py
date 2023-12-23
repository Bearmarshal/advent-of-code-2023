import collections
import enum
import io
import itertools
import math
import os
import queue
import re
import sys

def sign(x):
	return bool(x > 0) - bool(x < 0)

class EnumContainsValueMeta(enum.EnumMeta):
	def __contains__(cls, value):
		return value in cls.__members__.values()

class Direction(tuple, enum.Enum):
	def __init__(self, delta):
		self.dz, self.dy, self.dx = delta

	def __neg__(self):
		return Direction((-self.dz, -self.dy, -self.dx))
	
	def opposite(self):
		return -self
	
	BELOW = (-1, 0, 0)
	ABOVE = (1, 0, 0)
	UP = (0, -1, 0)
	DOWN = (0, 1, 0)
	LEFT = (0, 0, -1)
	RIGHT = (0, 0, 1)

BELOW = Direction.BELOW
ABOVE = Direction.ABOVE
UP = Direction.UP
DOWN = Direction.DOWN
LEFT = Direction.LEFT
RIGHT = Direction.RIGHT

class Position(tuple):
	def __new__(cls, z, y, x):
		self = tuple.__new__(cls, (z, y, x))
		self.z = z
		self.y = y
		self.x = x
		return self

	def __add__(self, direction: Direction):
		return Position(self.z + direction.dz, self.y + direction.dy, self.x + direction.dx)
	
	def get_manhattan_distance(self, other):
		return abs(self.z - other.z) + abs(self.y - other.y) + abs(self.x - other.x)
	
	def get_direction(self, other):
		if other == self:
			return Direction.ABOVE
		else:
			return Direction((sign(other.z - self.z), sign(other.y - self.y), sign(other.x - self.x)))
	
	def get_item(self, item_map):
		if self.y in range(len(item_map)) and self.x in range(len(item_map[self.y])):
			return item_map[self.z][self.y][self.x]
		else:
			return None
	
	def set_item(self, item_map, item):
		if self.y in range(len(item_map)) and self.x in range(len(item_map[self.y])):
			item_map[self.z][self.y][self.x] = item

	def __repr__(self):
		return f"{self.x},{self.y},{self.z}"

class Brick:
	def __init__(self, end0, end1):
		self.direction = end0.get_direction(end1)
		if self.direction in (ABOVE, DOWN, RIGHT):
			self.low_end = end0
			self.high_end = end1
		else:
			self.low_end = end1
			self.high_end = end0
			self.direction = self.direction.opposite()
		self.above = []
		self.below = []

	def __add__(self, direction: Direction):
		return Brick(self.low_end + direction, self.high_end + direction)
	
	def intersects(self, other):
		if self.low_end.z > other.high_end.z or other.low_end.z > self.high_end.z:
			return False
		if self.low_end.y > other.high_end.y or other.low_end.y > self.high_end.y:
			return False
		if self.low_end.x > other.high_end.x or other.low_end.x > self.high_end.x:
			return False
		return True
	
	def __contains__(self, position: Position):
		return position.z in range(self.low_end.z, self.high_end.z + 1) and position.y in range(self.low_end.y, self.high_end.y + 1) and position.x in range(self.low_end.x, self.high_end.x + 1)
	
	def __repr__(self):
		return f"{self.low_end}~{self.high_end}"


def part1(filename):
	with io.open(filename, mode = 'r') as file:
		bricks = [Brick(Position(int(z0), int(y0), int(x0)), Position(int(z1), int(y1), int(x1))) for x0, y0, z0, x1, y1, z1 in re.findall(r"(\d+),(\d+),(\d+)~(\d+),(\d+),(\d+)", file.read())]
	height_map = collections.defaultdict(set)
	z_max = 0
	for brick in bricks:
		height_map[brick.low_end.z].add(brick)
		height_map[brick.high_end.z].add(brick)
		z_max = max(z_max, brick.high_end.z)
	for z in range(2, z_max + 1):
		for brick in list(height_map[z]):
			if brick.low_end.z != z:
				continue
			height_map[z].remove(brick)
			if brick.high_end.z != z:
				height_map[brick.high_end.z].remove(brick)
			while brick.low_end.z > 1 and not brick.below:
				below = brick + BELOW
				for brick_below in height_map[below.low_end.z]:
					if below.intersects(brick_below):
						brick.below.append(brick_below)
						brick_below.above.append(brick)
				if not brick.below:
					brick = below
			height_map[brick.low_end.z].add(brick)
			height_map[brick.high_end.z].add(brick)
	safe_bricks = sum(all(len(above.below) > 1 for above in brick.above) for z in range(1, z_max + 1) for brick in height_map[z] if brick.low_end.z == z)
	print("Part 1: {}".format(safe_bricks))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		bricks = [Brick(Position(int(z0), int(y0), int(x0)), Position(int(z1), int(y1), int(x1))) for x0, y0, z0, x1, y1, z1 in re.findall(r"(\d+),(\d+),(\d+)~(\d+),(\d+),(\d+)", file.read())]
	height_map = collections.defaultdict(set)
	z_max = 0
	for brick in bricks:
		height_map[brick.low_end.z].add(brick)
		height_map[brick.high_end.z].add(brick)
		z_max = max(z_max, brick.high_end.z)
	for z in range(2, z_max + 1):
		for brick in list(height_map[z]):
			if brick.low_end.z != z:
				continue
			height_map[z].remove(brick)
			if brick.high_end.z != z:
				height_map[brick.high_end.z].remove(brick)
			while brick.low_end.z > 1 and not brick.below:
				below = brick + BELOW
				for brick_below in height_map[below.low_end.z]:
					if below.intersects(brick_below):
						brick.below.append(brick_below)
						brick_below.above.append(brick)
				if not brick.below:
					brick = below
			height_map[brick.low_end.z].add(brick)
			height_map[brick.high_end.z].add(brick)
	will_fall = 0
	for z in range(1, z_max + 1):
		for brick in height_map[z]:
			if brick.low_end.z != z:
				continue
			removed = {brick}
			open_set = collections.deque(brick.above)
			while open_set:
				brick = open_set.popleft()
				if brick in removed:
					continue
				if not set(brick.below) - removed:
					will_fall += 1
					removed.add(brick)
					open_set.extend(brick.above)
	print("Part 2: {}".format(will_fall))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
