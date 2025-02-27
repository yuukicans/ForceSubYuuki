import asyncio
import functools
import sys

from pyrogram.errors import RPCError
from pyrogram.types import BotCommand

from bot.client import Bot
from plugins import loadplugin
from plugins.helpers import helpers


async def main():
    await dbctrl()

    Bot.log.info('Memulai Mendeploy')
    await starting()

    Bot.log.info('Menginisialisasi DatabaseID')
    await getdbcid()
    Bot.log.info('DatabaseID Diinisialisasi')

    Bot.log.info('Mengambil Basis Data Mongo')
    await Bot.var.fetching()

    Bot.log.info('Menginisialisasi Lingkungan')
    await helpers.cached()

    Bot.log.info('Menetapkan Perintah Bot')
    await botcmd()

    Bot.log.info('Mengimpor Plugin')
    loadplugin()

    Bot.log.info('Memeriksa Data Restart')
    await rmsg('rmsg')
    await rmsg('bmsg')
    Bot.log.info('Data Restart Telah Diperiksa')


def rpchndlr(func):
    @functools.wraps(func)
    async def wrapper() -> callable:
        try:
            return await func()
        except RPCError as e:
            Bot.log.error(str(e))
            sys.exit(1)
    return wrapper


@rpchndlr
async def starting():
    await Bot.start()


@rpchndlr
async def getdbcid():
    hellomsg = await Bot.send_message(
        Bot.env.DATABASE_ID,
        'Hello Worldl!',
    )
    await hellomsg.delete()


async def dbctrl():
    bvar = await Bot.mdb.gvars('BOT_VARS')
    dvar = {
        'GEN_STATUS': True,
        'PROTECT_CONTENT': True,
        'START_MESSAGE': Bot.env.startmsg,
        'FORCE_MESSAGE': Bot.env.forcemsg,
        'ADMIN_IDS': Bot.env.OWNER_ID,
    }
    if not bvar:
        for key, value in dvar.items():
            await Bot.mdb.invar('BOT_VARS', key, value)


async def botcmd():
    await Bot.set_bot_commands(
        [
            BotCommand(Bot.cmd.start, 'Starting Bot'),
        ],
    )
    Bot.log.info('Bot Command Has Set')


async def rmsg(_id: str):
    rmsg = await Bot.mdb.gmsgs(_id)
    if rmsg:
        cid, mid, = rmsg['cid'], rmsg['mid']
        await Bot.send_message(
            cid,
            'Bot Restarted',
            reply_to_message_id=mid,
        )
        await Bot.mdb.rmmsg(_id)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
    Bot.log.info('Bot Berhasil Aktif')
    Bot.loop.run_forever()
