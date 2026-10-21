from bot.driver.bot import *
from app.services.task_service import *
from app.models import FORCE_MAJEURE_TYPES
from bot.services.notification_service import *
from telegram import ForceReply


async def send_force_majeure_types(message, chat_id, task_id):
    i_buttons = []
    for force_majeure_type in FORCE_MAJEURE_TYPES:
        if force_majeure_type[0] in ['depot', 'factory']:
            # these force majeures are created by depot manager and factory
            continue
        i_buttons.append(
            InlineKeyboardButton(
                await get_word_driver(force_majeure_type[0], chat_id=chat_id),
                callback_data=f'force_majeure_type-{task_id}-{force_majeure_type[0]}'
            )
        )
    await message.reply_text(
        text=await get_word_driver('select force majeure type', chat_id=chat_id),
        reply_markup=InlineKeyboardMarkup([i_buttons])
    )


async def force_majeure_detected(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')

    await query.answer()
    await send_force_majeure_types(query.message, query.message.chat.id, task_id)


async def force_majeure_button(update: Update, context: CustomContext):
    # force majeure from persistent keyboard: use driver's active task
    if await is_group(update):
        return
    chat_id = update.message.chat.id
    driver: Driver = await Driver.objects.filter(user_id=chat_id).afirst()
    if not driver:
        return
    task: Task = await Task.objects.filter(driver=driver, is_complete=False).order_by('-id').afirst()
    if not task:
        await update.message.reply_text(await get_word_driver('no active task', chat_id=chat_id))
        return

    await send_force_majeure_types(update.message, chat_id, task.id)


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


# factory (warehouse manager) force majeure. Factory chat is a group,
# so ask with ForceReply: bot receives replies to its messages even in privacy mode
async def factory_force_majeure_detected(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    user = update.effective_user

    await set_user_state(user.id, States.WAITING_FACTORY_FORCEMAJEURE_REASON)
    await set_user_data_field(user.id, 'fm_factory_task_id', task_id)

    await query.answer()
    await query.message.reply_html(
        f"{user.mention_html()}, {lang_dict['send reason of forcemajeure'][1]}",
        reply_markup=ForceReply(selective=True)
    )


async def get_reason_of_the_factory_forcemajeure(update: Update, context: CustomContext):
    user = update.effective_user
    await set_user_data_field(user.id, 'fm_factory_reason', update.effective_message.text)
    await set_user_state(user.id, States.WAITING_FACTORY_FORCEMAJEURE_PHOTO)

    await update.effective_message.reply_html(
        lang_dict['send photo of forcemajeure depot'][1],
        reply_markup=ForceReply(selective=True)
    )


async def get_photo_of_the_factory_forcemajeure(update: Update, context: CustomContext):
    user = update.effective_user
    user_data = await get_user_data(user.id)
    task: Task = await get_task_by_id(int(user_data.get('fm_factory_task_id')))
    reason = user_data.get('fm_factory_reason')

    photo_bytes, file_name = await download_photo_as_bytes(update, context)
    force_majeure: ForceMajeure = await create_force_majeure(
        task, 'factory', photo_bytes, file_name, reason=reason
    )

    await clear_user_state(user.id)
    await delete_user_data_field(user.id, 'fm_factory_task_id')
    await delete_user_data_field(user.id, 'fm_factory_reason')

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            text=lang_dict['completed'][1],
            callback_data=f"factory_completed_force_majeure-{force_majeure.id}"
        )]]
    )
    await update.effective_message.reply_html(
        f"{lang_dict['depot force majeure started'][1]}\n\n"
        f"🚚 {await task.get_car}\n📝 {reason}",
        reply_markup=reply_markup
    )


async def factory_complete_force_majeure(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, force_majeure_id = data.split('-')
    force_majeure: ForceMajeure = await get_force_majeure_by_id(int(force_majeure_id))

    if not force_majeure.end_time:
        await complete_force_majeure(force_majeure)

    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(lang_dict['force majeure completed'][1])
