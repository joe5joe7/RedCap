#This will be folded into the Character class when it's complete and tested

from pathlib import Path
import Levenshtein

class VirtueFlaw():
    def __init__(self,specification = ''):
        self.name = ''
        self.description = ''
        self.value = ''
        self.type = ''
        self.types = ('General', 'Hermetic', 'Supernatural', 'Social Status', 'Personality', 'Story', 'Special')
        self.valueTypes = ('Minor', 'Major', 'Free', 'Special')
        self.virtuesRef = {'name': '', 'description': '', 'value': '', 'type': ''}
        self.virtuesLib = {}
        self.referencePath = Path.cwd() / 'referenceFiles'
        self.specification = specification
        self.flags = []
        try:
            self.referencePath.mkdir(parents=True)
        except:
            pass
        similarity = 100

    def addSpecification(self,specification):
        self.specification = specification


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
            return (self.name + '\n' + self.value + '(' + self.speciality + '), ' + self.type + '\n Description: ' + self.description)
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
    def __init__(self, name, specification=''):
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
        if specification != '':
            self.addSpecification(specification)

    def isVirtue(self):
        return True


class Flaw(VirtueFlaw):
    def __init__(self, name, specification=''):
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
        if specification != '':
            self.addSpecification(specification)

    def isFlaw(self):
        return True
