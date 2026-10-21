from bot.depot_manager.bot import *
from bot.services.notification_service import *
from app.services.task_service import *
from telegram import ForceReply
from bot.models import DepotManager
from django.utils import timezone
from datetime import timedelta


@sync_to_async
def get_cars_in_depot(tg_id) -> list[tuple[TaskEvent, str]]:
    # cars that arrived to manager's depots and are not unloaded yet
    arrive_events = TaskEvent.objects.filter(
        event_type='arrive_to_depot',
        depot__tg_id=str(tg_id),
        end_time__isnull=False,
        task__is_complete=False,
        task__created_at__gte=timezone.now() - timedelta(days=7)
    ).select_related('task__car', 'depot').order_by('-id')

    result = []
    for arrive_event in arrive_events:
        in_depot_event = TaskEvent.objects.filter(
            task=arrive_event.task, depot=arrive_event.depot, event_type='in_depot'
        ).first()
        if in_depot_event and in_depot_event.end_time:
            # already unloaded
            continue
        result.append((in_depot_event or arrive_event, f"{arrive_event.task.car}"))
    return result


async def ask_reason_of_forcemajeure(update: Update, message, taskevent_id):
    await set_user_state(update.effective_user.id, States.WAITING_FORCEMAJEURE_REASON)
    await set_user_data_field(update.effective_user.id, 'fm_taskevent_id', taskevent_id)

    # ForceReply: in groups bot receives replies to its messages even in privacy mode
    await message.reply_html(
        f"{update.effective_user.mention_html()}, "
        f"{await get_word('send reason of forcemajeure', chat_id=message.chat.id)}",
        reply_markup=ForceReply(selective=True)
    )


async def force_majeure_detected(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, taskevent_id = data.split('-')

    await query.answer()
    await ask_reason_of_forcemajeure(update, query.message, taskevent_id)


async def force_majeure_button(update: Update, context: CustomContext):
    # force majeure from persistent keyboard: find cars in manager's depots
    chat_id = update.message.chat.id
    if not await DepotManager.objects.filter(user_id=chat_id).aexists():
        return
    cars = await get_cars_in_depot(chat_id)

    if not cars:
        await update.message.reply_text(await get_word('no cars in depot', update))
        return
    if len(cars) == 1:
        taskevent, car = cars[0]
        await ask_reason_of_forcemajeure(update, update.message, taskevent.id)
        return

    i_buttons = [
        [InlineKeyboardButton(text=car, callback_data=f"depot_force_majeure-{taskevent.id}")]
        for taskevent, car in cars
    ]
    await update.message.reply_text(
        await get_word('select car of forcemajeure', update),
        reply_markup=InlineKeyboardMarkup(i_buttons)
    )


async def get_reason_of_the_forcemajeure(update: Update, context: CustomContext):
    await set_user_data_field(update.effective_user.id, 'fm_reason', update.effective_message.text)
    await set_user_state(update.effective_user.id, States.WAITING_FORCEMAJEURE_PHOTO)

    await update.effective_message.reply_text(
        await get_word('send photo of forcemajeure depot', update),
        reply_markup=ForceReply(selective=True)
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
