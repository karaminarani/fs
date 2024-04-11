import subprocess
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

from pyromod.helpers import ikb

from Bot import ListOfBotAdmins, DatabaseChannelID, MustJoinID, ProtectContent


@Client.on_message(filters.command("start"))
async def Start(Bot, Msg):
    BotStartMessage = "**The bot is up and running. These bots can store messages in custom channels, and users access them through the bot.**"
    MustJoinMessage = "**\n\nTo view messages shared by bots. Join first, then press the Try Again button.**" 

    Bot.UserDB.Insert(Msg.from_user.id)

    reply_markup = Buttons(Bot, Msg)
    if len(Msg.command) > 1:
        if not await Subscriber(Bot, Msg):
            await Msg.reply(BotStartMessage + MustJoinMessage, reply_markup=reply_markup, quote=True)
        else:
            message_ids = []
            command_data = Bot.URLSafe.Decode(Msg.command[1]).split("-")
            if len(command_data) == 3:
                start, end = int(int(command_data[1]) / abs(DatabaseChannelID)), int(int(command_data[2]) / abs(DatabaseChannelID))
                message_ids = range(start, end + 1) if start <= end else range(start, end - 1, -1)
            elif len(command_data) == 2:
                message_ids.append(int(int(command_data[1]) / abs(DatabaseChannelID)))

            for msg in await Bot.get_messages(DatabaseChannelID, message_ids):
                try:
                    await msg.copy(chat_id=Msg.from_user.id, protect_content=ProtectContent)
                except FloodWait as e:
                    Bot.Logger.warning(f"START: {e}")
                    await asyncio.sleep(e.value)
                    continue
        return
    else:
        await Msg.reply(BotStartMessage, reply_markup=reply_markup, quote=True)


@Client.on_message(filters.command("restart") & filters.user(ListOfBotAdmins))
async def Restart(Bot, Msg):
    restart_message_process = await Msg.reply("Restarting...", quote=True)

    with open("restart_id.txt", "w") as restart_id:
        restart_id.write(f"{Msg.chat.id}\n{restart_message_process.id}")

    subprocess.run(["python", "-m", "bot"])


def Buttons(Bot, Msg):
    if MustJoinID:
        dynamic_buttons = []
        button_rows = []
        for key in MustJoinID.keys():
            button_rows.append((f"Join {key}", getattr(Bot, f"MustJoinID{key}"), "url"))

            if len(button_rows) == 3:
                dynamic_buttons.append(button_rows)
                button_rows = []

        if button_rows:
            dynamic_buttons.append(button_rows)

        try:
            dynamic_buttons.append([("Try Again", f"t.me/{Bot.me.username}?start={Msg.command[1]}", "url")])
        except Exception:
            pass

        return ikb(dynamic_buttons)


async def Subscriber(Bot, Msg):
    user_id = Msg.from_user.id
    if user_id in ListOfBotAdmins:
        return True

    for key, chat_id in MustJoinID.items():
        try: 
            await Bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        except RPCError:
            return False

    return True