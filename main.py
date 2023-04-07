import threading
from pytube import YouTube, Playlist
from colorama import *
import discord
from discord.ext import commands
import dotenv
import os
import datetime
import queue

"""

Please note, that this is a personal project for my free time. It's not production ready
and not meant for the public! If you really want to use this Bot, then please copy and paste all of
my Code into your own Application and run the code on your local computer. 
Replace the client_secret with your own client secret ID and everything is fine. 


This Bot was created on 6th of April in 2023 by EchterAlsFake.
This project is licensed under the Creative Commons license. 

You are free to use all of my stuff, but you MUST provide the source to this project which is:

https://github.com/EchterAlsFake/VidFetch_Discord_Bot

Thanks :)

"""


class Setup():

    def __init__(self):
        print(Fore.LIGHTGREEN_EX + "[+]" + "Setup Initialization...")
        self.configure()

    def configure(self):
        dotenv.load_dotenv()



Setup()

client_secret = os.getenv("TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)




def error(e):

    with open("log.log", "a") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{e}\n")
        f.close()

@bot.event
async def on_ready():
    print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTYELLOW_EX + "Bot is ready!")

    try:
        await bot.tree.sync()
        print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTCYAN_EX + f"Synced Application Commands.")

    except Exception as e:
        error(e)

download_queue = queue.Queue()
num_threads = 12
semaphore = threading.Semaphore(num_threads)


@bot.tree.command(name="download", description="Downloads a YouTube Video and sends it back as .m4a")
async def hello(interaction: discord.Interaction, url : str):
    await interaction.response.send_message("Proceeding your request...")
    user = interaction.user
    download_queue.put(url)

    def download(user):
        while True:
            try:
                url = download_queue.get(block=False)

            except queue.Empty:
                print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTYELLOW_EX + f"Queue is empty.  Sleeping for 5 seconds.")
                break

            with semaphore:
                try:
                    y = YouTube(url)

                    print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTMAGENTA_EX + f"Got download request / {url}")

                except Exception as e:
                    error(e)
                    bot.loop.create_task(user.send("Invalid URL.  If you are sure, that this URL is correct, please refer to the GitHub page, as there are listed some possible other issues."))
                    bot.loop.create_task(user.send(f"Exception for debugging: {e}"))


                try:

                    print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTWHITE_EX + f"Processing: {url}")

                    y = YouTube(url)
                    title = y.title
                    audio_stream = y.streams.get_audio_only()
                    disallowed_symbols = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]

                    for disallowed_symbol in disallowed_symbols:
                        title = title.replace(disallowed_symbol, "")


                    if title == "passwd" or title == "etc":
                        print(title)
                        print(Fore.LIGHTRED_EX + f"Someone probably tried to break into the system.  USER: {interaction.user}")

                    else:
                        print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTYELLOW_EX + f"Downloading: {title}")
                        audio_stream.download(filename=f"{title}.m4a")
                        print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTYELLOW_EX + f"Downloaded: {title}.m4a")
                        print(Fore.LIGHTGREEN_EX + "[+]" + Fore.LIGHTMAGENTA_EX + f"Sending to: {interaction.user}...")
                        bot.loop.create_task(user.send(file=discord.File(f"{title}.m4a")))

                except Exception as e:
                    error(e)
                    bot.loop.create_task(user.send(f"Something went wrong.  Here is the error: {e}"))

    t = threading.Thread(target=download, args=(user,))
    t.start()



@bot.tree.command(name="help", description="Shows a simple tutorial message.")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message("""

Commands:

/help - Shows this message
/download [url] - Downloads the video and sends it back as .m4a file
/credits - shows the sources / developing process

""")

@bot.tree.command(name="credits", description="Shows all sources.")
async def credits(interaction: discord.Interaction):
    await interaction.response.send_message("""

Vid Fetch is the Discord Bot of the Vid Fetch YouTube Downloader, which were
both created by EchterAlsFake in 2023. The Discord Bot itself is licensed under the 
Creative Commons license. The Source Code of this Bot can be found on:

https://github.com/EchterAlsFake/VidFetch_Discord_Bot

The URL of the Bot Picture is: https://uxwing.com/black-and-white-youtube-icon/
The Framework for the YouTube Downloads is: https://github.com/pytube/pytube

The Bot is hosted on: game.techstar.live

I can not guarantee for 24/7 Support or functionality!


Have a great day :) 
""")

bot.run(client_secret)
