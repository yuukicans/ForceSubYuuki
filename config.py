import os


class Config:
    startmsg = (
        'The bot is up and running. These bots '
        'can store messages in custom chats, '
        'and users access them through the bot.'
    )
    forcemsg = (
        'To view messages shared by bots. '
        'Join first, then press the Try Again button.'
    )

    OWNER_ID = int(os.environ.get('OWNER_ID', ''))
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
    DATABASE_ID = int(os.environ.get('DATABASE_ID', ''))
    MONGO_URL = os.environ.get('MONGO_URL', '')

    API_ID = 2040
    API_HASH = 'b18441a1ff607e10a989891a5462e627'
    BOT_ID = BOT_TOKEN.split(':', 1)[0]


Config = Config()
