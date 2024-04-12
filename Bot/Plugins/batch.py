from pyrogram import Client, filters

from pyromod.helpers import ikb

from Bot import ListOfBotAdmins, DatabaseChannelID


@Client.on_message(filters.command("batch") & filters.private & filters.user(ListOfBotAdmins))
async def Batch(Bot, Msg):
    InvalidBatchMessage= "The message is invalid or the message being forwarded is not from the DATABASE_CHANNEL."

    initial_message = await Bot.ask(chat_id=Msg.chat.id, text="**Initial Message:** Forward message from DATABASE_CHANNEL.", user_id=Msg.from_user.id)
    if initial_message.forward_from_chat and initial_message.forward_from_chat.id == DatabaseChannelID:
        initial_message_id = initial_message.forward_from_message_id
    else:
        await initial_message.reply(InvalidMessage, quote=True)
        return

    while True:
        last_message = await Bot.ask(chat_id=Msg.chat.id, text="**Last Message:** Forward message from DATABASE_CHANNEL.", user_id=Msg.from_user.id)
        if last_message.forward_from_chat and last_message.forward_from_chat.id == DatabaseChannelID:
            last_message_id = last_message.forward_from_message_id
            break
        else:
            await last_message.reply(InvalidMessage, quote=True)
            return

    encoded_data = Bot.URLSafe.Encode(f"id-{initial_message_id * abs(DatabaseChannelID)}-{last_message_id * abs(DatabaseChannelID)}")

    generated_link = f"t.me/{Bot.me.username}?start={encoded_data}"
    reply_markup = ikb([[("Share", f"t.me/share/url?url={generated_link}", "url")]])

    await last_message.reply(generated_link, reply_markup=reply_markup, quote=True, disable_web_page_preview=True)
