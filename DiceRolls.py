import discord
import os
import random
import math
import DiscordStyle
import Exclamations
from discord.ext import commands
from pathlib import Path
import pickle
import Character
from Character import Character
import Levenshtein
style = 'blue'


class DiceRolls(commands.Cog):
    def __init__(self,bot):
      self.bot = bot
      self.__last_member = None

    def loadChar(self,*args):
        roller = Character()
     #   print(args)
        for x in (args):
            try:
               # print('attempting to load grog ' + str(x) + ' at ' + str(list(Path.cwd().glob('**/'+str(x)))[0]))
                roller.load(x)
                return roller
            except:
                None
        return roller



    @commands.command(name='simple', help='Rolls a simple die. ex: !simple greg int charm', aliases=['s'])
    async def roll_simple(self, ctx,*args):
        print('Simple Die Rolled!')
        for x in args:
            try:
                roller = self.loadChar(x)
                if roller.name != 'default':
                    break
            except:
                None
        try:
            args=list(args)
            try:
                args.remove(roller.name)
            except:
                try:
                    args.remove(roller.name.lower())
                except:
                    roller = Character()
            print(args)
        except:
            None
        print(roller.name)
        rando = random.randint(1,10)
     #   print('random number generated, ' + str(rando))
        if roller.name != 'default':
            try:
                char = list(set(args)&set(roller.charList))[0]
                charadd = roller.characteristics[char]
                addition = int(charadd)
                #print(args)
                args.remove(char)
            except:
                char = '*no characteristic entered*'
                charadd = 0
                addition = 0
            try:
                abName = ''
                for x in args:
                    abName = abName + str(x)
                similarity = 100
                if abName == '':
                    raise Exception('no ability entered')
                for x in roller.referenceAbility.abilityList():
                    #rint('difference between ' + x + ' and ' + name.upper() + ' is ' + str(Levenshtein.distance(x,name.upper())))
                    if Levenshtein.distance(x,abName.upper()) < similarity:
                        ability = x
                        similarity = Levenshtein.distance(x,abName.upper())
                    else:
                        pass
                #ability = list(set(args)&set(roller.referenceAbility.abilityList()))[0]
                abiadd = roller.abilities[ability].score
                addition += int(abiadd)
            except Exception as e:
                print(e)
                print('no ability entered')
                ability = '*no ability entered*'
                abiadd = 0

            await ctx.send(DiscordStyle.style(roller.name + ' rolls a simple die, adds their ' + char + ' of ' + str(charadd) + ' and their ' + ability.capitalize() + ' of ' + str(abiadd)))
            await ctx.send((DiscordStyle.style('Simple Die Result: {' + str(rando) + '} + ' + str(addition) + ' equaling ' + str(rando + addition), style)))
        else:
            print('sending result to discord')
            await ctx.send((DiscordStyle.style('Simple Die Result: {' + str(rando) + '}')))

    @commands.command(name='stress', help='Rolls a stress die. ex: !stress greg int charm', aliases=['st'])
    async def roll_stress(self, ctx,*args):
        result = random.randint(1,10)
        for x in args:
            try:
                roller = self.loadChar(x)
                if roller.name != 'default':
                    break
            except:
                None
        try:
            args=list(args)
            try:
                args.remove(roller.name)
            except:
                try:
                    args.remove(roller.name.lower())
                except:
                    roller = Character()
            print(args)
        except:
            None
        print(roller.name)
        rando = random.randint(1,10)
     #   print('random number generated, ' + str(rando))
        if roller.name != 'default':
            try:
                char = list(set(args)&set(roller.charList))[0]
                charadd = roller.characteristics[char]
                addition = int(charadd)
                #print(args)
                args.remove(char)
            except:
                char = '*no characteristic entered*'
                charadd = 0
                addition = 0
            try:
                abName = ''
                for x in args:
                    abName = abName + str(x)
                similarity = 100
                if abName == '':
                    raise Exception('no ability entered')
                for x in roller.referenceAbility.abilityList():
                    #rint('difference between ' + x + ' and ' + name.upper() + ' is ' + str(Levenshtein.distance(x,name.upper())))
                    if Levenshtein.distance(x,abName.upper()) < similarity:
                        ability = x
                        similarity = Levenshtein.distance(x,abName.upper())
                    else:
                        pass
                #ability = list(set(args)&set(roller.referenceAbility.abilityList()))[0]
                abiadd = roller.abilities[ability].score
                addition += int(abiadd)
            except Exception as e:
                print(e)
                print('no ability entered')
                ability = '*no ability entered*'
                abiadd = 0

        if (result != 0 and result != 1):
            if roller.name != 'default':
                await ctx.send(DiscordStyle.style((roller.name + ' rolled a {' + str(result) + '} and added their ' + char + ' of ' + str(charadd) + ' and their ' + ability.capitalize() + ' of ' +str(abiadd) + ' for a result of ' + str(result + addition)), style))
            else:
                await ctx.send(DiscordStyle.style(('You rolled a {' + str(result) + '} '), style))
        elif result == 1:
            if roller.name != 'default':
                await ctx.send(DiscordStyle.style(roller.name + ' rolled a {1}, the die explodes!', style))
            else:
                await ctx.send(DiscordStyle.style('You rolled a {1}, the die explodes!', style))
            power = 2
            result = (random.randint(1,10))
            if (result == 1):
                while result == 1:
                    await ctx.send(DiscordStyle.style(('You rolled another {1}, the die explodes AGAIN!'), style))
                    power = ( power + power )
                    result = (random.randint(1,10))
                if roller.name != 'default':
                    await ctx.send(DiscordStyle.style((roller.name + '\'s die exploded ' + str(int(math.log(power,2))) + ' times! Resulting in a multiplier of ' + str(power) + '.\n' + roller.name + '\'s final die roll was {' + str(result) + '} equaling a total of ' + str(result*power) + '!\n' + roller.name + ' then adds their ' + char + ' of ' + str(charadd) + ' and their ' + ability.capitalize() + ' of ' +str(abiadd) + ' for a result of ' + str(result*power + addition)), style))
                else:
                    await ctx.send(DiscordStyle.style(('Your die exploded ' + str(int(math.log(power,2))) + ' times! Resulting in a multiplier of ' + str(power) + '.\nYour final die roll was {' + str(result) + '} equaling a total of ' + str(result*power) + '!\n'), style))
                if (result*power >= 20):
                    await ctx.send(Exclamations.surprise())
            else:
                if roller.name != 'default':
                    await ctx.send(DiscordStyle.style((roller.name + '\'s second roll was a {' + str(result) + '} which doubles to ' + str(result*power) + '!\n'+ roller.name + ' then adds their ' + char + ' of ' + str(charadd) + ' and their ' + ability.capitalize() + ' of ' +str(abiadd) + ' for a result of ' + str(result*power + addition)), style))
                else:
                    await ctx.send(DiscordStyle.style(('Your second roll was a {' + str(result) + '} which doubles to ' + str(result*power) + '!'), style))
                if (result*power >= 20):
                    await ctx.send(Exclamations.surprise())
        elif result == 0:
            if roller.name != 'default':
                await ctx.send(DiscordStyle.style((roller.name + ' rolled a {0}, you might botch! Use the !botch command to check!')))
            else:
                await ctx.send(DiscordStyle.style(('You rolled a {0}, you might botch! Use the !botch command to check!'),'red'))

    @commands.command(name='botch', help='Rolls your botch dice. Use the format !botch [number]', aliases=['b'])
    async def botch(self, ctx,num: int = 1):
        await ctx.send(DiscordStyle.style('Finger\'s crossed for you!', style))
        x = 0
        dice = []

        while x < num:
            dice.append(random.randint(0,9))
            x = x + 1

        results = 'Your results are'

        for x in range(len(dice)):
            results = results + ' {' + str(dice[x]) + '} '

        await ctx.send(DiscordStyle.style(results, style))
        botch = dice.count(0)

        if botch == 0:
            await ctx.send(DiscordStyle.style('You didn\'t botch, congrats!', style))
        elif botch == 1:
            await ctx.send(DiscordStyle.style('You botched 1 time. That\'s ' + Exclamations.unlucky() + '.', style))
        elif botch >1:
            await ctx.send(DiscordStyle.style('You botched ' + str(botch) + ' times. That\'s ' + Exclamations.unlucky() + '.', style))



    @commands.command(name='stressC', help='Rolls a stress die with an expected result')
    @commands.has_role('admin')
    async def roll_stressC(self, ctx,result: int,*args):
        roller = Character()
        for x in set(args):
            try:
                roller.load(x)
            except:
                None
        if roller.name != 'default':
            try:
                char = list(set(args)&set(roller.charList))[0]
                addition = roller.characteristics[char]
            except:
                char = 'nothing'
                addition = 0
        if (result != 0 and result != 1):
            if roller.name != 'default':
                await ctx.send(DiscordStyle.style((roller.name + ' rolled a {' + str(result) + '} and added their ' + char + ' of ' + str(addition) + ' for a result of ' + str(result + addition)), style))
            else:
                await ctx.send(DiscordStyle.style(('You rolled a {' + str(result) + '} '), style))
        elif result == 1:
            if roller.name != 'default':
                await ctx.send(DiscordStyle.style(roller.name + ' rolled a {1}, the die explodes!', style))
            else:
                await ctx.send(DiscordStyle.style('You rolled a {1}, the die explodes!', style))
            power = 2
            result = (random.randint(1,10))
            if (result == 1):
                while result == 1:
                    await ctx.send(DiscordStyle.style(('You rolled another {1}, the die explodes AGAIN!'), style))
                    power = ( power + power )
                    result = (random.randint(1,10))
                if roller.name != 'default':
                    await ctx.send(DiscordStyle.style((roller.name + '\'s die exploded ' + str(int(math.log(power,2))) + ' times! Resulting in a multiplier of ' + str(power) + '.\n' + roller.name + '\'s final die roll was {' + str(result) + '} equaling a total of ' + str(result*power) + '!\n' + roller.name + ' then adds their ' + char + ' of ' + str(addition) + ' for a total result of ' + str(result*power + addition)), style))
                else:
                    await ctx.send(DiscordStyle.style(('Your die exploded ' + str(int(math.log(power,2))) + ' times! Resulting in a multiplier of ' + str(power) + '.\nYour final die roll was {' + str(result) + '} equaling a total of ' + str(result*power) + '!\n'), style))
                if (result*power >= 20):
                    await ctx.send(Exclamations.surprise())
            else:
                if roller.name != 'default':
                    await ctx.send(DiscordStyle.style((roller.name + '\'s second roll was a {' + str(result) + '} which doubles to ' + str(result*power) + '!\n'+ roller.name + ' then adds their ' + char + ' of ' + str(addition) + ' for a total result of ' + str(result*power + addition)), style))
                else:
                    await ctx.send(DiscordStyle.style(('Your second roll was a {' + str(result) + '} which doubles to ' + str(result*power) + '!'), style))
                if (result*power >= 20):
                    await ctx.send(Exclamations.surprise())
        elif result == 0:
            if roller.name != 'default':
                await ctx.send(DiscordStyle.style((roller.name + ' rolled a {0}, you might botch! Use the !botch command to check!')))
            else:
                await ctx.send(DiscordStyle.style(('You rolled a {0}, you might botch! Use the !botch command to check!'),'red'))
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send(DiscordStyle.style('You do not have the correct role for this command.','red'))

def setup(bot):
    bot.add_cog(DiceRolls(bot))
