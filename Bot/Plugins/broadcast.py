import os
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

from Bot import AdminIDs, Protect

Running, Succeeded, Failed, Total = False, 0, 0, 0


@Client.on_message(filters.command("broadcast") & filters.user(AdminIDs))
async def Broadcast(Bot, Msg):
    AdminID = Msg.from_user.id

    global Running, Succeeded, Failed, Total

    Processing = "Broadcast is running, wait until the task is finished.\n\n<b>/status:</b> Show broadcast status."
    Nothing = "No broadcast is running."

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

    with open("broadcast_id.txt", "w") as broadcast_id:
        broadcast_id.write(f"{Msg.chat.id}\n{Process.id}")

    UserIDs = Bot.UserDB.Users()
    Total = len(UserIDs)

    Bot.Log.info(f"Broadcast by {AdminID}: Running")

    for UserID in UserIDs:
        if not Running:
            break

        if UserID not in AdminIDs:
            try:
                await Message.copy(chat_id=UserID, protect_content=Protect)
                Succeeded += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                Bot.Log.warning(e)
            except RPCError:
                Bot.UserDB.Delete(UserID)
                Failed += 1

            if (Succeeded + Failed) % 25 == 0:
                await Process.edit(text=f"<b>Broadcast Running</b>\n - Sent: {Succeeded}/{Total}\n - Failed: {Failed}\n\n<b>/cancel:</b> Cancel the process.")

    if not Running:
        await Msg.reply(text=f"<b>Broadcast Aborted</b>\n - Sent: {Succeeded}/{Total}\n - Failed: {Failed}", quote=True)
        Bot.Log.warning(f"Broadcast by {AdminID}: Aborted (Sent: {Succeeded}/{Total} - Failed: {Failed})")
    else:
        await Msg.reply(text=f"<b>Broadcast Finished</b>\n - Succeeded: {Succeeded}\n - Failed: {Failed}", quote=True)
        Bot.Log.info(f"Broadcast by {AdminID}: Finished (Sent: {Succeeded} - Failed: {Failed})")

    await Process.delete(revoke=True)

    os.remove("broadcast_id.txt")

    Running, Succeeded, Failed, Total = False, 0, 0, 0


@Client.on_message(filters.command("status") & filters.user(AdminIDs))
async def BroadcastStatus(_, Msg):
    global Running, Succeeded, Failed, Total

    if not Running:
        await Msg.reply(text=Nothing, quote=True)
    else:
        await Msg.reply(text=f"<b>Broadcast Status</b>\n - Sent: {Succeeded}/{Total}\n - Failed: {Failed}", quote=True)


@Client.on_message(filters.command("cancel") & filters.user(AdminIDs))
async def CancelBroadcast(_, Msg):
    global Running

    if not Running:
        await Msg.reply(text=Nothing, quote=True)
        return
    else:
        await Msg.reply(text="Broadcast has been aborted.", quote=True)
        Running = False