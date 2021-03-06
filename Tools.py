from typing import List, Union
from Character import VirtueFlaw
from discord.ext import commands
from pathlib import Path
from shutil import copyfile
import discord
import spacy
import json
import io
import re
import Levenshtein


# TODO Remove file access before full release
# TODO add .strip to custos permit abi
# TODO add versioning for virtue/flaws/abi libs and create update function
# TODO create clean function for libs that strips all unnecessary white space
# TODO fix update VF printing '[' instead of element name
# TODO have send lib send readable JSON


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__last_member = None
        self.style = 'blue'
        self.memberList = {}
        servers = self.bot.guilds
        try:
            for server in servers:
                # print(server.id)
                (Path.cwd() / 'servers' / str(server.id)).mkdir(parents=True, exist_ok=True)
                try:
                    a = open(Path.cwd() / 'servers' / str(server.id) / (server.name + '.txt'), 'x')
                    a.close()
                except FileExistsError:
                    pass
                print('RedCap has connected to ' + server.name + '!')
        except Exception as e:
            print(e)
        self.nlp = spacy.load('en_core_web_lg')

        self.updateMemberList()

    def basePath(self, ctx):
        if ctx.guild is not None:
            return Path.cwd() / 'servers' / str(ctx.guild.id)
        if ctx.guild is None:
            member = ctx.message.author
            t = Tools(self.bot)
            if str(member.id) in t.memberList:
                try:
                    member.send('Currently associated with the guild ' + t.memberList[str(member.id)][
                        2] + ', if you would like to upload to a different server use the !register command there.')
                except IndexError:
                    member.send(
                        'Server registration has been updated since last use, please use !register in your server of choice to use dms with RedCap. Thank you!')
                return Path.cwd() / 'servers' / str(t.memberList[str(member.id)][1])
            member.send(
                'You are currently not registered to a server. Please use the !register command in your server of choice before using dms with RedCap. Thank you!')
            return Path.cwd() / 'servers' / 'unClassified'

    @commands.command(name='echo', help='testing function, bot will reply with whatever you send', hidden=True)
    async def echo(self, ctx):
        member = ctx.message.author
        await member.send('What would you like me to say?')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        await member.send(msg.content)
        # print('checking for attachments')
        if msg.attachments[0] is not None:
            await member.send('You sent me an attachment!')
            try:
                attach = await msg.attachments[0].to_file()
                await member.send('Here you go!', file=attach)
            except Exception as e:
                print(e)
        else:
            pass
            # print('no attachments found!')

    @commands.command(name='register', help='Register to this server for the sake of accessing commands from DMs',
                      aliases=['reg'])
    async def register(self, ctx):
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
                    self.memberList[str(member.id)] = [member.name, str(member.guild.id), member.guild.name]
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
        self.saveMemberList()
        await ctx.send(member.name + ' registered to ' + member.guild.name + '!')

    def updateMemberList(self):
        try:
            a = open(Path.cwd() / 'servers' / 'members.txt', 'x')
            a.close()
        except FileExistsError:
            members = open(Path.cwd() / 'servers' / 'members.txt', 'r')
            membersData = members.readlines()
            members.close()
            # print(membersData)
            for line in membersData:
                memberInfo = line.split(' | ')
                copy = memberInfo.copy()
                y = 0
                for x in copy:
                    memberInfo[y] = x.replace(r'\|', '|')
                    y += 1
                self.memberList[memberInfo[0]] = memberInfo[1:].copy()
            # print(self.memberList)

    def saveMemberList(self):
        copyfile((Path.cwd() / 'servers' / 'members.txt'), (Path.cwd() / 'servers' / 'backup.members.txt'))
        output = ''
        for mem in self.memberList.keys():
            output += mem
            for data in self.memberList[mem]:
                output += ' | ' + str(data).replace(r'|', r'\|')
            output += '\n'
        # print('final:\n')
        # print(output)
        saveFile = open(Path.cwd() / 'servers' / 'members.txt', 'w')
        saveFile.write(output.strip())
        saveFile.close()

    @commands.command(name='sendRef', help='Send a copy of a reference file', aliases=['sRef'])
    async def sendRef(self, ctx):
        member = ctx.message.author
        content = 'Which reference file would you like?'
        x = 1
        fileList = {}
        for filePath in (Path.cwd() / 'referenceFiles').glob('**/*'):
            content += '\n' + str(x) + '. ' + filePath.stem
            fileList[str(x)] = filePath
            x += 1
        await member.send(content)
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        while msg.content not in fileList.keys() and msg.content != 'cancel' and msg.content != 'c':
            await member.send('Please respond with the number indicating the file you would like, or \'cancel\'.')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content == 'c' or msg.content == 'cancel':
            await member.send('Understandable, have a nice day!')
        else:
            try:
                await member.send('Here you go!', file=discord.File(fileList[msg.content]))
            except Exception as e:
                print(e)

    @commands.command(name='updateRef', help='Update a reference file', aliases=['uRef'])
    async def updateRef(self, ctx):
        member = ctx.message.author
        content = 'Which reference file would you like to update?\n0. Add a new reference file'
        x = 1
        fileList = {}
        for filePath in (Path.cwd() / 'referenceFiles' / 'libraries').glob('**/*'):
            content += '\n' + str(x) + '. ' + filePath.stem
            fileList[str(x)] = filePath
            x += 1
        await member.send(content)
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        while msg.content not in fileList.keys() and msg.content != 'cancel' and msg.content != 'c' and msg.content != '0':
            await member.send(
                'Please respond with the number indicating the file you would like to update, or \'cancel\'.')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content == 'c' or msg.content == 'cancel':
            await member.send('Understandable, have a nice day!')
            return
        elif msg.content == '0':
            await member.send(
                'Please send the file with the caption as the filename you would like. Please only send a single file, and include any necessary suffixes.')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await msg.attachments[0].save(Path.cwd() / 'referenceFiles' / msg.content)
            while msg.attachments[0] is None:
                await member.send('Please send a file, or reply \'cancel\'.')
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                if msg.content == 'c' or msg.content == 'cancel':
                    await member.send('Understandable, have a nice day!')
                    return
            await member.send(msg.content + ' saved! Have a nice day!')
        else:
            try:
                index = msg.content
                await member.send('Please send the updated copy of ' + fileList[index].stem)
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                while msg.attachments[0] is None:
                    await member.send('Please send a file, or reply \'cancel\'.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg.content == 'c' or msg.content == 'cancel':
                        await member.send('Understandable, have a nice day!')
                        return
                await member.send('Here\'s a backup of the current file.', file=discord.File(fileList[index]))
                await msg.attachments[0].save(fileList[index])
                await member.send('Saved ' + fileList[index].stem)

            except Exception as e:
                print(e)

    @commands.command(name='overwriteLib',
                      help='overwrites existing library for virtues, abilities, or flaws. Careful with use')
    async def overwriteLib(self, ctx):
        member = ctx.message.author
        content = 'Which library would you like to overwrite?\n'
        x = 1
        fileList = {}
        for filePath in (Path.cwd() / 'referenceFiles' / 'libraries').glob('**/*Lib'):
            content += '\n' + str(x) + '. ' + filePath.stem
            fileList[str(x)] = filePath
            x += 1
        await member.send(content)
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        while msg.content not in fileList.keys() and msg.content != 'cancel' and msg.content != 'c' and msg.content not in list(
                fileList.keys()):
            await member.send(
                'Please respond with the number indicating the file you would like to update, or \'cancel\'.')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content == 'c' or msg.content == 'cancel':
            await member.send('Understandable, have a nice day!')
            return
        else:
            index = msg.content
            await member.send('Please send the updated copy of ' + fileList[index].stem)
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            while msg.attachments[0] is None:
                await member.send('Please send a file, or reply \'cancel\'.')
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                if msg.content == 'c' or msg.content == 'cancel':
                    await member.send('Understandable, have a nice day!')
                    return
            await member.send('Here\'s a backup of ' + fileList[index].stem, file=discord.File(fileList[index]))

            # importing ability lib
            if fileList[index].stem == 'abilityLib':

                await msg.attachments[0].save(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilities.txt')

                with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilities.txt', 'r', encoding='utf-8') as file:
                    refsheet = file.readlines()

                abiLib = self.abilityProcess(refsheet)

                with open(fileList[index], 'w') as file:
                    json.dump(abiLib, file)

                await member.send('Overwrote ' + fileList[index].stem)
                currentAbis = 'List of current abilities: '
                for x in list(abiLib.keys()):
                    currentAbis += '\n' + x
                buf = io.StringIO(currentAbis)
                f = discord.File(buf, filename='currentAbilities.txt')
                await member.send('List of current abilities: ')
                await member.send(file=f)

            elif fileList[index].stem == 'virtueLib' or fileList[index].stem == 'flawLib':
                tempVF = VirtueFlaw()
                tempVF.virtuesLib = {}
                if fileList[index].stem == 'virtueLib':
                    tempVF.referenceFile = tempVF.referencePath / 'virtueLib.txt'
                elif fileList[index].stem == 'flawLib':
                    tempVF.referenceFile = tempVF.referencePath / 'flawLib.txt'
                await msg.attachments[0].save(tempVF.referenceFile)
                with open(tempVF.referenceFile, 'r', encoding='utf-8') as file:
                    refsheet = file.readlines()

                tempVF = self.vfProcess(tempVF, refsheet)

                with open(fileList[index], 'w') as file:
                    json.dump(tempVF.virtuesLib, file)
                await member.send('Overwrote ' + fileList[index].stem)
                if fileList[index].stem == 'virtueLib':
                    currentVF = 'List of current virtues: '
                    await member.send('List of current virtues:')
                elif fileList[index].stem == 'flawLib':
                    currentVF = 'List of current flaws: '
                    await member.send('List of current flaws:')
                else:
                    currentVF = 'ERROR WITH currentVF'
                for x in list(tempVF.virtuesLib.keys()):
                    currentVF += '\n' + x
                if fileList[index].stem == 'virtueLib':
                    buf = io.StringIO(currentVF)
                    f = discord.File(buf, filename='currentVirtues.txt')
                elif fileList[index].stem == 'flawLib':
                    buf = io.StringIO(currentVF)
                    f = discord.File(buf, filename='currentFlaws.txt')
                else:
                    raise Exception('error with current VF')

                await member.send(file=f)

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

    @commands.command(name='abilityList', help='lists all abilities in the game')
    async def abilityList(self, ctx):

        with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'r') as f:
            abiLib = json.load(f)
        general = ''
        academic = ''
        arcane = ''
        martial = ''
        supernatural = ''
        other = ''
        for x in list(abiLib.keys()):
            if abiLib[x]['type'] == '(General)':
                general += '\n' + (x.capitalize())
            elif abiLib[x]['type'] == '(Academic)':
                academic += '\n' + (x.capitalize())
            elif abiLib[x]['type'] == '(Arcane)':
                arcane += '\n' + (x.capitalize())
            elif abiLib[x]['type'] == '(Martial)':
                martial += '\n' + (x.capitalize())
            elif abiLib[x]['type'] == '(Supernatural)':
                supernatural += '\n' + (x.capitalize())
            else:
                other += '\n' + (x.capitalize())

        embed = discord.Embed(title='Ability List', color=discord.Colour.blue())
        embed.add_field(name='General:', value=general, inline=True)
        embed.add_field(name='Academic:', value=academic, inline=True)
        embed.add_field(name='Arcane:', value=arcane, inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=False)
        embed.add_field(name='Martial:', value=martial, inline=True)
        embed.add_field(name='Supernatural:', value=supernatural, inline=True)
        if other:
            embed.add_field(name='Other:', value=other, inline=True)

        await ctx.send(embed=embed)

    @commands.command(name='virtueList', help='lists all virtues in the game')
    async def virtueList(self, ctx):

        with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'virtueLib', 'r') as f:
            virtLib = json.load(f)
        typeLib = {
            'general': '',
            'hermetic': '',
            'supernatural': '',
            'socialStatus': '',
            'personality': '',
            'story': '',
            'other': ''
        }
        for x in list(virtLib.keys()):
            if virtLib[x]['type'] == 'General':
                typeLib['general'] += '\n' + (x.capitalize())
            elif virtLib[x]['type'] == 'Hermetic':
                typeLib['hermetic'] += '\n' + (x.capitalize())
            elif virtLib[x]['type'] == 'Supernatural':
                typeLib['supernatural'] += '\n' + (x.capitalize())
            elif virtLib[x]['type'] == 'Social Status':
                typeLib['socialStatus'] += '\n' + (x.capitalize())
            elif virtLib[x]['type'] == 'Personality':
                typeLib['personality'] += '\n' + (x.capitalize())
            elif virtLib[x]['type'] == 'Story':
                typeLib['story'] += '\n' + (x.capitalize())
            else:
                typeLib['other'] += '\n' + (x.capitalize())

        embed = discord.Embed(title='Virtues', color=discord.Colour.blue())
        numFields = 0
        for x in list(typeLib.keys()):
            if bool(typeLib[x]):
                numFields += 1
                embed.add_field(name=x.capitalize() + ':', value=typeLib[x], inline=True)
                if (numFields / 3).is_integer():
                    embed.add_field(name='\u200b', value='\u200b', inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='flawList', help='lists all flaws in the game')
    async def flawList(self, ctx):
        with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'flawLib', 'r') as f:
            virtLib = json.load(f)
        typeLib = {
            'general': '',
            'hermetic': '',
            'supernatural': '',
            'socialStatus': '',
            'personality': '',
            'story': '',
            'other': ''
        }
        for x in list(virtLib.keys()):
            if virtLib[x]['type'] == 'General':
                typeLib['general'] += '\n' + (x.capitalize())
            elif virtLib[x]['type'] == 'Hermetic':
                typeLib['hermetic'] += '\n' + (x.capitalize())
            elif virtLib[x]['type'] == 'Supernatural':
                typeLib['supernatural'] += '\n' + (x.capitalize())
            elif virtLib[x]['type'] == 'Social Status':
                typeLib['socialStatus'] += '\n' + (x.capitalize())
            elif virtLib[x]['type'] == 'Personality':
                typeLib['personality'] += '\n' + (x.capitalize())
            elif virtLib[x]['type'] == 'Story':
                typeLib['story'] += '\n' + (x.capitalize())
            else:
                typeLib['other'] += '\n' + (x.capitalize())

        embed = discord.Embed(title='Flaws', color=discord.Colour.blue())
        numFields = 0
        for x in list(typeLib.keys()):
            if bool(typeLib[x]):
                numFields += 1
                embed.add_field(name=x.capitalize() + ':', value=typeLib[x], inline=True)
                if (numFields / 3).is_integer():
                    embed.add_field(name='\u200b', value='\u200b', inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='virtueSum', help='gives a summary of any virtue or flaw', aliases=['vSum'])
    async def virtueSummary(self, ctx, *args):
        name = ''
        for x in args:
            name += x + ' '
        name = name.strip()
        await ctx.send(embed=self.vfSum('virtue', name)[0])

    @commands.command(name='flawSum', help='gives a summary of any virtue or flaw', aliases=['fSum'])
    async def flawSummary(self, ctx, *args):
        name = ''
        for x in args:
            name += x + ' '
        name = name.strip()
        await ctx.send(embed=self.vfSum('flaw', name)[0])

    @commands.command(name='abilitySum', help='gives a summary of any ability',
                      aliases=['abiSum', 'abisum', 'aSum', 'asum', 'abilitySummary'])
    async def abilitySummary(self, ctx, *args):
        name = ''
        for x in args:
            name += x + ' '
        name = name.strip()
        await ctx.send(embed=self.abilitySum(name)[0])

    @commands.command(name='editVirtue', help='edits the library value of a selected virtue',
                      aliases=['eVirtue'])
    async def editVirtue(self, ctx, *args):
        if not args:
            await ctx.send(
                'Which virtue would you like to edit? Note that you can call this command with !editVirtue *virtue* to select an virtue directly.')
            await self.virtueList(ctx)
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await self.editVirtue(ctx, msg.content)
        else:
            editing = True
            name = ''
            for x in args:
                name += x + ' '
            name = name.strip()
            while editing:
                try:
                    name = await self.editVF(ctx, 'virtue', name)
                except Exception as e:
                    print(e)
                if type(name) is bool:
                    editing = False
                    continue
                await ctx.send('Would you like to edit another aspect of this virtue?')
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                while msg.content.lower() not in ['yes', 'y', 'no', 'n']:
                    await ctx.send('Please respond with yes or no.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                if msg.content.lower() in ['yes', 'y']:
                    continue
                elif msg.content.lower() in ['no', 'n']:
                    editing = False
                    continue
            await ctx.send(embed=self.vfSum('virtue', name)[0])

    async def editVF(self, ctx, vf, name):
        if vf == 'virtue':
            lib = 'virtueLib'
        elif vf == 'flaw':
            lib = 'flawLib'
        else:
            raise Exception('EditVF received invalid VF')
        virtue = self.vfSum(vf, name)
        await ctx.send(embed=virtue[0])
        virtName = virtue[1]
        with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'r') as f:
            vfLib = json.load(f)
        choices = {'0': 'remove', '1': 'add'}
        i = 2
        output = '\n\n0. remove ' + vf + '\n1. add attribute'
        translation = {
            'type': 'Type',
            'value': 'Value',
            'excludesVF': 'Excludes virtues and flaws',
            'permitsAbi': 'Permits abilities',
            'excludesAbi': 'Excludes abilities',
            'grantRep': 'Grants reputation',
            'grantAbi': 'Grants abilities',
            # 'modifiers':'Modifiers',
            # 'botchMod':'Botch modifiers',
            # 'specification':'Default specifications:'
        }
        for x in list(vfLib[virtName].keys()):
            choices[str(i)] = x
            output += '\n' + str(i) + '. ' + x
            i += 1
        await ctx.send(
            'Which aspect of ' + virtName + ' would you like to edit? Please respond with the number it corresponds to.' + output)
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=180)
        while msg.content not in list(choices.keys()) and msg.content not in ['cancel', 'c']:
            await ctx.send(
                'Please respond with the number indicating the aspect you would like to update, or \'cancel\'.')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content == 'c' or msg.content == 'cancel':
            await ctx.send('Understandable, have a nice day!')
            return False
        index = msg.content
        if choices[index] == 'add' or index == 'add':
            output = 'Which element would you like to add to ' + choices[index] + '?\n'
            i = 1
            choices2 = {}
            for x in list(translation.keys()):
                if x not in list(vfLib[virtName].keys()):
                    choices2[str(i)] = x
                    output += '\n' + str(i) + '. ' + x
                    i += 1
            await ctx.send(output)
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=180)
            while msg.content not in list(choices2.keys()) and msg.content not in ['cancel', 'c']:
                await ctx.send(
                    'Please respond with the number indicating the aspect you would like to update, or \'cancel\'.')
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if msg.content == 'c' or msg.content == 'cancel':
                await ctx.send('Understandable, have a nice day!')
                return False
            index2 = msg.content
            if choices2[index2] in ['excludesVF', 'permitsAbi', 'excludesAbi']:
                more = True
                while more:
                    await ctx.send('What element would you like to add? Reply cancel to cancel.')
                    msg = await self.bot.wait_for('message',
                                                  check=lambda message: message.author == ctx.author)
                    if msg.content in ['cancel', 'c']:
                        await ctx.send('Adding element cancelled.')
                        more = False
                        continue
                    else:
                        confirmation = False
                        while not confirmation:
                            spec = msg.content.split(',')
                            await ctx.send(
                                'You are attempting to add the element: \n' + str(
                                    spec) + '\n to the virtue \n' + virtName + ': ' +
                                choices2[index2] + '\n Please confirm yes or no')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with a yes or a no.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content in ['no', 'n']:
                                confirmation = True
                                continue
                            elif msg.content in ['yes', 'y']:
                                try:
                                    vfLib[virtName][choices2[index2]]
                                except KeyError:
                                    vfLib[virtName][choices2[index2]] = []
                                vfLib[virtName][choices2[index2]].append(spec)
                                confirmation = True
                                await ctx.send('Element added. Would you like to add another element?')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                while msg.content not in ['yes', 'y', 'no', 'n']:
                                    await ctx.send('Please respond with a yes or a no.')
                                    msg = await self.bot.wait_for('message',
                                                                  check=lambda message: message.author == ctx.author)
                                if msg.content in ['no', 'n']:
                                    more = False
                                    continue
                with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                    json.dump(vfLib, f)
                return virtName
            elif choices2[index2] == 'grantRep':
                more = True
                while more:
                    await ctx.send(
                        'What element would you like to add? Please format as *reputation*,score. EX "Local: Brave, 5". Reply cancel to cancel.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg.content in ['cancel', 'c']:
                        await ctx.send('Adding element cancelled.')
                        more = False
                        continue
                    spec = msg.content.split(',')
                    if len(spec) < 2:
                        await ctx.send('Invalid format, missing a \',\'')
                        continue
                    spec[1] = spec[1].strip()
                    if not spec[1].isdigit():
                        await ctx.send('Score not recognized, please use the format "reputation,score".  EX "Local: Brave, 5"')
                        continue
                    else:
                        confirmation = False
                        while not confirmation:
                            await ctx.send(
                                'You are attempting to add the element: \n' + spec[0] + 'with a score of ' + spec[
                                    1] + '\n to the virtue \n' + virtName + ': ' + choices2[
                                    index2] + '\n Please confirm yes or no')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with a yes or a no.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content in ['no', 'n']:
                                confirmation = True
                                continue
                            elif msg.content in ['yes', 'y']:
                                try:
                                    vfLib[virtName][choices2[index2]]
                                except KeyError:
                                    vfLib[virtName][choices2[index2]] = []
                                except Exception as ex:
                                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                                    print(template.format(type(ex).__name__, ex.args))
                                vfLib[virtName][choices2[index2]].append(spec)
                                confirmation = True
                                await ctx.send('Element added. Would you like to add another element?')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                while msg.content not in ['yes', 'y', 'no', 'n']:
                                    await ctx.send('Please respond with a yes or a no.')
                                    msg = await self.bot.wait_for('message',
                                                                  check=lambda message: message.author == ctx.author)
                                if msg.content in ['no', 'n']:
                                    more = False
                                    continue
                with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                    json.dump(vfLib, f)
                return virtName
            elif choices2[index2] == 'grantAbi':
                more = True
                while more:
                    await ctx.send(
                        'What element would you like to add? Please format as "[ability1,ability2],xp,exclusive/split" EX "[charm,athletics],5,split" or "[arcane,academic],30,exclusive". Reply cancel to cancel.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg.content in ['cancel', 'c']:
                        await ctx.send('Adding element cancelled.')
                        more = False
                        continue
                    processing = msg.content.split(']')
                    if len(processing) < 2:
                        await ctx.send(
                            'no abilities found. Please remember to surround you abilities with [] even if you\'re only inputting a single ability')
                        continue
                    proc2 = processing[1].split(',')
                    proc2.pop(0)
                    if len(proc2) < 2:
                        await ctx.send('Invalid formatting, most likely forgot to include exclusive/split')
                        continue
                    spec = [processing[0][1:].split(','), proc2[0], proc2[1]]
                    spec[0] = [x.strip() for x in spec[0]]
                    if not spec[1].isdigit():
                        print(spec[1])
                        await ctx.send(
                            'Score not recognized, please use the format "[ability1,ability2],xp,exclusive/split" EX "[charm,athletics],5,split" or "[arcane,academic],30,exclusive"')
                        continue
                    if spec[2] == 'exclusive':
                        spec[2] = True
                    else:
                        spec[2] = False
                    spec[1] = int(spec[1])

                    confirmation = False
                    while not confirmation:
                        if spec[2]:
                            await ctx.send(
                                'You are attempting to add the ability(s): \n' + str(spec[0]) + 'with an xp value of ' +
                                str(spec[1]) + ' as an exclusive split to the virtue \n' + virtName + ': ' + choices2[
                                    index2] + '\n Please confirm yes or no')
                        else:
                            await ctx.send(
                                'You are attempting to add the ability(s): \n' + str(spec[0]) + 'with an xp value of ' +
                                str(spec[1]) + ' as a non-exclusive split to the virtue \n' + virtName + ': ' +
                                choices2[
                                    index2] + '\n Please confirm yes or no')

                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        while msg.content not in ['yes', 'y', 'no', 'n']:
                            await ctx.send('Please respond with a yes or a no.')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if msg.content in ['no', 'n']:
                            confirmation = True
                            continue
                        elif msg.content in ['yes', 'y']:
                            try:
                                vfLib[virtName][choices2[index2]]
                            except KeyError:
                                vfLib[virtName][choices2[index2]] = []
                            vfLib[virtName][choices2[index2]].append(spec)
                            confirmation = True
                            await ctx.send('Element added. Would you like to add another element?')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with a yes or a no.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content in ['no', 'n']:
                                more = False
                                continue
                with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                    json.dump(vfLib, f)
                return virtName

        if choices[index] == 'remove' or index == 'remove':
            await ctx.send('Are you sure that you want to remove ' + virtName + '? Please respond yes or no.')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            while msg.content not in ['yes', 'y', 'no', 'n']:
                await ctx.send('Please reply yes or no.')
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if msg.content in ['yes', 'y']:
                del vfLib[virtName]
                with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                    json.dump(vfLib, f)
                await ctx.send(virtName + ' removed.')
                return False
            else:
                return virtName
        elif choices[index] == 'name' or choices[index] == 'description':
            await ctx.send('The current ' + choices[index] + ' is:\n' + vfLib[virtName][
                choices[index]] + '\n\n What would you like to change it to?')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            replacement = msg.content
            confirmed = False
            while not confirmed:
                await ctx.send('You would like to update the ' + choices[
                    index] + ' to:\n' + replacement + '\n\n Is that correct? Please answer yes, no, or cancel')
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

                while msg.content.lower() not in ['yes', 'y', 'no', 'no'] and not confirmed:
                    if msg.content.lower() in ['cancel', 'c']:
                        await ctx.send('Ability not updated.')
                        confirmed = True
                        continue
                    await ctx.send('Please respond with yes or no to confirm the update.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

                while msg.content.lower() in ['no', 'n']:
                    await ctx.send('The current ' + choices[index] + ' is:\n' + vfLib[virtName][
                        choices[index]] + '\n\n What would you like to change it to?')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    replacement = msg.content
                    await ctx.send('You would like to update the ' + choices[
                        index] + ' to:\n' + replacement + '\n\n Is that correct? Please answer yes or no.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    while msg.content.lower() not in ['yes', 'y', 'no', 'no'] and not confirmed:
                        if msg.content.lower() in ['cancel', 'c']:
                            await ctx.send('Ability not updated.')
                            confirmed = True
                            continue
                        await ctx.send('Please respond with yes or no to confirm the update.')
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

                if msg.content.lower() in ['yes', 'y']:
                    if choices[index] == 'name':
                        vfLib[virtName][choices[index]] = replacement.upper()
                        vfLib[replacement.upper()] = vfLib[virtName]
                        if virtName != replacement.upper():
                            del vfLib[virtName]
                        virtName = replacement
                    else:
                        vfLib[virtName][choices[index]] = replacement
                    with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                        json.dump(vfLib, f)
                    confirmed = True
            return virtName
        elif choices[index] in ['type', 'value']:
            confirmed = False
            while not confirmed:
                if choices[index] == 'type':
                    typeChoices = {'1': 'General', '2': 'Hermetic', '3': 'Supernatural', '4': 'Social Status',
                                   '5': 'Personality', '6': 'Story'}
                else:
                    typeChoices = {'1': 'Minor', '2': 'Major', '3': 'Free', '4': 'Special'}
                output = ''
                i = 1
                for x in list(typeChoices.values()):
                    output += str(i) + ': ' + x + '\n'
                    i += 1

                await ctx.send('The current ' + choices[index] + ' is:\n' + vfLib[virtName][
                    choices[index]] + '\n\n Which type would you like to change it to?\n' + output)
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                while msg.content.lower() not in list(typeChoices.keys()) and msg.content.lower() not in ['cancel',
                                                                                                          'c']:
                    await ctx.send('Please respond with a number corresponding to a type, or cancel.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                if msg.content.lower() in ['cancel', 'c']:
                    await ctx.send('Ability not updated.')
                    confirmed = True
                    continue
                else:
                    newType = typeChoices[msg.content]
                    await ctx.send('Type will be updated to ' + newType + ' is that correct?')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    while msg.content.lower() not in ['yes', 'y', 'no', 'n', 'cancel', 'c']:
                        await ctx.send(
                            'Please respond with yes, no, or cancel.\nType will be updated to ' + newType + 'is that correct?')
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg.content.lower() in ['cancel', 'c']:
                        await ctx.send('Ability not updated.')
                        confirmed = True
                        continue
                    elif msg.content.lower() in ['no', 'n']:
                        continue
                    elif msg.content.lower() in ['yes', 'y']:
                        vfLib[virtName][choices[index]] = newType
                        with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                            json.dump(vfLib, f)
                        confirmed = True
            return virtName
        elif choices[index] in ['excludesVF', 'permitsAbi', 'excludesAbi']:
            output = 'Which element of ' + choices[index] + ' would you like to update?\n0. Add new element'
            i = 1
            for x in vfLib[virtName][choices[index]]:
                if isinstance(x, list):
                    output += '\n' + str(i) + '.'
                    for y in x:
                        output += ' ' + y
                else:
                    output += '\n' + str(i) + '. ' + x.capitalize()
                i += 1
            await ctx.send(output)
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            while not msg.content.isdigit() and msg.content not in ['cancel', 'c']:
                await ctx.send('Please respond with a number corresponding to the choices.')
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if msg.content.lower() in ['cancel', 'c']:
                await ctx.send(choices[index] + ' not updated.')
                return virtName
            if int(msg.content) == 0:
                more = True
                while more:
                    await ctx.send(
                        'What element would you like to add? Reply cancel to cancel. If it is a choice of multiple separate them with a \',\'')
                    msg = await self.bot.wait_for('message',
                                                  check=lambda message: message.author == ctx.author)
                    if msg.content in ['cancel', 'c']:
                        await ctx.send('Adding element cancelled.')
                        more = False
                        continue
                    else:
                        confirmation = False
                        while not confirmation:
                            spec = msg.content.split(',')
                            spec = [x.strip() for x in spec]
                            await ctx.send(
                                'You are attempting to add the element: \n' + str(
                                    spec) + '\n to the virtue \n' + virtName + ': ' +
                                choices[index] + '\n Please confirm yes or no')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with a yes or a no.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content in ['no', 'n']:
                                confirmation = True
                                continue
                            elif msg.content in ['yes', 'y']:
                                vfLib[virtName][choices[index]].append(spec)
                                confirmation = True
                                await ctx.send('Element added. Would you like to add another element?')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                while msg.content not in ['yes', 'y', 'no', 'n']:
                                    await ctx.send('Please respond with a yes or a no.')
                                    msg = await self.bot.wait_for('message',
                                                                  check=lambda message: message.author == ctx.author)
                                if msg.content in ['no', 'n']:
                                    more = False
                                    continue
                with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                    json.dump(vfLib, f)
                return virtName
            else:
                selection = int(msg.content) - 1
                confirmation = False
                while not confirmation:
                    await ctx.send('You are attempting to update ' + str(vfLib[virtName][choices[index]])[
                        selection] + ' please enter what you would like to replace it with. Alternatively respond cancel to cancel or remove to remove it. If it is a choice of multiple separate them with a \',\'')
                    msg = await self.bot.wait_for('message',
                                                  check=lambda message: message.author == ctx.author)
                    if msg.content in ['cancel', 'c']:
                        await ctx.send('Update cancelled.')
                        confirmation = True
                        continue
                    elif msg.content in ['remove', 'r']:
                        vfLib[virtName][choices[index]].pop(selection)
                        with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                            json.dump(vfLib, f)
                        await ctx.send('element removed.')
                        confirmation = True
                    else:
                        content = msg.content.split(',')
                        await ctx.send(
                            'Please confirm that you would like to replace ' + str(vfLib[virtName][choices[index]][
                                                                                       selection]) + ' with ' + str(
                                content))
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        while msg.content not in ['yes', 'y', 'no', 'n']:
                            await ctx.send('Please reply yes or no.')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if msg.content in ['no', 'n']:
                            await ctx.send('Update cancelled.')
                            confirmation = True
                            continue
                        elif msg.content in ['yes', 'y']:
                            vfLib[virtName][choices[index]][selection] = content
                            with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                                json.dump(vfLib, f)
                            confirmation = True
                return virtName
        elif choices[index] == 'grantRep':
            output = 'Which element of ' + choices[index] + ' would you like to update?\n0. Add new element'
            i = 1
            for x in vfLib[virtName][choices[index]]:
                output += '\n' + str(i) + '. ' + str(x)[1:-1]
                i += 1
            await ctx.send(output)
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            while not msg.content.isdigit() and msg.content not in ['cancel', 'c']:
                await ctx.send('Please respond with a number corresponding to the choices.')
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if msg.content.lower() in ['cancel', 'c']:
                await ctx.send(choices[index] + ' not updated.')
                return virtName
            if int(msg.content) == 0:
                more = True
                while more:
                    await ctx.send(
                        'What element would you like to add? Please format as *reputation*,score. EX "Local: Brave, 5". Reply cancel to cancel.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg.content in ['cancel', 'c']:
                        await ctx.send('Adding element cancelled.')
                        more = False
                        continue
                    spec = msg.content.split(',')
                    if not spec[1].isdigit():
                        await ctx.send(
                            'Score not recognized, please use the format "reputation,score".  EX "Local: Brave, 5"')
                        continue
                    else:
                        confirmation = False
                        while not confirmation:
                            await ctx.send(
                                'You are attempting to add the element: \n' + spec[0] + 'with a score of ' + spec[
                                    1] + '\n to the virtue \n' + virtName + ': ' + choices[
                                    index] + '\n Please confirm yes or no')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with a yes or a no.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content in ['no', 'n']:
                                confirmation = True
                                continue
                            elif msg.content in ['yes', 'y']:
                                vfLib[virtName][choices[index]].append(spec)
                                confirmation = True
                                await ctx.send('Element added. Would you like to add another element?')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                while msg.content not in ['yes', 'y', 'no', 'n']:
                                    await ctx.send('Please respond with a yes or a no.')
                                    msg = await self.bot.wait_for('message',
                                                                  check=lambda message: message.author == ctx.author)
                                if msg.content in ['no', 'n']:
                                    more = False
                                    continue
                with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                    json.dump(vfLib, f)
                return virtName
            else:
                selection = int(msg.content) - 1
                confirmation = False
                while not confirmation:
                    await ctx.send('You are attempting to update ' + str(vfLib[virtName][choices[index]][selection])[
                                                                     1:-1] + ' please enter what you would like to replace it with. Alternatively respond cancel to cancel or remove to remove it.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg.content in ['cancel', 'c']:
                        await ctx.send('Update cancelled.')
                        confirmation = True
                        continue
                    elif msg.content in ['remove', 'r']:
                        vfLib[virtName][choices[index]].pop(selection)
                        with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                            json.dump(vfLib, f)
                        await ctx.send('element removed.')
                        confirmation = True
                    spec = msg.content.split(',')
                    if not spec[1].isdigit():
                        await ctx.send(
                            'Score not recognized, please use the format "reputation,score".  EX "Local: Brave, 5"')
                        continue
                    else:
                        await ctx.send('Please confirm that you would like to replace ' + str(
                            vfLib[virtName][choices[index]][selection])[1:-1] + ' with ' + str(spec)[1:-1])
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        while msg.content not in ['yes', 'y', 'no', 'n']:
                            await ctx.send('Please reply yes or no.')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if msg.content in ['no', 'n']:
                            await ctx.send('Update cancelled.')
                            confirmation = True
                            continue
                        elif msg.content in ['yes', 'y']:
                            vfLib[virtName][choices[index]][selection] = spec
                            with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                                json.dump(vfLib, f)
                            confirmation = True
                return virtName
        elif choices[index] == 'grantAbi':
            output = 'Which element of ' + choices[index] + ' would you like to update?\n0. Add new element'
            i = 1
            for x in vfLib[virtName][choices[index]]:
                output += '\n' + str(i) + '. ' + str(x)[1:-1]
                i += 1
            await ctx.send(output)
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            while not msg.content.isdigit() and msg.content not in ['cancel', 'c']:
                await ctx.send('Please respond with a number corresponding to the choices.')
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if msg.content.lower() in ['cancel', 'c']:
                await ctx.send(choices[index] + ' not updated.')
                return virtName
            if int(msg.content) == 0:
                more = True
                while more:
                    await ctx.send(
                        'What element would you like to add? Please format as "[ability1,ability2],xp,exclusive/split" EX "[charm,athletics],5,split" or "[arcane,academic],30,exclusive". Reply cancel to cancel.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg.content in ['cancel', 'c']:
                        await ctx.send('Adding element cancelled.')
                        more = False
                        continue
                    processing = msg.content.split(']')
                    if len(processing) < 2:
                        await ctx.send(
                            'no abilities found. Please remember to surround you abilities with [] even if you\'re only inputting a single ability')
                        continue
                    proc2 = processing[1].split(',')
                    if len(proc2) < 2:
                        await ctx.send('Invalid formatting, most likely forgot to include exclusive/split')
                        continue
                    spec: List[Union[bool, int, str, list]] = [processing[0][1:].split(','), proc2[0], proc2[1]]
                    spec[0] = [x.strip() for x in spec[0]]
                    if not spec[1].isdigit():
                        await ctx.send(
                            'Score not recognized, please use the format "[ability1,ability2],xp,exclusive/split" EX "[charm,athletics],5,split" or "[arcane,academic],30,exclusive"')
                        continue
                    if spec[2] == 'exclusive':
                        spec[2] = True
                    else:
                        spec[2] = False

                    confirmation = False
                    while not confirmation:
                        if spec[2]:
                            await ctx.send(
                                'You are attempting to add the ability(s): \n' + spec[0] + 'with an xp value of ' +
                                spec[1] + ' as an exclusive split to the virtue \n' + virtName + ': ' + choices[
                                    index] + '\n Please confirm yes or no')
                        else:
                            await ctx.send(
                                'You are attempting to add the ability(s): \n' + spec[0] + 'with an xp value of ' +
                                spec[1] + ' as a non-exclusive split to the virtue \n' + virtName + ': ' + choices[
                                    index] + '\n Please confirm yes or no')

                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        while msg.content not in ['yes', 'y', 'no', 'n']:
                            await ctx.send('Please respond with a yes or a no.')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if msg.content in ['no', 'n']:
                            confirmation = True
                            continue
                        elif msg.content in ['yes', 'y']:
                            vfLib[virtName][choices[index]].append(spec)
                            confirmation = True
                            await ctx.send('Element added. Would you like to add another element?')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with a yes or a no.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content in ['no', 'n']:
                                more = False
                                continue
                with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                    json.dump(vfLib, f)
                return virtName
            else:
                selection = int(msg.content) - 1
                confirmation = False
                while not confirmation:
                    await ctx.send('You are attempting to update ' + str(vfLib[virtName][choices[index]][selection])[
                                                                     1:-1] + ' please enter what you would like to replace it with. Alternatively respond cancel to cancel or remove to remove it.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg.content in ['cancel', 'c']:
                        await ctx.send('Update cancelled.')
                        confirmation = True
                        continue
                    elif msg.content in ['remove', 'r']:
                        vfLib[virtName][choices[index]].pop(selection)
                        with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                            json.dump(vfLib, f)
                        await ctx.send('element removed.')
                        confirmation = True
                    processing = msg.content.split(']')
                    if len(processing) < 2:
                        await ctx.send(
                            'no abilities found. Please remember to surround you abilities with [] even if you\'re only inputting a single ability')
                        continue
                    proc2 = processing[1].split(',')
                    if len(proc2) < 2:
                        await ctx.send('Invalid formatting, most likely forgot to include exclusive/split')
                        continue
                    spec = [processing[0][1:].split(','), proc2[0], proc2[1]]
                    spec[0] = [x.strip() for x in spec[0]]
                    if not spec[1].isdigit():
                        await ctx.send(
                            'Score not recognized, please use the format "[ability1,ability2],xp,exclusive/split" EX "[charm,athletics],5,split" or "[arcane,academic],30,exclusive"')
                        continue
                    if spec[2] == 'exclusive':
                        spec[2] = True
                    else:
                        spec[2] = False

                    await ctx.send('Please confirm that you would like to replace ' + str(
                        vfLib[virtName][choices[index]][selection])[1:-1] + ' with ' + str(spec)[1:-1])
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    while msg.content not in ['yes', 'y', 'no', 'n']:
                        await ctx.send('Please reply yes or no.')
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    if msg.content in ['no', 'n']:
                        await ctx.send('Update cancelled.')
                        confirmation = True
                        continue
                    elif msg.content in ['yes', 'y']:
                        vfLib[virtName][choices[index]][selection] = spec
                        with open(Path.cwd() / 'referenceFiles' / 'libraries' / lib, 'w') as f:
                            json.dump(vfLib, f)
                        confirmation = True

                return virtName

    @commands.command(name='editAbility', help='edits the library value of a selected ability')
    async def editAbility(self, ctx, *args):
        if not args:
            await ctx.send(
                'Which ability would you like to edit? Note that you can call this command with !editAbility *ability* to select an ability directly.')
            await self.abilityList(ctx)
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await self.editAbility(ctx, msg.content)
        else:
            editing = True
            name = ''
            for x in args:
                name += x + ' '
            name = name.strip()
            while editing:
                abi = self.abilitySum(name)
                await ctx.send(embed=abi[0])
                abiName = abi[1]
                with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'r') as f:
                    abiLib = json.load(f)
                choices = {'0': 'remove'}
                i = 1
                output = '0. remove ability'
                for x in list(abiLib[abiName].keys()):
                    choices[str(i)] = x
                    output += '\n' + str(i) + '. ' + x
                    i += 1
                if (Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / abiName).exists():
                    choices[str(i)] = 'specifications'
                    output += '\n' + str(i) + '. specifications'
                await ctx.send(
                    'Which aspect of ' + abiName + ' would you like to edit? Please respond with the number it corresponds to.' + output)
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                              timeout=180)
                while msg.content not in list(choices.keys()) and msg.content not in list(
                        choices.values()) and msg.content not in ['cancel', 'c']:
                    print(list(choices.keys()))
                    print(msg.content)
                    await ctx.send(
                        'Please respond with the number indicating the aspect you would like to update, or \'cancel\'.')
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                if msg.content == 'c' or msg.content == 'cancel':
                    await ctx.send('Understandable, have a nice day!')
                    return
                else:
                    index = msg.content
                    if choices[index] == 'remove' or index == 'remove':
                        await ctx.send(
                            'Are you sure that you want to remove ' + abiName + '? Please respond yes or no.')
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        while msg.content not in ['yes', 'y', 'no', 'n']:
                            await ctx.send('Please reply yes or no.')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if msg.content in ['yes', 'y']:
                            del abiLib[abiName]
                            with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'w') as f:
                                json.dump(abiLib, f)
                            if (Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / abiName).exists():
                                (Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / abiName).unlink()
                            await ctx.send(name + ' removed.')
                            editing = False

                        else:
                            await ctx.send('Would you like to edit another aspect of this ability?')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content.lower() not in ['yes', 'y', 'no', 'no']:
                                await ctx.send('Please respond with yes or no.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content.lower() in ['yes', 'y']:
                                continue
                            elif msg.content.lower() in ['no', 'n']:
                                editing = False
                                continue

                    if choices[index] == 'name' or choices[index] == 'description' or index in ['name', 'description']:
                        await ctx.send('The current ' + choices[index] + ' is:\n' + abiLib[abiName][
                            choices[index]] + '\n\n What would you like to change it to?')
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        replacement = msg.content
                        confirmed = False
                        while not confirmed:
                            await ctx.send('You would like to update the ' + choices[
                                index] + ' to:\n' + replacement + '\n\n Is that correct? Please answer yes, no, or cancel')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

                            while msg.content.lower() not in ['yes', 'y', 'no', 'no'] and not confirmed:
                                if msg.content.lower() in ['cancel', 'c']:
                                    await ctx.send('Ability not updated.')
                                    confirmed = True
                                    continue
                                await ctx.send('Please respond with yes or no to confirm the update.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)

                            while msg.content.lower() in ['no', 'n']:
                                await ctx.send('The current ' + choices[index] + ' is:\n' + abiLib[abiName][
                                    choices[index]] + '\n\n What would you like to change it to?')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                replacement = msg.content
                                await ctx.send('You would like to update the ' + choices[
                                    index] + ' to:\n' + replacement + '\n\n Is that correct? Please answer yes or no.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                while msg.content.lower() not in ['yes', 'y', 'no', 'no'] and not confirmed:
                                    if msg.content.lower() in ['cancel', 'c']:
                                        await ctx.send('Ability not updated.')
                                        confirmed = True
                                        continue
                                    await ctx.send('Please respond with yes or no to confirm the update.')
                                    msg = await self.bot.wait_for('message',
                                                                  check=lambda message: message.author == ctx.author)

                            if msg.content.lower() in ['yes', 'y']:

                                if choices[index] == 'name':
                                    abiLib[abiName][choices[index]] = replacement.upper()
                                    abiLib[replacement.upper()] = abiLib[abiName]
                                    del abiLib[abiName]
                                    abiName = replacement
                                    name = replacement
                                else:
                                    abiLib[abiName][choices[index]] = replacement
                                with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'w') as f:
                                    json.dump(abiLib, f)
                                confirmed = True
                        await ctx.send('Would you like to edit another aspect of this ability?')
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        while msg.content.lower() not in ['yes', 'y', 'no', 'no']:
                            await ctx.send('Please respond with yes or no.')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if msg.content.lower() in ['yes', 'y']:
                            continue
                        elif msg.content.lower() in ['no', 'n']:
                            editing = False
                            continue

                    elif choices[index] == 'type' or index == 'type':
                        confirmed = False
                        while not confirmed:
                            typeChoices = {'1': '(General)', '2': '(Academic)', '3': '(Arcane)', '4': '(Martial)',
                                           '5': '(Supernatural)'}
                            output = '1. General\n2. Academic\n3. Arcane\n4. Martial\n5. Supernatural'
                            await ctx.send('The current ' + choices[index] + ' is:\n' + abiLib[abiName][
                                choices[index]] + '\n\n Which type would you like to change it to?\n' + output)
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content.lower() not in list(typeChoices.keys()) and msg.content.lower() not in ['cancel', 'c']:
                                await ctx.send('Please respond with a number corresponding to a type, or cancel.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content.lower() in ['cancel', 'c']:
                                await ctx.send('Ability not updated.')
                                confirmed = True
                                continue
                            else:
                                newType = typeChoices[msg.content]
                                await ctx.send('Type will be updated to ' + newType[1:-1] + ' is that correct?')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                while msg.content.lower() not in ['yes', 'y', 'no', 'n', 'cancel', 'c']:
                                    await ctx.send(
                                        'Please respond with yes, no, or cancel.\nType will be updated to ' + newType[
                                                                                                              1:-1] + 'is that correct?')
                                    msg = await self.bot.wait_for('message',
                                                                  check=lambda message: message.author == ctx.author)
                                if msg.content.lower() in ['cancel', 'c']:
                                    await ctx.send('Ability not updated.')
                                    confirmed = True
                                    continue
                                elif msg.content.lower() in ['no', 'n']:
                                    continue
                                elif msg.content.lower() in ['yes', 'y']:
                                    abiLib[abiName][choices[index]] = newType
                                    with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'w') as f:
                                        json.dump(abiLib, f)
                                    confirmed = True
                        await ctx.send('Would you like to edit another aspect of this ability?')
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        while msg.content.lower() not in ['yes', 'y', 'no', 'no']:
                            await ctx.send('Please respond with yes or no to confirm the update.')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if msg.content.lower() in ['yes', 'y']:
                            continue
                        elif msg.content.lower() in ['no', 'n']:
                            editing = False
                            continue
                    elif choices[index] == 'needTraining' or index == 'needTraining':
                        if abiLib[abiName]['needTraining']:
                            await ctx.send(
                                'The current ability is set to require training to attempt. Would you like to change that?')
                        elif not abiLib[abiName]['needTraining']:
                            await ctx.send(
                                'The current ability is set to not require training to attempt. Would you like to change that?')
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        while msg.content.lower() not in ['yes', 'y', 'no', 'no']:
                            await ctx.send('Please respond with yes or no to confirm the update.')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if msg.content.lower() in ['no', 'n']:
                            await ctx.send('Would you like to edit another aspect of this ability?')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content.lower() not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with yes or no to confirm the update.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content.lower() in ['yes', 'y']:
                                continue
                            elif msg.content.lower() in ['no', 'n']:
                                editing = False
                                continue
                        elif msg.content.lower() in ['yes', 'y']:
                            abiLib[abiName][choices[index]] = not abiLib[abiName]['needTraining']
                            with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'w') as f:
                                json.dump(abiLib, f)
                    elif choices[index] == 'specialties' or index == 'specialties':
                        output = 'Which specialty would you like to update?\n0. Add new specialty'
                        i = 1
                        for x in abiLib[abiName][choices[index]]:
                            if isinstance(x, list):
                                output += '\n' + str(i) + '.'
                                for y in x:
                                    output += ' ' + y
                            else:
                                output += '\n' + str(i) + '. ' + x.capitalize()
                            i += 1
                        await ctx.send(output)
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        while not msg.content.isdigit() and msg.content not in ['cancel', 'c']:
                            await ctx.send('Please respond with a number corresponding to the choices.')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if msg.content.lower() in ['cancel', 'c']:
                            await ctx.send('Specialty not updated.')
                            continue
                        if int(msg.content) == 0:
                            more = True
                            while more:
                                await ctx.send('What specialty would you like to add? Reply cancel to cancel.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                if msg.content in ['cancel', 'c']:
                                    await ctx.send('Adding specialty cancelled.')
                                    more = False
                                    continue
                                else:
                                    confirmation = False
                                    while not confirmation:
                                        spec = msg.content
                                        await ctx.send(
                                            'You are attempting to add the specialty: \n' + spec + '\n to the ability \n' + abiName + '\n Please confirm yes or no')
                                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                                        while msg.content not in ['yes', 'y', 'no', 'n']:
                                            await ctx.send('Please respond with a yes or a no.')
                                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                                        if msg.content in ['no', 'n']:
                                            confirmation = True
                                            continue
                                        elif msg.content in ['yes', 'y']:
                                            abiLib[abiName][choices[index]].append(spec)
                                            confirmation = True
                                            await ctx.send('Specialty added. Would you like to add another specialty?')
                                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                                            while msg.content not in ['yes', 'y', 'no', 'n']:
                                                await ctx.send('Please respond with a yes or a no.')
                                                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                                            if msg.content in ['no', 'n']:
                                                more = False
                                                continue
                            with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'w') as f:
                                json.dump(abiLib, f)
                            await ctx.send('Would you like to edit another aspect of this ability?')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content.lower() not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with yes or no to confirm the update.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content.lower() in ['no', 'n']:
                                editing = False
                        else:
                            selection = int(msg.content) - 1
                            confirmation = False
                            while not confirmation:
                                await ctx.send('You are attempting to update ' + abiLib[abiName][choices[index]][
                                    selection] + ' please enter what you would like to replace it with. Alternatively respond cancel to cancel or remove to remove it.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                if msg.content in ['cancel', 'c']:
                                    await ctx.send('Update cancelled.')
                                    confirmation = True
                                    continue
                                elif msg.content in ['remove', 'r']:
                                    abiLib[abiName][choices[index]].pop(selection)
                                    with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'w') as f:
                                        json.dump(abiLib, f)
                                    await ctx.send('Specialty removed.')
                                    confirmation = True
                                else:
                                    content = msg.content
                                    await ctx.send('Please confirm that you would like to replace ' +
                                                   abiLib[abiName][choices[index]][selection] + ' with ' + content)
                                    msg = await self.bot.wait_for('message',
                                                                  check=lambda message: message.author == ctx.author)
                                    while msg.content not in ['yes', 'y', 'no', 'n']:
                                        await ctx.send('Please reply yes or no.')
                                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                                    if msg.content in ['no', 'n']:
                                        await ctx.send('Update cancelled.')
                                        confirmation = True
                                        continue
                                    elif msg.content in ['yes', 'y']:
                                        abiLib[abiName][choices[index]][selection] = content
                                        with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'w') as f:
                                            json.dump(abiLib, f)
                                        confirmation = True
                            await ctx.send('Would you like to edit another aspect of this ability?')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content.lower() not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with yes or no to confirm the update.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content.lower() in ['no', 'n']:
                                editing = False
                    elif choices[index] == 'specifications' or index == 'specifications':
                        output = 'Which specification would you like to update?\n0. Add new specification'
                        i = 1
                        with open(Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / abiName, 'r') as refFile:
                            specList = json.load(refFile)
                        for x in specList:
                            output += '\n' + str(i) + '. ' + x
                            i += 1
                        await ctx.send(output)
                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        while not msg.content.isdigit() and msg.content not in ['cancel', 'c']:
                            await ctx.send('Please respond with a number corresponding to the choices.')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        if msg.content.lower() in ['cancel', 'c']:
                            await ctx.send('Specification not updated.')
                            continue
                        if int(msg.content) == 0:
                            more = True
                            while more:
                                await ctx.send('What specification would you like to add? Reply cancel to cancel.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                if msg.content in ['cancel', 'c']:
                                    await ctx.send('Adding specification cancelled.')
                                    more = False
                                    continue
                                else:
                                    confirmation = False
                                    while not confirmation:
                                        spec = msg.content
                                        await ctx.send(
                                            'You are attempting to add the specification: \n' + spec + '\n to the ability \n' + abiName + '\n Please confirm yes or no')
                                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                                        while msg.content not in ['yes', 'y', 'no', 'n']:
                                            await ctx.send('Please respond with a yes or a no.')
                                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                                        if msg.content in ['no', 'n']:
                                            confirmation = True
                                            continue
                                        elif msg.content in ['yes', 'y']:
                                            specList.append(spec.upper())
                                            confirmation = True
                                            await ctx.send(
                                                'Specification added. Would you like to add another specialty?')
                                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                                            while msg.content not in ['yes', 'y', 'no', 'n']:
                                                await ctx.send('Please respond with a yes or a no.')
                                                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                                            if msg.content in ['no', 'n']:
                                                more = False
                                                continue
                            with open(Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / abiName, 'w') as f:
                                json.dump(specList, f)
                            await ctx.send('Would you like to edit another aspect of this ability?')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content.lower() not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with yes or no to confirm the update.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content.lower() in ['no', 'n']:
                                editing = False
                        else:
                            selection = int(msg.content) - 1
                            confirmation = False
                            while not confirmation:
                                await ctx.send('You are attempting to update ' + specList[
                                    selection] + ' please enter what you would like to replace it with. Alternatively respond cancel to cancel or remove to remove it.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                                if msg.content in ['cancel', 'c']:
                                    await ctx.send('Update cancelled.')
                                    confirmation = True
                                    continue
                                elif msg.content in ['remove', 'r']:
                                    specList.pop(selection)
                                    with open(Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / abiName,
                                              'w') as f:
                                        json.dump(specList, f)
                                    await ctx.send('Specification removed.')
                                    confirmation = True
                                else:
                                    content = msg.content
                                    await ctx.send('Please confirm that you would like to replace ' +
                                                   specList[selection] + ' with ' + content)
                                    msg = await self.bot.wait_for('message',
                                                                  check=lambda message: message.author == ctx.author)
                                    while msg.content not in ['yes', 'y', 'no', 'n']:
                                        await ctx.send('Please reply yes or no.')
                                        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                                    if msg.content in ['no', 'n']:
                                        await ctx.send('Update cancelled.')
                                        confirmation = True
                                        continue
                                    elif msg.content in ['yes', 'y']:
                                        specList[selection] = content.upper()
                                        with open(Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / abiName,
                                                  'w') as f:
                                            json.dump(abiLib, f)
                                        confirmation = True
                            await ctx.send('Would you like to edit another aspect of this ability?')
                            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                            while msg.content.lower() not in ['yes', 'y', 'no', 'n']:
                                await ctx.send('Please respond with yes or no to confirm the update.')
                                msg = await self.bot.wait_for('message',
                                                              check=lambda message: message.author == ctx.author)
                            if msg.content.lower() in ['no', 'n']:
                                editing = False
                    else:
                        await ctx.send('Selection not found.')
            await ctx.send('Ability updated.')
            abi = self.abilitySum(name)
            await ctx.send(embed=abi[0])

    @commands.command(name='addAbility', help='Add a new ability to the ability library')
    async def addAbility(self, ctx):
        async def cancel(ctxCancel, message):
            if message in ['cancel', 'c']:
                await ctxCancel.send('adding ability cancelled.')
                return True
            else:
                return False

        newAbi = {}
        await ctx.send('What is the name of the ability you would like to add?')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if await cancel(ctx, msg.content):
            return
        name = msg.content.strip().upper()
        newAbi['name'] = name
        await ctx.send('What is the description of ' + name)
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if await cancel(ctx, msg.content):
            return
        newAbi['description'] = msg.content

        typeChoices = {'1': '(General)', '2': '(Academic)', '3': '(Arcane)', '4': '(Martial)', '5': '(Supernatural)'}
        output = '1. General\n2. Academic\n3. Arcane\n4. Martial\n5. Supernatural'
        await ctx.send('What type of ability is ' + name + '?\n' + output)
        while msg.content.lower() not in list(typeChoices.keys()) and msg.content.lower() not in ('cancel', 'c'):
            await ctx.send('Please respond with the number corresponding to the type you would like, or cancel.')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if await cancel(ctx, msg.content):
            return
        newAbi['type'] = typeChoices[msg.content]

        await ctx.send('Does ' + name + ' require training in order to use? Please answer yes or no.')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        while msg.content.lower() not in ('yes', 'y', 'true', 'no', 'n', 'false', 'cancel', 'c'):
            await ctx.send('Please reply yes or no')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if await cancel(ctx, msg.content):
            return

        if msg.content.lower() in ('yes', 'y', 'true'):
            newAbi['needTraining'] = True
        else:
            newAbi['needTraining'] = False

        await ctx.send(
            'What are the default specialties for ' + name + '? For example the default specialties of Carouse are drinking songs, games of chance, and power drinking. Please separate these specialties with a \',\'')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if await cancel(ctx, msg.content):
            return
        specs = msg.content.split(',')
        finalSpecs = []
        for x in specs:
            finalSpecs.append(x.strip())
        newAbi['specialties'] = finalSpecs

        found = re.findall(r'(\([^)]+\))', name)
        if bool(found):
            await ctx.send(
                'What specifications are available for this ability? For example profession (type) has the specifications farmer, cook, soldier. Please separate the specifications with a \',\'')
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if await cancel(ctx, msg.content):
                return
            specs = msg.content.split(',')
            finalSpecs = []
            for x in specs:
                finalSpecs.append(x.strip().upper())
            with open(Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / name, 'w') as refFile:
                json.dump(finalSpecs, refFile)

        with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'r') as f:
            abiLib = json.load(f)

        abiLib[name] = newAbi

        with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'w') as f:
            json.dump(abiLib, f)

        await ctx.send('Ability added!')
        await ctx.send(embed=self.abilitySum(name)[0])

    # @commands.command(name='serverInfo',hidden=True)
    # async def serverInfo(self,ctx):
    #     if ctx.guild is None:
    #         print('DM')
    #         print(ctx.message.author)
    #     print(ctx.guild.name)
    #     await ctx.send(ctx.guild.name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @staticmethod
    def abilitySum(name):
        with open(Path.cwd() / 'referenceFiles' / 'libraries' / 'abilityLib', 'r') as f:
            abiLib = json.load(f)
        similarity = 100
        abiName = ''
        for x in list(abiLib.keys()):

            # print('difference between ' + x + ' and ' + name.upper() + ' is ' + str(Levenshtein.distance(x,name.upper())))
            found = re.findall(r'(\([^)]+\))', x)
            if len(found) > 0:
                if (Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / x).exists():
                    with open(Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / x, 'r') as refFile:
                        ref = json.load(refFile)
                    for spec in ref:
                        y = x.replace(found[0], spec)
                        if Levenshtein.distance(y, name.upper()) < similarity:
                            similarity = Levenshtein.distance(y, name.upper())
                            abiName = x

            if Levenshtein.distance(x, name.upper()) < similarity:
                abiName = x
                similarity = Levenshtein.distance(x, name.upper())
            else:
                pass

        embed = discord.Embed(title=abiLib[abiName]['name'], description=abiLib[abiName]['description'],
                              color=discord.Colour.blue())
        embed.set_author(name='Ability Summary')
        details = 'Type: ' + abiLib[abiName]['type'] + '\nNeed training: ' + str(
            abiLib[abiName]['needTraining']) + '\nDefault specialties: '
        for x in abiLib[abiName]['specialties']:
            details += ' [' + x.capitalize() + '] '

        if (Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / abiName).exists():
            details += '\nSpecifications: '
            with open(Path.cwd() / 'referenceFiles' / 'abilitySpecifications' / abiName, 'r') as f:
                ref = json.load(f)
            for spec in ref:
                details += ' [' + spec.capitalize() + '] '
        embed.add_field(name='Details:', value=details, inline=True)
        return embed, abiName

    @staticmethod
    def vfSum(vf, name):
        if vf == 'virtue':
            refName = 'virtueLib'
        elif vf == 'flaw':
            refName = 'flawLib'
        else:
            raise Exception('Invalid input for vfSum')
        with open(Path.cwd() / 'referenceFiles' / 'libraries' / refName, 'r') as f:
            virtLib = json.load(f)
        similarity = 100
        virtName = ''
        for x in list(virtLib.keys()):
            found = re.findall(r'(\([^)]+\))', x)
            if len(found) > 0:
                if 'specifications' in list(virtLib[x].keys()):
                    ref = virtLib[x]['specifications']
                    for spec in ref:
                        y = x.replace(found[0], spec)
                        if Levenshtein.distance(y, name.upper()) < similarity:
                            similarity = Levenshtein.distance(y, name.upper())
                            virtName = x
            if Levenshtein.distance(x, name.upper()) < similarity:
                virtName = x
                similarity = Levenshtein.distance(x, name.upper())

        embed = discord.Embed(title=virtLib[virtName]['name'], description=virtLib[virtName]['description'],
                              color=discord.Colour.blue())
        embed.set_author(name=vf + ' Summary')

        details = ''
        translation = {
            'type': 'Type: ',
            'value': 'Value: ',
            'excludesVF': 'Excludes virtues and flaws: ',
            'permitsAbi': 'Permits abilities: ',
            'excludesAbi': 'Excludes abilities: ',
            'grantRep': 'Grants Reputation: ',
            'grantAbi': 'Grants abilities: ',
            'modifiers': 'Modifiers: ',
            'botchMod': 'Botch modifiers'
        }
        for x in list(virtLib[virtName].keys()):
            if x in ['name', 'description']:
                continue
            if x in list(translation.keys()):
                details += '\n' + translation[x] + str(virtLib[virtName][x])
            else:
                details += '\n' + x + '(unknown value): ' + str(virtLib[virtName][x])
        embed.add_field(name='Details:', value=details, inline=True)
        return embed, virtName

    @staticmethod
    def abilityProcess(refsheet):

        newAbility = {'name': '', 'description': '', 'needTraining': False, 'specialties': [], 'type': '(General)',
                      'xp': 0, 'score': 0}
        searchingFor = 'name'
        description = 'DESCRIPTION NOT FOUND'
        specialities = 'SPECIALTIES NOT FOUND'
        abilityLib = {}

        for line in refsheet:
            if searchingFor == 'name':
                if len(line) < 2:
                    continue
                elif line[-2] == '*':
                    newAbility['needTraining'] = True
                    data = line[:-2]
                else:
                    newAbility['needTraining'] = False
                    data = line[:-1]
                newAbility['name'] = data
                searchingFor = 'description'
                description = ''
            elif searchingFor == 'description':
                if 'Specialties:' in line:
                    x = line.split('Specialties:')
                    description = description + x[0]
                    newAbility['description'] = description
                    searchingFor = 'specialties'
                    specialities = x[1]
                else:
                    description = description + line
            elif searchingFor == 'specialties':
                for abiType in ('(General)', '(Academic)', '(Arcane)', '(Martial)', '(Supernatural)'):
                    if abiType in line:
                        newAbility['type'] = abiType
                        specialities = specialities + line.split(abiType)[0]
                        specialities = specialities.replace(abiType, '').replace('\n', '').replace('.', '').split(',')
                        for x in range(len(specialities)):
                            specialities[x] = specialities[x].strip()
                        newAbility['specialties'] = specialities
                        abilityLib[newAbility['name']] = newAbility
                        searchingFor = 'name'
                        newAbility = {}
                        break
                    else:
                        pass
                if abiType not in line:
                    specialities = specialities + line
        return abilityLib

    @staticmethod
    def vfProcess(tempVF, refsheet):
        firstIteration = True
        newVirtue = tempVF.virtuesRef.copy()
        oldLine = refsheet[0]
        tempDescription = []
        for line in refsheet:
            if firstIteration:
                for x in tempVF.valueTypes:
                    if x in line:
                        if x != 'Special':
                            for y in tempVF.types:
                                if x + ', ' + y in line:
                                    newVirtue['name'] = oldLine.strip()
                                    newVirtue['value'] = x
                                    newVirtue['type'] = y
                                    firstIteration = False
                                    continue
                        elif x == 'Special':
                            newVirtue['name'] = oldLine.strip()
                            newVirtue['value'] = 'Special'
                            newVirtue['type'] = 'Special'
                            firstIteration = False
                            continue
                oldLine = line
            else:
                for x in tempVF.valueTypes:
                    if x in line:
                        if x != 'Special':
                            for y in tempVF.types:
                                if x + ', ' + y in line:
                                    description = ''
                                    for d in tempDescription[1:-1]:
                                        description += d
                                    tempDescription = []
                                    newVirtue['description'] = description
                                    tempVF.virtuesLib[newVirtue['name']] = newVirtue
                                    newVirtue = {'name': oldLine.strip(), 'value': x, 'type': y}
                                    continue
                        elif x == 'Special':
                            description = ''
                            for d in tempDescription[1:-1]:
                                description += d
                            tempDescription = []
                            newVirtue['description'] = description
                            tempVF.virtuesLib[newVirtue['name']] = newVirtue
                            newVirtue = {'name': oldLine.strip(), 'value': x, 'type': x}
                            continue
                tempDescription.append(line)
                oldLine = line
        description = ''
        for d in tempDescription[1:-1]:
            description += d
        newVirtue['description'] = description
        tempVF.virtuesLib[newVirtue['name']] = newVirtue
        return tempVF


def setup(bot):
    bot.add_cog(Tools(bot))
    # print('tools cog connected')
