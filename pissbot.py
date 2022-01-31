# page is the best

import discord
import time
import pytube
from discord.ext.commands.help import Paginator # (page reference)
from discord.utils import get
from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
import os
import asyncio
import requests
import re
import yt_dlp as youtube_dl

# // CONFIG \\

TOKEN = open("C:\\Users\\tt\\Desktop\\projects\\bots\\pissbot_token.txt", "r").read()
GUILD = 916072511110803577
LOGS_CHANNEL = 916081066119405598
QUEUE = []
FFMPEG_PATH = "C:\\Users\\tt\\Desktop\\projects\\other\\ffmpeg-4.4-full_build\\bin\\ffmpeg.exe"

ydl_opts = {
        'format': 'bestaudio/best'
        #'postprocessors': [{
        #'key': 'FFmpegExtractAudio',
        #'preferredcodec': 'mp3',
        #'preferredquality': '196',
    ,
}

# // VARS \\

paused = False
song_title = ""

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=["p!", "P!"], intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# mod commands

@bot.command(brief="[MOD ONLY] - makes the bot say something :)")
@commands.has_permissions(administrator=True)
async def say(ctx, *, text):
    #if ctx.message.author.id not in MODERATORS:
    #    return
    await ctx.message.delete()
    await ctx.send(text)

@bot.command(brief="[MOD ONLY] - mutes someone")
@commands.has_permissions(administrator=True)
async def mute(ctx, id):
    user_id = re.sub('\D', '',id)
    user = await ctx.guild.fetch_member(user_id)
    role = discord.utils.get(ctx.guild.roles, id=916092636765499432)
    await user.add_roles(role)
    await ctx.send(f"successfully muted {user.mention}")

@bot.command(brief="[MOD ONLY] - unmutes someone")
@commands.has_permissions(administrator=True)
async def unmute(ctx, id):
    user_id = re.sub('\D', '',id)
    user = await ctx.guild.fetch_member(user_id)
    role = discord.utils.get(ctx.guild.roles, id=916092636765499432)
    await user.remove_roles(role)
    await ctx.send(f"successfully unmuted {user.mention}")

@bot.command(aliases=["st"], brief="[MOD ONLY] - completely stops a song")
@commands.has_permissions(administrator=True)
async def stop(ctx):
    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return
    member = ctx.guild.get_member(916132779043979264)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    global paused
    paused = False
    await voice.disconnect()

@bot.command(aliases=["sk"], brief="[MOD ONLY] - skips to the next song in queue")
@commands.has_permissions(administrator=True)
async def skip(ctx):
    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    global paused
    paused = False
    voice.stop()

@bot.command(aliases=["pa"], brief="[MOD ONLY] - pauses a song")
@commands.has_permissions(administrator=True)
async def pause(ctx):
    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused == True:
        await ctx.send("song is already paused!")
        return
    global paused
    paused = True
    voice.pause()
    await ctx.send("paused!")

@bot.command(aliases=["r", "re"], brief="[MOD ONLY] - resumes a song")
@commands.has_permissions(administrator=True)
async def resume(ctx):
    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused == False:
        await ctx.send("song is already playing!")
        return
    global paused
    voice.resume()
    paused = False
    await ctx.send("resumed!")

@bot.command(brief="[MOD ONLY] - don't worry about it :)", description="DOn'T")
@commands.has_permissions(administrator=True)
async def debug(ctx, *, msg):
    print(msg)

def index_in_list(a_list, index):
    print(index < len(a_list))

@bot.command(aliases=["rq", "removeq"], brief="[MOD ONLY] - deletes a song from the queue by using the song's queue position")
@commands.has_permissions(administrator=True)
async def removequeue(ctx, queue_position):
    print(queue_position)
    print(int(queue_position) - 1)
    if index_in_list(QUEUE, int(queue_position) - 1) == False or not QUEUE:
        await ctx.send("must enter a valid queue position")
        return
    QUEUE.pop(int(queue_position) - 1)
    await ctx.send("successfully removed song from queue")

@bot.command(brief="[MOD ONLY] - delets the last specified messages")
@commands.has_permissions(administrator=True)
async def purge(ctx, limit: int):
    await ctx.channel.purge(limit=limit+1)

# non-mod commands
frozen = False
@bot.command(aliases=["pl"], brief="plays a song (link or song search on youtube)", description="plays a song from either a youtube, bandcamp, spotify or file attachment. you can also type in the name of a song.")
async def play(ctx, *, url = ""):
    voice_bot = get(bot.voice_clients, guild=ctx.guild)
    global frozen
    global paused
    global song_title

    print(frozen)

    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return

    if frozen or paused:
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
        song_title = pytube.YouTube(url).title
    elif "bandcamp.com" in url:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        song_title = "couldn't get title!"
    elif "spotify.com" in url:
        os.system(f'cd C:\\Users\\tt && spotdl {url.strip()} -o {os.path.dirname(os.path.abspath(__file__))} --ffmpeg "{FFMPEG_PATH}"')
        song_title = "couldn't get title!"
    elif "youtu.be" in url:
        new_url = url.split(".be/")[1]
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([new_url])
        song_title = pytube.YouTube(url).title
    elif "cdn.discordapp.com" in url:
        r = requests.get(url, allow_redirects=True) 
        open('bfsdfsdhf.webm', 'wb').write(r.content)
        song_title = "couldn't get title!"
    else:
        await ctx.send("looking for youtube video...")
        r = requests.get("https://www.youtube.com/results?search_query=" + url)
        video_ids = re.findall(r"watch\?v=(\S{11})", r.text)
        url = "https://www.youtube.com/watch?v=" + video_ids[0]
        await ctx.send(f"found video {url}, preparing to play now!")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        song_title = pytube.YouTube(url).title
    time.sleep(0.5)
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

    while voice.is_playing() or paused:
        await asyncio.sleep(1)
    await voice.disconnect()
    if QUEUE: # if it's not empty
        link = QUEUE[0]
        print(link)
        QUEUE.pop(0)
        await play(ctx=ctx, url=link)
        
    
@bot.command(brief="shows a preview of the queue", description="i hate gay people", aliases=["q"])
async def queue(ctx):
    final_string = f"```// QUEUE \\\ \nPLAYING: {song_title}\n\n"
    index = 0
    for i in QUEUE:
        index += 1
        if not "youtube.com" in str(i):
            final_string += f"{str(index)}. {str(i)}" + "\n"
        else:
            final_string += f"{str(index)}. {pytube.YouTube(str(i)).title}" + "\n"

    final_string += "\n```"
    await ctx.send(final_string)

@bot.command(brief="PISS DOG", description="pissy dog")
async def dog(ctx):
    await ctx.send("https://media.discordapp.net/attachments/916075917648990219/916368883785531452/dog1.jpg?width=603&height=676")
    await ctx.send("https://media.discordapp.net/attachments/916075917648990219/916368839741161522/dog2.jpg")

@bot.command(brief="piss cat", description="piss cat")
async def cat(ctx):
    await ctx.send("https://media.discordapp.net/attachments/916075917648990219/917212236706095154/unknown.png?width=644&height=676")
    await ctx.send("https://media.discordapp.net/attachments/916075917648990219/917212284781203506/E_2MssCVQAEr6gG.png?width=507&height=676")

@bot.command(brief="piss", description="piss")
async def ss(ctx):
    await ctx.send("piss")

# other

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("you need to be a moderator to run this command!")
    else:
        raise error

# log module

@bot.event
async def on_message_delete(message: discord.Message):
    embed = discord.Embed()
    embed.colour = (0xa8323a)

    embed.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar_url}")

    if message.content != "":
        embed.add_field(name=f"message sent by {message.author} deleted in #{message.channel}", value=f"{message.content}", inline=False)
    else:
        embed.add_field(name=f"message sent by {message.author} deleted in #{message.channel}", value=f" ︎ ︎", inline=False)
    
    if message.attachments:
        embed.set_image(url=message.attachments[0].proxy_url)

    xd = str(message.created_at.time()).split(":") # i didnt know what to name this but its basically for making the string maniuplation more organized
    hour = str(int(xd[0]) + 1) + ":" + xd[1] + " AM"

    embed.add_field(name=f"info", value=f"ID: {message.id} • {message.created_at.month}/{message.created_at.day}/{message.created_at.year} {hour}", inline=False)
    

    channel = bot.get_channel(LOGS_CHANNEL)
    await channel.send(embed=embed)

@bot.event
async def on_message_edit(before_message: discord.Message, after_message: discord.Message):
    embed = discord.Embed()
    embed.colour = (0x6f40ad)
    embed.title = f"message sent by {before_message.author} edited in #{before_message.channel}"

    embed.set_author(name=f"{before_message.author}", icon_url=f"{before_message.author.avatar_url}")
    embed.add_field(name="before", value=f"{before_message.content}", inline=False)
    embed.add_field(name="after", value=f"{after_message.content}", inline=False)

    xd = str(after_message.edited_at.time()).split(":") # i didnt know what to name this but its basically for making the string maniuplation more organized
    hour = str(int(xd[0]) + 1) + ":" + xd[1] + " AM"

    embed.add_field(name=f"info", value=f"ID: {after_message.id} • {after_message.edited_at.month}/{after_message.edited_at.day}/{after_message.edited_at.year} {hour}", inline=False)

    channel = bot.get_channel(LOGS_CHANNEL)
    await channel.send(embed=embed)

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