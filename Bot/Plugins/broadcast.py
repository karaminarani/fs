import os
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

from Bot import ListOfBotAdmins, ProtectContent

BroadcastRunning, succeeded_sent, failed_sent, number_of_users = False, 0, 0, 0


@Client.on_message(filters.command("broadcast") & filters.user(ListOfBotAdmins))
async def Broadcast(Bot, Msg):
    global BroadcastRunning, succeeded_sent, failed_sent, number_of_users

    BroadcastRunningMessage = "Broadcast is running, wait until the task is finished.\n\n**/status:** Show broadcast status."

    if not Msg.reply_to_message:
        await Msg.reply("Please reply to a message you want to broadcast.", quote=True)
        return
    else:
        if not BroadcastRunning:
            BroadcastRunning, succeeded_sent, failed_sent, number_of_users = True, 0, 0, 0
            broadcast_message = Msg.reply_to_message
        else:
            await Msg.reply(BroadcastRunningMessage, quote=True)
            return

    broadcast_message_process = await Msg.reply("Sending...", quote=True)

    with open("broadcast_id.txt", "w") as broadcast_id:
        broadcast_id.write(f"{Msg.chat.id}\n{broadcast_message_process.id}")

    all_users = Bot.UserDB.AllUsers()
    number_of_users = len(all_users)

    for user_id in all_users:
        if not BroadcastRunning:
            break

        if user_id not in ListOfBotAdmins:
            try:
                await broadcast_message.copy(chat_id=user_id, protect_content=ProtectContent)
                succeeded_sent += 1
            except FloodWait as e:
                Bot.Logger.warning(f"BROADCAST: {e}")
                await asyncio.sleep(e.value)
                continue
            except RPCError:
                Bot.UserDB.Delete(user_id)
                failed_sent += 1

            if (succeeded_sent + failed_sent) % 25 == 0:
                await broadcast_message_process.edit(f"**Broadcast Running**\n - Sent: {succeeded_sent}/{number_of_users}\n - Failed: {failed_sent}\n\n**/cancel:** Cancel the process.")

    if not BroadcastRunning:
        await Msg.reply(f"**Broadcast Aborted**\n - Sent: {succeeded_sent}/{number_of_users}\n - Failed: {failed_sent}", quote=True)
    else:
        await Msg.reply(f"**Broadcast Finished**\n - Succeeded: {succeeded_sent}\n - Failed: {failed_sent}", quote=True)

    await broadcast_message_process.delete()

    os.remove("broadcast_id.txt")

    BroadcastRunning, succeeded_sent, failed_sent, number_of_users = False, 0, 0, 0


@Client.on_message(filters.command("status") & filters.user(ListOfBotAdmins))
async def BroadcastStatus(_, Msg):
    global BroadcastRunning, succeeded_sent, failed_sent, number_of_users

    if not BroadcastRunning:
        await Msg.reply("No broadcast is running.", quote=True)
    else:
        await Msg.reply(f"**Broadcast Status**\n - Sent: {succeeded_sent}/{number_of_users}\n - Failed: {failed_sent}", quote=True)


@Client.on_message(filters.command("cancel") & filters.user(ListOfBotAdmins))
async def CancelBroadcast(_, Msg):
    global BroadcastRunning

    if not BroadcastRunning:
        await Msg.reply("No broadcast is running.", quote=True)
        return
    else:
        await Msg.reply("Broadcast has been aborted.", quote=True)
        BroadcastRunning = False