from bot.driver.bot import *
from bot.services.driver_service import is_driver_registred
from app.services.car_service import get_car_by_tg_id, Car

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_group(update):
        return
    
    # check driver is registred or not
    if await is_driver_registred(update.message.chat_id):
        text = await get_word('you are successfully registred', update)
        await update_message_reply_text(update, text)
        return
    else:
    # check this driver ID is set on cars
    # car: Car = await get_car_by_tg_id(update.message.chat_id)
    # if not car:
        await update_message_reply_text(update, lang_dict['u r not driver'][0])
        your_id_text = f"{lang_dict['your id'][0]}<code>{update.message.chat.id}</code>"
        await bot_send_message(update, context, your_id_text)
        return

    # send langs
    i_uz = InlineKeyboardButton(text='🇺🇿 UZ', callback_data='set_lang-uz')
    i_ru = InlineKeyboardButton(text='🇷🇺 РУ', callback_data='set_lang-ru')
    markup = InlineKeyboardMarkup([[i_uz, i_ru]])
    text = lang_dict['hello']
    await update_message_reply_text(update, text, reply_markup=markup)
