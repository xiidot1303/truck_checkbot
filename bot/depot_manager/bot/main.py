from bot.depot_manager.bot import *
from bot.services.depot_manager_service import is_depot_manager_registred
from app.services.depot_service import get_depot_by_tg_id, Depot

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_group(update):
        return
    
    # check driver is registred or not
    if await is_depot_manager_registred(update.message.chat_id):
        # main menu
        return
    
    # check this driver ID is set on cars
    depot: Depot = await get_depot_by_tg_id(update.message.chat_id)
    if not depot:
        await update_message_reply_text(update, lang_dict['u r not depot manager'][0])
        return

    # send langs
    i_uz = InlineKeyboardButton(text='🇺🇿 UZ', callback_data='set_lang-uz')
    i_ru = InlineKeyboardButton(text='🇷🇺 РУ', callback_data='set_lang-ru')
    markup = InlineKeyboardMarkup([[i_uz, i_ru]])
    text = lang_dict['hello']
    await update_message_reply_text(update, text, reply_markup=markup)