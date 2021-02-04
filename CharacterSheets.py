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
from Tools import Tools

class CharacterSheet(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.__last_member = None
        self.mage={'mage','wizard','maga','magi','sorcerer','dickhead'}
        self.warrior={'fighter','puncher','brawler','warrior','knight','squire'}
        self.farmer={'farmer','peasant'}
        self.priest={'priest','monk','chaplain'}
        self.style='blue'
        self.associations = {}

    
    async def basePath(self,ctx,msg = False):
        if ctx.guild != None:
            return(Path.cwd()/'servers'/str(ctx.guild.id))
        if ctx.guild == None:
            member = ctx.message.author
            t = Tools(self.bot)
            if str(member.id) in t.memberList:
                try:
                    if msg:
                        await member.send('Currently associated with the guild ' + t.memberList[str(member.id)][2] + ', if you would like to upload to a different server use the !register command there.')
                except:
                        await member.send('Server regristration has been updated since last use, please use !register in your server of choice to use dms with RedCap. Thank you!')
                        raise Exception
                return (Path.cwd()/'servers'/str(t.memberList[str(member.id)][1]))
            await member.send('You are currently not registered to a server. Please use the !register command in your server of choice before using dms with RedCap. Thank you!')
            raise Exception
            return(Path.cwd()/'servers'/'unClassified')

    @commands.command(name='genGrog',help='Generates a random grog.')
    async def genGrog(self,ctx,*args):
        focus = []
        #print(args)
        if self.mage & set(args): focus.extend(['int','sta'])
        if self.warrior & set(args): focus.extend(['str','dex'])
        if self.farmer & set(args): focus.extend(['sta'])
        if self.priest & set(args): focus.extend(['pre','com'])

        #print(focus)
        name=names.get_first_name()
        
        grog=Character(await self.basePath(ctx),name)
        grog.genStats(*focus)
        grog.genAbilities(200)
        grog.genVirtuesFlaws(3)
        await ctx.send(DiscordStyle.style(grog.display(),self.style))
        grog.save('tg')

    @commands.command(name='loadChar',help='loads a previously generated character.')
    async def loadChar(self,ctx,name: str):
       # print('attempting to load ' + name)
        temp = Character(await self.basePath(ctx),'temp')
        temp.load(name)
       # print(temp.display())
        await ctx.send(DiscordStyle.style(temp.display(),self.style))

    @commands.command(name='charList',help='Gives a list of available grogs')
    async def charList(self,ctx):
        a = Character(await self.basePath(ctx))
        result = ''
        try:
            p = await self.basePath(ctx)/'characters'
            l = list(p.glob('*/*'))
            for x in l:
                if x.is_file():
                    result += x.stem.capitalize() + '\n'
        except Exception as e:
            print(e)
        await ctx.send(result)

    @commands.command(name='createGrog',help='Creates a grog via pm')
    async def importGrog(self,ctx):
        member = ctx.message.author
        await member.send('Hello, I\'m going to help you import your character!')
        await member.send('What is your character\'s name?')
        msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
        content = msg.content
        customCharacter = Character(await self.basePath(ctx),str(content))
        await member.send('Your character is named ' + customCharacter.name + '.')
        await member.send('What are your characters characteristics? Please copy and paste my next message and edit the numbers for your stats. Make sure to leave a space on either side of each number. I\'ll verify they add up for you.')
        char = ''
        for x in customCharacter.charList:
            char += x + ': 0 | '
        await member.send(char)
        msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
        msg = msg.content
        print(msg)
        charList=[]
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
        await member.send('Now we just need to add abilities. Send me a message containing the name of the ability, and when I have confirmed it send me how much xp in the ability your character has.')
        msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
        msg = msg.content
        print(msg)
        try:
            abi = customCharacter.addAbility(msg)
            print(abi)
        except Exception as e:
            print(e)
        await member.send('You want to add xp to ' + abi + '. Please send only a number with the amount of xp')
        msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
        msg = msg.content
        print(str(int(msg)))
        customCharacter.abilities[abi].addXp(int(msg))
        await member.send(str(msg) + ' xp added to ' + abi +'. Your score is now ' + str(customCharacter.abilities[abi].score))
        c = True
        while c:
            await member.send('Would you like to add another ability? y/n')
            msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
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
            msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
            msg = msg.content
            try:
                abi = customCharacter.addAbility(msg)
                print(abi)
            except Exception as e:
                print(e)
            await member.send('You want to add xp to ' + abi + '. Please send a number for the amount of xp')
            msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
            msg = msg.content
            customCharacter.abilities[abi].addXp(int(msg))
            await member.send(str(msg) + ' xp added to ' + abi +'. Your score is now ' + str(customCharacter.abilities[abi].score))
        customCharacter.save('g')
        await member.send('Character saved!')
        await member.send(customCharacter.display())

    async def checkExist(self,ctx,name):
        tempChar = Character(await self.basePath(ctx),'temp')
        try:
            tempChar.load(name)
            return True
        except:
            return False

    @commands.command(name='importMC',help='Import a character from a metacreator file via PM')
    async def importMC(self,ctx):
        try:
            member = ctx.message.author
            await self.basePath(ctx,True)
            await member.send('Hello, I\'m going to help you import your character from MetaCreator! Is this character a grog, companion, or magus? (respond g / c / or m)')
            waiting = True
            while waiting == True:
                msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
                if msg.content.lower() == 'grog' or msg.content.lower() == 'g':
                    waiting = False
                    charType = 'g'
                    await member.send('Please copy and paste the data for your grog below')
                elif msg.content.lower() =='companion' or msg.content.lower() == 'c':
                    waiting = False
                    charType = 'c'
                    await member.send('Please copy and paste the data for your companion below')
                elif msg.content.lower() =='magus' or msg.content.lower() == 'm':
                    waiting = False
                    charType = 'm'
                    await member.send('Please copy and paste the data for your magus below')
                else:
                    await member.send('Please enter g, c, or m')
            msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
            msg = msg.content
            contents = msg.splitlines()
            print('name = ' + contents[0])
            if await self.checkExist(ctx,contents[0]):
                print('check 0')
                await member.send('A character by this name already exists, would you like to update it, or check  it out before updating? y / n / c')
                waiting = True
                while waiting == True:
                    msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
                    if msg.content.lower() == 'n' or msg.content.lower() == 'no':
                        waiting = False
                        await member.send('Not a problem, feel free to use the importMC command again with a differently named character.')
                        contents = []
                    elif msg.content.lower() =='y' or msg.content.lower() == 'yes':
                        waiting = False
                        await member.send('Updating...')
                    elif msg.content.lower() =='c' or msg.content.lower() == 'check':
                        tempChar = Character(await self.basePath(ctx),contents[0])
                        tempChar.load(contents[0])
                        await member.send(tempChar.display())
                        await  member.send('\n \n Is this the character you would like to update? Please enter y / n')
                    else:
                        await member.send('Please enter y or n.')

            print('check 0.5')
            newChar = Character(await self.basePath(ctx),contents[0])
            #print('Characteristics =' + contents[1])
            char = contents[1].replace(',','')
            char = char.split(' ')
            charOrder=[0,1,4,5,2,3,6,7]
            #['int', 'per', 'str', 'sta', 'pre', 'com', 'dex', 'qik']
            charList=[]
            it = 0
            for x in char:
                try:
                    #print(x)
                    int(x)
                    newChar.characteristics[newChar.charList[charOrder[it]]] = int(x)
                    it += 1
                except:
                    None
            #print('Warping score = ' + contents[5])
            newChar.warpingScore = int(contents[5].split()[2])
            #print('Confidence = ' + contents[6])
            newChar.confidence = int(contents[6].split()[1])
            #print('Virtues and Flaws = ' + contents[7])
            l = contents[7][18:].split(',')
            #print(l)
            last = ''
            refVirt = Virtue('a')
            refFlaw = Flaw('a')
            for x in l:
                if x[0] == '(' and x[-1] == ')':
                    if x[-2] == '2':
                        if refFlaw.validity(last) < refVirt.validity(last):
                            newChar.addFlaw(last)
                        else:
                            newChar.addVirtue(last)
                    else:
                        continue
                if refFlaw.validity(x) < refVirt.validity(x):
                    #print(x)
                    newChar.addFlaw(x)
                else:
                    #print(x)
                    newChar.addVirtue(x)
            #print('Abilities = ' + contents[15])
            abils = contents[15][11:].split(',')
            #print(abils)
            for x in abils:
                y = x.replace('(','').replace(')','')
                y = y.split()
                abi = ''
                specialty = ''
                yCopy = y.copy()
                for iterable in yCopy:
                    try:
                        score = int(iterable)
                        break
                    except:
                        abi += iterable + ' '
                        y.remove(iterable)
                yCopy = y.copy()
                for iterable in yCopy[1:]:
                    try:
                        xp = int(iterable)
                        break
                    except:
                        specialty += iterable + ' '
                        y.remove(iterable)
                try:
                    abiName = newChar.addAbility(abi,specialty.strip())
                except:
                    abiName = newChar.addAbility(abi)
                try:
                    newChar.abilities[abiName].setScore(score)
                except:
                    None
                try:
                    newChar.abilities[abiName].setXP(xp)
                except:
                    None
            #print('arts = ' + contents[16])
            newChar.save(charType)
            await member.send('Character successfully saved!')
            await member.send(newChar.display())
            #print(newChar.display())
        except Exception as e:
            print(e)







def setup(bot):
    bot.add_cog(CharacterSheet(bot))

