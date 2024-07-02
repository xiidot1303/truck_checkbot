from bot.depot_manager.bot import *
from bot.services.depot_manager_service import is_depot_manager_registred
from bot.services.notification_service import *
from app.services.depot_service import get_depot_by_tg_id, Depot
from app.services.task_service import *
from app.models import *
import asyncio

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
        your_id_text = f"{lang_dict['your id'][0]}<code>{update.message.chat.id}</code>"
        await bot_send_message(update, context, your_id_text)
        return

    # send langs
    i_uz = InlineKeyboardButton(text='🇺🇿 UZ', callback_data='set_lang-uz')
    i_ru = InlineKeyboardButton(text='🇷🇺 РУ', callback_data='set_lang-ru')
    markup = InlineKeyboardMarkup([[i_uz, i_ru]])
    text = lang_dict['hello']
    await update_message_reply_text(update, text, reply_markup=markup)


async def depot_received_driver(update: Update, context: CustomContext):
    @sync_to_async
    def get_task_of_taskevent(taskevent: TaskEvent) -> Task:
        return taskevent.task
    
    @sync_to_async
    def get_depot_of_taskevent(taskevent: TaskEvent) -> Depot:
        return taskevent.depot

    query: CallbackQuery = update.callback_query
    data = query.data
    *args, taskevent_id = data.split('-')
    taskevent: TaskEvent = await get_taskevent_by_id(taskevent_id)
    task: Task = await get_task_of_taskevent(taskevent)
    # complete this taskevent
    await complete_taskevent(taskevent)

    # create new taskevent about car waiting in factory
    depot: Depot = await get_depot_of_taskevent(taskevent)
    taskevent: TaskEvent = await create_taskevent(task, 'in_depot', depot=depot)
    # send message to driver that depot received your car
    loop = asyncio.get_event_loop()
    loop.create_task(
        alert_driver_about_car_in_depot_notification(
            driver_app.bot, task, taskevent
        )
    )
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)