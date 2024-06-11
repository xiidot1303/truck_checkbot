from app.services import *
from bot.models import DepotManager
from asgiref.sync import sync_to_async

@sync_to_async
def is_depot_manager_registred(user_id: int):
    if DepotManager.objects.filter(user_id=user_id):
        return True
    else:
        return False

async def create_depot_manager(user_id, lang, firstname) -> DepotManager:
    depot_manager = await DepotManager.objects.acreate(
        user_id = user_id,
        lang = lang, firstname = firstname, name = firstname
    )
    return depot_manager