from bot.depot_manager.bot import *
from app.services.depot_service import get_depot_by_tg_id, Depot
from bot.services.depot_manager_service import create_depot_manager, DepotManager

async def get_lang(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    # get car by user id
    depot: Depot = await get_depot_by_tg_id(query.message.chat.id)
    # get lang from query data
    data = query.data
    args, lang = data.split('-')
    # create driver
    depot_manager: DepotManager = await create_depot_manager(
        query.message.chat.id, lang, query.message.chat.first_name
    )
    depot.bot_user = depot_manager
    await depot.asave()
    await query.answer()
    await query.edit_message_text(await get_word('successfully registred', query))
    return 