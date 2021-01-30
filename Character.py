import random
import discord
from discord.ext import commands

class Character():
	def __init__(self,name):
		self.name = name
		self.characteristics = {
			'int':0,
			'per':0,
			'str':0,
			'sta':0,
			'pre':0,
			'com':0,
			'dex':0,
			'qik':0,
		}
		self.charList=['int','per','str','sta','pre','com','dex','qik']
		self.scorePoints = {
		-3:-6,-2:-3,-1:-1,0:0,1:1,2:3,3:6
		}
	
	def checkPoints(self):
		pointTotal=0
		
		for x in self.characteristics:
			pointTotal += self.scorePoints[self.characteristics[x]]
		
		return pointTotal

	def genStats(self,*args):
			points = 7
			for x in args:
				try:
					points=int(x)
				except:
					None

			if points != 0:
				self.genStats(0)
			else:
				None
			prior = list(set(args) & set(self.charList))
			charListTemp = self.charList[:]
			if len(prior)>int(3+points/6):
				#print('too many prioritizations. Dropping ' + str(len(prior)-int(3+points/6)))
				prior=prior[:int(3+points/6)]
			else:
				None
			if len(prior)>0:
				#print('priotitizing ' +str(prior))
				for char in prior:
					self.characteristics[char]=3
					charListTemp.remove(char)
			else:
				None

			while self.checkPoints()!=points:
				change = random.randint(-3,3)
				modChar=charListTemp[random.randint(0,len(charListTemp))-1]
				self.characteristics[modChar]=change

				#print('points goal: ' + str(points))
				#print('current spent points: ' + str(self.checkPoints()))
			return(self.characteristics)
			#print(self.characteristics)

	def display(self):
		output = 'Character name: ' + str(self.name) + '\n'
		for char in self.characteristics:
			output += char.capitalize() + ': ' + str(self.characteristics[char]) + ' '
		return output

