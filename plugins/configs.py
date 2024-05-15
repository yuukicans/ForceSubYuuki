from pyrogram.errors import RPCError
from pyrogram.filters import command
from pyrogram.filters import private
from pyrogram.filters import regex
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.handlers import MessageHandler
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery
from pyrogram.types import Message

from .helpers import decorator
from .helpers import helpers
from .helpers import Markup
from bot.client import Bot


@decorator.Admins
async def configs(_, message: Message):
    await message.reply(
        'Bot Configuration Menu:',
        reply_markup=ikb(Markup.HOME),
    )
    await message.delete()


@decorator.Admins
async def cbqhome(client: Bot, cbq: CallbackQuery):
    data = cbq.data.split('-')[1]
    action = {
        'close': cbq.message.delete,
        'home': lambda: cbq.message.edit(
            'Configuration:',
            reply_markup=ikb(Markup.HOME),
        ),
        'stats': lambda: cbq.message.edit(
            'Monitor and Stats:',
            reply_markup=ikb(Markup.STATS),
        ),
    }
    if action := action.get(data):
        await action()


@decorator.Admins
async def cbqset(client: Bot, cbq: CallbackQuery):
    bvar = client.var.vars
    data = cbq.data.split('-')[1]

    def format_list(title, items):
        if items:
            fmtitems = ''.join(
                f'  {i + 1}. `{item}`\n' for i,
                item in enumerate(items)
            )
        else:
            fmtitems = '  `None`'
        return f'{title}:\n{fmtitems}'

    gprtct = bvar.get('PROTECT_CONTENT', [])[0]
    ggnrte = bvar.get('GEN_STATUS', [])[0]
    action = {
        'admnids': lambda: cbq.message.edit(
            format_list(
                'List Admin IDs',
                bvar.get('ADMIN_IDS', []),
            ),
            reply_markup=ikb(Markup.SET_ADMIN),
        ),
        'fscids': lambda: cbq.message.edit(
            format_list(
                'List FSub IDs',
                bvar.get('FSUB_IDS', []),
            ),
            reply_markup=ikb(Markup.SET_FSUB),
        ),
        'prtctcntnt': lambda: cbq.message.edit(
            f'Protect Content: {gprtct}',
            reply_markup=ikb(Markup.SET_PROTECT),
        ),
        'gen': lambda: cbq.message.edit(
            f'Generator: {ggnrte}',
            reply_markup=ikb(Markup.SET_GENERATOR),
        ),
        'strtmsg': lambda: cbq.message.edit(
            'Start Text:\n  '
            f'`{bvar.get("START_MESSAGE", [])[0]}`',
            reply_markup=ikb(Markup.SET_START),
        ),
        'frcmsg': lambda: cbq.message.edit(
            'Force Text:\n  '
            f'`{bvar.get("FORCE_MESSAGE", [])[0]}`',
            reply_markup=ikb(Markup.SET_FORCE),
        ),
    }
    if action := action.get(data):
        await action()


@decorator.Admins
async def cbqchange(client: Bot, cbq: CallbackQuery):
    async def replace(field, new):
        await client.mdb.outvars('BOT_VARS', field)
        await client.mdb.invar('BOT_VARS', field, new)
        await client.var.fetching()
        await helpers.cached()

    bvar = client.var.vars
    data = cbq.data.split('-')[1]

    if data in ['prtctcntnt', 'gen']:
        field = (
            'PROTECT_CONTENT' if data == 'prtctcntnt'
            else 'GEN_STATUS'
        )
        crrnt = bvar.get(field, [])[0]
        await replace(field, not crrnt)
        smsg = (
            'Protect Content' if data == 'prtctcntnt'
            else 'Generator'
        )
        await cbq.message.edit(
            smsg + ' Changed',
            reply_markup=ikb(Markup.BACK),
        )
    elif data in ['strtmsg', 'frcmsg']:
        mtype = 'Start' if data == 'strtmsg' else 'Force'
        await cbq.message.edit(f'Send {mtype} Text')
        lstn = await client.listen(
            user_id=cbq.message.chat.id,
        )
        await lstn.delete()
        if not lstn or not lstn.text:
            return await cbq.message.edit(
                'Invalid! Just Send a Text',
                reply_markup=ikb(Markup.SET_START),
            )
        field = 'START_MESSAGE' if data == 'strtmsg' else 'FORCE_MESSAGE'
        await replace(field, lstn.text)
        await cbq.message.edit(
            f'{mtype} Text:\n  `{lstn.text}`',
            reply_markup=ikb(Markup.BACK),
        )


@decorator.Admins
async def cbqadd(client: Bot, cbq: CallbackQuery):
    async def addvar(field, new):
        await client.mdb.invar(
            'BOT_VARS',
            field,
            new,
        )
        await client.var.fetching()
        await helpers.cached()

    bvar = client.var.vars
    data = cbq.data.split('-')[1]
    enti = 'Admin' if data == 'admnids' else 'FSub'
    vari = 'ADMIN_IDS' if data == 'admnids' else 'FSUB_IDS'
    await cbq.message.edit(
        f'Send {"User" if enti == "Admin" else "Chat"} ID '
        f'to Add {enti}',
    )
    lstn = await client.listen(
        user_id=cbq.message.chat.id,
    )
    await lstn.delete()
    if lstn and not lstn.text:
        return await cbq.message.edit(
            'Invalid! Just Send a '
            f'{"User" if enti == "Admin" else "Chat"} ID',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    try:
        enid = int(lstn.text)
    except ValueError:
        return await cbq.message.edit(
            'Invalid! Just Send a '
            f'{"User" if enti == "Admin" else "Chat"} ID',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    if enid in bvar.get(vari, []):
        return await cbq.message.edit(
            f'{"User" if enti == "Admin" else "Chat"} ID '
            'Already Exists',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    await cbq.message.edit('Initializing...')
    try:
        if data == 'admnids':
            await client.get_users(enid)
        else:
            (await client.get_chat(enid)).invite_link
    except RPCError:
        return await cbq.message.edit(
            'Invalid! '
            f'{"User" if enti == "Admin" else "Chat"} ID '
            'Not Found',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    await addvar(vari, enid)
    await cbq.message.edit(
        f'Added {enti}: `{enid}`',
        reply_markup=ikb(Markup.BACK),
    )


@decorator.Admins
async def cbqdel(client: Bot, cbq: CallbackQuery):
    async def delvar(field, newkey):
        await client.mdb.rmvar(
            'BOT_VARS',
            field,
            newkey,
        )
        await client.var.fetching()
        await helpers.cached()

    bvar = client.var.vars
    data = cbq.data.split('-')[1]
    enti = 'Admin' if data == 'admnids' else 'FSub'
    vari = 'ADMIN_IDS' if data == 'admnids' else 'FSUB_IDS'
    await cbq.message.edit(
        f'Send {enti} ID to Delete {enti}',
    )
    lstn = await client.listen(
        user_id=cbq.message.chat.id,
    )
    await lstn.delete()
    if lstn and not lstn.text:
        return await cbq.message.edit(
            'Invalid! Just Send a '
            f'{"User" if enti == "Admin" else "Chat"} ID',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    try:
        enid = int(lstn.text)
    except ValueError:
        return await cbq.message.edit(
            'Invalid! Just Send a '
            f'{"User" if enti == "Admin" else "Chat"} ID',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    if enid not in bvar.get(vari, []):
        return await cbq.message.edit(
            'Invalid! '
            f'{"User" if enti == "Admin" else "Chat"} ID '
            'Not Found',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    if enid == cbq.message.chat.id:
        return await cbq.message.edit(
            "No Rights! That's You",
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    await delvar(vari, enid)
    await cbq.message.edit(
        f'Deleted {enti}: `{enid}`',
        reply_markup=ikb(Markup.BACK),
    )


Bot.add_handler(
    MessageHandler(
        configs,
        filters=command(Bot.cmd.configs) & private,
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqhome,
        filters=regex(r'^home'),
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqset,
        filters=regex(r'^set'),
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqchange,
        filters=regex(r'^change'),
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqadd,
        filters=regex(r'^add'),
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqdel,
        filters=regex(r'^del'),
    ),
)
