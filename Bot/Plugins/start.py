import subprocess
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

from Bot import AdminIDs, DatabaseID, FSubIDs, Protect


@Client.on_message(filters.command("start"))
async def Start(Bot, Msg):
    UserID = Msg.from_user.id

    Greeting = "<b>The bot is up and running. These bots can store messages in custom channels, and users access them through the bot.</b>"
    Must = "<b>\n\nTo view messages shared by bots. Join first, then press the Try Again button.</b>" 

    Bot.UserDB.Insert(UserID)

    Button = Buttons(Bot, Msg)
    if len(Msg.command) > 1:
        if not await Subscriber(Bot, Msg):
            await Msg.reply(text=Greeting + Must, reply_markup=Button, quote=True)
        else:
            Process = await Msg.reply(text="...")
            MessageIDs = []
            Decoded = Bot.URLSafe.Decode(Msg.command[1]).split("-")
            if len(Decoded) == 3:
                Start, End = int(int(Decoded[1]) / abs(DatabaseID)), int(int(Decoded[2]) / abs(DatabaseID))
                MessageIDs = range(Start, End + 1) if Start <= End else range(Start, End - 1, -1)
            elif len(Decoded) == 2:
                MessageIDs.append(int(int(Decoded[1]) / abs(DatabaseID)))

            for Message in await Bot.get_messages(chat_id=DatabaseID, message_ids=MessageIDs):
                try:
                    await Message.copy(chat_id=UserID, protect_content=Protect)
                except FloodWait as e:
                    Bot.Log.warning(e)
                    Bot.Log.info(f"Sleep: {e.value}s")
                    await asyncio.sleep(e.value + 5)
                except RPCError:
                    pass

            await Process.delete(revoke=True)

        return
    else:
        await Msg.reply(text=Greeting, quote=True, reply_markup=Button)


@Client.on_message(filters.command("restart") & filters.user(AdminIDs))
async def Restart(Bot, Msg):
    Bot.Log.info(f"Restart by {Msg.from_user.id}")

    Process = await Msg.reply(text="Restarting...", quote=True)

    with open(".RestartID", "w") as RestartID:
        RestartID.write(f"{Msg.chat.id}\n{Process.id}")

    subprocess.run(["python", "-m", "Bot"])


def Buttons(Bot, Msg):
    if FSubIDs:
        Dynamic = []
        Rows = []
        for key, chat_id in enumerate(FSubIDs):
            Rows.append((f"Join {key + 1}", getattr(Bot, f"FSub{key}"), "url"))

            if len(Rows) == 3:
                Dynamic.append(Rows)
                Rows = []

        if Rows:
            Dynamic.append(Rows)

        try:
            Dynamic.append([("Try Again", f"t.me/{Bot.Username}?start={Msg.command[1]}", "url")])
        except Exception:
            pass

        return Bot.Button(Dynamic)


async def Subscriber(Bot, Msg):
    UserID = Msg.from_user.id
    if UserID in AdminIDs:
        return True
    for key, chat_id in enumerate(FSubIDs):
        try:
            await Bot.get_chat_member(chat_id=chat_id, user_id=UserID)
        except RPCError:
            return False

    return True