from Character import Character
from Character import Ability
from discord.ext import commands
from pathlib import Path
import DiscordStyle
from shutil import copyfile
import discord
import requests
import spacy


# Remove file access before full release

class Tools(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.__last_member = None
        self.style = 'blue'
        self.memberList={}
        servers = self.bot.guilds
        try:
            for server in servers:
                #print(server.id)
                (Path.cwd()/'servers'/str(server.id)).mkdir(parents = True,exist_ok=True)
                try:
                    a = open(Path.cwd()/'servers'/str(server.id)/(server.name + '.txt'),'x')
                    a.close()
                except:
                    None
                print('RedCap has connected to ' + server.name + '!')
        except Exception as e:
            print(e)
        self.nlp = spacy.load('en_core_web_lg')

        self.updateMemberList()



    def basePath(self,ctx):
        if ctx.guild != None:
            return(Path.cwd()/'servers'/str(ctx.guild.id))
        if ctx.guild == None:
            member = ctx.message.author
            t = Tools(self.bot)
            if str(member.id) in t.memberList:
                try:
                    member.send('Currently associated with the guild ' + t.memberList[str(member.id)][2] + ', if you would like to upload to a different server use the !register command there.')
                except:
                    member.send('Server regristration has been updated since last use, please use !register in your server of choice to use dms with RedCap. Thank you!')
                return (Path.cwd()/'servers'/str(t.memberList[str(member.id)][1]))
            member.send('You are currently not registered to a server. Please use the !register command in your server of choice before using dms with RedCap. Thank you!')
            return(Path.cwd()/'servers'/'unClassified')


    @commands.command(name='echo',help='testing function, bot will reply with whatever you send',hidden=True)
    async def echo(self,ctx):
        member = ctx.message.author
        await member.send('What would you like me to say?')
        msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
        await member.send(msg.content)
        #print('checking for attachments')
        if msg.attachments[0] != None:
            await member.send('You sent me an attachment!')
            try:
                attach = await msg.attachments[0].to_file()
                await member.send('Here you go!',file=attach)
            except Exception as e:
                print(e)
        else:
            None
            #print('no attachments found!')

    @commands.command(name='register', help='Register to this server for the sake of accessing commands from DMs', aliases=['reg'])
    async def register(self,ctx):
        self.updateMemberList()
        member = ctx.message.author
        try:
            if str(member.id) in self.memberList.keys():
                    self.memberList[str(member.id)] = [member.name]
                    self.memberList[str(member.id)].append(str(member.guild.id))
                    self.memberList[str(member.id)].append(member.guild.name)
                    print('updated guild to ' + str(member.guild.name))
            else:
                    try:
                      self.memberList[str(member.id)]=[member.name,str(member.guild.id),member.guild.name]
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)
        self.saveMemberList()
        await ctx.send(member.name + ' registered to ' + member.guild.name +'!')


    def updateMemberList(self):
        try:
            a = open(Path.cwd()/'servers'/'members.txt','x')
            a.close()
        except:
            members = open(Path.cwd()/'servers'/'members.txt','r')
            membersData = members.readlines()
            members.close()
            #print(membersData)
            for line in membersData:
                memberInfo = line.split(' | ')
                copy = memberInfo.copy()
                y = 0
                for x in copy:
                    memberInfo[y] = x.replace('\|','|')
                    y+=1
                self.memberList[memberInfo[0]] = memberInfo[1:].copy()
            print(self.memberList)

    def saveMemberList(self):
        copyfile((Path.cwd()/'servers'/'members.txt'),(Path.cwd()/'servers'/'backup.members.txt'))
        output = ''
        for mem in self.memberList.keys():
            output += mem
            for data in self.memberList[mem]:
                output += ' | ' + str(data).replace('|','\|')
            output += '\n'
        #print('final:\n')
        #print(output)
        saveFile = open(Path.cwd()/'servers'/'members.txt','w')
        saveFile.write(output.strip())
        saveFile.close()

    @commands.command(name='sendRef', help='Send a copy of a reference file', aliases=['sRef'])
    async def sendRef(self,ctx):
        member = ctx.message.author
        await member.send('Which reference file would you like?')
        x = 1
        fileList = {}
        for filePath in (Path.cwd() / 'referenceFiles').glob('**/*'):
            await member.send(str(x) + '. ' + filePath.stem)
            fileList[str(x)] = filePath
            x += 1
        msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
        while msg.content not in fileList.keys() and msg.content != 'cancel' and msg.content!= 'c':
            await member.send('Please respond with the number indicating the file you would like, or \'cancel\'.')
            msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
        if msg.content == 'c' or msg.content == 'cancel':
            await member.send('Understandable, have a nice day!')
        else:
            try:
                await member.send('Here you go!',file=discord.File(fileList[msg.content]))
            except Exception as e:
                print(e)

    @commands.command(name='updateRef', help='Update a reference file', aliases=['uRef'])
    async def updateRef(self,ctx):
        member = ctx.message.author
        await member.send('Which reference file would you like to update?')
        await member.send('0. Add a new reference file')
        x = 1
        fileList = {}
        for filePath in (Path.cwd() / 'referenceFiles').glob('**/*'):
            await member.send(str(x) + '. ' + filePath.stem)
            fileList[str(x)] = filePath
            x += 1
        msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
        while msg.content not in fileList.keys() and msg.content != 'cancel' and msg.content!= 'c' and msg.content != '0':
            await member.send('Please respond with the number indicating the file you would like to update, or \'cancel\'.')
            msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
        if msg.content == 'c' or msg.content == 'cancel':
            await member.send('Understandable, have a nice day!')
            return
        elif msg.content == '0':
            await member.send('Please send the file with the caption as the filename you would like. Please only send a single file, and include any necessary suffixes.')
            msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
            await msg.attachments[0].save(Path.cwd()/'referenceFiles'/msg.content)
            while msg.attachments[0] == None:
                await member.send('Please send a file, or reply \'cancel\'.')
                msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
                if msg.content == 'c' or msg.content == 'cancel':
                    await member.send('Understandable, have a nice day!')
                    return
            await member.send(msg.content + ' saved! Have a nice day!')
        else:
            try:
                index = msg.content
                await member.send('Please send the updated copy of ' + fileList[index].stem)
                msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
                while msg.attachments[0] == None:
                    await member.send('Please send a file, or reply \'cancel\'.')
                    msg = await self.bot.wait_for('message',check=lambda message: message.author == ctx.author)
                    if msg.content == 'c' or msg.content == 'cancel':
                        await member.send('Understandable, have a nice day!')
                        return
                await member.send('Here\s a backup of the current file.',file=discord.File(fileList[index]))
                await msg.attachments[0].save(fileList[index])
                await member.send('Saved ' + fileList[index].stem)



            except Exception as e:
                print(e)


    # @commands.command(name='regServer',help='registers members of the server with RedCap')
    # async def regServer(self,ctx):
    #     self.updateMemberList()
    #     print('registering ' + ctx.guild.name)
    #     guildMembers = ctx.guild.members
    #     for mem in guildMembers:
    #         if str(mem.id) in self.memberList:
    #             print(mem.name + ' is already in member list')
    #             if mem.guild.id in self.memberList[str(mem.id)][1]:
    #                 continue
    #             else:
    #                 self.memberList[str(mem.id)][1].append(mem.guild.id)
    #         else:
    #             print(mem.name + ' is not on the member list')
    #             try:
    #               self.memberList[str(mem.id)]=[mem.name,[mem.guild.id]]
    #             except Exception as e:
    #                 print(e)
    #             print(mem.name + ' was added to member list')
    #     self.saveMemberList()




    # Depreciated with the gen grog command development
    # @commands.command(name='getStats',help='Generate a random block of characteristics')
    # async def getStats(self,ctx,*args):
    #     #await ctx.send(args)
    #     temp = Character(self.nlp,self.basePath(ctx),'temp')
    #     #print(args)
    #     #print(*args)
    #     temp.genStats(*args)
    #     await ctx.send(DiscordStyle.style(temp.display(),self.style))

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

    # @commands.command(name='serverInfo',hidden=True)
    # async def serverInfo(self,ctx):
    #     if ctx.guild is None:
    #         print('DM')
    #         print(ctx.message.author)
    #     print(ctx.guild.name)
    #     await ctx.send(ctx.guild.name)

    @commands.Cog.listener()
    async def on_member_join(self,member):
        None

def setup(bot):
    bot.add_cog(Tools(bot))
    #print('tools cog connected')
