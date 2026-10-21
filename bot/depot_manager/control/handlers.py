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
    main, login, force_majeure
)
from bot.depot_manager.bot import States
from bot.services.redis_service import *
from bot.resources.strings import lang_dict
import re


async def text_router(update, context):
    state = await get_user_state(update.effective_user.id)

    if state == States.WAITING_FORCEMAJEURE_REASON:
        await force_majeure.get_reason_of_the_forcemajeure(update, context)
    elif state == States.WAITING_FORCEMAJEURE_PHOTO:
        await update.effective_message.reply_text(
            await force_majeure.get_word('send photo of forcemajeure depot', update)
        )


async def photo_router(update, context):
    state = await get_user_state(update.effective_user.id)

    if state == States.WAITING_FORCEMAJEURE_PHOTO:
        await force_majeure.get_photo_of_the_forcemajeure(update, context)
    elif state == States.WAITING_FORCEMAJEURE_REASON:
        await update.effective_message.reply_text(
            await force_majeure.get_word('send text reason', update)
        )


start = CommandHandler('start', main.start)
get_lang = CallbackQueryHandler(login.get_lang, pattern=r"^set_lang")
depot_received_driver_handler = CallbackQueryHandler(
    main.depot_received_driver,
    pattern=r'^depot_receive_driver'
)

depot_completed_unloading_handler = CallbackQueryHandler(
    main.depot_completed_unloading,
    pattern=r'^depot_completed_unloading'
)

force_majeure_detected_handler = CallbackQueryHandler(
    force_majeure.force_majeure_detected,
    pattern=r'^depot_force_majeure-'
)

depot_completed_force_majeure_handler = CallbackQueryHandler(
    force_majeure.complete_force_majeure_by_depot,
    pattern=r'^depot_completed_force_majeure-'
)

force_majeure_button_handler = MessageHandler(
    filters.Regex(
        "^(" + "|".join(re.escape(text) for text in lang_dict['force majeure button']) + ")$"
    ),
    force_majeure.force_majeure_button
)

text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, text_router)
photo_handler = MessageHandler(filters.PHOTO, photo_router)

handlers = [
    start,
    get_lang,
    depot_received_driver_handler,
    depot_completed_unloading_handler,
    force_majeure_detected_handler,
    depot_completed_force_majeure_handler,
    text_handler,
    photo_handler,
    # handlers are added in reverse order, so this one is checked before text_handler
    force_majeure_button_handler,
]