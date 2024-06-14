from bot.services.language_service import get_word_driver, get_word_depot_manager, lang_dict
from bot.models import *
from app.models import *
from asgiref.sync import sync_to_async

async def new_task_for_driver_string(user_id):
    text = "{set_new_task_text}"
    text = text.format(
        set_new_task_text = await get_word_driver('set new task for driver', chat_id=user_id)
    )
    return text

async def driver_info_string_for_factory(driver: Driver):
    @sync_to_async
    def get_car_of_driver(driver):
        return driver.car

    car: Car = await get_car_of_driver(driver)
    text = "🚛 <b>{car_title_text}</b>: {car_title}\n\n🔢<b>{car_number_text}</b>: {car_number}"
    text = text.format(
        car_title_text = lang_dict['car'][1],
        car_title = car.title,
        car_number_text = lang_dict['number'][1],
        car_number = car.number
    )
    return text

async def car_in_factory_string_for_driver(user_id):
    text = f"{await get_word_driver('factory received car', chat_id=user_id)}\n\n" \
        f"{await get_word_driver('click button after get car', chat_id=user_id)}"
    
    return text

async def driver_info_string_for_depot(driver: Driver, user_id):
    @sync_to_async
    def get_car_of_driver(driver):
        return driver.car

    car: Car = await get_car_of_driver(driver)
    text = "🚛 <b>{car_title_text}</b>: {car_title}\n\n🔢<b>{car_number_text}</b>: {car_number}"
    text = text.format(
        car_title_text = await get_word_depot_manager('car', chat_id=user_id),
        car_title = car.title,
        car_number_text = await get_word_depot_manager('number', chat_id=user_id),
        car_number = car.number
    )
    return text


async def car_in_depot_string_for_driver(user_id):
    text = f"{await get_word_driver('depot received car', chat_id=user_id)}\n\n" \
        f"{await get_word_driver('click button after get car', chat_id=user_id)}"
    
    return text