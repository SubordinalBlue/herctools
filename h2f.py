#!/usr/bin/env python3

import os, re, json, argparse

parser = argparse.ArgumentParser()
parser.add_argument("HERC_QUESTS", nargs='+', help='all Heracles quest files in a chapter')
parser.add_argument('-d', help='Use {id:name} dict, D', type=argparse.FileType('r'))
parser.add_argument('-o', help='Print {id:name} dict to stdout', action='store_true')
#parser.add_argument('-o', help='Print {id:name} dict to stdout', nargs='?', type=argparse.FileType('w'), const=sys.stdout, default=False)
parser.add_argument('-j', help='Output JSON', action='store_true')
parser.add_argument('-s', help='Output SNBT', action='store_true')
parser.add_argument('-v', help='Print extra debug info', action='store_true')
args = parser.parse_args()


# IDs are random 8 byte hex values, as strings ( Globals?! Baguette! )
IDdict = {}		# { name: id }
IDset = set()	# set of ids

def newID(id):
	while(id == 0 or id not in IDset):
		id = os.urandom(8).hex().upper()
		IDset.add(id)
	return id
	
def getID(name):
	IDdict[name] = IDdict.get(name, newID(0))
	return IDdict[name]

def print_IDdict():
	for name, id in IDdict.items():
		print(id, name)

def load_IDdict(dict_file):
	for line in dict_file.readlines():
		id, name = line.split(' ', 1)
		IDdict[name.strip()] = id
		IDset.add(id)		


# The Meat of the Matter

def convertCoord(n):
	return str(round(n/24,2)) + 'd'

def convertCoords(coords):
	return list(map(convertCoord, coords))

def convertHeraclesQuest(hercName, hercGroup, hercData):
	quest = {}
		
	quest['id'] = getID(hercName)
	quest['title'] = hercData['display']['title']['translate']
	quest['dependencies'] = list(map(getID, hercData['dependencies']))

	# For Inno's layouts, use the quest icon as the only task
	itemID = hercData['display']['icon']['item']['id']
	item = { 'id': itemID, 'count': 1 }
	task = { 'type': 'item', 'id': getID(itemID), 'item': item, 'count': 1 }
	tasks = [ task ]
	quest['tasks'] = tasks

	quest['x'], quest['y'] = convertCoords(hercData['display']['groups'][hercGroup]['position'])

	return quest	

def checkAssumptions(hercName, hercData):
	# Assumption 1: Heracles' quests are in only one group
	groups = hercData['display']['groups']
	if len(groups) > 1:
		print(f"Oops: {hercName} has multiple groups")
		exit()

def convertHeraclesChapter():
	ftbqData = {}
	ftbqData['quests'] = []

	for hercQuestFile in args.HERC_QUESTS:
		hercName = hercQuestFile.removesuffix('.json')
		hercData = json.load(open(hercQuestFile))
		checkAssumptions(hercName, hercData)

		hercGroup = list(hercData['display']['groups'].keys())[0]
		ftbqData['quests'].append(convertHeraclesQuest(hercName, hercGroup, hercData))
	
	ftbqData['default_hide_dependency_lines'] = 'false'
	ftbqData['default_quest_shape'] = ''
	ftbqData['filename'] = hercGroup
	ftbqData['title'] = hercGroup
	ftbqData['id'] = getID(hercGroup)
	ftbqData['group'] = ''
	ftbqData['order_index'] = 0
	ftbqData['quest_links'] = ''
	return ftbqData

def output(ftbqData):
	output = json.dumps(ftbqData, sort_keys=True, indent=2)
	if args.j:
		# Print as JSON
		print(output)
	if args.s:
		# Print as SNBT
		replacements = [
			(r',$', ''),					# remove trailing commas
			(r'"(\w+)":', r'\1:'),			# unquote keys
			(r'"(-?\d+\.?\d*d)"', r'\1')	# unquote numerical values
			]
		for pat,repl in replacements:
			output = re.sub(pat,repl,output)

		print(output)

def main():
	if args.d:
		load_IDdict(args.d)
		
	output(convertHeraclesChapter())
		
	if args.o:
		print_IDdict()
		exit()

# end matter
if __name__=='__main__':
	main()

# code scraps
