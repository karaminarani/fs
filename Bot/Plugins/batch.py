from pyrogram import Client, filters

from Bot import AdminIDs, DatabaseID


@Client.on_message(filters.command("batch") & filters.private & filters.user(AdminIDs))
async def Batch(Bot, Msg):
    AdminID = Msg.from_user.id

    Invalid= "The message is invalid or the message being forwarded is not from the database."

    Initial = await Bot.ask(chat_id=Msg.chat.id, text="<b>Initial:</b> Forward message from database.", user_id=AdminID)
    if Initial.forward_from_chat and Initial.forward_from_chat.id == DatabaseID:
        InitialID = Initial.forward_from_message_id
        InitialCID = str(abs(Initial.forward_from_chat.id))[3:]
        InitialLink = f"t.me/c/{int(InitialCID)}/{InitialID}"
    else:
        await Initial.reply(text=Invalid, quote=True)
        return

    while True:
        Last = await Bot.ask(chat_id=Msg.chat.id, text="<b>Last:</b> Forward message from database.", user_id=AdminID)
        if Last.forward_from_chat and Last.forward_from_chat.id == DatabaseID:
            LastID = Last.forward_from_message_id
            LastCID = str(abs(Last.forward_from_chat.id))[3:]
            LastLink = f"t.me/c/{int(LastCID)}/{LastID}"
            break
        else:
            await Last.reply(text=Invalid, quote=True)
            return

    Encoded = Bot.URLSafe.Encode(f"id-{InitialID * abs(DatabaseID)}-{LastID * abs(DatabaseID)}")

    Generated = f"t.me/{Bot.Username}?start={Encoded}"
    Button = Bot.Button([[("Initial", InitialLink, "url"), ("Last", LastLink, "url")], [("Share", f"t.me/share/url?url={Generated}", "url")]])

    await Last.reply(text=Generated, quote=True, disable_web_page_preview=True, reply_markup=Button)

    Bot.Log.info(f"Batch by {AdminID}: {Generated}")