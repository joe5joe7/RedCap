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
        print(args)
        if self.mage & set(args): focus.extend(['int','sta'])
        if self.warrior & set(args): focus.extend(['str','dex'])
        if self.farmer & set(args): focus.extend(['sta'])
        if self.priest & set(args): focus.extend(['pre','com'])

        print(focus)
        name=names.get_first_name()
        grog=Character(name)
        grog.genStats(*focus)
        await ctx.send(DiscordStyle.style(grog.display(),self.style))
        outfile=open(Path.cwd()/'grogs'/name,'wb')
        pickle.dump(grog,outfile)
        outfile.close()

    @commands.command(name='loadGrog',help='loads a previously generated grog.')
    async def loadGrog(self,ctx,name: str):
        print('attempting to load ' + name)
        print('using path ' + str(Path.cwd()/'grogs'/name))
        infile = open(Path.cwd()/'grogs'/name,'rb')
        grog=pickle.load(infile)
        print('successfully unpickled')
        infile.close()
        print(grog.display())
        await ctx.send(DiscordStyle.style(grog.display(),self.style))


def setup(bot):
    bot.add_cog(Grog(bot))

