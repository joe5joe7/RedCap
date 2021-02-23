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
        self.referencePath = Path.cwd() / 'referenceFiles'
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
        with open(self.referenceFile, 'r', encoding='utf-8') as file:
            refsheet = file.readlines()
        firstIteration = True
        newVirtue = self.virtuesRef.copy()
        oldLine = refsheet[0]
        tempDescription = []
        for line in refsheet:
            if firstIteration:
                for x in self.valueTypes:
                    if x in line:
                        if x != 'Special':
                            for y in self.types:
                                if x + ', ' + y in line:
                                    newVirtue['name'] = oldLine.strip()
                                    newVirtue['value'] = x
                                    newVirtue['type'] = y
                                    firstIteration = False
                                    continue
                        elif x == 'Special':
                            newVirtue['name'] = oldLine.strip()
                            newVirtue['value'] = 'Special'
                            newVirtue['type'] = 'Special'
                            firstIteration = False
                            continue
                oldLine = line
            else:
                for x in self.valueTypes:
                    if x in line:
                        if x != 'Special':
                            for y in self.types:
                                if x + ', ' + y in line:
                                    description = ''
                                    for d in tempDescription[1:-1]:
                                        description += d
                                    tempDescription = []
                                    newVirtue['description'] = description
                                    self.virtuesLib[newVirtue['name']] = newVirtue
                                    newVirtue = {}
                                    newVirtue['name'] = oldLine.strip()
                                    newVirtue['value'] = x
                                    newVirtue['type'] = y
                                    continue
                        elif x == 'Special':
                            description = ''
                            for d in tempDescription[1:-1]:
                                description += d
                            tempDescription = []
                            newVirtue['description'] = description
                            self.virtuesLib[newVirtue['name']] = newVirtue
                            newVirtue = {}
                            newVirtue['name'] = oldLine.strip()
                            newVirtue['value'] = x
                            newVirtue['type'] = x
                            continue
                tempDescription.append(line)
                oldLine = line
        description = ''
        for d in tempDescription[1:-1]:
            description += d
        newVirtue['description'] = description
        self.virtuesLib[newVirtue['name']] = newVirtue

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
        self.referenceFile = self.referencePath / 'virtues.txt'
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
        self.referenceFile = self.referencePath / 'flaws.txt'
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
    def __init__(self, name, speciality='default'):
        self.referencePath = Path.cwd() / 'referenceFiles'
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

        similarity = 100
        for x in self.abilitiesLib:
            # print('difference between ' + x + ' and ' + name.upper() + ' is ' + str(Levenshtein.distance(x,name.upper())))
            if Levenshtein.distance(x, name.upper()) < similarity:
                self.name = x
                similarity = Levenshtein.distance(x, name.upper())
            else:
                pass
        if speciality == 'default':
            self.specialty = random.choice(self.abilitiesLib[self.name]['specialties'])
        else:
            self.specialty = speciality
        self.description = self.abilitiesLib[self.name]['description']
        self.needTraining = self.abilitiesLib[self.name]['needTraining']
        self.type = self.abilitiesLib[self.name]['type']

    def addXp(self, xp):
        self.xp += xp
        self.score = int((-5 + math.sqrt(25 + 40 * xp)) / 10)

    def setScore(self, score):
        self.score = score
        xp = 0
        while score > 0:
            xp += score * 5
            score -= 1
        self.xp = xp

    def loadReference(self):
        with open(self.referencePath / 'abilities.txt', 'r', encoding='utf-8') as file:
            refsheet = file.readlines()
        searchingFor = 'name'
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
                newAbility['name'] = data
                searchingFor = 'description'
                description = ''
            elif searchingFor == 'description':
                if 'Specialties:' in line:
                    x = line.split('Specialties:')
                    description = description + x[0]
                    newAbility['description'] = description
                    searchingFor = 'specialties'
                    specialities = x[1]
                else:
                    description = description + line
            elif searchingFor == 'specialties':
                for type in self.types:
                    if type in line:
                        newAbility['type'] = type
                        specialities = specialities + line.split(type)[0]
                        specialities = specialities.replace(type, '').replace('\n', '').replace('.', '').split(',')
                        for x in range(len(specialities)):
                            specialities[x] = specialities[x].strip()
                        newAbility['specialties'] = specialities
                        self.abilitiesLib[newAbility['name']] = newAbility
                        searchingFor = 'name'
                        newAbility = {}
                        break
                    else:
                        pass
                if not type in line:
                    specialities = specialities + line

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

    def genStartingAbilities(self,*args):
        None

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
        try:
            points = 3
            virtuePoints = 0
            # generate a list of virtues and flaws based on supplied phrase
            # parse args into single string
            keyWord = ''
            for word in args:
                keyWord += word + ' '
            keyWord = keyWord.strip()


            keyToken = self.nlp(re.sub(r'([^\s\w]|_)+', "", keyWord))
            v = Virtue('placeholder')
            virtRefList = list(v.virtuesLib.values())
            virtList = []
            weight = []
            for virtue in virtRefList:
                virtToken = self.nlp(virtue['name'])
                sim = keyToken.similarity(virtToken)
                weight.append(sim)
                virtList.append(virtue['name'])
            c = weight.copy()
            c2 = c.copy()
            popped = 0
            for x in range(len(c)):
                if c[x] <= 0:
                    c2.pop(x - popped)
                    virtList.pop(x - popped)
                    popped += 1

            c = [x * 100.0 for x in c2]
            c2 = [pow(x, 10.0) for x in c]
            total = sum(c2)
            weight = [x / total for x in c2]

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
                    if (virtuePoints + 3) <= points:
                        virtuePoints += 3
                        self.virtues[randVirtue.name] = randVirtue
                    else:
                        continue

                elif randVirtue.value == 'Minor':
                    virtuePoints += 1
                    self.virtues[randVirtue.name] = randVirtue
                elif randVirtue.value == 'Free':
                    self.virtues[randVirtue.name] = randVirtue

            flawPoints = 0
            f = Flaw('placeholder')
            FlawRefList = list(f.virtuesLib.values())
            FlawList = []
            weight = []
            for flaw in FlawRefList:
                flawToken = self.nlp(flaw['name'])
                sim = keyToken.similarity(flawToken)
                weight.append(sim)
                FlawList.append(flaw['name'])
            c = weight.copy()
            c2 = c.copy()
            popped = 0
            for x in range(len(c)):
                if c[x] <= 0:
                    c2.pop(x - popped)
                    FlawList.pop(x - popped)
                    popped += 1

            c = [x * 100.0 for x in c2]
            c2 = [pow(x, 10.0) for x in c]
            total = sum(c2)
            weight = [x / total for x in c2]

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

    def addAbility(self, name, speciality='default'):
        tempAbi = Ability(name, speciality)
        try:
            self.abilities[tempAbi.name]
            raise Exception('ability already exists')
        except:
            None
        self.abilities[tempAbi.name] = tempAbi
        return (tempAbi.name)

    def addAbilityCheck(self,name, speciality='default'):
        tempAbi = Ability(name)
        #('(General)', '(Academic)', '(Arcane)', '(Martial)', '(Supernatural)')
        try:
            self.abilities[tempAbi.name]
            return False
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
                    return False
            elif self.hasVirtue('WISE ONE'):
                if self.virtues['WISE ONE'].speciality == '(Academic)':
                    self.abilities[tempAbi.name] = tempAbi
                    return(tempAbi.name)
                else:
                    return False

        elif tempAbi.type == '(Arcane)':
            if self.hasVirtue('ARCANE LORE',''):
                self.abilities[tempAbi.name] = tempAbi
                return(tempAbi.name)
            elif self.hasVirtue('WISE ONE'):
                if self.virtues['WISE ONE'].speciality == '(Arcane)':
                    self.abilities[tempAbi.name] = tempAbi
                    return(tempAbi.name)
                else:
                    return False


    def hasVirtue(self,virtueName):
        if virtueName in list(self.virtues.keys()):
            return True
        else:
            return False

    def save(self, type='g'):
        # type is the type of character which determines the save folder
        print('saving ' + self.name)
        try:
            try:
                # Tries to access a saved character with the same name
                existingPath = list(self.basePath.glob('**/' + self.name))[0]
                infile = open(existingPath, 'rb')
                savedChar = pickle.load(infile)
                infile.close()

                # Checks the identifier to see if we are saving an upadated version of the existing character.
                if savedChar.identifier != self.identifier:
                    # Returns without saving if we aren't
                    return ('A different character with this name already exists')
                else:
                    # updates type to whatever type existing character is
                    type = list(self.filepaths.keys())[list(self.filepaths.values()).index(existingPath.parents[0])]
                    pass

            except Exception as e:
                print(e)
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

            try:
                saveFile = open(self.filepaths[type] / self.name, 'wb')
            except:
                print('Character not saved, likely invalid type')
                return ('Character not saved, likely invalid type')
            pickle.dump(self, saveFile, protocol=-1)
            saveFile.close()
            try:
                shutil.rmtree(self.filepaths[type] / ('info.' + self.name))
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
                saveFile = open(self.filepaths[type] / ('info.' + self.name) / ('virute.' + x), 'wb')
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
        print('TS:          load subroutine initialized: ' + str(datetime.utcnow()))
        #	print('attempting to load ' + name)
        #	print('using path ' + str(Path.cwd() / 'characters' / '**' / name))
        # p = list(Path.cwd().glob('**/'+name))[0]
        name = name.capitalize()
        # print(name)
        # print((list(self.basePath.glob('**/' + name))[0]))
        try:
            infile = open(list(self.basePath.glob('**/' + name))[0], 'rb')
            print('TS:          first pickle load started: ' + str(datetime.utcnow()))
            char = pickle.load(infile)
            print('TS:          first pickle load finished: ' + str(datetime.utcnow()))
            infoF = Path(list(self.basePath.glob('**/' + name))[0]).parent / ('info.' + char.name)
            infile.close()
            #	print('successfully unpickled')
            try:
                char.isCharacter()
            except:
                print('load failed, provided pickle was not a character')
                return ('load failed, provided pickle was not a character')
            try:
                self.name = char.name
                self.characteristics = char.characteristics
                self.identifier = char.identifier
                self.warpingScore = char.warpingScore
                self.confidence = char.confidence
                self.covenant = char.covenant
                self.age = char.age
                self.techniques = char.techniques
                self.techniquesXP = char.techniquesXP
                self.forms = char.forms
                self.formsXP = char.formsXP
            except Exception as e:
                print(e)
            for x in list(infoF.glob('*')):
                try:
                    file = open(x, 'rb')
                    try:
                        print('TS:          Second pickle load started: ' + str(datetime.utcnow()))
                        infoTemp = pickle.load(file)
                        print('TS:          Second pickle load finished: ' + str(datetime.utcnow()))
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
        print('TS:          load subroutine finished: ' + str(datetime.utcnow()))
        return (self.name + ' successfully loaded')

    def isCharacter(self):
        return True

    def display(self):
        output = 'Character name: ' + str(self.name) + '\n'
        for char in self.characteristics:
            output += char.capitalize() + ': ' + str(self.characteristics[char]) + ' '
        output += '\n \n*Abilities:* '
        for x in self.abilities:
            if self.abilities[x].specialty != '':
                output += '\n' + x.capitalize() + '(' + self.abilities[x].specialty.capitalize() + '): {' + str(
                    self.abilities[x].score) + '} '
            else:
                output += '\n' + x.capitalize() + ': {' + str(self.abilities[x].score) + '} '
        output += '\n \n*Virtues:* '
        for x in self.virtues:
            output += '\n' + x.capitalize()
        output += '\n \n*Flaws:* '
        for x in self.flaws:
            output += '\n' + x.capitalize()
        output += '\n \n*Arts:*'
        for x in self.techniques:
            output += x.capitalize() + ': ' + str(self.techniques[x]) + ' '
            if self.techniquesXP[x] != None:
                output += '(' + str(self.techniquesXP[x]) + ') '
        for x in self.forms:
            output += x.capitalize() + ': ' + str(self.forms[x]) + ' '
            if self.formsXP[x] != None:
                output += '(' + str(self.formsXP[x]) + ') '
        return output
