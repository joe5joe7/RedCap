from Character import Character
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

def setup(bot):
    bot.add_cog(Tools(bot))
    print('tools cog connected')
