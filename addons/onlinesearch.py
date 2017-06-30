import discord
import json
import requests
import wikipedia
import configparser
from discord.ext import commands
from sys import argv
from string import capwords
from urllib.parse import urlencode

#Read config for Google API Key
config = configparser.ConfigParser()
config.read("config.ini")
apiKey = config['Google']['API_Key']

class OnlineSearch:
    """
    Search stuff, or get stuff from the internet
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.command()
    async def urban(self, *, term=None):
        """Lookup a term on Urban Dictionnary. If no term is specified, returns a random definition. Use a comma followed by a number to specify the definition that should be returned."""
        
        if term is None:
            r = requests.get("http://api.urbandictionary.com/v0/random")
        else:
            n = 1
            if "," in term:
                n = term.split(",", 1)[1]
                term = term.split(",", 1)[0]
            r = requests.get("http://api.urbandictionary.com/v0/define?term={}".format(term))
        
        js = r.json()

        
        if js["result_type"] != "no_results":
            try:
                firstResult = js["list"][int(n)-1]
                word = firstResult["word"]
                definition = firstResult["definition"]
                example = firstResult["example"]
                author = firstResult["author"]
                permalink = firstResult["permalink"]
                thumbsup = firstResult["thumbs_up"]
                thumbsdown = firstResult["thumbs_down"]

                chars = ['[', ']', '\\r\\n', "\\n"]
                for c in chars:
                    if c == chars[0] or c == chars[1]:
                        definition = definition.replace(c, '')
                        example = example.replace(c, '')
                    elif c == chars[2] or c == chars [3]:
                        definition = definition.replace(c, '\n')
                        example = example.replace(c, '\n')

                if example != "":
                    textExamples = example
                else:
                    textExamples = "None"

                try:
                    embed = discord.Embed(title="Definition of {}\n\n".format(word), colour=discord.Color.orange())
                    embed.set_thumbnail(url="http://i.imgur.com/B1gZbQz.png")
                    embed.url = permalink
                    embed.description = definition + "\n"
                    if textExamples != "None":
                        embed.add_field(name="__Example(s) :__", value=textExamples, inline=False)
                    embed.add_field(name="Upvotes", value="👍 **{}**".format(thumbsup), inline=True)
                    embed.add_field(name="Downvotes", value="👎 **{}**\n\n".format(thumbsdown), inline=True)
                    embed.set_footer(text="Defined by {0}".format(author))
                    await self.bot.say(embed=embed)
                except discord.errors.Forbidden:
                    await self.bot.say("**__Definition of {0}__**__ ({1})__\n\n\n".format(word, permalink) + definition + "\n\n" + "__Example(s) :__\n\n" + textExamples + "\n\n\n" + str(thumbsup) + " 👍\n\n" + str(thumbsdown) + " 👎\n\n\n\n" + "*Defined by " + author + "*")
            except ValueError:
                await self.bot.say("`Invalid syntax. If you want to specify which definition should be returned, use the following syntax :\n\".urban [term], [number]\"`")
            except IndexError:
                await self.bot.say("The specified definition does not exist! There are less than {} definitons for this term!".format(n))
        else:
            try:
                embed = discord.Embed(title="¯\_(ツ)_/¯", colour=discord.Color.orange())
                embed.url = "http://www.urbandictionary.com/define.php?term={}".format(term.replace(" ", "%20"))
                embed.description = "\nThere aren't any definitions for *{0}* yet.\n\n[Can you define it?](http://www.urbandictionary.com/add.php?word={1})\n".format(term, term.replace(" ", "%20"))
                embed.set_footer(text="Error 404", icon_url="http://i.imgur.com/w6TtWHK.png")
                await self.bot.say(embed=embed)
            except discord.errors.Forbidden:
                await self.bot.say("¯\_(ツ)_/¯\n\n\n" + "There are no definitions for *{}* yet\n\n".format(term) + "Can you define it ?\n( http://www.urbandictionary.com/add.php?word={} )".format(term.replace(" ", "%20")))

    @commands.command(name='whats', aliases=["what", "what's"])
    async def whats(self, *, term):
        """Defines / explains stuff"""

        if term[0:2] == "a " and term != "a":
            term = term[2:]
        elif term[0:3] == "an " and term != "an":
            term = term[3:]
        elif term[0:5] == "is a " and term != "is a":
            term = term[5:]
        elif term[0:6] == "is an " and term != "is an":
            term = term[6:]
        elif term[0:3] == "is " and term != "is":
            term = term[3:]
        elif term[0:4] == "are " and term != "are":
            term = term[4:]

        term = capwords(term)

        if term.lower() == "kai" or term.lower == "mitchy":
            kai = await self.bot.get_user_info("272908611255271425")
            try:
                embed = discord.Embed(title="Kai", colour=discord.Color.orange())
                embed.set_thumbnail(url=kai.avatar_url)
                embed.description = "An edgy kid that spends too much time on tumblr, previously named mitchy, previously named sans-serif"
                await self.bot.say(embed=embed)
            except discord.errors.Forbidden:
                await self.bot.say("**__Kai :__**\n\nAn edgy kid that spends too much time on tumblr, previously named mitchy, previously named sans-serif")
        elif term.lower() == "ubuntu":
                embed = discord.Embed(title="Ubuntu", colour=discord.Color.orange())
                embed.set_thumbnail(url="http://i.imgur.com/B1gZbQz.png")
                embed.url = "http://www.urbandictionary.com/define.php?term=ubuntu"
                embed.description = "Ubuntu is an ancient african word, meaning \"I can't configure Debian\"" + "\n"
                embed.add_field(name="__Example :__", value="I installed Ubuntu yesterday, it was way more easier than Debian", inline=False)
                embed.set_footer(text="Defined by oSuperDaveo")
                try:
                    await self.bot.say(embed=embed)
                except discord.errors.Forbidden:
                    await self.bot.say("**__Ubuntu :__**\n\n{}\n\n__Example :__\nI installed Ubuntu yesterday, it was way more easier than Debian.\n\n*Defined by oSuperDaveo*".format(embed.description))
        else:
            exception = False
            try:
                #Start wikipedia search
                wiki = wikipedia.page(term)
                permalink = "https://en.wikipedia.org/wiki/{}".format(term.replace(" ", "_"))
                embed = discord.Embed(title=term, colour=discord.Color.orange())
                embed.url = permalink
                if wiki.summary[-13:] == "may refer to:":
                    if len(wiki.content) > 1950:
                        embed.description = "{}...".format(wiki.content[0:1950])
                    else:
                        embed.description = wiki.content
                else:
                    if len(wiki.summary) > 1950:
                        embed.description = "{}...".format(wiki.summary[0:1950])
                    else:
                        embed.description = wiki.summary
                embed.set_footer(text="From Wikipedia", icon_url="http://i.imgur.com/DO4wDN4.png")
                try: 
                    await self.bot.say(embed=embed)
                except discord.errors.Forbidden:
                    await self.bot.say("**__{}__**\n\n\n{}\n\n*Link : {}*".format(term, embed.description, permalink))
                #Images soon

            except wikipedia.exceptions.PageError:
                exception = True
                disambig = False
            except wikipedia.exceptions.DisambiguationError:
                exception = True
                disambig = True
            if exception is True:
                #Start Google Graph Knowledge search
                params = {
                    'query': term,
                    'limit': 1,
                    'indent': True,
                    'key': apiKey,
                }
                url = "https://kgsearch.googleapis.com/v1/entities:search?{}".format(urlencode(params))
                r = requests.get(url)
                js = r.json()

                try:
                    if js["itemListElement"]:
                        js = js["itemListElement"][0]["result"]

                        name = js["name"]
                        briefDescription = js["description"]
                        detailedDescription = js["detailedDescription"]["articleBody"]
                        if detailedDescription[-1] == " ":
                            detailedDescription = detailedDescription[:-1]
                        image = js["image"]["contentUrl"]
                        permalink = js["detailedDescription"]["url"]

                        embed = discord.Embed(title=name, colour=discord.Color.orange())
                        embed.url = permalink
                        embed.description = "\n{}\n\n\n*{}*\n".format(briefDescription, detailedDescription)
                        embed.set_image(url=image)
                        embed.set_footer(text="From Google Graph Knowledge", icon_url="http://i.imgur.com/2obljmu.png")
                    
                        try:
                            await self.bot.say(embed=embed)
                        except discord.errors.Forbidden:
                            await self.bot.say("__**{}** ({})__\n\n{}\n\n\n*{}*\n\n{}\n".format(name, permalink, briefDescription, detailedDescription, image))
                        if disambig is True:
                            await self.bot.say("If this is not the definition you wanted, try being a bit more precise next time. {} can refer to many things!".format(term))
                    else:
                        await self.bot.say("Sorry, none of my sources have an explanation for this term :(")
                        #Coming soon : WikiData and urban dictionnary support

                except KeyError:
                    if js["error"]["code"] == 403: #Checks if API Key is specified
                        await self.bot.say("You did not mention a Google kgsearch API Key in the config.ini file! Please set up one here : https://console.developers.google.com/project/_/apiui/credential")
                    elif js["error"]["code"] == 400: #Checks if API Key is valid
                        await self.bot.say("The mentioned Google kgsearch API Key is invalid! Please set up a correct API Key here : https://console.developers.google.com/project/_/apiui/credential")


#TO-DO : google web and image search

#Load the extension
def setup(bot):
    bot.add_cog(OnlineSearch(bot))