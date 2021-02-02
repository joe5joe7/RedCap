from discord import client

from Character import Character
import random
import pickle
from discord.ext import commands
from pathlib import Path
import names
import DiscordStyle

class Grog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.__last_member = None
        self.mage={'mage','wizard','maga','magi','sorcerer','dickhead'}
        self.warrior={'fighter','puncher','brawler','warrior','knight','squire'}
        self.farmer={'farmer','peasant'}
        self.priest={'priest','monk','chaplain'}
        self.style='blue'

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
        grog=Character(name)
        grog.genStats(*focus)
        grog.genAbilities(200)
        await ctx.send(DiscordStyle.style(grog.display(),self.style))
        grog.save('tg')

    @commands.command(name='loadGrog',help='loads a previously generated grog.')
    async def loadGrog(self,ctx,name: str):
       # print('attempting to load ' + name)
        temp = Character('temp')
        temp.load(name)
       # print(temp.display())
        await ctx.send(DiscordStyle.style(temp.display(),self.style))

    @commands.command(name='grogList',help='Gives a list of available grogs')
    async def grogList(self,ctx):
        a = Character()
        result = ''
        try:
            p = Path.cwd() / 'characters'
            l = list(p.glob('*/*'))
            for x in l:
                if x.is_file():
                    result += x.stem.capitalize() + '\n'
        except Exception as e:
            print(e)
        await ctx.send(result)

    @commands.command(name='importGrog',help='imports a grog via pm')
    async def importGrog(self,ctx):
        member = ctx.message.author
        await member.send('Hello, I\'m going to help you import your character!')
        await member.send('What is your character\'s name?')
        msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
        content = msg.content
        customCharacter = Character(str(content))
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






def setup(bot):
    bot.add_cog(Grog(bot))

