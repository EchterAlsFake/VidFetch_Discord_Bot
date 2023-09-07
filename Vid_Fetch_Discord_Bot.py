
"""
Copyright (C) 2023  EchterAlsFake* | Johannes Habel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

* EchterAlsFake is the internet pseudonym for Johannes Habel.
"""

import threading
import time

import requests
from pytube import YouTube, Playlist
from colorama import *
import discord
from discord.ext import commands
import os
import queue
from moviepy.editor import AudioFileClip
from logger import logger

"""
Please note:

This project is for my free time. It's not meant to be used for commercial purposes.
I can not guarantee that this service is available at any time. 
There will be crashes and errors. I try to fix them of course.


This Discord Bot was created by EchterAlsFake.

It needs the following permissions:

    - Read Messages
    - Send Messages

    Info: You need to enable, that you can get messages from a server member, so that the Bot can send the file.
    Info: I can not send files, that exceed 8 Megabytes. 

https://github.com/EchterAlsFake/VidFetch_Discord_Bot

Thanks :)"""

def get_api_key():
    """
    If you host the bot on your own:
    1) Create a Discord Bot on discord developer site
    2) Set up the Bot (See YouTube tutorials...)
    3) Get the Bot Secret token
    4) Create a file called 'api_key'
    5) Paste the API key into the file
    6) Done :)
    """

    with open("api_key", "r") as api:
        x = api.read()
        return x


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
download_queue = queue.Queue()
num_threads = 12
semaphore = threading.Semaphore(num_threads)


def download_playlist(user, url):

    try:
        p = Playlist(url)
        logger(msg=f"Got Playlist object for {url}")

    except Exception as e:
        logger(e, level=1)

    else:

        for video in p.video_urls:
            download_queue.put(video)
            t1 = threading.Thread(target=download, args=(user, ))
            t1.start()


def download(user):
    while True:
        try:
            url = download_queue.get(block=False)
            logger(f"URL in download queue: {url}")

        except queue.Empty:
            logger(msg="Queue is empty...")
            break

        with semaphore:
            try:
                y = YouTube(url)
                title = y.title
                logger(f"Download requested for: {title} from {user}")
                disallowed_symbols = ["/", ":", "*", "?", "<", ">", "|", "\\"]

                for disallowed_symbol in disallowed_symbols:
                    title = title.replace(disallowed_symbol, "")

                audio_stream = y.streams.filter(only_audio=True).order_by("abr").last()

                audio_stream.download(filename=str(title))
                location = convert_m4a(filename=str(title))
                bot.loop.create_task(user.send(file=discord.File(str(location))))
                logger("Sent audio file to user...")
                time.sleep(20)
                clean_up(file1=str(title), file2=str(location))
                logger("Cleaned files...")

            except Exception as e:
                logger(e, level=1)
                bot.loop.create_task(user.send(f"There was an error with your request... Here's the error: {e}.  Sorry."))

def get_highest_resolution(streams):

    valid_resolutions = []
    resolutions = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "3840p"]

    for stream in streams:
        for resolution in resolutions:

            if resolution in stream:
                valid_resolutions.append(resolution)

    if len(valid_resolutions) == 0:
        logger(msg="Error sorting ")

    else:
        return valid_resolutions[-1]


def get_direct_link(user, url, music, video, highest_res_possible):
    y = YouTube(url)

    if music:
        stream = y.streams.get_audio_only().url
        if requests.get(stream, None).status_code == 200:
            logger(f"Valid Video Stream for url: {url}")
            bot.loop.create_task(user.send_message(f"""
URL for music stream: {url}"""))

        else:
            logger("Error with music stream", level=1)
            bot.loop.create_task(user.send(f"There was an error with your request... Sorry'"))

    elif video:

        if highest_res_possible:
            stream = y.streams.filter(only_video=True, resolution=get_highest_resolution(streams=y.streams.all())).first().url
            logger(f"Got high quality stream for: {url}")
            bot.loop.create_task(user.send_message(f"High quality video stream: {url}  Note: the video maybe has NO sound. That's expected and is an 'error' from YouTube"))

        else:
            streams = y.streams.get_highest_resolution().url
            logger(f"Got usual quality stream for: {url}")
            bot.loop.create_task(user.send_message(f"Video: {url}"))









def convert_m4a(filename):
    audio_stream = AudioFileClip(str(filename))
    audio_stream.write_audiofile(str(filename) + ".m4a", codec="aac")
    return str(filename) + ".m4a"


def clean_up(file1, file2):
    os.remove(file1)
    os.remove(file2)


@bot.tree.command(name="download", description="Please set Fast Download to False. It helps my CPU, thanks.)")
async def video(interaction: discord.Interaction, url : str):

    await interaction.response.send_message(f"""
Downloading: {url}

The download / upload will take 1-3 minutes. 
You will get a message in your DMs with the .m4a file.
Please remember: You need to allow getting messages from unknown server members in your DC settings!
""")

    user = interaction.user
    download_queue.put(url)

    try:
        t = threading.Thread(target=download, args=(user, ))
        t.start()
    except Exception as e:
        logger(e, level=1)
        bot.loop.create_task(user.send_message(f"There was an error: {e} Sorry for the inconvenience!"))


@bot.tree.command(name="playlist", description="Downloads all videos in a playlist.  See /help for more info")
async def playlist(interaction: discord.Interaction, url : str):

    await interaction.response.send_message(f"""
The following playlist will be downloaded: {url}
Check your DMs for more information.
""")

    user = interaction.user
    try:
        t1 = threading.Thread(target=download_playlist, args=(user, url,))
        t1.start()

    except Exception as e:
        logger(e, level=1)
        bot.loop.create_task(user.send_message(f"There was an error: {e} Sorry for the inconvenience!"))


@bot.tree.command(name="get_direct_link", description="Gives you the direct download link to the video. This function supports high quality videos!")
async def direct_link(interaction: discord.Interaction, url : str, music : bool, video: bool):
    user = interaction.user

    try:
        t1 = threading.Thread(target=get_direct_link, args=(user, url, music, video))
        t1.start()

    except Exception as e:
        logger(e, level=1)
        bot.loop.create_task(user.send_message(f"There was an error: {e} Sorry for the inconvenience!"))

@bot.tree.command(name="help", description="Shows a simple tutorial message.")
async def help(interaction: discord.Interaction):
    user = interaction.user

    def send_help_english_thread():
        bot.loop.create_task(interaction.response.send_message("""

Commands:

/help - Shows this message
/download [url] - Downloads the video and sends it back as .m4a file
/credits - shows the sources / developing process

Optional:

/download [fast_download] - True: The Video will be downloaded with Pytube, on max speed.
                            False: The Video will be downloaded with wget. Takes longer, but
                            helps my computer, as it doesn't need so much CPU Power. If you can, please
                            set fast_download to False. Thanks :) 

Error messages:

Error messages will be sent to the user. Maybe you can do something with it, or at least you can post them
on my GitHub, so that I can fix them. Thanks :) 

"""))
    try:
        t = threading.Thread(target=send_help_english_thread, args=(user, ))
        t.start()

    except Exception as e:
        logger(e, level=1)
        bot.loop.create_task(user.send_message(f"There was an error: {e} Sorry for the inconvenience!"))


@bot.tree.command(name="credits", description="Shows all sources.")
async def credits(interaction: discord.Interaction):
    user = interaction.user

    def send_credits_english_thread():
        bot.loop.create_task(interaction.response.send_message("""

Vid Fetch is the Discord Bot of the Vid Fetch YouTube Downloader, which were
both created by EchterAlsFake in 2023. The Discord Bot itself is licensed under the 
GPLv3 license. The Source Code of this Bot can be found on:

(You should have received a copy of the license within the .zip Archive)

https://github.com/EchterAlsFake/VidFetch_Discord_Bot

The URL of the Bot Picture is: https://uxwing.com/black-and-white-youtube-icon/
The Framework for the YouTube Downloader is: https://github.com/pytube/pytube

The bot is hosted on my own Laptop or by some random guys from the Internet.
Everyone can access the bot on my GitHub and host it on their own system.

I am not responsible for damages on your system caused by third party sources.

Have a great day :) 

[Donation link (Only if you want)  paypal.me/EchterAlsFake]


For developers:

All libraries used by this:

threading - built-in
time      - built-in
pytube    - github.com/pytube/pytube
colorama  - github.com/tartley/colorama
discord   - github.com/Rapptz/discord.py
os        - built-in
queue     - built-in
moviepy   - github.com/Zulko/moviepy

Coded with Python 3.11.4 on Arch Linux
Compiled with Pyinstaller

Release: 1.5
6th of September 2023 - Signed by EchterAlsFake | Johannes Habel
"""))

    try:
        t = threading.Thread(target=send_credits_english_thread)
        t.start()

    except Exception as e:
        logger(e, level=1)
        bot.loop.create_task(user.send_message(f"There was an error: {e} Sorry for the inconvenience!"))


@bot.event
async def on_ready():
    print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTYELLOW_EX + "Bot is ready!")

    try:
        await bot.tree.sync()
        print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTCYAN_EX + f"Synced Application Commands.")

    except Exception as e:
        print(e)


bot.run(get_api_key())

