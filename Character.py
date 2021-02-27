from pathlib import Path
import pickle
import random
import math
import Levenshtein
import shutil
import re
import numpy
import os
from datetime import datetime
import json
import discord

#Test Test

# Todo
# give virtues character creation ability permissions:
# ARCANE LORE gives perm for arcane abilities and additional 50 experience points, which must be spent on Arcane Abilities.
# EDUCATED additional 50 experience points, which must be spent on Latin and Artes Liberales.
# ENTRANCEMENT gives entrancement 1
# GREAT increases a characteristic by 1
# IMPROVED CHARACTERISTICS increases characteristic points by 3
# LARGE size +1
# MENDICANT FRIAR may take acedemic abilities
# PREMONITIONS gives Premonitions 1
# PRIVILEGED UPBRINGING You have an additional 50 experience points, which may be spent on General, Academic, or Martial Abilities
# SECOND SIGHT gives Second Sight 1
# SHAPESHIFTER gives Shapeshift 1
# STUDENT OF (REALM) gives You may take that Lore at character generation even if you cannot learn other Arcane Abilities
# WARRIOR May aquire martial abliities during character gen
# WELL-TRAVELED You have fifty bonus experience points to spend on living languages, Area Lores, and Bargain, Carouse, Charm, Etiquette, Folk Ken, or Guile.
# WILDERNESS SENSE gives wilderness sense 1
# WISE ONE may take either Arcane or Academic Abilities, but not both, at character creation.


# Affinity abilities increase xp spent on certain arts/abilities during character creation
# MASTERED SPELLS Gives 50 xp on spells known

# Divide virtues (and possibly flaws) into classifications. IE: Character Gen, Roll effecting, Occasional Modifier, RP
# Within character gen, there appears to be a limited number of things virtues do. Give permission to get certain skills, give xp points limited to certain skills, or modify xp spent on certain skills.
# maybe .addXPcharGen which checks for limitations like not having requisit virtues?

class alreadyExist(Exception):
    pass

class VirtueFlaw():
    def __init__(self, speciality=''):
        self.name = ''
        self.description = ''
        self.value = ''
        self.type = ''
        self.types = ('General', 'Hermetic', 'Supernatural', 'Social Status', 'Personality', 'Story', 'Special')
        self.valueTypes = ('Minor', 'Major', 'Free', 'Special')
        self.virtuesRef = {'name': '', 'description': '', 'value': '', 'type': ''}
        self.virtuesLib = {}
        self.referencePath = Path.cwd() / 'referenceFiles' / 'libraries'
        self.speciality = speciality
        self.flags = []
        try:
            self.referencePath.mkdir(parents=True)
        except:
            pass
        similarity = 100

    def addSpecialty(self, speciality):
        self.speciality = speciality

    def loadReference(self):
        with open(self.referenceFile,'r') as file:
            self.virtuesLib = json.load(file)


    def printOptions(self):
        value = ''
        for x in self.virtuesLib.values():
            value += x['name'] + '\n'
            value += x['value'] + '\n'
            value += x['type'] + '\n'
            value += x['description'] + '\n \n \n'
        return value

    def availableOptions(self):
        available = ''
        for a in self.types:
            available += '\n' + a + ': \n'
            for x in self.virtuesLib:
                if self.virtuesLib[x]['type'] == a:
                    available += x + '\n'
        return available

    def optionList(self):
        result = []
        for x in self.virtuesLib:
            result.append(x)
        return result

    def summary(self):
        if self.speciality != '':
            return (
                    self.name + '\n' + self.value + '(' + self.speciality + '), ' + self.type + '\n Description: ' + self.description)
        else:
            return (self.name + '\n' + self.value + ', ' + self.type + '\n Description: ' + self.description)

    def validity(self, name):
        similarity = 100
        for x in self.virtuesLib:
            # print('difference between ' + x + ' and ' + name.upper() + ' is ' + str(Levenshtein.distance(x,name.upper())))
            if Levenshtein.distance(x, name.upper()) < similarity:
                self.name = x
                similarity = Levenshtein.distance(x, name.upper())
            else:
                pass
        return similarity


class Virtue(VirtueFlaw):
    def __init__(self, name, speciality = 'default'):
        self.speciality = speciality
        super().__init__()
        self.referenceFile = self.referencePath / 'virtueLib'
        self.loadReference()
        similarity = 100
        for x in self.virtuesLib:
            # print('difference between ' + x + ' and ' + name.upper() + ' is ' + str(Levenshtein.distance(x,name.upper())))
            if Levenshtein.distance(x, name.upper()) < similarity:
                self.name = x
                similarity = Levenshtein.distance(x, name.upper())
            else:
                pass
        self.description = self.virtuesLib[self.name]['description']
        self.value = self.virtuesLib[self.name]['value']
        self.type = self.virtuesLib[self.name]['type']
        if self.speciality == 'default' and self.name == 'CUSTOS':
            self.speciality = random.choice(['(Martial)','(Academic)','(Arcane)'])
        if self.speciality == 'default' and self.name == 'WISE ONE':
            self.speciality = random.choice(['(Arcane)','(Academic)'])

    def isVirtue(self):
        return True


class Flaw(VirtueFlaw):
    def __init__(self, name, speciality = 'default'):
        self.speciality = speciality
        super().__init__()
        self.referenceFile = self.referencePath / 'flawLib'
        self.loadReference()
        similarity = 100
        for x in self.virtuesLib:
            # print('difference between ' + x + ' and ' + name.upper() + ' is ' + str(Levenshtein.distance(x,name.upper())))
            if Levenshtein.distance(x, name.upper()) < similarity:
                self.name = x
                similarity = Levenshtein.distance(x, name.upper())
            else:
                pass
        self.description = self.virtuesLib[self.name]['description']
        self.value = self.virtuesLib[self.name]['value']
        self.type = self.virtuesLib[self.name]['type']

    def isFlaw(self):
        return True


class Ability():
    def __init__(self, name, speciality='default',specification='none'):
        self.referencePath = Path.cwd() / 'referenceFiles'/'libraries'
        self.types = ('(General)', '(Academic)', '(Arcane)', '(Martial)', '(Supernatural)')
        self.abilitiesRef = {'name': '', 'description': '', 'needTraining': False, 'specialties': [],
                             'type': self.types[0], 'xp': 0, 'score': 0}
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

        newName = 'BAD ABILITY'
        similarity = 100
        for x in self.abilitiesLib:
            # print('difference between ' + x + ' and ' + name.upper() + ' is ' + str(Levenshtein.distance(x,name.upper())))
            found = re.findall(r'(\([^)]+\))', x)
            if len(found) > 0:
                if (Path.cwd()/'referenceFiles'/'abilitySpecifications'/x).exists():
                    with open(Path.cwd()/'referenceFiles'/'abilitySpecifications'/x,'r') as refFile:
                        ref = json.load(refFile)
                        for spec in ref:

                            y = x.replace(found[0],spec)
                            if Levenshtein.distance(y, name.upper()) < similarity:
                                self.name = y
                                similarity = Levenshtein.distance(y, name.upper())
                                self.base=x

            if Levenshtein.distance(x, name.upper()) < similarity:
                self.name = x
                similarity = Levenshtein.distance(x, name.upper())
                self.base=x
            else:
                pass

        try:
            modularPart = re.search(r'\((.*?)\)',self.name).group(1)
            if specification != 'none':
                self.name = self.name.replace('('+modularPart+')',specification)
        except AttributeError:
            pass
        except FileNotFoundError:
            print('Reference File not found for ' + self.name)
        if speciality == 'default':
            self.specialty = random.choice(self.abilitiesLib[self.base]['specialties'])
        else:
            self.specialty = speciality
        self.description = self.abilitiesLib[self.base]['description']
        self.needTraining = self.abilitiesLib[self.base]['needTraining']
        self.type = self.abilitiesLib[self.base]['type']

    def addXp(self, xp):
        self.xp += xp
        self.score = int((-5 + math.sqrt(25 + 40 * self.xp)) / 10)

    def setScore(self, score):
        self.score = score
        xp = 0
        while score > 0:
            xp += score * 5
            score -= 1
        self.xp = xp

    def loadReference(self):
        if not (self.referencePath/'abilityLib').exists():
            print('abilityLib does not exist in expected location ' + str(self.referencePath/'abilityLib'))
        with open(self.referencePath/'abilityLib','r') as file:
            self.abilitiesLib = json.load(file)


    def summary(self):
        return (
                'Name: ' + self.name + '\n Description: ' + self.description + '\n Type: ' + self.type + '\n Speciality: ' + self.specialty + '\n XP: ' + str(
            self.xp) + '\n Score: ' + str(self.score))

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

    def isAbility(self):
        return True


class Character():
    def __init__(self,nlp, basePath=(Path.cwd() / 'servers' / 'unClassified'), name='default'):
        self.referencePath = Path.cwd() / 'referenceFiles'
        self.nlp = nlp
        self.name = name
        self.basePath = basePath
        tempGrogs = basePath / 'characters' / 'tempGrogs'
        Grogs = basePath / 'characters' / 'Grogs'
        tempCompanions = basePath / 'characters' / 'tempCompanions'
        Companions = basePath / 'characters' / 'Companions'
        tempMagi = basePath / 'characters' / 'tempMagi'
        Magi = basePath / 'characters' / 'Magi'
        self.identifier = basePath / 'identifier'
        self.filepaths = {'tg': tempGrogs, 'g': Grogs, 'tc': tempCompanions, 'c': Companions, 'tm': tempMagi, 'm': Magi,
                          'i': self.identifier}
        self.identifier = -1
        self.referenceAbility = Ability('LIVING LANGUAGE')
        self.referenceVirtue = Virtue('ADEPT LABORATORY STUDENT')
        self.referenceFlaw = Flaw('ABILITY BLOCK')
        self.warpingScore = 0
        self.confidence = 0
        self.covenant = 'undefined'
        self.age = 0
        self.description = ''
        for key in self.filepaths:
            try:
                self.filepaths[key].mkdir(parents=True)
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
        self.techniques = {
            'cr': None,
            'in': None,
            'mu': None,
            'pe': None,
            're': None
        }
        self.forms = {
            'an': None,
            'aq': None,
            'au': None,
            'co': None,
            'he': None,
            'ig': None,
            'im': None,
            'me': None,
            'te': None,
            'vi': None
        }
        self.techniquesXP = {
            'cr': None,
            'in': None,
            'mu': None,
            'pe': None,
            're': None
        }
        self.formsXP = {
            'an': None,
            'aq': None,
            'au': None,
            'co': None,
            'he': None,
            'ig': None,
            'im': None,
            'me': None,
            'te': None,
            'vi': None
        }
        self.techniqueList = ['cr', 'in', 'mu', 'pe', 're']
        self.formList = ['an', 'aq', 'au', 'co', 'he', 'ig', 'im', 'me', 'te', 'vi']
        self.charList = ['int', 'per', 'str', 'sta', 'pre', 'com', 'dex', 'qik']
        self.scorePoints = {
            -3: -6, -2: -3, -1: -1, 0: 0, 1: 1, 2: 3, 3: 6
        }
        self.abilities = {}
        self.virtues = {}
        self.flaws = {}
        self.type='unTyped'
        self.referencePath = Path.cwd() / 'referenceFiles'
        self.avatar = self.referencePath/'defaultIcon.png'

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

    def weightedSim(self,keyWord,refList,mag = 10.0):
        keyToken = self.nlp(re.sub(r'([^\s\w]|_)+', "", keyWord))
        finalList = []
        weight = []
        for x in refList:
            # Generate check the similarity of each abilities to the keyword given, and create a list of virtues and their similarity
            testToken = self.nlp(x)
            sim = keyToken.similarity(testToken)
            weight.append(sim)
            finalList.append(x)

        # Turn weight into a weighted probability list with each weight corresponding to its ability, and remove any values under 0
        c = weight.copy()
        c2 = c.copy()
        popped = 0
        for x in range(len(c)):
            if c[x] <= 0:
                c2.pop(x - popped)
                finalList.pop(x - popped)
                popped += 1
        c = [x * 100.0 for x in c2]
        c2 = [pow(x, mag) for x in c]
        total = sum(c2)
        weight = [x / total for x in c2]
        return(finalList,weight)

    def genSimStats(self,*args):
        points = 7
        charistics = [('Intelligence','int'),('Perception','per'),('Strength','str'),('Stamina','sta'),('Presence','pre'),('Communication','com'),('Dexterity','dex'),('Quickness','qik')]
        keyWord = ''
        for word in args:
            keyWord += word + ' '
        keyWord = keyWord.strip()

        keyToken = self.nlp(re.sub(r'([^\s\w]|_)+', "", keyWord))
        charisticList = []
        weight = []
        for x in range(len(charistics)):
            charToken = self.nlp(charistics[x][0])
            sim = keyToken.similarity(charToken)
            charisticList.append((sim,charistics[x][1]))
        charisticList.sort()
        self.genStats(charisticList[0][1] + ' ' + charisticList[1][1])

    def genGrogAbilities(self,age,*args):
        print('TS: gen Grog abilities started: ' + str(datetime.utcnow()))
        keyWord = ''
        for word in args:
            keyWord += word + ' '
        keyWord = keyWord.strip()

        a = Ability('placeholder')
        abis = list(a.abilitiesLib.keys()).copy()
        fullAbiLib = []
        for x in abis:
            found = re.findall(r'(\([^)]+\))', x)
            if len(found) > 0:
                if (Path.cwd()/'referenceFiles'/'abilitySpecifications'/x).exists():
                    with open(Path.cwd()/'referenceFiles'/'abilitySpecifications'/x,'r') as refFile:
                        ref = json.load(refFile)
                        for spec in ref:
                            fullAbiLib.append(x.replace(found[0],spec))
            else:
                fullAbiLib.append(x)

        wList = self.weightedSim(keyWord,fullAbiLib)
        abiList = wList[0]
        weight = wList[1]

        xp = age*15
        while xp > 0:

            cAbi = numpy.random.choice(abiList, p=weight)
            copy = cAbi
            try:
                print('c1')
                modular = re.search('\(([^)]+)\)',cAbi)[0]
                if (self.referencePath/'abilitySpecifications'/cAbi).exists():
                    with open(self.referencePath/'abilitySpecifications'/cAbi,'r') as refFile:
                        ref = json.load(refFile)
                        wList = self.weightedSim(keyWord,ref)
                        print('c4')
                        try:
                            cAbi = self.addAbilityCheck(cAbi,specification=numpy.random.choice(wList[0],p=wList[1]))
                            print('c5')
                            if cAbi == 'False':
                                #print('Ability not allowed ' + copy)
                                num = abiList.index(copy)
                                abiList.pop(num)
                                weight.pop(num)
                                total = sum(weight)
                                c2 = weight.copy()
                                weight = [x / total for x in c2]
                                continue
                        except alreadyExist:
                            cAbi = self.closestAbi(cAbi)
            except TypeError:
                try:
                    copy = cAbi
                    cAbi = self.addAbilityCheck(cAbi)
                    if cAbi == 'False':
                                #print('Ability not allowed ' + copy)
                                num = abiList.index(copy)
                                abiList.pop(num)
                                weight.pop(num)
                                total = sum(weight)
                                c2 = weight.copy()
                                weight = [x / total for x in c2]
                                continue

                except alreadyExist:
                    cAbi = self.closestAbi(cAbi)
            except Exception as e:
                print('CURRENT TEST')
                print(cAbi)
                print('Unexpected exception!')
                print(e)
            #print(str(self.abilities[cAbi].score) + ' score, compared with ' + str(max(math.ceil((self.age-30)/5+5),5)) + ' max.')
            if self.abilities[cAbi].score >= max(math.ceil((self.age-30)/5+5),5):
                #print(cAbi + ' has reached a max score of ' + str(self.abilities[cAbi].score))
                num = abiList.index(copy)
                abiList.pop(num)
                weight.pop(num)
                total = sum(weight)
                c2 = weight.copy()
                weight = [x / total for x in c2]
                continue
            self.abilities[cAbi].addXp(5)
            xp -= 5


        print('TS: gen Grog abilities completed: ' + str(datetime.utcnow()))



    def genStartingAbilities(self,*args):
        print('TS: gen Grog starting abilities started: ' + str(datetime.utcnow()))

        keyWord = ''
        for word in args:
            keyWord += word + ' '
        keyWord = keyWord.strip()
        if (self.referencePath/'abilitySpecifications'/'(LIVING LANGUAGE)').exists():
            with open(self.referencePath/'abilitySpecifications'/'(LIVING LANGUAGE)','r') as langFile:
                lang = json.load(langFile)
                wList = self.weightedSim(keyWord,lang)
                langName = self.addAbilityCheck('(LIVING LANGUAGE)',specification=numpy.random.choice(wList[0],p=wList[1]))
        self.abilities[langName].setScore(5)



        abiRefList = ['(AREA) LORE','Athletics','Awareness','Brawl','Charm','Folk Ken','Guile','(LIVING LANGUAGE)','Stealth','Survival','Swim']
        fullAbiLib = []
        for x in abiRefList:
            found = re.findall(r'(\([^)]+\))', x)
            if len(found) > 0:
                if (Path.cwd()/'referenceFiles'/'abilitySpecifications'/x).exists():
                    with open(Path.cwd()/'referenceFiles'/'abilitySpecifications'/x,'r') as refFile:
                        ref = json.load(refFile)
                        for spec in ref:
                            fullAbiLib.append(x.replace(found[0],spec))
            else:
                fullAbiLib.append(x)
        wList = self.weightedSim(keyWord,fullAbiLib,mag=5.0)
        abiList = wList[0]
        weight = wList[1]
        xp = 45
        while xp > 0:
            cAbi = numpy.random.choice(abiList, p=weight)
            copy = cAbi
            try:
                modular = re.search('\(([^)]+)\)',cAbi)[0]
                if (self.referencePath/'abilitySpecifications'/cAbi).exists():
                    with open(self.referencePath/'abilitySpecifications'/cAbi,'r') as refFile:
                        ref = json.load(refFile)
                        wList = self.weightedSim(keyWord,ref)
                        try:

                            cAbi = self.addAbilityCheck(cAbi,specification=numpy.random.choice(wList[0],p=wList[1]))
                            if cAbi == 'False':
                                num = abiList.index(copy)
                                abiList.pop(num)
                                weight.pop(num)
                                total = sum(weight)
                                c2 = weight.copy()
                                weight = [x / total for x in c2]
                                continue

                        except alreadyExist:
                            cAbi = self.closestAbi(cAbi)
            except TypeError:
                try:
                    copy = cAbi
                    cAbi = self.addAbilityCheck(cAbi)
                    if cAbi == 'False':
                                num = abiList.index(copy)
                                abiList.pop(num)
                                weight.pop(num)
                                total = sum(weight)
                                c2 = weight.copy()
                                weight = [x / total for x in c2]
                                continue
                except alreadyExist:
                    cAbi = self.closestAbi(cAbi)
            self.abilities[cAbi].addXp(5)
            xp -= 5
        print('TS: gen Grog starting abilities completed: ' + str(datetime.utcnow()))


    def genAbilities(self, xp):
        while xp > 0:
            change = random.randint(1, int(xp / 2) + 1)
            xp -= change
            randAbility = random.choice(list(self.referenceAbility.abilitiesLib.values()))
            #	print(randAbility)
            #	print('Applying ' + str(xp) + ' xp to ' + randAbility['name'])
            self.abilities[randAbility['name']] = Ability(randAbility['name'])
            self.abilities[randAbility['name']].addXp(change)

    def genVirtuesFlawsGrog(self, *args):
        print('TS: gen Grog V/F started: ' + str(datetime.utcnow()))
        try:
            points = 3
            virtuePoints = 0
            # generate a list of virtues and flaws based on supplied phrase
            # parse args into single string
            keyWord = ''
            for word in args:
                keyWord += word + ' '
            keyWord = keyWord.strip()

            v = Virtue('placeholder')
            c1 = list(v.virtuesLib.keys())
            c2 = list(v.virtuesLib.keys())
            for x in c1:
                tempVirt = Virtue(x)
                if tempVirt.value == 'Major':
                    c2.remove(x)
                elif tempVirt.name == 'The Gift':
                    c2.remove(x)
                elif tempVirt.type == 'Hermetic':
                    c2.remove(x)
            wList = self.weightedSim(keyWord,c2)
            virtList = wList[0]
            weight = wList[1]
            socialStatus = False
            while virtuePoints < points:
                skip = False
                choice = numpy.random.choice(virtList, p=weight)
                if Virtue(choice).type != 'Social Status' and socialStatus is False:
                    continue
                num = virtList.index(choice)

                virtList.pop(num)
                weight.pop(num)
                total = sum(weight)
                c2 = weight.copy()
                weight = [x / total for x in c2]

                randVirtue = Virtue(choice)
                if randVirtue.type == 'Social Status':
                    for virt in list(self.virtues.keys()):
                        if self.virtues[virt].type == 'Social Status':
                            skip = True
                        else:
                            socialStatus = True
                if skip:
                    continue
                if randVirtue.type == 'Social Status':
                    socialStatus = True
                if randVirtue.type == 'Hermetic':
                    continue
                if randVirtue.name == 'The Gift':
                    continue
                else:
                    None
                if randVirtue.value == 'Major':
                    # commented out because grogs are not allowed major virtues
                    # if (virtuePoints + 3) <= points:
                    #     virtuePoints += 3
                    #     self.virtues[randVirtue.name] = randVirtue
                    # else:
                        continue

                elif randVirtue.value == 'Minor':
                    virtuePoints += 1
                    self.virtues[randVirtue.name] = randVirtue
                elif randVirtue.value == 'Free':
                    self.virtues[randVirtue.name] = randVirtue

            flawPoints = 0
            f = Flaw('placeholder')
            c1 = list(f.virtuesLib.keys()).copy()
            c2 = list(f.virtuesLib.keys()).copy()
            for x in c1:
                tempFlaw = Flaw(x)
                if tempFlaw.value == 'Major':
                    c2.remove(x)
                elif tempFlaw.name == 'The Gift':
                    c2.remove(x)
                elif tempFlaw.type == 'Hermetic':
                    c2.remove(x)
                elif tempFlaw.type == 'Story':
                    c2.remove(x)
            wList = self.weightedSim(keyWord,c2)
            FlawList = wList[0]
            weight = wList[1]

            while flawPoints < points:
                choice = numpy.random.choice(FlawList, p=weight)
                num = FlawList.index(choice)
                FlawList.pop(num)
                weight.pop(num)
                total = sum(weight)
                c2 = weight.copy()
                weight = [x / total for x in c2]

                randFlaw = Flaw(choice)
                if randFlaw.type == 'Story':
                    continue
                if randFlaw.type == 'Hermetic':
                    continue
                if randFlaw.type == 'Personality':
                    for fla in self.flaws:
                        if self.flaws[fla].type == 'Personality':
                            continue
                if randFlaw.value == 'Major':
                    if (flawPoints + 3) <= points:
                        flawPoints += 3
                        self.flaws[randFlaw.name] = randFlaw
                    else:
                        continue
                elif randFlaw.value == 'Minor':
                    flawPoints += 1
                    self.flaws[randFlaw.name] = randFlaw
                elif randFlaw.value == 'Free':
                    self.flaws[randFlaw.name] = randFlaw
        except Exception as e:
            print(e)
        print('TS: gen Grog V/F finished: ' + str(datetime.utcnow()))

    def printVirtuesFlaws(self):
        print('Virtues: \n')
        for x in self.virtues.values():
            print(x.name + '(' + x.value + ')')
        print('Flaws: \n')
        for x in self.flaws.values():
            print(x.name + '(' + x.value + ')')

    def printAbilities(self):
        for x in self.abilities.values():
            print(x.summary())
            print('\n \n \n')

    def addVirtue(self, name, specialty=''):
        tempVir = Virtue(name, specialty)
        self.virtues[tempVir.name] = tempVir
        return tempVir.name

    def addFlaw(self, name, specialty=''):
        tempFlaw = Flaw(name, specialty)
        self.flaws[tempFlaw.name] = tempFlaw
        return tempFlaw.name

    def closestAbi(self,name):
        similarity = 100
        result = ''
        for x in self.abilities.keys():
            # print('difference between ' + x + ' and ' + name.upper() + ' is ' + str(Levenshtein.distance(x,name.upper())))
            if Levenshtein.distance(x, name.upper()) < similarity:
                result = x
                similarity = Levenshtein.distance(x, name.upper())
            else:
                pass

        return result

    def addAbility(self, name, speciality='default',specification='none'):
        tempAbi = Ability(name, speciality,specification)
        try:
            self.abilities[tempAbi.name]
            raise alreadyExist('ability already exists')
        except alreadyExist:
            raise alreadyExist('ability already exists')
        except:
            None
        self.abilities[tempAbi.name] = tempAbi
        return (tempAbi.name)

    def addAbilityCheck(self,name, speciality='default',specification='none'):
        tempAbi = Ability(name, speciality,specification)
        try:
            self.abilities[tempAbi.name]
            raise alreadyExist('ability already exists')
        except alreadyExist:
            raise alreadyExist('ability already exists')
        except:
            None


        if tempAbi.type == '(General)':
            self.abilities[tempAbi.name] = tempAbi
            return(tempAbi.name)

        elif tempAbi.type == '(Academic)':
            if self.hasVirtue('REDCAP') or self.hasVirtue('PRIEST') or self.hasVirtue('MENDICANT FRIAR') or self.hasVirtue('MAGISTER IN ARTIBUS') or self.hasVirtue('FAILED APPRENTICE') or self.hasVirtue('EDUCATED') or self.hasVirtue('CLERK'):
                self.abilities[tempAbi.name] = tempAbi
                return(tempAbi.name)
            elif self.hasVirtue('CUSTOS'):
                if self.virtues['CUSTOS'].speciality == '(Academic)':
                    self.abilities[tempAbi.name] = tempAbi
                    return(tempAbi.name)
                else:
                    return 'False'
            elif self.hasVirtue('WISE ONE'):
                if self.virtues['WISE ONE'].speciality == '(Academic)':
                    self.abilities[tempAbi.name] = tempAbi
                    return(tempAbi.name)
                else:
                    return 'False'
            else:
                return 'False'

        elif tempAbi.type == '(Arcane)':
            if self.hasVirtue('ARCANE LORE') or self.hasVirtue('FAILED APPRENTICE') or self.hasVirtue('REDCAP'):
                self.abilities[tempAbi.name] = tempAbi
                return(tempAbi.name)
            elif self.hasVirtue('WISE ONE'):
                if self.virtues['WISE ONE'].speciality == '(Arcane)':
                    self.abilities[tempAbi.name] = tempAbi
                    return(tempAbi.name)
                else:
                    return 'False'
            elif self.hasVirtue('CUSTOS'):
                if self.virtues['CUSTOS'].speciality == '(Arcane)':
                    self.abilities[tempAbi.name] = tempAbi
                    return(tempAbi.name)
                else:
                    return 'False'
            else:
                return 'False'

        elif tempAbi.type == '(Martial)':
            if self.hasVirtue('BERSERK') or self.hasVirtue('KNIGHT') or self.hasVirtue('MERCENARY CAPTAIN') or self.hasVirtue('REDCAP') or self.hasVirtue('WARRIOR'):
                self.abilities[tempAbi.name] = tempAbi
                return(tempAbi.name)
            elif self.hasVirtue('CUSTOS'):
                if self.virtues['CUSTOS'].speciality == '(Martial)':
                    self.abilities[tempAbi.name] = tempAbi
                    return(tempAbi.name)
                else:
                    return 'False'
            else:
                return 'False'
        elif tempAbi.type == '(Supernatural)':
            if self.hasVirtue('FAILED APPRENTICE'):
                self.abilities[tempAbi.name] = tempAbi
                return(tempAbi.name)
            elif self.hasVirtue(tempAbi.name):
                self.abilities[tempAbi.name] = tempAbi
                return(tempAbi.name)
            elif tempAbi.name == 'SHAPESHIFT' and self.hasVirtue('SHAPESHIFTER'):
                self.abilities[tempAbi.name] = tempAbi
                return(tempAbi.name)
            elif tempAbi.name == 'SECOND SIGHT' and self.hasVirtue('STRONG FAERIE BLOOD'):
                self.abilities[tempAbi.name] = tempAbi
                return(tempAbi.name)
            else:
                return 'False'


    def hasVirtue(self,virtueName):
        if virtueName in list(self.virtues.keys()):
            return True
        else:
            return False

    def save(self, type='g'):
        # type is the type of character which determines the save folder
        #print('saving ' + self.name)
        oldType = type
        typeTranslator = {'g':'grog','tg':'tempGrog','c':'companion','tc':'tempCompanion','m':'magus','tm':'tempMagus'}
        self.type = typeTranslator[type]
        try:
            # Tries to access a saved character with the same name
            existingPath = list(self.basePath.glob('**/' + self.name))[0]
            tempChar = Character(self.nlp,self.basePath)
            tempChar.load(self.name)
            #print('tempChar loaded')

            # Checks the identifier to see if we are saving an upadated version of the existing character.
            if tempChar.identifier != self.identifier:
                # Returns without saving if we aren't
                print('Attempted to save a character with a mismatched identifier')
                print('Current identifier: ' + str(self.identifier) + ' Saved identifier: ' + str(tempChar.identifier))
                return ('A different character with this name already exists')
            else:
                # updates type to whatever type existing character is
                oldType = list(self.filepaths.keys())[list(self.filepaths.values()).index(existingPath.parents[0])]
                pass

        except IndexError:
            # If we don't find an existing character, we need to create an identifier
            try:
                # Checking to make sure that we have an identifier.txt, if not creates one
                identF = open(self.filepaths['i'] / 'identifier.txt', 'x')
                self.identifier = 0
                identF.write(str(self.identifier))
                identF.close()

            except (FileExistsError):
                # If we already have one, reads the current identifier, adds one and resaves it.
                identF = open(self.filepaths['i'] / 'identifier.txt', 'r')
                try:
                    ident = int(identF.read())
                    self.identifier = ident + 1
                    identF.close()
                    identF = open(self.filepaths['i'] / 'identifier.txt', 'w')
                    identF.write(str(self.identifier))
                    identF.close()
                except:
                    print('identifier file not found')
                    # If for whatever reason the contents of identifier.txt have changed resets the number. Could potentially cause problems later, and should probably implement something to scan existing characters for identifiers and pull the highest number.
                    self.identifier = 0
                    identF.write(str(self.identifier))
                    identF.close()


        #print('saving')
        try:
            #Create JSON serialable data value
            data = {
                'name': self.name,
                'characteristics' : self.characteristics,
                'identifier' : self.identifier,
                'warpingScore' : self.warpingScore,
                'confidence' : self.confidence,
                'covenant' : self.covenant,
                'age' : self.age,
                'techniques' : self.techniques,
                'techniquesXP' : self.techniquesXP,
                'forms' : self.forms,
                'formsXP' : self.formsXP,
                'description': self.description,
                'type':self.type

                }

            if (self.filepaths[oldType] / self.name).exists():
                (self.filepaths[oldType] / self.name).unlink()
            with open(self.filepaths[type] / self.name, 'w') as saveFile:
                json.dump(data,saveFile)

            try:
                shutil.rmtree(self.filepaths[oldType] / ('info.' + self.name))
                os.mkdir(self.filepaths[type]/('info.' + self.name))
            except:
                None
            for x in self.abilities:
                p = self.filepaths[type] / ('info.' + self.name)
                try:
                    #	print(p)
                    p.mkdir(parents=True, exist_ok=True)
                #	print('made directory')
                except:
                    None
                try:
                    saveFile = open(self.filepaths[type] / ('info.' + self.name) / ('ability.' + x), 'wb')
                except Exception as e:
                    print(e)
                pickle.dump(self.abilities[x], saveFile,protocol=-1)
            for x in self.virtues:
                p = self.filepaths[type] / ('info.' + self.name)
                try:
                    #	print(p)
                    p.mkdir(parents=True, exist_ok=True)
                #	print('made directory')
                except:
                    None
                saveFile = open(self.filepaths[type] / ('info.' + self.name) / ('virtue.' + x), 'wb')
                pickle.dump(self.virtues[x], saveFile,protocol=-1)
            for x in self.flaws:
                p = self.filepaths[type] / ('info.' + self.name)
                try:
                    #	print(p)
                    p.mkdir(parents=True, exist_ok=True)
                #	print('made directory')
                except:
                    None
                saveFile = open(self.filepaths[type] / ('info.' + self.name) / ('flaw.' + x), 'wb')
                pickle.dump(self.flaws[x], saveFile,protocol=-1)
        except Exception as e:
            print(e)
        return ('Character saved')

    # print(self.characteristics)
    def load(self, name):
        #print('TS:          load subroutine initialized: ' + str(datetime.utcnow()))
        #	print('attempting to load ' + name)
        #	print('using path ' + str(Path.cwd() / 'characters' / '**' / name))
        # p = list(Path.cwd().glob('**/'+name))[0]
        name = name.capitalize()
        # print(name)
        # print((list(self.basePath.glob('**/' + name))[0]))
        try:
          tempName = list(self.basePath.glob('**/' + name))[0]
        except IndexError:
            return
        try:
            infile = open(tempName, 'r')
            #print('TS:          first JSON load started: ' + str(datetime.utcnow()))
            data = json.load(infile)
            #print('TS:          first JSON load finished: ' + str(datetime.utcnow()))
            infoF = Path(list(self.basePath.glob('**/' + name))[0]).parent / ('info.' + data['name'])
            infile.close()
            #	print('successfully unpickled')
            try:
                self.name = data['name']
                self.characteristics = data['characteristics']
                self.identifier = data['identifier']
                self.warpingScore = data['warpingScore']
                self.confidence = data['confidence']
                self.covenant = data['covenant']
                self.age = data['age']
                self.techniques = data['techniques']
                self.techniquesXP = data['techniquesXP']
                self.forms = data['forms']
                self.formsXP = data['formsXP']
                self.description = data['description']
                self.type = data['type']
            except Exception as e:
                print(e)
                print('some data not found, character file likely out of date for ' + self.name)
            for x in list(infoF.glob('*')):
                try:
                    file = open(x, 'rb')
                    try:
                        #print('TS:          Second pickle load started: ' + str(datetime.utcnow()))
                        infoTemp = pickle.load(file)
                        #print('TS:          Second pickle load finished: ' + str(datetime.utcnow()))
                    except Exception as e:
                        print(e)

                    try:
                        if infoTemp.isAbility():
                            self.abilities[infoTemp.name] = infoTemp
                    except:
                        None

                    try:
                        if infoTemp.isVirtue():
                            self.virtues[infoTemp.name] = infoTemp
                    except:
                        None

                    try:
                        if infoTemp.isFlaw():
                            self.flaws[infoTemp.name] = infoTemp
                    except:
                        None
                except:
                    None
        except Exception as e:
            print(e)
        #print('TS:          load subroutine finished: ' + str(datetime.utcnow()))
        return (self.name + ' successfully loaded')

    def isCharacter(self):
        return True

    def display(self):
        try:
            if self.type == 'unTyped':
                typeColor = discord.Colour.dark_red()
            elif self.type in ['tg','tm','tc']:
                typeColor = discord.Colour.dark_grey()
            elif self.type =='g':
                typeColor = discord.Colour.green()
            elif self.type =='c':
                typeColor = discord.Colour.gold()
            elif self.type =='m':
                typeColor = discord.Colour.purple()
            else:
                typeColor = discord.Colour.red()
            desc = self.description
            desc += '\n' + 'Age: ' + str(self.age) + ' years old.'
            desc += '\n' + 'Covenant: ' + self.covenant
            desc += '\n' + 'Warping Score: [' + str(self.warpingScore) + ']\u200B \u200B Confidence: [' + str(self.confidence) + ']'
            embed = discord.Embed(title=self.type,description=desc,color=typeColor)
            file = discord.File(self.avatar,filename='avatar.png')
            embed.set_author(name=self.name,icon_url='attachment://avatar.png')
            embed.set_thumbnail(url='attachment://avatar.png')
            charOutput = 'Int: [' + str(self.characteristics['int']) + '] \u200B \u200BPer: [' + str(self.characteristics['per']) + '] \u200B \u200BStr: [' + str(self.characteristics['str']) + '] \u200B \u200BSta: [' + str(self.characteristics['sta']) + '] \nPre: [' + str(self.characteristics['pre']) + '] \u200B \u200BCom: [' + str(self.characteristics['com']) + '] \u200B \u200BDex: [' + str(self.characteristics['dex']) + '] \u200B \u200BQik: [' + str(self.characteristics['qik']) + ']'
            embed.add_field(name='Characteristics',value=charOutput,inline=False)
            virtOutput = ''
            for x in list(self.virtues.keys()):
                virtOutput += x.capitalize() + '\n'
            flawOutput = ''
            for x in list(self.flaws.keys()):
                flawOutput += x.capitalize() + '\n'
            embed.add_field(name='Virtues',value=virtOutput,inline=True)
            embed.add_field(name='Flaws',value=flawOutput,inline=True)
            abiOutput = ''
            scoreOutput = ''
            for x in list(self.abilities.keys()):
                abiOutput += x.capitalize() + '\n'
                scoreOutput += str(self.abilities[x].score) + '\n'
            embed.add_field(name='\u200b',value='\u200b',inline=False)
            embed.add_field(name='Abilities',value=abiOutput,inline=True)
            embed.add_field(name='Score',value=scoreOutput,inline=True)
            arts = False
            for x in list(self.forms.values()):
                if x != None:
                    arts = True
            for x in list(self.techniques.values()):
                if x != None:
                    arts = True
            if arts:
                formsOutput = ''
                formTranslator = {'an':'animal','aq':'aqaum','au':'auram','co':'corpus','he':'herbam','ig':'ignam','im':'imaginem','me':'mentem','te':'terram','vi':'vim'}
                for x in list(self.forms.keys()):
                    if x != None:
                        formsOutput += x + ': ' + str(formTranslator[self.forms[x]]).capitalize() + '\n'
                techOutput = ''
                techTranslator = {'cr':'creo','in':'intellego','mu':'muto','pe':'perdo','re':'rego'}
                for x in list(self.techniques.keys()):
                    if x != None:
                        techOutput += x + ': ' + str(techTranslator[self.techniques[x]]).capitalize() + '\n'
                embed.add_field(name='\u200b',value='\u200b',inline=False)
                embed.add_field(name='Forms',value=formsOutput,inline=True)
                embed.add_field(name='Techniques',value=techOutput,inline=True)

        except Exception as e:
            print(e)
        return (embed,file)
