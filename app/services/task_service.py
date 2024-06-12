from app.services import *
from app.models import Task, TaskEvent

async def get_task_by_id(id) -> Task:
    obj = await Task.objects.aget(id=id)
    return obj

async def create_taskevent(task: Task, event_type) -> TaskEvent:
    start_time = await datetime_now()
    obj: TaskEvent = await TaskEvent.objects.acreate(
        task = task, event_type = event_type, start_time = start_time
    )
    return obj

async def get_taskevent_by_task_and_event_type(task: Task, event_type) -> TaskEvent:
    obj = await TaskEvent.objects.aget(
        task = task, event_type = event_type
    )
    return obj

async def complete_taskevent(taskevent: TaskEvent):
    end_time = await datetime_now()
    taskevent.end_time = end_time
    await taskevent.asave()
    return