import random
from pathlib import Path
import pickle
from glob import glob
import random
import math
import Levenshtein
import re

class Ability():
	def __init__(self,name,speciality='default'):
		self.referencePath = Path.cwd()/'referenceFiles'
		self.types = ('(General)','(Academic)','(Arcane)','(Martial)','(Supernatural)')
		self.abilitiesRef = {'name':'','description':'','needTraining': False ,'specialties':[],'type':self.types[0],'xp':0,'score':0}
		self.abilitiesLib = {}
		self.name = ''
		self.description = ''
		self.needTraining = False
		self.type = ''
		self.xp = 0
		self.score = 0
		try:
			self.referencePath.mkdir(parents=True)
		except:
			pass
		self.loadReference()

		similarity = 100
		for x in self.abilitiesLib:
			#print('difference between ' + x + ' and ' + name.upper() + ' is ' + str(Levenshtein.distance(x,name.upper())))
			if Levenshtein.distance(x,name.upper()) < similarity:
				self.name = x
				similarity = Levenshtein.distance(x,name.upper())
			else:
				pass
		if speciality == 'default':
			self.specialty = random.choice(self.abilitiesLib[self.name]['specialties'])
		else:
			self.specialty = speciality
		self.description = self.abilitiesLib[self.name]['description']
		self.needTraining = self.abilitiesLib[self.name]['needTraining']
		self.type = self.abilitiesLib[self.name]['type']




	def addXp(self,xp):
		self.xp += xp
		self.score = int((-5+math.sqrt(25+40*xp))/10)


	def loadReference(self):
		with open(self.referencePath / 'abilities.txt', 'r',encoding='utf-8') as file:
			refsheet = file.readlines()
		searchingFor='name'
		newAbility = self.abilitiesRef.copy()
		for line in refsheet:

			if searchingFor == 'name':
				if len(line) < 2:
					continue
				elif line[-2] == '*':
					newAbility['needTraining'] = True
					data = line[:-2]
				else:
					newAbility['needTraining'] = False
					data = line[:-1]
				newAbility['name']= data
				searchingFor = 'description'
				description = ''
			elif searchingFor == 'description':
				if 'Specialties:' in line:
					x = line.split('Specialties:')
					description = description + x[0]
					newAbility['description']=description
					searchingFor = 'specialties'
					specialities = x[1]
				else:
					description = description + line
			elif searchingFor == 'specialties':
				for type in self.types:
					if type in line:
						newAbility['type']=type
						specialities = specialities + line.split(type)[0]
						specialities = specialities.replace(type,'').replace('\n','').replace('.','').split(',')
						for x in range(len(specialities)):
							specialities[x] = specialities[x].strip()
						newAbility['specialties']=specialities
						self.abilitiesLib[newAbility['name']]=newAbility
						searchingFor = 'name'
						newAbility = {}
						break
					else:
						pass
				if not type in line:
					specialities = specialities + line
	def summary(self):
		return('Name: ' + self.name + '\n Description: ' + self.description + '\n Type: ' + self.type + '\n Speciality: ' + self.specialty + '\n XP: ' + str(self.xp) + '\n Score: ' + str(self.score))


	def availableAbilities(self):
		available = ''
		for a in self.types:
			available += '\n' + a + ': \n'
			for x in self.abilitiesLib:
				if self.abilitiesLib[x]['type'] == a:
					available += x + '\n'
		return available

	def abilityList(self):
		result = []
		for x in self.abilitiesLib:
			result.append(x)
		return result


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
		self.referenceAbility = Ability('charm')
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
		language = Ability('LIVING LANGUAGE')
		print(language.name)
		self.abilities = {language.name: language}



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

	def genAbilities(self,xp):
		while xp > 0:
			change = random.randint(1,int(xp/2)+1)
			xp -= change
			randAbility = random.choice(list(self.abilities['(LIVING LANGUAGE)'].abilitiesLib.values()))
			print(randAbility)
			print('Applying ' + str(xp) + ' xp to ' + randAbility['name'])
			self.abilities[randAbility['name']] = Ability(randAbility['name'])
			self.abilities[randAbility['name']].addXp(change)

	def printAbilities(self):
		for x in self.abilities.values():
			print(x.summary())
			print('\n \n \n')




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
		for x in self.abilities:
			p = self.filepaths[type]/('abi.' + self.name)
			try:
				print(p)
				p.mkdir(parents=True,exist_ok=True)
				print('made directory')
			except:
				None
			saveFile = open(self.filepaths[type]/('abi.' + self.name)/x,'wb')
			pickle.dump(self.abilities[x],saveFile)
		print('Character saved')
		return('Character saved')


	# print(self.characteristics)
	def load(self,name):
		print('attempting to load ' + name)
		print('using path ' + str(Path.cwd() / 'characters' / '**' / name))
		#p = list(Path.cwd().glob('**/'+name))[0]
		infile = open(list(Path.cwd().glob('**/'+name))[0], 'rb')
		char = pickle.load(infile)
		abilityF = Path(list(Path.cwd().glob('**/'+name))[0]).parent/('abi.'+char.name)
		infile.close()
		print('successfully unpickled')
		try:
			char.isCharacter()
		except:
			print('load failed, provided pickle was not a character')
			return('load failed, provided pickle was not a character')
		self.name = char.name
		self.characteristics = char.characteristics
		self.identifier = char.identifier
		print('loading abilities')
		print(abilityF)
		for x in list(abilityF.glob('*')):
			try:
				file = open(x,'rb')
				print('opened' + str(x))
				try:
					abilityTemp = pickle.load(file)
				except Exception as e:
					print(e)
				print('unpickled')
				self.abilities[abilityTemp.name]=abilityTemp
				print('abilityLoaded')
			except:
				None


		return(self.name + ' successfully loaded')

	def isCharacter(self):
		return True

	def display(self):
		output = 'Character name: ' + str(self.name) + '\n'
		for char in self.characteristics:
			output += char.capitalize() + ': ' + str(self.characteristics[char]) + ' '
		output += '\nAbilities: '
		for x in self.abilities:
			output += '\n' + x + ': {' + str(self.abilities[x].score) + '} '
		return output







