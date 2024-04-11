from pyrogram import Client, filters

from pyromod.helpers import ikb

from Bot import ListOfBotAdmins, DatabaseChannelID, ListOfBotCommands


@Client.on_message(~filters.command(ListOfBotCommands) & filters.private & filters.user(ListOfBotAdmins))
async def Generate(Bot, Msg):
    copied_message = await Msg.copy(chat_id=DatabaseChannelID, disable_notification=True)

    encoded_data = Bot.URLSafe.Encode(f"id-{copied_message.id * abs(DatabaseChannelID)}")

    generated_link = f"t.me/{Bot.me.username}?start={encoded_data}"
    reply_markup = ikb([[("Share", f"t.me/share/url?url={generated_link}", "url")]])

    await Msg.reply(generated_link, reply_markup=reply_markup, quote=True, disable_web_page_preview=True)