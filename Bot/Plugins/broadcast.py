import os
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

from Bot import AdminIDs, Protect

Running, Succeeded, Failed, Total = False, 0, 0, 0
Nothing = "No broadcast is running."


@Client.on_message(filters.command("broadcast") & filters.user(AdminIDs))
async def Broadcast(Bot, Msg):
    AdminID = Msg.from_user.id

    global Running, Succeeded, Failed, Total

    Processing = "Broadcast is running, wait until the task is finished.\n\n<b>/status:</b> Show broadcast status."

    if not (Message := Msg.reply_to_message):
        await Msg.reply(text="Please reply to a message you want to broadcast.", quote=True)
        return
    else:
        if not Running:
            Running, Succeeded, Failed, Total = True, 0, 0, 0
        else:
            await Msg.reply(text=Processing, quote=True)
            return

    Process = await Msg.reply(text="Sending...", quote=True)

    with open(".BroadcastID", "w") as BroadcastID:
        BroadcastID.write(f"{Msg.chat.id}\n{Process.id}")

    UserIDs = Bot.UserDB.Users()
    Total = len(UserIDs)

    Bot.Log.info(f"Broadcast: Started by {AdminID}")

    for UserID in UserIDs:
        if not Running:
            break

        if UserID not in AdminIDs:
            try:
                await Message.copy(chat_id=UserID, protect_content=Protect)
                Succeeded += 1
            except FloodWait as e:
                Bot.Log.warning(f"FloodWait: Sleep {e.value}s")
                await asyncio.sleep(e.value + 5)
            except RPCError:
                Bot.UserDB.Delete(UserID)
                Failed += 1

            if (Succeeded + Failed) % 25 == 0:
                await Process.edit(text=f"<b>Broadcast Running</b>\n - Sent: {Succeeded}/{Total}\n - Failed: {Failed}\n\n<b>/cancel:</b> Cancel the process.")

    if not Running:
        await Msg.reply(text=f"<b>Broadcast Aborted</b>\n - Sent: {Succeeded}/{Total}\n - Failed: {Failed}", quote=True)
        Bot.Log.warning(f"Broadcast: Aborted (Sent: {Succeeded}/{Total} - Failed: {Failed}) by {AdminID}")
    else:
        await Msg.reply(text=f"<b>Broadcast Finished</b>\n - Succeeded: {Succeeded}\n - Failed: {Failed}", quote=True)
        Bot.Log.info(f"Broadcast: Finished (Sent: {Succeeded} - Failed: {Failed}) by {AdminID}")

    await Process.delete(revoke=True)

    os.remove(".BroadcastID")

    Running, Succeeded, Failed, Total = False, 0, 0, 0


@Client.on_message(filters.command("status") & filters.user(AdminIDs))
async def Status(_, Msg):
    global Running, Succeeded, Failed, Total

    if not Running:
        await Msg.reply(text=Nothing, quote=True)
    else:
        await Msg.reply(text=f"<b>Broadcast Status</b>\n - Sent: {Succeeded}/{Total}\n - Failed: {Failed}", quote=True)


@Client.on_message(filters.command("cancel") & filters.user(AdminIDs))
async def Cancel(_, Msg):
    global Running

    if not Running:
        await Msg.reply(text=Nothing, quote=True)
        return
    else:
        await Msg.reply(text="Broadcast has been aborted.", quote=True)
        Running = False