import random
from pathlib import Path
import pickle
from glob import glob
import random


class Character():
	def __init__(self, name='default'):
		self.name = name
		tempGrogs = Path.cwd() / 'characters' / 'tempGrogs'
		Grogs = Path.cwd() / 'characters' / 'Grogs'
		tempCompanions = Path.cwd() / 'characters' / 'tempCompanions'
		Companions = Path.cwd() / 'characters' / 'Companions'
		tempMagi = Path.cwd() / 'characters' / 'tempMagi'
		Magi = Path.cwd() / 'characters' / 'Magi'
		self.identifier = Path.cwd()/'identifier'
		self.filepaths = {'tg': tempGrogs,'g': Grogs,'tc': tempCompanions,'c': Companions,'tm': tempMagi,'m': Magi,'i': self.identifier}
		self.identifier = -1
		for key in self.filepaths:
			try:
				self.filepaths[key].mkdir(parents=True)
				print(str(self.filepaths[key]) + 'created')
			except:
				pass
		self.characteristics = {
			'int': 0,
			'per': 0,
			'str': 0,
			'sta': 0,
			'pre': 0,
			'com': 0,
			'dex': 0,
			'qik': 0,
		}
		self.charList = ['int', 'per', 'str', 'sta', 'pre', 'com', 'dex', 'qik']
		self.scorePoints = {
			-3: -6, -2: -3, -1: -1, 0: 0, 1: 1, 2: 3, 3: 6
		}



	def checkPoints(self):
		pointTotal = 0

		for x in self.characteristics:
			pointTotal += self.scorePoints[self.characteristics[x]]

		return pointTotal

	def genStats(self, *args):
		points = 7
		for x in args:
			try:
				points = int(x)
			except:
				None

		if points != 0:
			self.genStats(0)
		else:
			None
		prior = list(set(args) & set(self.charList))
		charListTemp = self.charList[:]
		if len(prior) > int(3 + points / 6):
			# print('too many prioritizations. Dropping ' + str(len(prior)-int(3+points/6)))
			prior = prior[:int(3 + points / 6)]
		else:
			None
		if len(prior) > 0:
			# print('priotitizing ' +str(prior))
			for char in prior:
				self.characteristics[char] = 3
				charListTemp.remove(char)
		else:
			None

		while self.checkPoints() != points:
			change = random.randint(-3, 3)
			modChar = charListTemp[random.randint(0, len(charListTemp)) - 1]
			self.characteristics[modChar] = change

		# print('points goal: ' + str(points))
		# print('current spent points: ' + str(self.checkPoints()))
		return (self.characteristics)

	def save(self, type='g'):
		#type is the type of character which determines the save folder
		print('saving ' + self.name)
		try:
			#Tries to access a saved character with the same name
			existingPath = list(Path.cwd().glob('**/'+self.name))[0]
			infile = open(existingPath, 'rb')
			savedChar = pickle.load(infile)
			infile.close()

			#Checks the identifier to see if we are saving an upadated version of the existing character.
			if savedChar.identifier != self.identifier:
				#Returns without saving if we aren't
				return('A different character with this name already exists')
			else:
				#updates type to whatever type existing character is
				type=list(self.filepaths.keys())[list(self.filepaths.values()).index(existingPath.parents[0])]
				pass

		except:
			# If we don't find an existing character, we need to create an identifier
			try:
				# Checking to make sure that we have an identifier.txt, if not creates one
				identF = open(self.filepaths['i']/'identifier.txt','x')
				self.identifier = 0
				identF.write(str(self.identifier))
				identF.close()

			except (FileExistsError):
				# If we already have one, reads the current identifier, adds one and resaves it.
				identF = open(self.filepaths['i']/'identifier.txt','r')
				try:
					ident = int(identF.read())
					self.identifier = ident + 1
					identF.close()
					identF = open(self.filepaths['i']/'identifier.txt','w')
					identF.write(str(self.identifier))
					identF.close()
				except:
					# If for whatever reason the contents of identifier.txt have changed resets the number. Could potentially cause problems later, and should probably implement something to scan existing characters for identifiers and pull the highest number.
					self.identifier = 0
					identF.write(str(self.identifier))
					identF.close()

		try:
			saveFile= open(self.filepaths[type]/self.name,'wb')
		except:
			print('Character not saved, likely invalid type')
			return('Character not saved, likely invalid type')
		pickle.dump(self,saveFile)
		saveFile.close()
		print('Character saved')
		return('Character saved')


	# print(self.characteristics)
	def load(self,name):
		print('attempting to load ' + name)
		print('using path ' + str(Path.cwd() / 'characters' / '**' / name))
		#p = list(Path.cwd().glob('**/'+name))[0]
		infile = open(list(Path.cwd().glob('**/'+name))[0], 'rb')
		char = pickle.load(infile)
		print('successfully unpickled')
		infile.close()
		try:
			char.isCharacter()
		except:
			print('load failed, provided pickle was not a character')
			return('load failed, provided pickle was not a character')
		self.name = char.name
		self.characteristics = char.characteristics
		self.identifier = char.identifier
		return(self.name + ' successfully loaded')

	def isCharacter(self):
		return True

	def display(self):
		output = 'Character name: ' + str(self.name) + '\n'
		for char in self.characteristics:
			output += char.capitalize() + ': ' + str(self.characteristics[char]) + ' '
		return output
