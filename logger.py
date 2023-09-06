"""
Copyright (C) 2023  EchterAlsFake | Johannes Habel
Full copyright information can be found in the 'Vid_Fetch_Discord_Bot.py' file
"""

from colorama import *
from datetime import datetime

def logger(msg, level=0):

    with open("log.log", "a") as file:
        date = datetime.now()

        if level == 0:
            print(f":: {date}{Fore.LIGHTWHITE_EX} :: {Fore.LIGHTCYAN_EX}DEBUG{Fore.LIGHTCYAN_EX} :: {msg} :: ")
            file.write(f":: {date} :: DEBUG :: {msg} :: \n")

        elif level == 1:
            print(f":: {date}{Fore.LIGHTCYAN_EX} :: {Fore.LIGHTRED_EX}ERROR{Fore.LIGHTCYAN_EX} :: {msg} :: ")
            file.write(f":: {date} :: ERROR :: {msg} :: \n")