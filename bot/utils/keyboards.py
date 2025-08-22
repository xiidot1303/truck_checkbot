from bot.services.language_service import get_word_driver, get_word_depot_manager
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)


# async def _inline_footer_buttons(update, buttons, back=True, main_menu=True):
#     new_buttons = []
#     if back:
#         new_buttons.append(
#             InlineKeyboardButton(text=get_word('back', update), callback_data='back'),
#         )
#     if main_menu:
#         new_buttons.append(
#             InlineKeyboardButton(text=get_word('main menu', update), callback_data='main_menu'),
#         )

#     buttons.append(new_buttons)
#     return buttons

# async def settings_keyboard(update):

#     buttons = [
#         [get_word("change lang", update)],
#         [get_word("change name", update)],
#         [get_word("change phone number", update)],
#         [get_word("main menu", update)],
#     ]

#     return buttons

async def arrived_keyboard(update, callback_data, task_id) -> InlineKeyboardMarkup:
    i_arrived = InlineKeyboardButton(
        await get_word_driver('arrived', update),
        callback_data=callback_data
    )
    i_force_majeure = InlineKeyboardButton(
        await get_word_driver('force majeure', update),
        callback_data=f'force_majeure-{task_id}'
    )
    markup = InlineKeyboardMarkup([[i_arrived], [i_force_majeure]])
    return markup