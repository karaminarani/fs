import time

from pyrogram import Client, filters

from Bot import AdminIDs


@Client.on_message(filters.command("ping"))
async def Ping(_, Msg):
    Start = time.time()
    Process = await Msg.reply(text="...", quote=True)
    Result = time.time() - Start
    await Process.edit(text=f"Latency: {Result * 1000:.3f} ms")


@Client.on_message(filters.command("users") & filters.user(AdminIDs))
async def Users(Bot, Msg):
    Process = await Msg.reply(text="...", quote=True)
    await Process.edit(text=f"{len(Bot.UserDB.Users())} users")


@Client.on_message(filters.command("log") & filters.user(AdminIDs))
async def Log(_, Msg):
    Process = await Msg.reply(text="...", quote=True)
    await Msg.reply_document(document="log.txt", quote=True)
    await Process.delete(revoke=True)