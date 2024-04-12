from pyrogram import Client, filters

from Bot import AdminIDs, DatabaseID, Commands


@Client.on_message(~filters.command(Commands) & filters.private & filters.user(AdminIDs))
async def Generate(Bot, Msg):
    Process = await Msg.reply(text="...", quote=True)

    Copied = await Msg.copy(chat_id=DatabaseID, disable_notification=True)

    Encoded = Bot.URLSafe.Encode(f"id-{Copied.id * abs(DatabaseID)}")

    Generated = f"t.me/{Bot.Username}?start={Encoded}"
    Button = Bot.Button([[("Message", Copied.link, "url"), ("Share", f"t.me/share/url?url={Generated}", "url")]])

    await Process.edit(text=Generated, disable_web_page_preview=True, reply_markup=Button)

    Bot.Log.info(f"Generate by {Msg.from_user.id}: {Generated}")