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
    main, login, task, location
)

start = CommandHandler('start', main.start)
get_lang = CallbackQueryHandler(login.get_lang, pattern=r"^set_lang")
received_news_task_handler = CallbackQueryHandler(task.received_new_task, pattern=r"^driver_receive_task")
driver_arrived_to_factory_handler = CallbackQueryHandler(
    task.driver_arrived_to_factory,
    pattern=r"^driver_arrived_to_factory"
)
factory_received_driver_handler = CallbackQueryHandler(
    task.factory_received_driver, 
    pattern=r"^factory_receive_driver"
    )
driver_arrived_to_warehouse_handler = CallbackQueryHandler(
    task.driver_arrived_to_warehouse,
    pattern=r"^driver_arrived_to_warehouse"
)
driver_received_car_from_factory_handler = CallbackQueryHandler(
    task.driver_received_car_from_factory,
    pattern=r"^driver_receive_car_from_factory"
)
driver_arrived_to_depot_handler = CallbackQueryHandler(
    task.driver_arrived_to_depot,
    pattern=r"^driver_arrived_to_depot"
)
driver_received_car_from_depot_handler = CallbackQueryHandler(
    task.driver_received_car_from_depot,
    pattern=r"^driver_receive_car_from_depot"
)
driver_back_to_factory_handler = CallbackQueryHandler(
    task.driver_back_to_factory,
    pattern=r"^driver_back_to_factory"
)

update_driver_location_handler = MessageHandler(filters.LOCATION, location.update_driver_location)

handlers = [
    start,
    get_lang,
    received_news_task_handler,
    driver_arrived_to_factory_handler,
    factory_received_driver_handler,
    driver_arrived_to_warehouse_handler,
    driver_received_car_from_factory_handler,
    driver_arrived_to_depot_handler,
    driver_received_car_from_depot_handler,
    driver_back_to_factory_handler,

    update_driver_location_handler,
    
]