# page is the best

import discord
import time
import pytube
import datetime
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
import pytz

# // CONFIG \\

TOKEN = open("C:\\Users\\tt\\Desktop\\projects\\bots\\pissbot_token.txt", "r").read()
GUILD = 916072511110803577
LOGS_CHANNEL = 916081066119405598
QUEUE = []
TIMEZONE = pytz.timezone("Europe/Warsaw")
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

# // MOD COMMANDS \\

@bot.command(brief="[MOD ONLY] - makes the bot say something :)")
@commands.has_permissions(administrator=True)
async def say(ctx, *, text):
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

@bot.command(aliases=["clearq", "cq"], brief="[MOD ONLY] - clears the queue and stops the current song playing")
@commands.has_permissions(administrator=True)
async def clearqueue(ctx):
    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return
    member = ctx.guild.get_member(916132779043979264)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    global paused
    global song_title
    paused = False
    song_title = ""
    QUEUE.clear()
    await ctx.send("cleared songs from queue")
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
    if ctx.message.author.voice == None:
        await ctx.send("must be in a voice channel")
        return
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

# // NON-MOD COMMANDS \\ 
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
            if not "youtube.com" in url and not "&list" in url:
                await ctx.send("song is already playing, adding to queue")
                QUEUE.append(url)
                return
            else:
                playlist = pytube.Playlist(url)
                playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
                for url in playlist.video_urls:
                    QUEUE.append(url)
                await ctx.send("song is already playing, added songs from playlist to queue")
                return

    await ctx.send("preparing to play song")

    print(url)
    frozen = True
    if "youtube.com" in url and not "&list" in url:
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
    elif "youtube.com" in url and "&list" in url:
        print("O")
        playlist = pytube.Playlist(url)
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        for url in playlist.video_urls:
            if url == playlist.video_urls[0]:
                continue
            QUEUE.append(url)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist.video_urls[0]])
        song_title = pytube.YouTube(playlist.video_urls[0]).title
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

@bot.command(aliases=["av"], brief="gets someone's avatar")
async def avatar(ctx, id):
    user_id = re.sub('\D', '',id)
    user = await ctx.guild.fetch_member(user_id)
    await ctx.send(user.avatar_url)

@bot.command(brief="lists the amount of members in the server")
async def membercount(ctx):
    embed = discord.Embed()
    embed.colour = (0x2163b5)
    embed.title = f"member count"

    embed.add_field(name="including bots", value=f"{ctx.guild.member_count}", inline=False)
    embed.add_field(name="without bots", value=f"{len([m for m in ctx.guild.members if not m.bot])}")

    await ctx.send(embed=embed)

@bot.command(brief="gets info of a user")
async def whois(ctx, member):
    user_id = re.sub('\D', '',member)
    member = await ctx.guild.fetch_member(user_id)

    embed = discord.Embed()
    embed.colour = (0x2163b5)
    embed.title = f""
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")

    joined_at = member.joined_at.strftime("%m/%d/%Y\n%I:%M %p UTC")
    embed.add_field(name="joined", value=joined_at, inline=True)
    registered_at = member.created_at.strftime("%m/%d/%Y\n%I:%M %p UTC")
    embed.add_field(name="registered", value=registered_at, inline=True)
    status = "server member"

    yassiest = discord.utils.get(ctx.guild.roles, name="yassiest")
    if yassiest in member.roles:
        status = "server owner"
    embed.add_field(name="status", value=status, inline=False)

    await ctx.send(embed=embed)



# // OTHER \\

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("you need to be a moderator to run this command!")
    else:
        raise error

# // LOG MODULE \\

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

    now = datetime.datetime.now(tz=TIMEZONE)
    time = now.strftime("%m/%d/%Y, %I:%M %p")
    embed.add_field(name=f"info", value=f"ID: {message.id} • {time}", inline=False)
    

    channel = bot.get_channel(LOGS_CHANNEL)
    await channel.send(embed=embed)

@bot.event
async def on_message_edit(before_message: discord.Message, after_message: discord.Message):
    if before_message == None or after_message == None:
        return
    if before_message.content == after_message.content:
        return
    embed = discord.Embed()
    embed.colour = (0x6f40ad)
    embed.title = f"message sent by {before_message.author} edited in #{before_message.channel}"

    embed.set_author(name=f"{before_message.author}", icon_url=f"{before_message.author.avatar_url}")
    embed.add_field(name="before", value=f"{before_message.content}", inline=False)
    embed.add_field(name="after", value=f"{after_message.content}", inline=False)

    now = datetime.datetime.now(tz=TIMEZONE)
    time = now.strftime("%m/%d/%Y, %I:%M %p")

    embed.add_field(name=f"info", value=f"ID: {after_message.id} • {time}", inline=False)

    channel = bot.get_channel(LOGS_CHANNEL)
    await channel.send(embed=embed)

@bot.event
async def on_invite_create(invite: discord.Invite):
    embed = discord.Embed()
    embed.colour = (0x2163b5)
    embed.title = f"invited created by {invite.inviter} in #{invite.channel}"

    embed.set_author(name=f"{invite.inviter}", icon_url=f"{invite.inviter.avatar_url}")
    max_uses = invite.max_uses
    if max_uses == 0:
        max_uses = "no limit"
    embed.add_field(name="invite info", value=f"URL: {invite.url}\n expires: {str(datetime.timedelta(seconds=invite.max_age))}\n used: {invite.uses} times\n max uses: {max_uses}\n temporary: {str(invite.temporary)}", inline=False)

    now = datetime.datetime.now(tz=TIMEZONE)
    time = now.strftime("%m/%d/%Y, %I:%M %p")

    embed.add_field(name=f"info", value=f"ID: {invite.id} • {time}", inline=False)

    channel = bot.get_channel(LOGS_CHANNEL)
    await channel.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    if before.nick == after.nick:
        return
    embed = discord.Embed()
    embed.colour = (0x2163b5)
    embed.title = f"member {before} changed their nickname"

    embed.set_author(name=f"{after}", icon_url=f"{after.avatar_url}")
    embed.add_field(name="before", value=f"{before.nick}", inline=False)
    embed.add_field(name="after", value=f"{after.nick}", inline=False)

    now = datetime.datetime.now(tz=TIMEZONE)
    time = now.strftime("%m/%d/%Y, %I:%M %p")

    embed.add_field(name=f"info", value=f"ID: {after.id} • {time}", inline=False)

    channel = bot.get_channel(LOGS_CHANNEL)
    await channel.send(embed=embed)

@bot.event
async def on_member_join(member):
    embed = discord.Embed()
    embed.colour = (0x6dbf39)
    embed.title = f"{member}"
    embed.set_thumbnail(url=member.avatar_url)

    time1 = member.created_at.strftime("%m/%d/%Y, %I:%M %p UTC")

    embed.set_author(name=f"member joined", icon_url=f"{member.avatar_url}")
    embed.add_field(name="account created", value=f"{time1}", inline=False)

    now = datetime.datetime.now(tz=TIMEZONE)
    time = now.strftime("%m/%d/%Y, %I:%M %p")

    embed.add_field(name=f"info", value=f"ID: {member.id} • {time}", inline=False)

    channel = bot.get_channel(LOGS_CHANNEL)
    await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    embed = discord.Embed()
    embed.colour = (0xa8323a)
    embed.title = f"{member}"
    embed.set_thumbnail(url=member.avatar_url)

    embed.set_author(name=f"member left", icon_url=f"{member.avatar_url}")

    now = datetime.datetime.now(tz=TIMEZONE)
    time = now.strftime("%m/%d/%Y, %I:%M %p")

    embed.add_field(name=f"info", value=f"ID: {member.id} • {time}", inline=False)

    channel = bot.get_channel(LOGS_CHANNEL)
    await channel.send(embed=embed)

bot.run(TOKEN)