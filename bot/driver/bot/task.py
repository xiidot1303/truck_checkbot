from bot.driver.bot import *
from bot.services.driver_service import *
from app.services.car_service import get_car_by_tg_id, Car
from app.services.task_service import *
from bot.services.notification_service import *
from bot.depot_manager.control.updater import application as _depot_manager_app

async def received_new_task(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    task: Task = await get_task_by_id(int(task_id))
    # create taskevent about driver arriving to factory
    taskevent: TaskEvent = await create_taskevent(task, 'arrive_to_factory')
    
    # ask from driver about telling when arrive to the point and ask live location
    await bot_send_message(
        query,
        context,
        await get_word('send live location', query)
    )

    markup = await arrived_keyboard(query, f'driver_arrived_to_factory-{task_id}', task_id)
    await bot_send_message(
        query,
        context,
        await get_word('click button after arrive to factory', query),
        reply_markup=markup
    )
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

async def driver_arrived_to_factory(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    task: Task = await get_task_by_id(int(task_id))
    # get driver by update
    driver: Driver = await get_driver_by_update(query)
    # get factory
    factory: Factory = await get_factory()
    # check driver is arrived to factory
    if await is_driver_arrived_to_address(driver.lat, driver.lon, factory.lat, factory.lon):
        # continue
        pass
    else:
        await query.answer(
            text = await get_word('your location is wrong', query),
            show_alert=True,
        )
        return

    # get taskevent about driver arriving to factory
    taskevent: TaskEvent = await get_taskevent_by_task_and_event_type(task, 'arrive_to_factory')
    # complete this taskevent
    await complete_taskevent(taskevent)

    # send message to driver that have to arrive to warehouse
    markup = await arrived_keyboard(query, f'driver_arrived_to_warehouse-{task.id}', task.id)
    await bot_send_message(
        query,
        context,
        await get_word('arrive to warehouse', query),
        reply_markup=markup
    )

    # create new taskevent about placing car in warehouse
    await create_taskevent(task, 'placing_in_warehouse')

    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)


async def driver_arrived_to_warehouse(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    task: Task = await get_task_by_id(int(task_id))
    # get driver by update
    driver: Driver = await get_driver_by_update(query)

    # send message to factory man that driver is arriving
    context.application.create_task(
        alert_factory_about_driver_arriving_notification(context.bot, task)
    )
    await query.answer(
        await get_word('wait for the load', query),
    )
    await query.edit_message_reply_markup(reply_markup=None)
    

async def factory_received_driver(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    task: Task = await get_task_by_id(int(task_id))
    # get taskevent about driver arriving to factory
    taskevent: TaskEvent = await get_taskevent_by_task_and_event_type(task, 'placing_in_warehouse')
    # complete this taskevent
    await complete_taskevent(taskevent)

    # create new taskevent about car waiting in factory
    await create_taskevent(task, 'in_factory')
    # send message to driver that factory received your car
    context.application.create_task(
        alert_driver_about_car_in_factory_notification(context.bot, task)
    )
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)


async def driver_received_car_from_factory(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    task: Task = await get_task_by_id(int(task_id))
    # get taskevent about car waiting in factory
    taskevent: TaskEvent = await get_taskevent_by_task_and_event_type(task, 'in_factory')
    # complete this taskevent
    await complete_taskevent(taskevent)

    depot: Depot = await task.get_next_depot
    # get task depot
    taskdepot = await get_taskdepot_by_task_and_depot(task, depot)
    # update current depot index
    task.current_depot_index = taskdepot.order
    await task.asave()
    # create new taskevent about driver arrive to depot
    taskevent: TaskEvent = await create_taskevent(task, 'arrive_to_depot', depot=depot)

    # ask from driver about telling when arrive to the depot
    markup = await arrived_keyboard(query, f'driver_arrived_to_depot-{taskevent.id}', task_id)
    address = f"{depot.branch}, {depot.title}"
    
    await bot_send_message(
        query,
        context,
        await drivers_next_address_string(query.message.chat.id, address),
        reply_markup=markup
    )
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)


async def driver_arrived_to_depot(update: Update, context: CustomContext):
    @sync_to_async
    def get_task_of_taskevent(taskevent: TaskEvent) -> Task:
        return taskevent.task

    @sync_to_async
    def get_depot_of_taskevent(taskevent: TaskEvent) -> Depot:
        return taskevent.depot

    query: CallbackQuery = update.callback_query
    data = query.data
    *args, taskevent_id = data.split('-')
    taskevent: TaskEvent = await get_taskevent_by_id(taskevent_id)
    task: Task = await get_task_of_taskevent(taskevent)
    depot: Depot = await get_depot_of_taskevent(taskevent)
    # get driver by update
    driver: Driver = await get_driver_by_update(query)
    # check driver is arrived to factory
    if await is_driver_arrived_to_address(driver.lat, driver.lon, depot.lat, depot.lon):
        # continue
        pass
    else:
        await query.answer(
            text = await get_word('your location is wrong', query),
            show_alert=True,
        )
        return

    # send message to depot manager that driver is arriving to depot
    context.application.create_task(
        alert_depot_manager_about_driver_arriving_notification(
            _depot_manager_app.bot, task, depot, taskevent
        )
    )
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)


async def driver_received_car_from_depot(update: Update, context: CustomContext):
    @sync_to_async
    def get_task_of_taskevent(taskevent: TaskEvent) -> Task:
        return taskevent.task
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, taskevent_id = data.split('-')
    taskevent: TaskEvent = await get_taskevent_by_id(taskevent_id)
    task: Task = await get_task_of_taskevent(taskevent)
    # complete this taskevent
    await complete_taskevent(taskevent)

    depot: Depot = await task.get_next_depot
    if depot:
        # get task depot
        taskdepot = await get_taskdepot_by_task_and_depot(task, depot)
        # update current depot index
        task.current_depot_index = taskdepot.order
        await task.asave()

        # create new taskevent about driver arrive to depot
        taskevent: TaskEvent = await create_taskevent(task, 'arrive_to_depot', depot=depot)
        # ask from driver about telling when arrive to the depot
        markup = await arrived_keyboard(query, f'driver_arrived_to_depot-{taskevent.id}', task.id)
        address = f"{depot.branch}, {depot.title}"
        await bot_send_message(
            query,
            context,
            await drivers_next_address_string(query.message.chat.id, address),
            reply_markup=markup
        )
    else:
        # create taskevent about driver back to factory
        taskevent: TaskEvent = await create_taskevent(task, 'back_to_factory')
        # ask from driver about telling when back to factory
        markup = await arrived_keyboard(query, f'driver_back_to_factory-{task.id}', task.id)
        # send message to driver that have to back to factory
        await bot_send_message(
            query,
            context,
            await get_word('back to factory', query),
            reply_markup=markup
        )

    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)


async def driver_back_to_factory(update: Update, context: CustomContext):
    query: CallbackQuery = update.callback_query
    data = query.data
    *args, task_id = data.split('-')
    task: Task = await get_task_by_id(int(task_id))
    # get driver by update
    driver: Driver = await get_driver_by_update(query)
    # get factory
    factory: Factory = await get_factory()
    # check driver is arrived to factory
    if await is_driver_arrived_to_address(driver.lat, driver.lon, factory.lat, factory.lon):
        # continue
        pass
    else:
        await query.answer(
            text = await get_word('your location is wrong', query),
            show_alert=True,
        )
        return

    # get taskevent about driver arriving to factory
    taskevent: TaskEvent = await get_taskevent_by_task_and_event_type(task, 'back_to_factory')
    # complete this taskevent
    await complete_taskevent(taskevent)

    # end task
    task.is_complete = True
    await task.asave()
    # generate excel report
    excel_file_path = await generate_excel_report_of_taks(task)
    # send report to group
    context.application.create_task(
        send_report_of_task_newsletter(
            context.bot,
            task,
            excel_file_path
        )
    )
    # send message to driver that task completed successfully
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await bot_send_message(
        query,
        context,
        await get_word('task completed successfully', query),
    )