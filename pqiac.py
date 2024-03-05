#!/usr/bin/env python3
"""Put Quests in a Circle

Usage:
	pqiac [-n] <radius> <x> <y> <quest>...
	pqiac [-n] slice <count> <offset> <radius> <x> <y> <quest>...

Options:
	-n	Dry-run: print quest names and coordinates; doesn't alter files.

"""

from itertools import cycle
from docopt import docopt
from pprint import pprint
import math
import re

pi = math.pi

def pointsInCircle(x=0, y=0, r=100, n=10):
	return [(round(x+(math.cos(2*pi/n*i)*r)), round(y+(math.sin(2*pi/n*i)*r))) for i in range(0,n)]

def setPosInQuest(questFile, pos):
	posPattern = r'\s+-?\d+,\n\s+-?\d+\s+'
	with open(questFile, 'r+') as file:
		text = file.read()
		text = re.sub(posPattern, f'{pos[0]}, {pos[1]}', text)
		file.seek(0,0)
		file.write(text)
		file.truncate()
	
if __name__ == "__main__":
	args = docopt(__doc__)

	if args['slice']:
		n = int(args['<count>'])
		offset = int(args['<offset>'])
	else:
		n = len(args['<quest>'])
		offset = 0

	points = cycle(pointsInCircle(int(args['<x>']), int(args['<y>']), int(args['<radius>']), n))

	for _ in range(offset):
		next(points) 

	for quest in args['<quest>']:
		if args['-n']:
			pprint(quest, next(points))
		else:
			setPosInQuest(quest, next(points))
