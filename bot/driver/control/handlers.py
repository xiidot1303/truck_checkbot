from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    InlineQueryHandler,
    TypeHandler,
    ConversationHandler
)

from bot.driver.bot import (
    main, login
)

start = CommandHandler('start', main.start)
get_lang = CallbackQueryHandler(login.get_lang, pattern=r"^set_lang")
received_news_task_handler = CallbackQueryHandler(main.received_new_task, pattern=r"^driver_receive_task")

handlers = [
    start,
    get_lang,
    received_news_task_handler
]