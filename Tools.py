from Character import Character
from Character import Ability
from discord.ext import commands
import DiscordStyle

class Tools(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.__last_member = None
        self.style = 'blue'

    @commands.command(name='getStats',help='Generate a random block of characteristics')
    async def getStats(self,ctx,*args):
        #await ctx.send(args)
        temp = Character('temp')
        #print(args)
        #print(*args)
        temp.genStats(*args)
        await ctx.send(DiscordStyle.style(temp.display(),self.style))

    @commands.command(name='abilityList',help='lists all abilities in the game')
    async def abilityList(self,ctx):
        a = Ability('charm')
        print(a.availableAbilities())
        await ctx.send(DiscordStyle.style(a.availableAbilities(),self.style))

    @commands.command(name='abilitySum',help='gives a summary of any ability')
    async def abilitySum(self,ctx,*args: str):
        print(''.join([str(elem) for elem in args]))
        a = Ability(''.join([str(elem) for elem in args]))
        await ctx.send(DiscordStyle.style(a.summary(),self.style))

def setup(bot):
    bot.add_cog(Tools(bot))
    print('tools cog connected')
