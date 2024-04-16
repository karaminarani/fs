import os
import sys
import datetime
import logging
import base64
import asyncio
import uvloop

from pymongo import MongoClient

from pyromod import Client
from pyromod.helpers import ikb

from pyrogram import idle
from pyrogram.types import BotCommand
from pyrogram.enums import ChatType, ParseMode
from pyrogram.errors import FloodWait, RPCError


class Time:
    def __init__(self, Local):
        self.Local = Local

    def Delta(self):
        return datetime.datetime.utcnow() + datetime.timedelta(hours=self.Local)

    def Convert(self, *args):
        return self.Delta().timetuple()

Local = Time(7)


logging.Formatter.converter = Local.Convert
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%c", handlers=[logging.FileHandler(".Log"), logging.StreamHandler()], level=logging.INFO)

logging.getLogger("pyrogram").setLevel(logging.ERROR)
Logger = logging.getLogger(__name__)

ApiID = 2040
ApiHash = "b18441a1ff607e10a989891a5462e627"
BotToken = os.getenv("BOT_TOKEN")

DatabaseID = int(os.getenv("DATABASE_ID"))

AdminIDs = [int(i) for i in os.getenv("ADMIN_IDS").split()]

FSubIDs = [int(i) for i in os.environ.get("FSUB_IDS", "").split()]

Protect = eval(os.environ.get("PROTECT_CONTENT","True"))

MongoDBURL = os.environ.get("MONGODB_URL", "mongodb://root:passwd@mongo")
MongoDBName = BotToken.split(":", 1)[0]

BotCommands = [
    BotCommand("start", "Start Bot"),
    BotCommand("ping", "Bot Latency"),
    BotCommand("batch", "Batch Message (Admin)"),
    BotCommand("broadcast", "Broadcast Message (Admin)"),
    BotCommand("cancel", "Cancel Broadcast (Admin)"),
    BotCommand("status", "Broadcast Status (Admin)"),
    BotCommand("users", "User Stats (Admin)"),
    BotCommand("log", "Bot Logs (Admin)"),
    BotCommand("restart", "Restart Bot (Admin)")
]

Commands = [command.command for command in BotCommands]

Branch = os.environ.get("BRANCH", "master")

Version = "Released: Apr 16th, 2024"


class UserDB:
    def __init__(self, URL, Database):
        self.MongoClient = MongoClient(URL)
        self.Database = self.MongoClient[Database]
        self.UserIDs = self.Database["users"]

    def Insert(self, UserID: int):
        if not self.UserIDs.find_one({"_id": UserID}):
            self.UserIDs.insert_one({"_id": UserID})
            Logger.info(f"Insert: {UserID}")

    def Users(self):
        Users = self.UserIDs.find()
        UserIDs = [User["_id"] for User in Users]
        return UserIDs

    def Delete(self, UserID: int):
        self.UserIDs.delete_one({"_id": UserID})
        Logger.info(f"Delete: {UserID}")


class URLSafe:
    @staticmethod
    def Encode(Data):
        Encoder = base64.urlsafe_b64encode(Data.encode("utf-8"))
        Encoded = str(Encoder, "utf-8").rstrip("=")
        return Encoded

    @staticmethod
    def Decode(Data):
        Padding = (4 - len(Data) % 4) % 4
        Data += "=" * Padding
        Decoder = base64.urlsafe_b64decode(Data)
        Decoded = str(Decoder, "utf-8")
        return Decoded


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_id=ApiID,
            api_hash=ApiHash,
            bot_token=BotToken,
            in_memory=True,
            plugins=dict(root="Bot/Plugins"),
            parse_mode=ParseMode.HTML
        )

        self.Log = Logger
        self.UserDB = UserDB(MongoDBURL, MongoDBName)
        self.URLSafe = URLSafe()

    async def start(self):
        if os.path.exists(".Log"):
            with open(".Log", "r+") as Log:
                Log.truncate(0)

        Logger.info("Updating")
        os.system(f"git fetch origin -q; git reset --hard origin/{Branch} -q")
        Logger.info("Updated")

        Logger.info("Deploying")

        uvloop.install()

        try:
            await super().start()
            self.Button = ikb
            self.Username = self.me.username
            Logger.info(f"{self.me.id} Started")
        except FloodWait as e:
            Logger.warning(e)
            Logger.info(f"Sleep: {e.value}s")
            await asyncio.sleep(e.value + 5)
        except RPCError as e:
            Logger.error(e)
            sys.exit(1)

        await self.set_bot_commands(BotCommands)

        try:
            Hello = await self.send_message(chat_id=DatabaseID, text="Hello World!")
            await Hello.delete(revoke=True)
            Logger.info("DATABASE: Passed")
        except FloodWait as e:
            Logger.warning(e)
            Logger.info(f"Sleep: {e.value}s")
            await asyncio.sleep(e.value + 5)
        except RPCError as e:
            Logger.error(f"DATABASE: {e}")
            sys.exit(1)

        for key, chat_id in enumerate(FSubIDs):
            try:
                Get = await self.get_chat(chat_id)
                Link = Get.invite_link
                setattr(self, f"FSub{key}", Link)
                Logger.info(f"FSUB_{key + 1}: Passed")
            except FloodWait as e:
                ClientLog.warning(e)
                ClientLog.info(f"Sleep: {e.value}s")
                await asyncio.sleep(e.value + 5)
            except RPCError as e:
                Logger.error(f"FSUB_{key + 1}: {e}")
                sys.exit(1)

        if os.path.exists(".RestartID"):
            with open(".RestartID") as Read:
                ChatID, MessageID = map(int, Read)
                await self.edit_message_text(chat_id=ChatID, message_id=MessageID, text="Bot has been restarted.")
            os.remove(".RestartID")

        if os.path.exists(".BroadcastID"):
            with open(".BroadcastID") as Read:
                ChatID, MessageID = map(int, Read)
                await self.send_message(chat_id=ChatID, text="Bot restarted, broadcast has been aborted.", reply_to_message_id=MessageID)
            os.remove(".BroadcastID")

        Logger.info(Version)
        Logger.info(f"{self.me.id} Deployed")

        await idle()

    async def stop(self, *args):
        Logger.warning("Stopped")
        await super().stop()
        sys.exit()

Client = Bot()