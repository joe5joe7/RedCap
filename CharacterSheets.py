from discord import client

import Character
from Character import Character
from Character import Virtue
from Character import Flaw
import random
import pickle
from discord.ext import commands
from pathlib import Path
import names
import DiscordStyle
import re
import spacy
import shutil


# TODO
# add more aliases for lowercased commands
# add association for loadchar


class CharacterSheet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__last_member = None
        self.mage = {'mage', 'wizard', 'maga', 'magi', 'sorcerer', 'dickhead'}
        self.warrior = {'fighter', 'puncher', 'brawler', 'warrior', 'knight', 'squire'}
        self.farmer = {'farmer', 'peasant'}
        self.priest = {'priest', 'monk', 'chaplain'}
        self.style = 'blue'
        self.associations = {}
        self.nlp = spacy.load('en_core_web_lg')
        self.memberList = {}

        self.updateMemberList()

        try:
            (Path.cwd() / 'referenceFiles' / 'libraries').mkdir(parents=True)
        except:
            pass
        try:
            (Path.cwd() / 'referenceFiles' / 'abilitySpecifications').mkdir(parents=True)
        except:
            pass
        if not (Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib').exists():
            print('Ability library does not exist in expected place ' + str(
                Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib'))
        if not (Path.cwd() / 'referenceFiles' / 'libraries' / 'virtueLib').exists():
            print('Virtue library does not exist in expected place ' + str(
                Path.cwd() / 'referenceFiles' / 'libraries' / 'virtueLib'))
        if not (Path.cwd() / 'referenceFiles' / 'libraries' / 'flawLib').exists():
            print('Virtue library does not exist in expected place ' + str(
                Path.cwd() / 'referenceFiles' / 'libraries' / 'flawLib'))
        if not (Path.cwd() / 'referenceFiles' / 'defaultIcon.png').exists():
            print('Default icon does not exist in expected place ' + str(
                Path.cwd() / 'referenceFile' / 'defaultIcon.png'))

    async def basePath(self, ctx, msg=False):
        if ctx.guild != None:
            return (Path.cwd() / 'servers' / str(ctx.guild.id))
        if ctx.guild == None:
            member = ctx.message.author
            self.updateMemberList()
            if str(member.id) in self.memberList:
                try:
                    if msg:
                        await member.send('Currently associated with the guild ' + self.memberList[str(member.id)][
                            2] + ', if you would like to upload to a different server use the !register command there.')
                except:
                    await member.send(
                        'Server regristration has been updated since last use, please use !register in your server of choice to use dms with RedCap. Thank you!')
                    raise Exception
                return (Path.cwd() / 'servers' / str(self.memberList[str(member.id)][1]))
            await member.send(
                'You are currently not registered to a server. Please use the !register command in your server of choice before using dms with RedCap. Thank you!')
            raise Exception
            # return(Path.cwd()/'servers'/'unClassified')

    @commands.command(name='genGrog', help='Generates a random grog.')
    async def genGrog(self, ctx, *args):

        # first step is to generate a name
        print('genning grog')
        try:
            name = names.get_first_name()
            grog = Character(self.nlp, await self.basePath(ctx), name)
            grog.genVirtuesFlawsGrog(*args)
            grog.genSimStats()
            grog.genStartingAbilities(*args)
            grog.age = random.randint(18, 35)
            grog.genGrogAbilities(grog.age, *args)

            keyWord = ''
            for word in args:
                keyWord += word + ' '
            keyWord = keyWord.strip()

            grog.description = keyWord
            grog.save('tg')
        except Exception as e:
            print(e)
        # focus = []
        # #print(args)
        # if self.mage & set(args): focus.extend(['int','sta'])
        # if self.warrior & set(args): focus.extend(['str','dex'])
        # if self.farmer & set(args): focus.extend(['sta'])
        # if self.priest & set(args): focus.extend(['pre','com'])
        #
        # #print(focus)
        # name=names.get_first_name()
        #
        # grog=Character(self.nlp,await self.basePath(ctx),name)
        # grog.genStats(*focus)
        # grog.genAbilities(200)
        # grog.genVirtuesFlaws(3)
        output = grog.display()
        await ctx.send(file=output[1], embed=output[0])
        # grog.save('tg')

    @commands.command(name='saveGrog', help='Saves a temp grog')
    async def saveGrog(self, ctx, name: str):
        temp = Character(self.nlp, await self.basePath(ctx), 'temp')
        temp.load(name)
        temp.save('g')
        await ctx.send(DiscordStyle.style(temp.name + ' saved!', self.style))

    @commands.command(name='purge', help='Purges temp grogs')
    async def purge(self, ctx):
        try:
            shutil.rmtree(await self.basePath(ctx) / 'characters' / 'tempGrogs')
            await ctx.send(DiscordStyle.style('Temp grogs purged!', self.style))
        except Exception as e:
            print(e)

    @commands.command(name='loadChar', help='loads a previously generated character.')
    async def loadChar(self, ctx, name: str):
        # print('attempting to load ' + name)
        temp = Character(self.nlp, await self.basePath(ctx), 'temp')
        temp.load(name)
        # print(temp.display())
        output = temp.display()
        await ctx.send(file=output[1], embed=output[0])

    @commands.command(name='charList', help='Gives a list of available grogs')
    async def charList(self, ctx):
        a = Character(self.nlp, await self.basePath(ctx))
        result = ''
        try:
            p = await self.basePath(ctx) / 'characters'
            l = list(p.glob('*/*'))
            for x in l:
                if x.is_file():
                    result += x.stem.capitalize() + '\n'
        except Exception as e:
            print(e)
        await ctx.send(result)

    @commands.command(name='createGrog', help='Creates a grog via pm')
    async def importGrog(self, ctx):
        member = ctx.message.author
        await member.send('Hello, I\'m going to help you import your character!')
        await member.send('What is your character\'s name?')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        content = msg.content
        customCharacter = Character(self.nlp, await self.basePath(ctx), str(content))
        await member.send('Your character is named ' + customCharacter.name + '.')
        await member.send(
            'What are your characters characteristics? Please copy and paste my next message and edit the numbers for your stats. Make sure to leave a space on either side of each number. I\'ll verify they add up for you.')
        char = ''
        for x in customCharacter.charList:
            char += x + ': 0 | '
        await member.send(char)
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        msg = msg.content
        charList = []
        for x in msg.split(' '):
            try:
                charList.append(int(x))
            except:
                None
        confirm = ''
        y = 0
        for x in customCharacter.charList:
            customCharacter.characteristics[x] = charList[y]
            confirm = confirm + x + ': ' + str(charList[y]) + ' '
            y += 1
        await member.send('Your characteristics are: ' + confirm)
        await member.send(
            'Now we just need to add abilities. Send me a message containing the name of the ability, and when I have confirmed it send me how much xp in the ability your character has.')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        msg = msg.content
        try:
            abi = customCharacter.addAbility(msg)
        except Exception as e:
            print(e)
        await member.send('You want to add xp to ' + abi + '. Please send only a number with the amount of xp')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        msg = msg.content
        customCharacter.abilities[abi].addXp(int(msg))
        await member.send(
            str(msg) + ' xp added to ' + abi + '. Your score is now ' + str(customCharacter.abilities[abi].score))
        c = True
        while c:
            await member.send('Would you like to add another ability? y/n')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            msg = msg.content
            if msg == 'n':
                c = False
                break
            elif msg == 'y':
                None
            else:
                await member.send('Invalid response. Please respond with only a y or an n')
                continue
            await member.send('What abliity would you like to add?')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            msg = msg.content
            try:
                abi = customCharacter.addAbility(msg)
            except Exception as e:
                print(e)
            await member.send('You want to add xp to ' + abi + '. Please send a number for the amount of xp')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            msg = msg.content
            customCharacter.abilities[abi].addXp(int(msg))
            await member.send(
                str(msg) + ' xp added to ' + abi + '. Your score is now ' + str(customCharacter.abilities[abi].score))
        customCharacter.save('g')
        await member.send('Character saved!')
        output = customCharacter.display()
        await ctx.send(file=output[1], embed=output[0])

    async def checkExist(self, ctx, name):
        tempChar = Character(self.nlp, await self.basePath(ctx), 'temp')
        try:
            tempChar.load(name)
            return True
        except:
            return False

    @commands.command(name='importMC', help='Import a character from a metacreator file via PM')
    async def importMC(self, ctx):
        try:
            member = ctx.message.author
            await self.basePath(ctx, True)
            await member.send(
                'Hello, I\'m going to help you import your character from MetaCreator! Is this character a grog, companion, or magus? (respond g / c / or m)')
            waiting = True
            while waiting == True:
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                if msg.content.lower() == 'grog' or msg.content.lower() == 'g':
                    waiting = False
                    charType = 'g'
                    await member.send('Please copy and paste the data for your grog below')
                elif msg.content.lower() == 'companion' or msg.content.lower() == 'c':
                    waiting = False
                    charType = 'c'
                    await member.send('Please copy and paste the data for your companion below')
                elif msg.content.lower() == 'magus' or msg.content.lower() == 'm':
                    waiting = False
                    charType = 'm'
                    await member.send('Please copy and paste the data for your magus below')
                else:
                    await member.send('Please enter g, c, or m')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            msg = msg.content
            contents = msg.splitlines()
            # print('name = ' + contents[0])
            if await self.checkExist(ctx, contents[0]):
                await member.send('A character named ' + contents[
                    0] + ' already exists on this server. Would you like to update that character? yes / no / check')
                waiting = True
                while waiting == True:
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg.content.lower() == 'n' or msg.content.lower() == 'no':
                        waiting = False
                        await member.send(
                            'Not a problem, feel free to use the importMC command again with a differently named character.')
                        contents = []
                    elif msg.content.lower() == 'y' or msg.content.lower() == 'yes':
                        waiting = False
                        await member.send('Updating...')
                        oldChar = Character(self.nlp, await self.basePath(ctx), 'old')
                        oldChar.load(contents[0])

                    elif msg.content.lower() == 'c' or msg.content.lower() == 'check':
                        tempChar = Character(self.nlp, await self.basePath(ctx), contents[0])
                        tempChar.load(contents[0])
                        output = tempChar.display()
                        await ctx.send(file=output[1], embed=output[0])
                        await  member.send('\n \n Is this the character you would like to update? Please enter y / n')
                    else:
                        await member.send('Please enter yes, no, or check')

            newChar = Character(self.nlp, await self.basePath(ctx), contents[0])
            try:
                newChar.identifier = oldChar.identifier
            except:
                None
            for line in contents:
                title = line.split(':')[0]
                title = title.strip()
                content = line.replace(title + ':', '')
                if title == 'Covenant':
                    newChar.covenant = content
                elif title == 'Characteristics':
                    content = content.replace(',', '').split(' ')
                    # ['int', 'per', 'str', 'sta', 'pre', 'com', 'dex', 'qik']
                    charOrder = [0, 1, 4, 5, 2, 3, 6, 7]
                    it = 0
                    for x in content:
                        try:
                            int(x)
                            newChar.characteristics[newChar.charList[charOrder[it]]] = int(x)
                            it += 1
                        except:
                            None
                elif title == 'Age':
                    try:
                        newChar.age = int(content.split()[0])
                    except ValueError:
                        print('age did not start with an int')
                elif title == 'Warping Score':
                    try:
                        newChar.warpingScore = int(content.replace('(', '').replace(')', '').split(' ')[0])
                        newChar.warpingPoints = int(content.replace('(', '').replace(')', '').split(' ')[1])
                    except:
                        None
                elif title == 'Confidence':
                    newChar.confidence = int(content.replace('(', '').replace(')', '').strip().split(' ')[0])
                elif title == 'Virtues and Flaws':
                    l = content.split(',')
                    # print(l)
                    last = ''
                    refVirt = Virtue('a')
                    refFlaw = Flaw('a')
                    spec = None
                    for x in l:
                        test = re.search('\((.*)\)', x)
                        if test != None:
                            if test != '':
                                spec = test.group().replace('(', '').replace(')', '').strip()
                                x = x.replace(test.group(), '')
                        test = re.search('\[(.*)\]', x)
                        if test != None:
                            if test != '' and spec != None:
                                spec += ' ' + test.group().replace('(', '').replace(')', '').strip()
                                x = x.replace(test.group(), '')
                            elif test != '' and spec == None:
                                spec = test.group().replace('(', '').replace(')', '').strip()
                                x = x.replace(test.group(), '')
                        if refFlaw.validity(x) < refVirt.validity(x):
                            # print(x)
                            if spec == None:
                                newChar.addFlaw(x)
                            elif spec != None:
                                newChar.addFlaw(x, spec)
                        else:
                            # print(x)
                            if spec == None:
                                newChar.addVirtue(x)
                            elif spec != None:
                                newChar.addVirtue(x, spec)
                        spec = None
                elif title == 'Abilities':
                    abils = content.split(',')
                    # print(abils)
                    for x in abils:
                        found = re.findall(r'(\([^)]+\))', x)
                        if len(found)>0:
                            x = x.replace(found[0], '')
                            spec = found[0][1:-1]
                            if len(found)>1:
                                x = x.replace(found[1], '')
                                try:
                                    xp = int(found[1][1:-1])
                                except ValueError:
                                    print('expected int for XP, got str')
                            else:
                                xp = 0
                        else:
                            spec = 'none'
                            xp = 0

                        y = x.split()
                        abi = ''
                        score = 0

                        for iterable in y:
                            try:
                                score = int(iterable)
                                break
                            except:
                                abi += iterable + ' '

                        print(abi)
                        if ':' in abi:
                            specification = abi.split(':')[1].strip()
                            abi = abi.split(':')[0].strip()
                        else:
                            specification = 'none'
                        abiName = newChar.addAbility(abi, speciality = spec.strip(),specification=specification)

                        try:
                            newChar.abilities[abiName].setScore(score)
                        except:
                            pass
                        try:
                            newChar.abilities[abiName].setXP(xp)
                        except:
                            pass
                elif title == 'Arts':
                    arts = content.split(',')
                    for x in arts:
                        art = x.strip().split(' ')[0]
                        x = x.replace(art, '')
                        art = art.lower()
                        b = x.split('+')
                        score = int(b[0].strip())
                        xp = None
                        try:
                            xp = int(b[1].strip())
                        except:
                            None
                        if art in newChar.formList:
                            newChar.forms[art] = score
                            newChar.formsXP[art] = xp
                        elif art in newChar.techniqueList:
                            newChar.techniques[art] = score
                            newChar.techniquesXP[art] = xp

                        score
            try:
                newChar.save(charType)
            except Exception as e:
                print(e)
            await member.send('Character successfully saved!')
            output = newChar.display()
            await ctx.send(file=output[1], embed=output[0])
            # print(newChar.display())
        except Exception as e:
            print(e)

    def updateMemberList(self):
        try:
            a = open(Path.cwd() / 'servers' / 'members.txt', 'x')
            a.close()
        except:
            members = open(Path.cwd() / 'servers' / 'members.txt', 'r')
            membersData = members.readlines()
            members.close()
            # print(membersData)
            for line in membersData:
                memberInfo = line.split(' | ')
                copy = memberInfo.copy()
                y = 0
                for x in copy:
                    memberInfo[y] = x.replace('\|', '|')
                    y += 1
                self.memberList[memberInfo[0]] = memberInfo[1:].copy()


def setup(bot):
    bot.add_cog(CharacterSheet(bot))
