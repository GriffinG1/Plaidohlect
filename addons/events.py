import asyncio
import discord
import json
import re
from discord.ext import commands
from subprocess import call
from string import printable
from sys import argv
from urllib.parse import urlparse

class Events:
    """
    Special event handling.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))


    drama_alert = (
        'attackhelicopter',
        'gender',
        'faggot',
        'retarded',
        'cunt',
        'tranny',
        'nigger',
        'incest',
    )

    ignored_file_extensions = (
        '.jpg',
        '.jpeg',
        '.gif',
        '.png',
        '.bmp',
    )

    # I hate naming variables sometimes
    user_antispam = {}
    channel_antispam = {}
    help_notice_anti_repeat = []

    async def add_restriction(self, member, rst):
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id not in rsts:
            rsts[member.id] = []
        if rst not in rsts[member.id]:
            rsts[member.id].append(rst)
        with open("data/restrictions.json", "w") as f:
            json.dump(rsts, f)

    async def user_spam_check(self, message):
        if message.author.id not in self.user_antispam:
            self.user_antispam[message.author.id] = []
        self.user_antispam[message.author.id].append(message)
        if len(self.user_antispam[message.author.id]) == 6:  # it can trigger it multiple times if I use >. it can't skip to a number so this should work
            await self.bot.add_roles(message.author, self.bot.muted_role)
            await self.add_restriction(message.author, "Muted")
            msg_user = "You were automatically muted for sending too many messages in a short period of time!\n\nIf you believe this was done in error, send a direct message to one of the staff in {}.".format(self.bot.welcome_channel.mention)
            try:
                await self.bot.send_message(message.author, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            log_msg = "🔇 **Auto-muted**: {} muted for spamming | {}#{}\n🗓 __Creation__: {}\n🏷 __User ID__: {}".format(message.author.mention, message.author.name, message.author.discriminator, message.author.created_at, message.author.id)
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            msgs_to_delete = self.user_antispam[message.author.id][:]  # clone list so nothing is removed while going through it
            for msg in msgs_to_delete:
                embed.add_field(name="#"+msg.channel.name, value="\u200b" + msg.content)  # added zero-width char to prevent an error with an empty string (lazy workaround)
            await self.bot.send_message(self.bot.memberlogs_channel, log_msg, embed=embed)
            await self.bot.send_message(self.bot.automod_channel, log_msg + "\nSee {} for a list of deleted messages.".format(self.bot.adminlogs_channel.mention))
            for msg in msgs_to_delete:
                try:
                    await self.bot.delete_message(msg)
                except discord.errors.NotFound:
                    pass  # don't fail if the message doesn't exist
        await asyncio.sleep(3)
        self.user_antispam[message.author.id].remove(message)
        try:
            if len(self.user_antispam[message.author.id]) == 0:
                self.user_antispam.pop(message.author.id)
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

    async def channel_spam_check(self, message):
        if message.channel.id not in self.channel_antispam:
            self.channel_antispam[message.channel.id] = []
        self.channel_antispam[message.channel.id].append(message)
        if len(self.channel_antispam[message.channel.id]) == 25:  # it can trigger it multiple times if I use >. it can't skip to a number so this should work
            overwrites_everyone = message.channel.overwrites_for(self.bot.everyone_role)
            overwrites_everyone.send_messages = False
            await self.bot.edit_channel_permissions(message.channel, self.bot.everyone_role, overwrites_everyone)
            msg_channel = "This channel has been automatically locked for spam. Please wait while staff review the situation."
            embed = discord.Embed(title="Deleted messages", color=discord.Color.gold())
            msgs_to_delete = self.user_antispam[message.author.id][:]  # clone list so nothing is removed while going through it
            for msg in msgs_to_delete:
                embed.add_field(name="@"+self.bot.escape_name(msg.author), value="\u200b" + msg.content)  # added zero-width char to prevent an error with an empty string (lazy workaround)
            await self.bot.send_message(message.channel, msg_channel)
            log_msg = "🔒 **Auto-locked**: {} locked for spam".format(message.channel.mention)
            await self.bot.send_message(self.bot.adminlogs_channel, log_msg, embed=embed)
            await self.bot.send_message(self.bot.automod_channel, log_msg + " @here\nSee {} for a list of deleted messages.".format(self.bot.adminlogs_channel.mention))
            msgs_to_delete = self.channel_antispam[message.channel.id][:]  # clone list so nothing is removed while going through it
            for msg in msgs_to_delete:
                try:
                    await self.bot.delete_message(msg)
                except discord.errors.NotFound:
                    pass  # don't fail if the message doesn't exist
        await asyncio.sleep(5)
        self.channel_antispam[message.channel.id].remove(message)
        try:
            if len(self.channel_antispam[message.channel.id]) == 0:
                self.channel_antispam.pop(message.channel.id)
        except KeyError:
            pass  # if the array doesn't exist, don't raise an error

def setup(bot):
    bot.add_cog(Events(bot))