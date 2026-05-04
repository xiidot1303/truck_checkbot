from bot.driver.bot import *
from bot.services.driver_service import is_driver_registred
from app.services.car_service import get_car_by_tg_id, Car
import json
import logging
import traceback
import html
from django.db import close_old_connections
from telegram.error import TimedOut

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



async def error_handler(update: Update, context: CustomContext):
    # restart db connection if error is "connection already closed"
    if "connection already closed" in str(context.error):
        await sync_to_async(close_old_connections)()
        return


    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
    )
    error_message = f"{html.escape(tb_string)}"

    # Finally, send the message
    try:
        await context.bot.send_message(
            chat_id=206261493, text=message, parse_mode=ParseMode.HTML
        )
        for i in range(0, len(error_message), 4000):
            await context.bot.send_message(
                chat_id=206261493, text=f"<pre>{error_message[i:i+4000]}</pre>", parse_mode=ParseMode.HTML
            )
    except Exception as ex:
        print(ex)
