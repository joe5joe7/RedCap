# main.py
import os
import random
import math
import DiscordStyle
import Exclamations
from dotenv import load_dotenv
import DropboxInt

# 1
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2
bot = commands.Bot(command_prefix='!')
style = 'blue'



#bot.load_extension('DropboxInt')
bot.load_extension('DiceRolls')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')



# @bot.command(name='simp', help='Rolls a simple die')
# async def roll_simp(ctx):
#     print('Simple Die Rolled!')
#     await ctx.send((DiscordStyle.style(style,'Simple Die Result: {' + str(random.randint(1,10)) + '} ')))
#
# @bot.command(name='stress', help='Rolls a stress die')
# async def roll_stress(ctx):
#
#     #initial result of the d10
#     result = random.randint(0,9)
#
#     if (result != 0 and result != 1):
#         await ctx.send(DiscordStyle.style(style,('You rolled a {' + str(result) + '} ')))
#     elif result == 1:
#         await ctx.send(DiscordStyle.style(style,('You rolled a {1}, the die explodes!')))
#         power = 2
#         result = (random.randint(1,10))
#         if (result == 1):
#             while result == 1:
#                 await ctx.send(DiscordStyle.style(style,('You rolled another {1}, the die explodes AGAIN!')))
#                 power = ( power + power )
#                 result = (random.randint(1,10))
#             await ctx.send(DiscordStyle.style(style,('Your die exploded ' + str(int(math.log(power,2))) + ' times! Resulting in a multiplier of ' + str(power) + '.\nYour final die roll was {' + str(result) + '} equaling a total of ' + str(result*power) + '!\n')))
#             if (result*power >= 20):
#                 await ctx.send(Exclamations.surprise())
#         else:
#             await ctx.send(DiscordStyle.style(style,('Your second roll was a {' + str(result) + '} which doubles to ' + str(result*power) + '!')))
#             if (result*power >= 20):
#                 await ctx.send(Exclamations.surprise())
#     elif result == 0:
#         await ctx.send(DiscordStyle.style('red',('You rolled a {0}, you might botch! Use the !botch command to check!')))
#
# @bot.command(name='botch', help='Rolls your botch dice')
# async def botch(ctx,num: int):
#     await ctx.send(DiscordStyle.style(style,'Finger\'s crossed for you!'))
#     x = 0
#     dice = []
#
#     while x < num:
#         dice.append(random.randint(0,9))
#         x = x + 1
#
#     results = 'Your results are'
#
#     for x in range(len(dice)):
#         results = results + ' {' + str(dice[x]) + '} '
#
#     await ctx.send(DiscordStyle.style(style,results))
#     botch = dice.count(0)
#
#     if botch == 0:
#         await ctx.send(DiscordStyle.style(style,'You didn\'t botch, congrats!'))
#     elif botch == 1:
#         await ctx.send(DiscordStyle.style(style,'You botched 1 time. That\'s ' + Exclamations.unlucky() + '.'))
#     elif botch >1:
#         await ctx.send(DiscordStyle.style(style,'You botched ' + str(botch) + ' times. That\'s ' + Exclamations.unlucky() + '.'))
#
#
#
# @bot.command(name='stressC', help='Rolls a stress die with an expected result')
# @commands.has_role('admin')
# async def roll_stressC(ctx,result: int):
#     print('Stress Die Rolled')
#     #initial result of the d10
#
#     if (result != 0 and result != 1):
#         await ctx.send(DiscordStyle.style(style,('You rolled a {' + str(result) + '} ')))
#     elif result == 1:
#         await ctx.send(DiscordStyle.style(style,('You rolled a {1}, the die explodes!')))
#         power = 2
#         result = (random.randint(1,10))
#         if (result == 1):
#             while result == 1:
#                 await ctx.send(DiscordStyle.style(style,('You rolled another {1}, the die explodes AGAIN!')))
#                 power = ( power + power )
#                 result = (random.randint(1,10))
#             await ctx.send(DiscordStyle.style(style,('Your die exploded ' + str(int(math.log(power,2))) + ' times! Resulting in a multiplier of ' + str(power) + '.\nYour final die roll was {' + str(result) + '} equaling a total of ' + str(result*power) + '!\n')))
#             if (result*power >= 20):
#                 await ctx.send(Exclamations.surprise())
#         else:
#             await ctx.send(DiscordStyle.style(style,('Your second roll was a {' + str(result) + '} which doubles to ' + str(result*power) + '!')))
#             if (result*power >= 20):
#                 await ctx.send(Exclamations.surprise())
#     elif result == 0:
#         await ctx.send(DiscordStyle.style('red',('You rolled a {0}, you might botch! Use the !botch command to check!')))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(DiscordStyle.style('You do not have the correct role for this command.','red'))

bot.run(TOKEN)

