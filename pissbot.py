# page is the best

import discord
from discord.ext.commands.help import Paginator # (page reference)
from discord.utils import get
from discord.ext import commands
import os
import asyncio
import requests
import re
import yt_dlp as youtube_dl

# // CONFIG \\

TOKEN = open("C:\\Users\\tt\\Desktop\\projects\\bots\\pissbot_token.txt", "r").read()
GUILD = 916072511110803577
MODERATORS = [800087654791249942, 638579111035666457, 574952383780618240]
QUEUE = []
FFMPEG_PATH = "C:\\Users\\tt\\Desktop\\projects\\other\\ffmpeg-4.4-full_build\\bin\\ffmpeg.exe"
Paused = False

ydl_opts = {
        'format': 'bestaudio/best'
        #'postprocessors': [{
        #'key': 'FFmpegExtractAudio',
        #'preferredcodec': 'mp3',
        #'preferredquality': '196',
    ,
}

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=["p!", "P!"], intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# mod commands

@bot.command()
async def say(ctx, *, text):
    if ctx.message.author.id not in MODERATORS:
        return
    await ctx.message.delete()
    await ctx.send(text)

@bot.command()
async def mute(ctx, id):
    if ctx.message.author.id not in MODERATORS:
        return
    user_id = re.sub('\D', '',id)
    user = await ctx.guild.fetch_member(user_id)
    role = discord.utils.get(ctx.guild.roles, id=916092636765499432)
    await user.add_roles(role)
    await ctx.send(f"successfully muted {user.mention}")

@bot.command()
async def unmute(ctx, id):
    if ctx.message.author.id not in MODERATORS:
        return
    user_id = re.sub('\D', '',id)
    user = await ctx.guild.fetch_member(user_id)
    role = discord.utils.get(ctx.guild.roles, id=916092636765499432)
    await user.remove_roles(role)
    await ctx.send(f"successfully unmuted {user.mention}")

@bot.command()
async def stop(ctx):
    if ctx.message.author.id not in MODERATORS:
        return
    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return
    member = ctx.guild.get_member(916132779043979264)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    global Paused
    Paused = False
    await voice.disconnect()

@bot.command()
async def skip(ctx):
    if ctx.message.author.id not in MODERATORS:
        return
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    global Paused
    Paused = False
    voice.stop()

@bot.command()
async def pause(ctx):
    if ctx.message.author.id not in MODERATORS:
        return
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused == True:
        await ctx.send("song is already paused!")
        return
    global Paused
    Paused = True
    voice.pause()
    await ctx.send("paused!")

@bot.command()
async def resume(ctx):
    if ctx.message.author.id not in MODERATORS:
        return
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused == False:
        await ctx.send("song is already playing!")
        return
    global Paused
    voice.resume()
    Paused = False
    await ctx.send("resumed!")

@bot.command()
async def debug(ctx, *, msg):
    if ctx.message.author.id not in MODERATORS:
        return
    print(msg)

# non-mod commands
frozen = False
@bot.command()
async def play(ctx, *, url = ""):
    voice_bot = get(bot.voice_clients, guild=ctx.guild)
    global frozen

    print(frozen)

    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return

    if frozen:
        return

    if ctx.message.attachments: # if attachment exists
        url = str(ctx.message.attachments[0])

    if url == "":
        await ctx.send("need a link or a file attachment!")
    
    if voice_bot != None:
        if voice_bot.is_playing():
            await ctx.send("song is already playing, adding to queue")
            QUEUE.append(url)
            return

    await ctx.send("preparing to play song")

    print(url)
    frozen = True
    if "youtube.com" in url:
        print("J")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    elif "bandcamp.com" in url:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    elif "spotify.com" in url:
        os.system(f'cd C:\\Users\\tt && spotdl {url.strip()} -o {os.path.dirname(os.path.abspath(__file__))} --ffmpeg "{FFMPEG_PATH}"')
    elif "youtu.be" in url:
        new_url = url.split(".be/")[1]
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([new_url])
    elif "cdn.discordapp.com" in url:
        r = requests.get(url, allow_redirects=True) 
        open('bfsdfsdhf.webm', 'wb').write(r.content)
    else:
        await ctx.send("looking for youtube video...")
        r = requests.get("https://www.youtube.com/results?search_query=" + url)
        video_ids = re.findall(r"watch\?v=(\S{11})", r.text)
        url = "https://www.youtube.com/watch?v=" + video_ids[0]
        await ctx.send(f"found video {url}, preparing to play now!")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    for file in os.listdir("./"):
            print(file)
            if file.endswith(".webm"):
                os.replace(file, "song.webm")
            elif file.endswith(".mp3"):
                os.replace(file, "song.webm")
            elif file.endswith(".m4a"):
                os.replace(file, "song.webm")

    member = ctx.guild.get_member(916132779043979264)
    try:
        await member.move_to(None)
    except discord.ext.commands.errors.CommandInvokeError:
        print("Error disconnecting, already connected to a voice channel.")
    await ctx.send("playing song")

    voiceChannel = discord.utils.get(ctx.guild.voice_channels)
    await voiceChannel.connect()
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    voice.play(discord.FFmpegPCMAudio("song.webm"))
    frozen = False
    global Paused

    while voice.is_playing() or Paused:
        await asyncio.sleep(1)
    await voice.disconnect()
    if QUEUE: # if it's not empty
        link = QUEUE[0]
        print(link)
        QUEUE.pop(0)
        await play(ctx=ctx, url=link)
        
    
@bot.command()
async def queue(ctx):
    if not QUEUE:
        await ctx.send("nothing in queue :rolling_eyes:")
        return
    final_string = "```// QUEUE \\\ \n\n"
    index = 0
    for i in QUEUE:
        index += 1
        final_string += f"{str(index)}. {str(i)}" + "\n"

    final_string += "\n```"
    await ctx.send(final_string)

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


"""
@bot.event
async def on_member_update(before, after):
    print(before.nick)
    if "page" in str(before):
        await after.edit(nick="silly page")
        return
    elif "RoboticFade" in str(before):
        await after.edit(nick="mink")
        return
"""

bot.run(TOKEN)