import collections
import io
import itertools
import math
import os
import re
import sys

def part1(filename):
	print("Part 1: {}".format(sum(rank * bid for (_, bid), rank in zip(sorted({{(1, 1, 1, 1, 1): 0, (1, 1, 1, 2): 1, (1, 2, 2): 2, (1, 1, 3): 3, (2, 3): 4, (1, 4): 5, (5,): 6}[tuple(sorted(collections.Counter(hand).values()))] * len("23456789TJQKA") ** len(hand) + sum({card: value for value, card in enumerate("23456789TJQKA")}[card] * len("23456789TJQKA") ** (len(hand) - index - 1) for index, card in enumerate(hand)): int(bid) for hand, bid in re.findall(r"(?P<hand>[2-9TJQKA]{5}) (?P<bid>\d+)", io.open(filename, mode = 'r').read())}.items()), itertools.count(1)))))

def part2(filename):
	with io.open(filename, mode = 'r') as file:
		lines = [line for line in file]

	cards = "J23456789TQKA"
	card_values = {card: value for card, value in zip(cards, itertools.count())}
	type_values = {(1, 1, 1, 1, 1): 0, (1, 1, 1, 2): 1, (1, 2, 2): 2, (1, 1, 3): 3, (2, 3): 4, (1, 4): 5, (5,): 6}

	hands = dict()
	for line in lines:
		hand_match = re.match(r"(?P<hand>[2-9TJQKA]{5}) (?P<bid>\d+)", line)
		if hand_match:
			hand = hand_match["hand"]
			raw_type = collections.Counter(hand)
			jokers = raw_type.pop("J", 0)
			hand_type = sorted(raw_type.values())
			if hand_type == []:
				hand_type = [0]
			hand_type[-1] += jokers
			value = type_values[tuple(hand_type)]
			for card in hand:
				value *= len(cards)
				value += card_values[card]
			hands[value] = int(hand_match["bid"])

	print("Part 2: {}".format(sum(rank * bid for (_, bid), rank in zip(sorted(hands.items()), itertools.count(1)))))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = os.path.dirname(sys.argv[0]) + "/input.txt"
	part1(filename)
	part2(filename)
