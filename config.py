class Config:
    startmsg = 'The bot is up and running. These bots ' \
               'can store messages in custom chats, '\
               'and users access them through the bot.'
    forcemsg = 'To view messages shared by bots. '\
               'Join first, then press the Try Again button.'

    BOT_TOKEN = '12345:Abc'
    DATABASE_ID = -100

    API_ID = 12345
    API_HASH = 'Abc'
    BOT_ID = BOT_TOKEN.split(':', 1)[0]
    OWNER_ID = 12345
    MONGO_URL = 'mongodb+srv://'


Config = Config()
