import threading
import time
from pytube import YouTube, Playlist
from colorama import *
import discord
from discord.ext import commands
import dotenv
import os
import queue
from moviepy.editor import AudioFileClip
import requests
import random
from tqdm import tqdm
import logging


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
    Info: I can not send files, which exceed 8 Megabytes. 

https://github.com/EchterAlsFake/VidFetch_Discord_Bot

Thanks :)

"""

languages = """
de - German
en - English
es - Spanish
fr - French
zh - Chinese
hi - Hindi
ar - Arabic
jp - Japanese
ru - Russian
pt - Portuguese
"""
language_interaction_response = f"""
Sorry the selected language is not available yet.

Please use one of the following languages:

{languages}"""
release = "1.3"

class Logger():

    def error(self, msg):
        logger = logging.getLogger("discord")
        logging.basicConfig(filename="log.log")
        logger.setLevel(logging.ERROR)
        logger.error(msg)

    def debug(self, msg):
        logger = logging.getLogger("discord")
        logging.basicConfig(filename="log.log")
        logger.setLevel(logging.DEBUG)
        logger.debug(msg)


class Setup():

    def __init__(self):
        print(Fore.LIGHTGREEN_EX + "[+]" + "Setup Initialization...")
        self.configure()

    def configure(self):
        dotenv.load_dotenv()

Setup()

client_secret = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
download_queue = queue.Queue()
num_threads = 12
semaphore = threading.Semaphore(num_threads)

def download_playlist(fast_download, user, url):

    try:
        p = Playlist(url)

    except Exception as e:
        Logger().error(e)

    p = Playlist(url)
    # Enumerating videos

    for video in p.video_urls:
        download_queue.put(video)
        t1 = threading.Thread(target=download, args=(fast_download, user))
        t1.start()

def download(fast_download, user):
    while True:
        try:
            url = download_queue.get(block=False)

        except queue.Empty:
            print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTYELLOW_EX + f"Queue is empty.")
            break

        with semaphore:
            try:
                y = YouTube(url)
                title = y.title
                print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTCYAN_EX + f"Download request: {title}")
                disallowed_symbols = ["/", ":", "*", "?", "<", ">", "|", "\\"]

                for disallowed_symbol in disallowed_symbols:
                    title = title.replace(disallowed_symbol, "")


                audio_stream = y.streams.filter(only_audio=True).order_by("abr").last()
                download_url = audio_stream.url
                size = audio_stream.filesize

                if fast_download == "Yes" or "yes":
                    fast_download = True

                elif fast_download == "No" or "no":
                    fast_download = False

                if fast_download == False:

                    print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTMAGENTA_EX + "Fast Download: No")
                    download_with_progressbar(url=download_url, filename=title, total_size=size)
                    bot.loop.create_task(user.send(file=discord.File(str(location))))
                    print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTCYAN_EX + f"Finished request: {title}")
                    time.sleep(5)
                    clean_up(file1=str(title), file2=str(location))

                elif fast_download == True:

                    print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTRED_EX + "Fast Download: Yes")
                    audio_stream.download(filename=str(title))
                    location = convert_m4a(filename=str(title))
                    bot.loop.create_task(user.send(file=discord.File(str(location))))
                    print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTCYAN_EX + f"Finished request: {title}")
                    time.sleep(5)
                    clean_up(file1=str(title), file2=str(location))

            except Exception as e:
                Logger().error(e)

def download_with_progressbar(url, filename, total_size):
    response = requests.get(url, stream=True)
    block_size = 8192
    colors = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    color = random.choice(colors)
    with open(filename, "wb") as f:
        with tqdm(total=total_size, unit="B", unit_scale=True, colour=color) as progress:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    progress.update(len(chunk))

    convert_m4a(filename)

def convert_m4a(filename):

    try:
        audio_stream = AudioFileClip(str(filename))
        audio_stream.write_audiofile(str(filename) + ".m4a", codec="aac")
        location = str(filename) + ".m4a"
        return location

    except Exception as e:
        Logger().error(e)

def clean_up(file1, file2):

    try:
        os.remove(file1)
        os.remove(file2)

    except Exception as e:
        Logger().error(e)

@bot.tree.command(name="download", description="Please set Fast Download to False. It helps my CPU, thanks.)")
async def video(interaction: discord.Interaction, url : str, fast_download : bool = True, language : str = "en"):

    if fast_download:
        fast_download_msg = "✔"

    elif fast_download == False:
        fast_download = "✖"

    else:
        fast_download_msg = "?"

    if language == "":
        pass


    else:
        await interaction.response.send_message(language_interaction_response)

    if language == "en":

        await interaction.response.send_message(f"""
The download / upload will take 1-3 minutes. 
You will get a message in your DMs with the .m4a file.
""")

    elif language == "de":
        await interaction.response.send_message(f"""
Downloading: {url}

Das Herunterladen und Hochladen wird ca. 1-3 Minuten dauern.
Schau in deinen DMs nach der .m4a Datei.

Schneller Download: {fast_download_msg}""")

    user = interaction.user
    download_queue.put(url)

    try:
        t = threading.Thread(target=download, args=(fast_download, user, ))
        t.start()
    except Exception as e:
        bot.loop.create_task(user.send(f"ERROR: {e}"))

@bot.tree.command(name="playlist", description="Downloads all videos in a playlist.  See /help for more info")
async def playlist(interaction: discord.Interaction, url : str, fast_download : bool = True, language : str = "en"):

    if fast_download:
        fast_download_msg = "✔"

    elif fast_download == False:
        fast_download_msg = "✖"

    else:
        fast_download_msg = "?"

    if language == "en" or language == "de":
        pass

    else:
        await interaction.response.send_message(f"""
Sorry, {language} is not available.

1) de - German / Deutsch
2) en - English / English  (default)


""")

    if language == "en":
        await interaction.response.send_message(f"""
The following playlist will be downloaded: {url}
Check your DMs for more information.

Fast Download: {fast_download_msg}""")

    elif language == "de":
        await interaction.response.send_message(f"""
Die folgende Playlist wird herunterladen: {url}
Schau in deinen DMs für mehr Informationen.

Schneller Download: {fast_download_msg}
""")

    user = interaction.user

    try:

        t1 = threading.Thread(target=download_playlist, args=(fast_download, user, url,))
        t1.start()

    except Exception as e:
        print(e)

@bot.tree.command(name="help", description="Shows a simple tutorial message.")
async def help(interaction: discord.Interaction, language : str = "en"):
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

    def send_help_german_thread():
        bot.loop.create_task(interaction.response.send_message("""

Befehle:

/help - Zeigt diese Nachricht an
/download [url] - Lädt ein Video herunter und sendet es dir als .m4a Datei.
/credits - Zeigt die Quellen und ein paar Entwickler Informationen.

Optional:

/download [fast_download] - True:  Lädt das Video sehr schnell herunter.
                            False: Braucht länger (2-3 Minuten), aber spart mir
                            ein wenig CPU Leistung. Wenn du etwas Zeit hast, würde ich
                            dich darum bitten, die Option auf False zu setzen. Danke :) 
Fehlermeldungen:

Fehlermeldungen werdem zu dem Nutzer gesendet. Du kannst sie auf GitHub melden, dann kann ich sie
beheben. Danke :) 
        """))

    if language == "en" or language == "de":
        pass

    else:
        await interaction.response.send_message(f"""
Sorry {language} is not available.

1) de - German / Deutsch
2) en - English / Englisch (default)

""")

    if language == "en":

        try:
            t = threading.Thread(target=send_help_english_thread)
            t.start()
        except Exception as e:
            Logger().error(e)

    elif language == "de":

        try:
            t = threading.Thread(target=send_help_german_thread)
            t.start()

        except Exception as e:
            Logger().error(e)

@bot.tree.command(name="credits", description="Shows all sources.")
async def credits(interaction: discord.Interaction, language : str = "en"):

    user = interaction.user
    def send_credits_english_thread():
        bot.loop.create_task(interaction.response.send_message("""

Vid Fetch is the Discord Bot of the Vid Fetch YouTube Downloader, which were
both created by EchterAlsFake in 2023. The Discord Bot itself is licensed under the 
Creative Commons license. The Source Code of this Bot can be found on:

https://github.com/EchterAlsFake/VidFetch_Discord_Bot

The URL of the Bot Picture is: https://uxwing.com/black-and-white-youtube-icon/
The Framework for the YouTube Downloader is: https://github.com/pytube/pytube

The Bot is hosted on my OWN Laptop with LIMITED resources.

!!! I can not guarantee for 24/7 Support or functionality !!! 


Have a great day :) 

[Donation link (Only if you want)  paypal.me/EchterAlsFake]


For developers:

All libraries used by this:

threading - built-in
time      - built-in
pytube    - github.com/pytube/pytube
colorama  - github.com/tartley/colorama
discord   - github.com/Rapptz/discord.py
dotenv    - github.com/theskumar/python-dotenv
os        - built-in
queue     - built-in
moviepy   - github.com/Zulko/moviepy
requests  - github.com/psf/requests
random    - built-in
tqdm      - github.com/tqdm/tqdm

Coded with Python 3.9 - 3.11.3

Release: 1.3
6th of May 2023 - Signed by EchterAlsFake
"""))

    def send_credits_german_thread():
        bot.loop.create_task(interaction.response.send_message("""

Vid Fetch ist der Discord Bot vom Vid Fetch YouTube Downloader, welche beide von 
EchterAlsFake in 2023 erstellt wurden. Der Bot ist mit der Creative Commons-Lizenz versehen.
Der Quellcode kann auf der folgenden Website eingesehen werden:

https://github.com/EchterAlsFake/VidFetch_Discord_Bot

Die URL des Bildes: https://uxwing.com/black-and-white-youtube-icon/
Das Framework zum herunterladen der Videos: https://github.com/pytube/pytube

Der Bot läuft auf meinem eigenen Laptop mit meinem Internet.
!!! Ich kann für keine Stabilität oder Sicherheit gerantieren !!! 


Spendenlink (Nur wenn du möchtest) paypal.me/EchterAlsFake]

Für Entwickler:

Alle benutzten Bibliotheken:

threading - built-in
time      - built-in
pytube    - github.com/pytube/pytube
colorama  - github.com/tartley/colorama
discord   - github.com/Rapptz/discord.py
dotenv    - github.com/theskumar/python-dotenv
os        - built-in
queue     - built-in
moviepy   - github.com/Zulko/moviepy
requests  - github.com/psf/requests
random    - built-in
tqdm      - github.com/tqdm/tqdm

Programmiert mit Python 3.9 - 3.11.3

Release: 1.3
06.05.2023 - Signed by EchterAlsFake"""))

    if language == "en" or language == "de":
        pass

    else:
        await interaction.response.send_message(f"""
Sorry {language} is not available.

1) de - German / Deutsch
2) en - English / Englisch (default)


""")

        try:
            t = threading.Thread(target=send_credits_english_thread)
            t.start()

        except Exception as e:
            Logger().error(e)

    if language == "de":

        try:
            t = threading.Thread(target=send_credits_german_thread)
            t.start()

        except Exception as e:
            Logger().error(e)

    elif language == "en":

        try:
            t = threading.Thread(target=send_credits_english_thread)
            t.start()

        except Exception as e:
            Logger().error(e)


@bot.event
async def on_ready():
    print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTYELLOW_EX + "Bot is ready!")

    try:
        await bot.tree.sync()
        print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTCYAN_EX + f"Synced Application Commands.")

    except Exception as e:
        Logger().error(e)



bot.run(client_secret)

