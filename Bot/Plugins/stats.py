import os
import time

from pyrogram import Client, filters

from Bot import ListOfBotAdmins


@Client.on_message(filters.command("ping"))
async def Ping(_, Msg):
    ping_start_time = time.time()
    ping_message_process = await Msg.reply("...", quote=True)
    ping_time_results = time.time() - ping_start_time
    await ping_message_process.edit(f"Latency: {ping_time_results * 1000:.3f} ms")


@Client.on_message(filters.command("users") & filters.user(ListOfBotAdmins))
async def Users(Bot, Msg):
    users_message_process = await Msg.reply("...", quote=True)
    number_of_users = len(Bot.UserDB.AllUsers())
    await users_message_process.edit(f"{number_of_users} users")


@Client.on_message(filters.command("log") & filters.user(ListOfBotAdmins))
async def Log(_, Msg):
    if os.path.exists("log.txt"):
        await Msg.reply_document("log.txt", quote=True)
        os.remove("log.txt")
    else:
        await Msg.reply("Currently no logs exist.", quote=True)