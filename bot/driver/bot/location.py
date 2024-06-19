from bot.driver.bot import *
from bot.services.driver_service import get_driver_by_update

async def update_driver_location(update: Update, context: CustomContext):
    message = update.message if update.message else update.edited_message
    if message.location.live_period:
        lat = message.location.latitude
        lon = message.location.longitude
        # get driver by update
        driver: Driver = await Driver.objects.aget(user_id = message.chat.id)
        driver.lat = lat
        driver.lon = lon
        await driver.asave()
    return