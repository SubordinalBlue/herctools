#!/usr/bin/env python3
"""Put Quests in a Circle

Usage:
	pqiac [-n|-d] <radius> <x> <y> <quest>...
	pqiac [-n|-d] [--arc] <count> <offset> <radius> <x> <y> <quest>...

Options:
	-n	dry-run: print quest names and coordinates; doesn't alter files.
	-d  debug: print extra info; doesn't alter files 

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
	args = docopt(__doc__, options_first = True)
	dryrun = True if args['-n'] else False
	debug = True if args['-d'] else False

	quests_count = len(args['<quest>'])

	if debug:
		pprint(args)

	if args['--arc']:
		count = int(args['<count>'])
		start = int(args['<offset>'])
	else:
		count = quests_count
		start = 0

	if count == 0:
		count = quests_count

	points = pointsInCircle(int(args['<x>']), int(args['<y>']), int(args['<radius>']), count)
	circle = cycle(points)

	# Fixed cycle of circle points, with a shifted loop of quests
	# Done this way so print-out (-n or -d options) matches model of ultimate result.

	quests = cycle(args['<quest>'] + [None]*(count-quests_count))
	for _ in range((count - start) % count):
		next(quests)

	for _ in range(count):
		q = next(quests)
		p = next(circle)
		if dryrun or debug:
			print(p, q)
		elif q:
			setPosInQuest(q, p)

# Original, straight-forward way:
#	for _ in range(start):
#		next(circle) #if not debug else print(next(circle))
#		
#	for quest in args['<quest>']:
#		setPosInQuest(quest, next(circle)) if not dryrun else print(next(circle), quest)
