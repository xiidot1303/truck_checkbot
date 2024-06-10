from bot.driver.bot import *
from app.services.car_service import get_car_by_tg_id, Car
from bot.services.driver_service import create_driver

async def get_lang(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    # get car by user id
    car: Car = await get_car_by_tg_id(query.message.chat.id)
    # get lang from query data
    data = query.data
    args, lang = data.split('-')
    # create driver
    await create_driver(
        query.message.chat.id, car, lang, query.message.chat.first_name
    )
    await query.answer()
    await query.edit_message_text(await get_word('successfully registred', query))
    return 