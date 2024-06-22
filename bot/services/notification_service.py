from bot.utils.bot_functions import *
from bot.models import *
from app.models import *
from bot.services.string_service import *
from bot.services.driver_service import get_factory, get_driver_by_id, driver_of_task, get_report_group
from asgiref.sync import *
import aiofiles

async def alert_driver_about_new_task_notification(bot: Bot, task: Task):
    driver: Driver = task.driver
    user_id = driver.user_id
    task_id = task.id
    text = await new_task_for_driver_string(user_id)
    i_get = InlineKeyboardButton(
        text=await get_word_driver('i received it', chat_id=user_id),
        callback_data=f'driver_receive_task-{task_id}'
        )
    markup = InlineKeyboardMarkup([[i_get]])
    await send_newsletter(bot, user_id, text, reply_markup=markup)

async def alert_factory_about_driver_arriving_notification(bot, task: Task):
    driver: Driver = await driver_of_task(task)
    factory: Factory = await get_factory()
    text = await driver_info_string_for_factory(driver)
    i_get = InlineKeyboardButton(
        text=lang_dict['i received it'][1],
        callback_data=f'factory_receive_driver-{task.id}'
        )
    markup = InlineKeyboardMarkup([[i_get]])
    await send_newsletter(bot, factory.tg_id, text, reply_markup=markup)

async def alert_driver_about_car_in_factory_notification(bot, task: Task):
    driver: Driver = await driver_of_task(task)
    user_id = driver.user_id
    text = await car_in_factory_string_for_driver(user_id)
    i_get = InlineKeyboardButton(
        text=await get_word_driver('i received it', chat_id=user_id),
        callback_data=f'driver_receive_car_from_factory-{task.id}'
        )
    markup = InlineKeyboardMarkup([[i_get]])
    await send_newsletter(bot, user_id, text, reply_markup=markup)

async def alert_depot_manager_about_driver_arriving_notification(bot: Bot, task: Task, depot: Depot, taskevent: TaskEvent):
    driver: Driver = await driver_of_task(task)
    user_id = depot.tg_id
    text = await driver_info_string_for_depot(driver, user_id)
    i_get = InlineKeyboardButton(
        text=await get_word_depot_manager('i received it', chat_id=user_id),
        callback_data=f'depot_receive_driver-{taskevent.id}'
        )
    markup = InlineKeyboardMarkup([[i_get]])
    await send_newsletter(bot, user_id, text, reply_markup=markup)

async def alert_driver_about_car_in_depot_notification(bot, task: Task, taskevent: TaskEvent):
    driver: Driver = await driver_of_task(task)
    user_id = driver.user_id
    text = await car_in_depot_string_for_driver(user_id)
    i_get = InlineKeyboardButton(
        text=await get_word_driver('i received it', chat_id=user_id),
        callback_data=f'driver_receive_car_from_depot-{taskevent.id}'
        )
    markup = InlineKeyboardMarkup([[i_get]])
    await send_newsletter(bot, user_id, text, reply_markup=markup)

async def send_report_of_task_newsletter(bot: Bot, task: Task, file_path):
    report_group: ReportGroup = await get_report_group()
    await send_newsletter(
        bot,
        report_group.tg_id,
        f"{task.driver.car}",
        document=file_path
        )