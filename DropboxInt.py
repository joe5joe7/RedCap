import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
import os
from discord.ext import commands




class dropboxInt(commands.Cog):
    def __init__(self,bot):
      self.bot = bot
      self.__last_member = None


    @commands.command(name='authorize')
    async def authorize(self, ctx):
        print('working')
        await ctx.send('working')


        authorize_url = auth_flow.start()

        try:
            oauth_result = auth_flow.finish('tu1LaETjc_kAAAAAAAAKwRVCj8CLlYhW6-nJOvoQN8Q')
        except Exception as e:
            await ctx.send('Error: %s' % (e,))
            exit(1)

        with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token) as dbx:
            dbx.users_get_current_account()
            await ctx.send("Successfully set up client!")

    @commands.command(name='readChar')
    async def readChar(self,ctx):
        print('triggered')
        token = os.getenv('DROPBOX_TOKEN')
        ACCESS_TOKEN = token
        print('triggered2')
        dbx = dropbox.Dropbox('9p6hYv9rT3sAAAAAAAAAAb0huQmloHSOlAGZi_8kRQuHvNKBT3_BTbE_hs4d1oFW')
        print('triggered3')

        dbx.files_download_to_file('/Bjorn.txt','/Bjorn.txt')
        print('accessed?')
        print(f)
        for line in f:
            await ctx.sent(line)







def setup(bot):
    bot.add_cog(dropboxInt(bot))
    key = os.getenv('DROPBOX_KEY')
    secret = os.getenv('DROPBOX_SECRET')
    token = os.getenv('DROPBOX_TOKEN')

    APP_KEY = key
    APP_SECRET = secret


    auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
