from app.services import *
from bot.models import Driver
from asgiref.sync import sync_to_async

@sync_to_async
def is_driver_registred(user_id: int):
    # filter drivers
    if Driver.objects.filter(user_id=user_id):
        return True
    else:
        return False

async def create_driver(user_id, car, lang, firstname) -> Driver:
    driver = await Driver.objects.acreate(
        user_id = user_id, car = car, 
        lang = lang, firstname = firstname, name = firstname
    )
    return driver