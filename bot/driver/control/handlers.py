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
factory_received_driver_handler = CallbackQueryHandler(
    main.factory_received_driver, 
    pattern=r"^factory_receive_driver"
    )
driver_received_car_from_factory_handler = CallbackQueryHandler(
    main.driver_received_car_from_factory,
    pattern=r"^driver_receive_car_from_factory"
)

handlers = [
    start,
    get_lang,
    received_news_task_handler,
    factory_received_driver_handler,
    driver_received_car_from_factory_handler,
    
]