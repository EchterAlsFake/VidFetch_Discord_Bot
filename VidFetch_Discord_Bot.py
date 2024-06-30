
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
import os
import queue

from pytube import YouTube, Playlist
from colorama import Fore
from discord.ext import commands
from discord import File, Intents, Interaction, app_commands
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

Thanks :)
"""


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

    with open("api_key.txt", "r") as api:
        return api.read()


intents = Intents.default()
intents.message_content = False
bot = commands.Bot(command_prefix="!", intents=intents)
download_queue = queue.Queue()
num_threads = 2
semaphore = threading.Semaphore(num_threads)

android = True
text = """
Warning: This bot currently runs on my Android device! Downloading is NOT possible due to my low upload speed. 
Please use the `get direct link` function instead!
"""


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
                bot.loop.create_task(user.send(file=File(str(location))))
                logger("Sent audio file to user...")
                time.sleep(10)
                clean_up(file1=str(title), file2=str(location))
                logger("Cleaned files...")

            except Exception as e:
                logger(e, level=1)
                bot.loop.create_task(user.send(f"There was an error with your request... Here's the error: {e}.  Sorry."))


def verify_stream(user, stream):
    h = requests.head(stream, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        logger("Error with music stream", level=1)
        bot.loop.create_task(user.send(f"There was an error with your request... Sorry'"))

    if 'html' in content_type.lower():
        logger("Error with music stream", level=1)
        bot.loop.create_task(user.send(f"There was an error with your request... Sorry'"))

    else:
        logger(f"Valid Video Stream for url: {stream}")
        bot.loop.create_task(user.send(f"""
URL: {stream}

1) Open the URL in your browser
2) Click on the 3 dot menu
3) Click on the Download button

Enjoy :)"""))


def get_direct_link(user, url, music, video, highest_res_possible):
    y = YouTube(url)

    if music == "True":
        music = True

    else:
        music = False

    if video == "True":
        video = True

    else:
        video = False

    if highest_res_possible == "True":
        highest_res_possible = True

    else:
        highest_res_possible = False

    if video or video and music:
        if highest_res_possible:
            resolutions = y.streams.order_by("resolution")
            x = resolutions[-1]

            stream = y.streams.filter(only_video=True, resolution=x.resolution).first().url
            logger(f"Got high quality stream for: {url}")
            verify_stream(user, stream)

        else:
            stream = y.streams.get_highest_resolution().url
            logger(f"Got usual quality stream for: {url}")
            verify_stream(user, stream)

    else:
        stream = y.streams.get_audio_only().url
        logger(msg="Got a music stream")
        verify_stream(user, stream)


def convert_m4a(filename):
    audio_stream = AudioFileClip(str(filename))
    audio_stream.write_audiofile(str(filename) + ".m4a", codec="aac")
    return str(filename) + ".m4a"


def clean_up(file1, file2):
    os.remove(file1)
    os.remove(file2)


@bot.tree.command()
@app_commands.describe(url="The URL of the YouTube Playlist")
async def playlist(interaction: Interaction, url : str):
    if android:
        await interaction.response.send_message(text)
        return

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


@bot.tree.command()
@app_commands.describe(url="The URL of the Video", music="If you want to convert it to music",
                               video="If it's supposed to be a video",
                               highest_resolution="If the video should be highest resolution (The video doesn't have sound then)")
@app_commands.choices(music=[
    app_commands.Choice(name="Yes", value="True"),
    app_commands.Choice(name="No", value="False"),
],
    video=[
        app_commands.Choice(name="Yes", value="True"),
        app_commands.Choice(name="No", value="False"),
    ],

    highest_resolution=[
        app_commands.Choice(name="Yes", value="True"),
        app_commands.Choice(name="No", value="False")])
async def direct_link(interaction: Interaction, url: str, music: str, video: str, highest_resolution: str):
    user = interaction.user
    await interaction.response.send_message("Processing your request...")

    try:
        t1 = threading.Thread(target=get_direct_link, args=(user, url, music, video, highest_resolution))
        t1.start()

    except Exception as e:
        logger(e, level=1)
        bot.loop.create_task(user.send_message(f"There was an error: {e} Sorry for the inconvenience!"))


@bot.tree.command(name="help", description="Sends a help message")
async def help(interaction: Interaction):
    user = interaction.user

    def send_help_english_thread():
        bot.loop.create_task(interaction.response.send_message("""

Commands:

/help - Shows this message
/download [url] - Downloads the video and sends it back as .m4a file
/playlist [url] - Downloads all videos in a playlist
/get_direct_link [url] [video] [music] [highest_resolution]  *
/credits - shows the sources / developing process

* returns you the direct download url of the video.
So you can download like a really big video. Just click on the link 
and the download should be started in your default browser :) 

"""))

    try:
        t = threading.Thread(target=send_help_english_thread)
        t.start()

    except Exception as e:
        logger(e, level=1)
        bot.loop.create_task(user.send_message(f"There was an error: {e} Sorry for the inconvenience!"))


@bot.tree.command(name="credits", description="Shows all sources.")
async def credits(interaction: Interaction):
    user = interaction.user

    def send_credits_english_thread():
        bot.loop.create_task(interaction.response.send_message("""

Vid Fetch is the Discord Bot of the Vid Fetch YouTube Downloader, which were
both created by EchterAlsFake in 2023. The Discord Bot itself is licensed under the 
GPLv3 license. The Source Code of this Bot can be found on:

<https://github.com/EchterAlsFake/VidFetch_Discord_Bot>

The URL of the Bot Picture is: <https://uxwing.com/black-and-white-youtube-icon/>
The Framework for the YouTube Downloader is: <https://github.com/pytube/pytube>

The bot is hosted on my own Laptop or by some random guys from the Internet.
Everyone can access the bot on my GitHub and host it on their own system.

I am not responsible for damages on your system caused by third party sources.

Have a great day :) 

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

Coded with Python 3.11 on Arch Linux
Compiled with Pyinstaller

Release: 1.6
28th of April 2024
"""))

    try:
        t = threading.Thread(target=send_credits_english_thread)
        t.start()

    except Exception as e:
        logger(e, level=1)
        bot.loop.create_task(user.send_message(f"There was an error: {e} Sorry for the inconvenience!"))


@bot.tree.command()
@app_commands.describe(url="The URL of the YouTube video")
async def video(interaction: Interaction, url: str):
    if android:
        await interaction.response.send_message(text)
        return

    await interaction.response.send_message(f"You request ({url}) was added to the queue. Please wait, it can take some time.")

    download_queue.put(url)
    try:
        t = threading.Thread(target=download, args=(interaction.user, ))
        t.start()

    except Exception as e:
        bot.loop.create_task(interaction.user.send_message(f"There was an unexpected error. Please report the following: {e}"))


@bot.event
async def on_ready():
    print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTYELLOW_EX + "Bot is ready!")
    try:
        await bot.tree.sync()
        print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTCYAN_EX + f"Synced Application Commands.")

    except Exception as e:
        print(e)


bot.run(get_api_key())

