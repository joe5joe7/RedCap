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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(DiscordStyle.style('You do not have the correct role for this command.','red'))

bot.run(TOKEN)

