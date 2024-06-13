from bot.driver.bot import *
from bot.services.driver_service import is_driver_registred
from app.services.car_service import get_car_by_tg_id, Car
from app.services.task_service import *
from bot.services.notification_service import *
from bot.depot_manager.control.updater import application as depot_manager_app

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_group(update):
        return
    
    # check driver is registred or not
    if await is_driver_registred(update.message.chat_id):
        await update_message_reply_text(update, '.')
        return
    
    # check this driver ID is set on cars
    car: Car = await get_car_by_tg_id(update.message.chat_id)
    if not car:
        await update_message_reply_text(update, lang_dict['u r not driver'][0])
        return

    # send langs
    i_uz = InlineKeyboardButton(text='🇺🇿 UZ', callback_data='set_lang-uz')
    i_ru = InlineKeyboardButton(text='🇷🇺 РУ', callback_data='set_lang-ru')
    markup = InlineKeyboardMarkup([[i_uz, i_ru]])
    text = lang_dict['hello']
    await update_message_reply_text(update, text, reply_markup=markup)

async def received_new_task(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    task: Task = await get_task_by_id(int(task_id))
    # create taskevent about driver arriving to factory
    taskevent: TaskEvent = await create_taskevent(task, 'arrive_to_factory')
    # send message to factory man that driver is arriving
    loop = asyncio.get_event_loop()
    loop.create_task(
        alert_factory_about_driver_arriving_notification(context.bot, task)
    )
    await query.answer()
    # await query.edit_message_reply_markup(reply_markup=None)
    
async def factory_received_driver(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    task: Task = await get_task_by_id(int(task_id))
    # get taskevent about driver arriving to factory
    taskevent: TaskEvent = await get_taskevent_by_task_and_event_type(task, 'arrive_to_factory')
    # complete this taskevent
    await complete_taskevent(taskevent)

    # create new taskevent about car waiting in factory
    await create_taskevent(task, 'in_factory')
    # send message to driver that factory received your car
    loop = asyncio.get_event_loop()
    loop.create_task(
        alert_driver_about_car_in_factory_notification(context.bot, task)
    )
    await query.answer()
    # await query.edit_message_reply_markup(reply_markup=None)

async def driver_received_car_from_factory(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    task: Task = await get_task_by_id(int(task_id))
    # get taskevent about car waiting in factory
    taskevent: TaskEvent = await get_taskevent_by_task_and_event_type(task, 'in_factory')
    # complete this taskevent
    await complete_taskevent(taskevent)

    depot: Depot = await task.get_next_depot
    # create new taskevent about driver arrive to depot
    await create_taskevent(task, 'arrive_to_depot', depot=depot)
    # send message to depot manager that driver is arriving to depot
    loop = asyncio.get_event_loop()
    loop.create_task(
        alert_depot_manager_about_driver_arriving_notification(
            depot_manager_app.bot, task, depot
        )
    )
    await query.answer()
    # await query.edit_message_reply_markup(reply_markup=None)