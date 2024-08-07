#!/usr/bin/env python3

import re, json, random, argparse

parser = argparse.ArgumentParser()
parser.add_argument("HERC_QUESTS", nargs='+', help='all Heracles quest files in a chapter')
parser.add_argument('-d', help='Use {id:name} dict, D', type=argparse.FileType('r'))
parser.add_argument('-o', help='Print {id:name} dict to stdout', action='store_true')
parser.add_argument('-k', help="Convert from Inno's 'just an icon' style", action='store_true')
parser.add_argument('-j', help='Output JSON', action='store_true')
parser.add_argument('-s', help='Output SNBT', action='store_true')
parser.add_argument('-v', help='Print extra debug info', action='store_true')
args = parser.parse_args()

def mesg(thing):
	if args.v:
		print(thing)

def applyReplacements(replacements, text):
	'''replacements is a list of pattern and replacement tuples'''
	for pat, repl in replacements:
		text = re.sub(pat, repl, text)
	return text

IDdict = {}	# { name: id }, IDs are random 8 byte hex values, as strings
maxID = 2**64 - 1

def _newID(id):
	while (id == 0) or (id in IDdict.values()):
		bytesID = random.randbytes(8)
		while bytesID[0] > 127:
			bytesID = random.randbytes(8)
		id = bytesID.hex().upper()
		#id = random.randbytes(8).hex().upper()
	return id

def newID():
	IDdict['-'] = _newID(0)
	return IDdict['-']
	
def getID(name):
	if name not in IDdict:
		IDdict[name] = _newID(0)
	return IDdict[name]

def print_IDdict():
	for name, id in IDdict.items():
		print(id, name)

def load_IDdict(dict_file):
	for line in dict_file.readlines():
		id, name = line.split(' ', 1)
		IDdict[name.strip()] = id
		#IDset.add(id)

# The Meat of the Matter

def convertCoord(n):
	return str(round(n/24,2)) + 'd'

def convertCoords(coords):
	return list(map(convertCoord, coords))

def convertTask(taskName, hercTask):
	ftbqTask = {}
	ftbqTask['id'] = newID() #getID(taskName)

	match hercTask['type']:
		case 'heracles:item':
			ftbqTask['type'] = 'item'
			ftbqTask['item'] = {}
			ftbqTask['item']['id'] = hercTask['item']
			ftbqTask['item']['count'] = hercTask['amount']
		case 'heracles:check':
			ftbqTask['type'] = 'checkmark'
		case 'heracles:xp':
			# double check this against Heracles XP Task
			ftbqTask['type'] = 'xp'
			match hercTask['xptype']:
				case 'POINTS':
					ftbqTask['value'] = '1L'
				case 'LEVEL':
					ftbqTask['value'] = str(hercTask['amount']) + 'L'
		case _:
			print(f"Oopsie: I don't yet understand the task type, {hercTask['type']}")
			exit()
	return ftbqTask

def convertReward(rewardName, hercReward):
	ftbqReward = {}
	ftbqReward['id'] = newID() #getID(rewardName)
	match hercReward['type']:
		case 'heracles:item':
			ftbqReward['type'] = 'item'
			ftbqReward['item'] = {}
			ftbqReward['item']['id'] = hercReward['item']['id']
			if 1 < hercReward['item']['count']:
				ftbqReward['item']['count'] = 1
				ftbqReward['count'] = hercReward['item']['count']
			else:
				ftbqReward['item']['count'] = hercReward['item']['count']
			#ftbqReward['item']['count'] = hercReward['item']['count']
			
		case 'heracles:xp':
			match hercReward['xptype']:
				case 'POINTS':
					ftbqReward['type'] = 'xp'
					ftbqReward['value'] = str(hercReward['amount']) + 'L'
				case 'LEVEL':
					ftbqReward['type'] = 'xp_levels'
					ftbqReward['xp_levels'] = hercReward['amount']
				case _:
					print(f"Oopsie: problem converting Reward, {rewardName}")
		case _:
			print(f"Oopsie: I don't yet understand the reward type, {hercReward['type']}")
			exit()
	return ftbqReward

def convertTasks(hercTasks):
	ftbqTasks = []
	for name, task in hercTasks.items():
		ftbqTasks.append(convertTask(name, task))
		mesg(ftbqTasks)
	return ftbqTasks

def convertRewards(hercRewards):
	ftbqRewards = []
	for name, reward in hercRewards.items():
		ftbqRewards.append(convertReward(name, reward))
	return ftbqRewards

def filterHermes(line):
	replacements = [
		(r'<.*>', ''),
		(r'&&', r'&'),
		(r'/([abcdef\d])/([\w ]+)/\1/', r'&\1\2&r')
		#(r'/b/([\w ]+)/b/', r'&i\1&r')
		]
	return applyReplacements(replacements, line)
	#return re.sub(r'<.*>', '', line)

def convertDescription(hercDesc):
	return list(map(filterHermes, hercDesc))

def convertQuest(hercName, hercGroup, hercData):
	quest = {}
	quest['id'] = getID(hercName)
	quest['title'] = hercData['display']['title']['translate']
	quest['dependencies'] = list(map(getID, hercData['dependencies']))

	if args.k:
		# For Inno's 'just an icon' style starting templates, use the quest icon as the only task
		itemID = hercData['display']['icon']['item']['id']
		item = { 'id': itemID, 'count': 1 }
		task = { 'type': 'item', 'id': getID(hercName), 'item': item }
		tasks = [ task ]
		quest['tasks'] = tasks
	else:
		quest['tasks'] = convertTasks(hercData['tasks'])

	quest['rewards'] = convertRewards(hercData['rewards'])
	quest['description'] = convertDescription(hercData['display']['description'])
	quest['x'], quest['y'] = convertCoords(hercData['display']['groups'][hercGroup]['position'])
	#print(hercName, hercData['settings']['showDependencyArrow'])
	if not hercData['settings']['showDependencyArrow']:
		quest['hide_dependency_lines'] = 'true'
	return quest

def checkAssumptions(hercName, hercData):
	# Assumption 1: Input Heracles' quests are in only one group
	groups = hercData['display']['groups']
	if len(groups) > 1:
		print(f"Oops: {hercName} has multiple groups")
		exit()

def convertChapter():
	ftbqData = {}

	ftbqData['quests'] = []
	for hercQuestFile in args.HERC_QUESTS:
		hercName = hercQuestFile.removesuffix('.json')
		hercData = json.load(open(hercQuestFile))
		checkAssumptions(hercName, hercData)
		hercGroup = list(hercData['display']['groups'].keys())[0]
		ftbqData['quests'].append(convertQuest(hercName, hercGroup, hercData))

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
			(r',\n', '\n'),					# remove trailing commas
			(r'"(\w+)":', r'\1:'),			# unquote keys
			(r'"(-?\d+\.?\d*d)"', r'\1'),	# unquote numerical values
			(r'"((?:true|false))"', r'\1'),	# unquote boolean values
			(r'(dependencies: \[)\n\s+("[A-F\d]{16}")\n\s+(\],?)\n', r'\1\2\3\n'),
			]
		output = applyReplacements(replacements, output)
		#for pat,repl in replacements:
		#	output = re.sub(pat,repl,output)

		print(output)

def main():
	if args.d:
		load_IDdict(args.d)
		
	output(convertChapter())
		
	if args.o:
		print_IDdict()
		exit()

# end matter
if __name__=='__main__':
	main()

# code scraps
