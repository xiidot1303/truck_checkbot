from app.services import *
from bot.models import Driver, Factory
from asgiref.sync import sync_to_async

@sync_to_async
def is_driver_registred(user_id: int):
    # filter drivers
    if Driver.objects.filter(user_id=user_id):
        return True
    else:
        return False

async def get_driver_by_id(id) -> Driver:
    obj = await Driver.objects.aget(id=id)
    return obj

async def create_driver(user_id, lang, firstname) -> Driver:
    driver = await Driver.objects.acreate(
        user_id = user_id, 
        lang = lang, firstname = firstname, name = firstname
    )
    return driver

async def get_factory() -> Factory:
    obj: Factory = await Factory.objects.aget(pk=1)
    return obj

@sync_to_async
def driver_of_task(task) -> Driver:
    return task.driver