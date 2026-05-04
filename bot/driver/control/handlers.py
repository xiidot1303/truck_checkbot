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
    main, login, task, location, force_majeure
)
from bot.driver.bot import States
from bot.services.redis_service import *


async def photo_router(update, context):
    user_id = update.effective_user.id
    state = await get_user_state(user_id)

    if state == States.WAITING_FORCEMAJEURE_PHOTO:
        await force_majeure.get_photo_of_the_forcemajeure(update, context)


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
factory_completed_loading_handler = CallbackQueryHandler(
    task.factory_completed_loading, 
    pattern=r"^factory_completed_loading"
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

force_majeure_detected_handler = CallbackQueryHandler(
    force_majeure.force_majeure_detected,
    pattern=r"^force_majeure-"
)
force_majeure_selected_handler = CallbackQueryHandler(
    force_majeure.force_majeure_type_selected,
    pattern=r"^force_majeure_type"
)
controller_confirm_force_majeure_handler = CallbackQueryHandler(
    force_majeure.controller_confirm_force_majeure,
    pattern=r"^confirm_force_majeure"
)
driver_completed_force_majeure_handler = CallbackQueryHandler(
    force_majeure.driver_complete_force_majeure,
    pattern=r"^driver_completed_force_majeure"
)

photo_handler = MessageHandler(filters.PHOTO, photo_router)

handlers = [
    photo_handler,
    start,
    get_lang,
    received_news_task_handler,
    driver_arrived_to_factory_handler,
    factory_received_driver_handler,
    factory_completed_loading_handler,
    driver_arrived_to_warehouse_handler,
    driver_received_car_from_factory_handler,
    driver_arrived_to_depot_handler,
    driver_received_car_from_depot_handler,
    driver_back_to_factory_handler,

    force_majeure_detected_handler,
    force_majeure_selected_handler,
    controller_confirm_force_majeure_handler,
    driver_completed_force_majeure_handler,


    update_driver_location_handler,
    
]