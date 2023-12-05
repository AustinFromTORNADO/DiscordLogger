import discord
from discord.ext import commands
import os
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image
import tkinter as tk
from tkinter import simpledialog, ttk
from ttkthemes import ThemedTk


def get_token():
    root = ThemedTk(theme="equilux")  
    root.withdraw() 

    
    icon_path = r"resources\tornado_38041.png" 
    root.iconphoto(True, tk.PhotoImage(file=icon_path))

    
    style = ttk.Style()
    style.configure("TLabel", foreground="white", background="black")
    style.configure("TEntry", fieldbackground="black", foreground="white")

    
    token = simpledialog.askstring("Ввод токена", "Введите TOKEN вашего бота Discord:")

    
    root.destroy()

    with open(r'resources\token.txt', 'w', encoding='utf-8') as token_file:
        token_file.write(token)
    return token


def check_files():
    required_files = [r'resources\Access_List_Member.txt', 'last_message.txt']
    for file_path in required_files:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as new_file:
                new_file.write('')
                print(f'Создан файл: {file_path}')


def load_token():
    token_filepath = r'resources\token.txt'
    if os.path.exists(token_filepath):
        with open(token_filepath, 'r', encoding='utf-8') as token_file:
            return token_file.read().strip()
    return None


def load_allowed_nicks():
    access_list_filename = r'resources\Access_List_Member.txt'
    with open(access_list_filename, 'r', encoding='utf-8') as access_file:
        return [line.strip() for line in access_file.readlines()]


def on_exit(icon, item):
    icon.stop()
    os._exit(0)


def create_tray_icon():
    image = Image.open(r"resources\tornado_38041.ico")  
    menu = Menu(MenuItem('Завершить программу', on_exit))
    icon = Icon("DiscordLogger", image, "LoggerDiscord", menu)
    return icon


def run_tray_icon(icon):
    icon.run()

if __name__ == "__main__":
    check_files()
    TOKEN = load_token()

    if TOKEN is None:
        TOKEN = get_token()

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guild_messages = True

    client = commands.Bot(command_prefix='!', intents=intents)

    filename = 'last_message.txt'

    
    tray_icon_thread = threading.Thread(target=run_tray_icon, args=(create_tray_icon(),))
    tray_icon_thread.start()

    @client.event
    async def on_ready():
        print(f'Бот {client.user.name} подключен к Discord!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        allowed_nicks = load_allowed_nicks()

        if message.author.name not in allowed_nicks:
            print(f'Ignoring message from {message.author.name} as it is not in the allowed list.')
            return

        if isinstance(message.channel, discord.DMChannel):
            await message.channel.send("Команда принята!")

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f'{message.author.name}: {message.content}')

    
    bot_thread = threading.Thread(target=client.run, args=(TOKEN,))
    bot_thread.start()

    
    bot_thread.join()
