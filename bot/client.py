import uvloop
from pyrogram import Client

from .utils.cache import Cache
from .utils.db import Database
from .utils.logger import Logger
from .utils.misc import Commands
from .utils.misc import URLSafe
from config import Config


class Bot(Client):
    log = Logger
    env = Config
    var = Cache
    cmd = Commands
    url = URLSafe
    mdb = Database

    def __init__(self):
        name: str = self.env.BOT_ID
        api_id: int = self.env.API_ID
        api_hash: str = self.env.API_HASH
        bot_token: str = self.env.BOT_TOKEN

        super().__init__(
            name, api_id, api_hash,
            bot_token=bot_token,
            mongodb=dict(
                connection=self.mdb.Client,
                remove_peers=True,
            ),
        )

    async def start(self):
        uvloop.install()
        await super().start()
        self.log.info(f'{self.me.id} sᴛᴀʀᴛᴇᴅ')

    async def stop(self, *args):
        await super().stop()
        self.log.warning('ᴄʟɪᴇɴᴅ sᴛᴏᴘᴘᴇᴅ')


Bot = Bot()
