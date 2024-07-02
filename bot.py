import os
import discord
from discord.ext import commands
import discord.utils
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import sentiment
from table2ascii import table2ascii as t2a, PresetStyle

# Loading the .env file and reading the token 
load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')
client = commands.Bot(command_prefix='$', intents=discord.Intents.all())

@client.event
async def on_ready():
    # On ready event. Checks bot availiblity
    print(f'{client.user} is now running!!')

@client.command(name='scan')
async def scanCommand(ctx, *args):
    """
    The function will be used to scann all the messages from the channel
    and then will be used to analyse the data. All the messages will be
    encrypted and stored into a SQLite database and post analysis, all the 
    data will be wiped out ensuring no infringement to user's privacy.
    """

    # Using the limit is optional to user. If the user feels to analyse a particular
    # amount of messages, they can do the same.
    #
    # $scan         -> analyses all the messages in the channel
    # $scan <limit> -> analyses the ammount of messages specified by user
    
    if args:
        limit = int(args[0])
        messages = [(message.content, message.author, message.created_at) async for message in ctx.channel.history(limit=int(limit))]
    else:
        messages = [(message.content, message.author, message.created_at) async for message in ctx.channel.history()]
    
    guildName = (ctx.guild.name)  # Referencing server name to get a reference for the file name 
    guildName = guildName.replace(" ", "")
    
    messagesDF = pd.DataFrame(messages, columns=['Content', 'Author', 'Timestamp'])

    # Returning the analysis
    #
    # Analysing the messages
    analysedMesages = sentiment.analyseMessage(messagesDF)
    counts = sentiment.countType(analysedMesages)
    negAuthors = sentiment.topNegAuthor(analysedMesages)
    posAuthors = sentiment.topPosAuthor(analysedMesages)

    # Embed settings
    analysisEmbed = discord.Embed(
        title= "Message analysis",
        description=f"""
        Heya :wave:,\n
        Find the message analysis you requested for attached below -> \n
        **MESSAGE INSIGHTS**\n
        1. **Total NEUTRAL messages =** {counts[0]}\n
        2. **Total POSITIVE messages =** {counts[1]}\n
        3. **Total NEGATIVE messages =** {counts[2]}\n\n
        
        **USER INSIGHTS**\n
        1. **User with most positive messages =** {negAuthors[0]}\n
        2. **User with most negative messages =** {posAuthors[0]}
        """,
        color= discord.Color.blue()
    )
    await ctx.author.send(embed=analysisEmbed)

if __name__ == "__main__":
    client.run(TOKEN)