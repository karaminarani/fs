import os
import sys
import logging
import uvloop
import base64

from pymongo import MongoClient

from pyromod import Client

from pyrogram.types import BotCommand
from pyrogram.enums import ParseMode
from pyrogram.errors import RPCError

logging.basicConfig(handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()], level=logging.INFO)


Logger = logging.getLogger("Bot")

TelegramApiID = 2040
TelegramApiHash = "b18441a1ff607e10a989891a5462e627"

TelegramBotToken = os.getenv("BOT_TOKEN")
DatabaseChannelID = int(os.getenv("DATABASE_CHANNEL"))

ListOfBotAdmins = [int(i) for i in os.getenv("BOT_ADMINS").split()]

NumberOfMustJoinIDs = 1
MustJoinID = {}
while True:
    key = f"FORCE_SUB_{NumberOfMustJoinIDs}"
    value = os.environ.get(key)
    if value is None:
        break
    MustJoinID[NumberOfMustJoinIDs] = int(value)
    NumberOfMustJoinIDs += 1

ProtectContent = eval(os.environ.get("PROTECT_CONTENT","True"))

MongoDBURL = os.environ.get("MONGODB_URL", "mongodb://root:passwd@mongo")
MongoDBName = TelegramBotToken.split(":", 1)[0]

CompleteListOfBotCommands = [
    BotCommand("start", "Start Bot"),
    BotCommand("ping", "Bot Latency"),
    BotCommand("batch", "Batch Message"),
    BotCommand("broadcast", "Broadcast Message"),
    BotCommand("cancel", "Cancel Broadcast"),
    BotCommand("status", "Broadcast Status"),
    BotCommand("users", "User Stats"),
    BotCommand("log", "Bot Logs"),
    BotCommand("restart", "Restart Bot")
]

ListOfBotCommands = [command.command for command in CompleteListOfBotCommands]


class UserDB:
    def __init__(self, DatabaseURL, DatabaseName):
        self.DatabaseClient = MongoClient(DatabaseURL)
        self.DatabaseName = self.DatabaseClient[DatabaseName]
        self.ListOfUserIDs = self.DatabaseName["users"]

    def Insert(self, user_id: int):
        if not self.ListOfUserIDs.find_one({"_id": user_id}):
            self.ListOfUserIDs.insert_one({"_id": user_id})

    def AllUsers(self):
        users = self.ListOfUserIDs.find()
        user_id = [user["_id"] for user in users]
        return user_id

    def Delete(self, user_id: int):
        self.ListOfUserIDs.delete_one({"_id": user_id})


class URLSafe:
    @staticmethod
    def Encode(data):
        encoded_bytes = base64.urlsafe_b64encode(data.encode("utf-8"))
        encoded_data = str(encoded_bytes, "utf-8").rstrip("=")
        return encoded_data

    @staticmethod
    def Decode(data):
        padding_factor = (4 - len(data) % 4) % 4
        data += "=" * padding_factor
        decoded_bytes = base64.urlsafe_b64decode(data)
        decoded_data = str(decoded_bytes, "utf-8")
        return decoded_data


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            in_memory=True,
            api_id=TelegramApiID,
            api_hash=TelegramApiHash,
            bot_token=TelegramBotToken,
            parse_mode=ParseMode.MARKDOWN,
            plugins=dict(root="Bot/Plugins")
        )

        self.Logger = Logger
        self.UserDB = UserDB(MongoDBURL, MongoDBName)
        self.URLSafe = URLSafe()

    async def start(self):
        if os.path.exists(".git"):
            os.system("git fetch origin -q; git reset --hard origin/master -q")

        uvloop.install()

        try:
            await super().start()
        except RPCError as e:
            logging.error(e)
            sys.exit(1)

        await self.set_bot_commands(CompleteListOfBotCommands)

        try:
            hello_world = await self.send_message(chat_id=DatabaseChannelID, text="Hello World!")
            await hello_world.delete()
        except RPCError as e:
            self.Logger.error(f"DATABASE_CHANNEL: {e}")
            sys.exit(1)

        for key, chat_id in MustJoinID.items():
            try:
                get_chat = await self.get_chat(chat_id)
                setattr(self, f"MustJoinID{key}", get_chat.invite_link)
            except RPCError as e:
                self.Logger.error(f"FORCE_SUB_{key}: {e}")
                sys.exit(1)

        if os.path.exists("restart_id.txt"):
            with open("restart_id.txt") as read:
                chat_id, message_id = map(int, read)
                await self.edit_message_text(chat_id=chat_id, message_id=message_id, text="Bot has been restarted.")
            os.remove("restart_id.txt")

        if os.path.exists("broadcast_id.txt"):
            with open("broadcast_id.txt") as read:
                chat_id, message_id = map(int, read)
                await self.send_message(chat_id=chat_id, text="Bot restarted, broadcast has been aborted.", reply_to_message_id=message_id)
            os.remove("broadcast_id.txt")

    async def stop(self, *args):
        await super().stop()
        sys.exit()

Client = Bot()