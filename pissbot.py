# page is the best

import discord
from discord.utils import get
from discord.ext import commands
import os
import asyncio
import re
import yt_dlp as youtube_dl

# // CONFIG \\

TOKEN = open("C:\\Users\\tt\\Desktop\\projects\\bots\\pissbot_token.txt", "r").read()
GUILD = 916072511110803577
MODERATORS = ["ele#9030", "page#2577", "vixel#4059"]
QUEUE = []
FFMPEG_PATH = "C:\\Users\\tt\\Desktop\\projects\\other\\ffmpeg-4.4-full_build\\bin\\ffmpeg.exe"

ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '196',
    }],
}

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=["p!", "P!"], intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# mod commands

@bot.command()
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command()
async def mute(ctx, id):
    user_id = re.sub('\D', '',id)
    user = await ctx.guild.fetch_member(user_id)
    role = discord.utils.get(ctx.guild.roles, id=916092636765499432)
    await user.add_roles(role)
    await ctx.send(f"successfully muted {user.mention}")

@bot.command()
async def unmute(ctx, id):
    user_id = re.sub('\D', '',id)
    user = await ctx.guild.fetch_member(user_id)
    role = discord.utils.get(ctx.guild.roles, id=916092636765499432)
    await user.remove_roles(role)
    await ctx.send(f"successfully unmuted {user.mention}")

# non-mod commands
frozen = False
@bot.command()
async def play(ctx, url):
    voice_bot = get(bot.voice_clients, guild=ctx.guild)
    global frozen

    print(frozen)

    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return
    
    if voice_bot != None:
        if voice_bot.is_playing():
            await ctx.send("song is already playing, adding to queue")
            QUEUE.append(url)
            return

    if frozen:
        return

    if os.path.exists("song.mp3"):
        os.remove("song.mp3")

    await ctx.send("preparing to play song")

    print(url)
    frozen = True
    if "youtube.com" in url:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    elif "spotify.com" in url:
        os.system(f'cd C:\\Users\\tt && spotdl {url.strip()} -o {os.path.dirname(os.path.abspath(__file__))} --ffmpeg "{FFMPEG_PATH}"')
    for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "song.mp3")

    member = ctx.guild.get_member(916132779043979264)
    try:
        await member.move_to(None)
    except discord.ext.commands.errors.CommandInvokeError:
        print("Error disconnecting, already connected to a voice channel.")
    await ctx.send("playing song")

    voiceChannel = discord.utils.get(ctx.guild.voice_channels)
    await voiceChannel.connect()
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    voice.play(discord.FFmpegPCMAudio("song.mp3"))
    frozen = False

    while voice.is_playing():
        await asyncio.sleep(1)
    await voice.disconnect()
    if QUEUE: # if it's not empty
        link = QUEUE[0]
        QUEUE.pop(0)
        await play(ctx, link)
        

@bot.command()
async def stop(ctx):
    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return
    member = ctx.guild.get_member(916132779043979264)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    await voice.disconnect()
    
@bot.command()
async def queue(ctx):
    await ctx.send(QUEUE)

@bot.command()
async def dog(ctx):
    await ctx.send("https://media.discordapp.net/attachments/916075917648990219/916368883785531452/dog1.jpg?width=603&height=676")
    await ctx.send("https://media.discordapp.net/attachments/916075917648990219/916368839741161522/dog2.jpg")

@bot.command()
async def cat(ctx):
    await ctx.send("https://media.discordapp.net/attachments/916075917648990219/917212236706095154/unknown.png?width=644&height=676")
    await ctx.send("https://media.discordapp.net/attachments/916075917648990219/917212284781203506/E_2MssCVQAEr6gG.png?width=507&height=676")

@bot.command()
async def ss(ctx):
    await ctx.send("piss")

bot.run(TOKEN)