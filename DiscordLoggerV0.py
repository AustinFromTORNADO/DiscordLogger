import discord
from discord.ext import commands
import os
import threading
import asyncio
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


def load_token():
    token_filepath = r'resources\token.txt'
    if os.path.exists(token_filepath):
        with open(token_filepath, 'r', encoding='utf-8') as token_file:
            return token_file.read().strip()
    return None


def load_channel_id(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as channel_id_file:
            return int(channel_id_file.read().strip())
    return None


def load_path_proc_log(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as path_proc_log_file:
            return path_proc_log_file.read().strip()
    return None


def check_files():
    required_files = [r'resources\Access_List_Member.txt', 'resources\channel_id.txt', 'resources\id_proc_channel.txt', 'resources\path_proc_log.txt']
    for file_path in required_files:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as new_file:
                new_file.write('')
                print(f'Создан файл: {file_path}')


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


async def send_log_to_channel(bot, channel_id, filename):
    channel = bot.get_channel(channel_id)
    if channel is None:
        print(f"Не удалось найти канал с ID {channel_id}. Убедитесь, что бот имеет доступ к этому каналу.")
        return

    message = None

    while True:
        await asyncio.sleep(5)  # Регулируйте интервал отправки сообщений
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if content:
                    if message is None:
                        message = await channel.send(content)
                    else:
                        await message.edit(content=content)
        except Exception as e:
            print(f"Произошла ошибка при отправке лога в канал: {e}")


if __name__ == "__main__":
    check_files()
    TOKEN = load_token()

    if TOKEN is None:
        TOKEN = get_token()

    CHANNEL_ID = load_channel_id('resources\channel_id.txt')
    ID_PROC_CHANNEL = load_channel_id('resources\id_proc_channel.txt')
    PATH_PROC_LOG = load_path_proc_log('resources\path_proc_log.txt')

    if CHANNEL_ID is None:
        print("Не удалось загрузить ID канала. Убедитесь, что файл channel_id.txt содержит корректное значение.")
        os._exit(1)

    if ID_PROC_CHANNEL is None:
        print("Не удалось загрузить ID канала для отправки лога. Убедитесь, что файл id_proc_channel.txt содержит корректное значение.")
        os._exit(1)

    if PATH_PROC_LOG is None:
        print("Не удалось загрузить путь к файлу лога. Убедитесь, что файл path_proc_log.txt содержит корректное значение.")
        os._exit(1)

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guild_messages = True

    client = commands.Bot(command_prefix='!', intents=intents)

    filename = 'last_message.txt'
    proc_log_filename = PATH_PROC_LOG

    tray_icon_thread = threading.Thread(target=run_tray_icon, args=(create_tray_icon(),))
    tray_icon_thread.start()

    @client.event
    async def on_ready():
        print(f'Бот {client.user.name} подключен к Discord!')
        bot_loop = asyncio.get_event_loop()
        bot_loop.create_task(send_log_to_channel(client, ID_PROC_CHANNEL, proc_log_filename))

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        allowed_nicks = load_allowed_nicks()

        if message.author.name not in allowed_nicks:
            print(f'Ignoring message from {message.author.name} as it is not in the allowed list.')
            return

        # Проверка, что сообщение пришло из нужного канала
        if message.channel.id == CHANNEL_ID:
            if isinstance(message.channel, discord.DMChannel):
                await message.channel.send("Команда принята!")

            with open(filename, 'w', encoding='utf-8') as file:
                file.write(f'{message.author.name}: {message.content}')

    bot_thread = threading.Thread(target=client.run, args=(TOKEN,))
    bot_thread.start()

    bot_thread.join()
