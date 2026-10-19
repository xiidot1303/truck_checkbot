from bot.depot_manager.bot import *
from bot.services.notification_service import *
from app.services.task_service import *


async def force_majeure_detected(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, taskevent_id = data.split('-')

    await set_user_state(update.effective_user.id, States.WAITING_FORCEMAJEURE_REASON)
    await set_user_data_field(update.effective_user.id, 'fm_taskevent_id', taskevent_id)

    await query.answer()
    await query.message.reply_text(
        await get_word('send reason of forcemajeure', query)
    )


async def get_reason_of_the_forcemajeure(update: Update, context: CustomContext):
    await set_user_data_field(update.effective_user.id, 'fm_reason', update.effective_message.text)
    await set_user_state(update.effective_user.id, States.WAITING_FORCEMAJEURE_PHOTO)

    await update.effective_message.reply_text(
        await get_word('send photo of forcemajeure depot', update)
    )


async def get_photo_of_the_forcemajeure(update: Update, context: CustomContext):
    user_id = update.effective_user.id
    user_data = await get_user_data(user_id)
    taskevent: TaskEvent = await get_taskevent_by_id(int(user_data.get('fm_taskevent_id')))
    reason = user_data.get('fm_reason')
    task: Task = await taskevent.get_task
    depot: Depot = await taskevent.get_depot()

    photo_bytes, file_name = await download_photo_as_bytes(update, context)
    force_majeure: ForceMajeure = await create_force_majeure(
        task, 'depot', photo_bytes, file_name, reason=reason, depot=depot
    )

    await clear_user_state(user_id)
    await delete_user_data_field(user_id, 'fm_taskevent_id')
    await delete_user_data_field(user_id, 'fm_reason')

    # controller is registered in driver bot, so send photo as bytes (file_id is bot specific)
    context.application.create_task(
        alert_controller_about_depot_force_majeure_notification(
            await get_driver_bot(), task, depot, reason, bytes(photo_bytes)
        )
    )

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            text=await get_word('completed', update),
            callback_data=f"depot_completed_force_majeure-{force_majeure.id}"
        )]]
    )
    await update.effective_message.reply_html(
        await get_word('depot force majeure started', update),
        reply_markup=reply_markup
    )


async def complete_force_majeure_by_depot(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, force_majeure_id = data.split('-')
    force_majeure: ForceMajeure = await get_force_majeure_by_id(int(force_majeure_id))

    if not force_majeure.end_time:
        await complete_force_majeure(force_majeure)

    await query.answer()
    await query.edit_message_text(
        await get_word('force majeure completed', query)
    )
