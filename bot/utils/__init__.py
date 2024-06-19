from bot.utils.bot_functions import *
import math

async def get_callback_query_data(update):
    data = await update.data
    *args, result = str(data).split('_')
    return result

async def get_location_coordinates(l):
    return l['latitude'], l['longitude']

async def split_text_and_text_id(msg):
    return msg.split('<>?')

async def get_last_msg_and_markup(context):
    return await context.user_data['last_msg'], await context.user_data['last_markup'] if 'last_markup' in context.user_data else None

async def remove_inline_keyboards_from_last_msg(update, context):
    try:
        last_msg, markup = await get_last_msg_and_markup(context)
        await bot_edit_message_reply_markup(update, context, last_msg.message_id)
        return True
    except:
        return None

async def is_group(update):
    if update.message.chat.type == 'group' or update.message.chat.type == 'supergroup':
        return True
    return False

async def save_and_get_photo(update, context):
    bot = context.bot
    photo_id = await bot.getFile(update.message.photo[-1].file_id)
    *args, file_name = str(photo_id.file_path).split('/')
    d_photo = await photo_id.download('files/photos/{}'.format(file_name))
    return str(d_photo).replace('files/', '')

async def set_last_msg_and_markup(context, msg, markup=None):
    context.user_data['last_msg'] = msg
    context.user_data['last_markup'] = markup

async def calc_distance_of_two_points(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points 
    on the Earth's surface given their latitude and longitude.\n
    The result is in meters.
    """
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    r = 6371.0
    
    # Calculate the result
    distance = r * c
    distance_m = distance * 1000
    return distance_m