from bot.driver.bot import *
from app.services.task_service import *
from app.models import FORCE_MAJEURE_TYPES
from bot.services.notification_service import *


async def force_majeure_detected(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    task: Task = await get_task_by_id(int(task_id))

    i_buttons = []
    for force_majeure_type in FORCE_MAJEURE_TYPES:
        i_buttons.append(
            InlineKeyboardButton(
                await get_word_driver(force_majeure_type[0], query),
                callback_data=f'force_majeure_type-{task_id}-{force_majeure_type[0]}'
            )
        )
    await query.answer()
    await query.message.reply_text(
        text=await get_word_driver('select force majeure type', query),
        reply_markup=InlineKeyboardMarkup([i_buttons])
    )


async def force_majeure_type_selected(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id, force_majeure_type = data.split('-')
    task: Task = await get_task_by_id(int(task_id))

    await query.edit_message_text(
        await get_word_driver('send photo of forcemajeure', query),
        reply_markup=None
    )
    await set_user_state(update.effective_user.id, States.WAITING_FORCEMAJEURE_PHOTO)
    await set_user_data_field(update.effective_user.id, 'task_id', task_id)
    await set_user_data_field(update.effective_user.id, 'force_majeure_type', force_majeure_type)
    return


async def get_photo_of_the_forcemajeure(update: Update, context: CustomContext):
    # get user data
    user_data = await get_user_data(update.effective_user.id)
    force_majeure_type = user_data.get('force_majeure_type', None)
    task_id = user_data.get('task_id', None)
    task: Task = await get_task_by_id(int(task_id))
    # send message to controller
    photo_id = update.effective_message.photo[-1].file_id
    context.application.create_task(
        alert_controller_about_force_majeure_notification(
            context.bot, task, force_majeure_type, photo_id
        )
    )

    await update.effective_message.reply_html(
        await get_word_driver('wait response of the controller', update)
    )


async def controller_confirm_force_majeure(update: Update, context: CustomContext):
    # photo_path = await save_and_get_photo(update, context, 'forcemajeures')
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id, force_majeure_type = data.split('-')
    task: Task = await get_task_by_id(int(task_id))
    # get photo from message if exist
    if update.effective_message.photo:
        photo_bytes, file_name = await download_photo_as_bytes(update, context)
    else:
        photo_bytes, file_name = None, None
    # create force majeure record
    force_majeure: ForceMajeure = await create_force_majeure(task, force_majeure_type, photo_bytes, file_name)

    await query.answer(
        lang_dict['force majeure confirmed'][1]
    )

    # alert driver about confirmed force majeure
    context.application.create_task(
        alert_driver_about_confirmed_force_majeure_notification(
            context.bot, force_majeure
        )
    )
    await query.edit_message_reply_markup(reply_markup=None)


async def driver_complete_force_majeure(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, force_majeure_id = data.split('-')
    force_majeure: ForceMajeure = await get_force_majeure_by_id(int(force_majeure_id))

    await complete_force_majeure(force_majeure)
    await bot_delete_message(query, context)