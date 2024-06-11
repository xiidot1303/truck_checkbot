from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    InlineQueryHandler,
    TypeHandler,
    ConversationHandler
)

from bot.depot_manager.bot import (
    main, login
)

start = CommandHandler('start', main.start)
get_lang = CallbackQueryHandler(login.get_lang, pattern=r"^set_lang")

handlers = [
    start,
    get_lang
]