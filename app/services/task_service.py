from app.services import *
from app.models import Task, TaskEvent, Depot, TaskDepot, EvenDurationNorm
from django.utils.timezone import now
import pandas as pd
import os
from django.conf import settings
from asgiref.sync import sync_to_async

async def get_task_by_id(id) -> Task:
    obj = await Task.objects.aget(id=id)
    return obj

async def get_taskevent_by_id(id) -> TaskEvent:
    obj = await TaskEvent.objects.aget(id=id)
    return obj

async def create_taskevent(task: Task, event_type, depot = None) -> TaskEvent:
    start_time = await datetime_now()
    obj: TaskEvent = await TaskEvent.objects.acreate(
        task = task, event_type = event_type, start_time = start_time
    )
    obj.depot = depot
    await obj.asave()
    return obj

async def get_taskevent_by_task_and_event_type(task: Task, event_type) -> TaskEvent:
    obj = await TaskEvent.objects.aget(
        task = task, event_type = event_type
    )
    return obj

async def complete_taskevent(taskevent: TaskEvent):
    end_time = await datetime_now()
    taskevent.end_time = end_time
    # set duration norm 
    try:
        duration_norm = await EvenDurationNorm.objects.aget(event_type = taskevent.event_type, depot = taskevent.depot)
        taskevent.duration_norm = duration_norm.duration
    except:
        None

    await taskevent.asave()
    return

async def get_taskdepot_by_task_and_depot(task: Task, depot: Depot) -> TaskDepot:
    obj = await TaskDepot.objects.aget(task = task, depot = depot)
    return obj

async def filter_completed_tasks():
    query = Task.objects.filter(is_complete = True)
    return query

@sync_to_async
def generate_excel_report_of_taks(task: Task):
    # Filter TaskEvent data based on some criteria
    task_events = task.events.all()

    # Create a list of dictionaries containing the data
    data = []
    for event in task_events:
        delta = event.end_time - event.start_time
        depot_title = f" ({event.depot})" if event.depot else ""
        data.append({
            '': event.get_event_type_display() + depot_title,
            'Время начала': event.start_time,
            'Конечное время': event.end_time,
            'Пройденное время (Минуты)': round(delta.seconds / 60, 2),
            'Норма (Минуты)': event.duration_norm
        })

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data)

    # Create a new DataFrame to add information at the top
    top_info = pd.DataFrame({
        'A': ['Дата', 'Машина', 'Водитель'], 
        'B': [now().strftime('%Y-%m-%d %H:%M:%S'), task.car, task.driver.name]
    })

    # Define the file path
    file_name = f'taskreport_{task.id}.xlsx'
    file_path = os.path.join(f"{settings.MEDIA_ROOT}/reports", file_name)

    # Ensure the directory exists
    os.makedirs(f"{settings.MEDIA_ROOT}/reports", exist_ok=True)

    # Generate and save the Excel file
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        top_info.to_excel(writer, index=False, header=False, sheet_name='События задания', startrow=0)
        df.to_excel(writer, index=False, sheet_name='События задания', startrow=4)  # Start data from row 3 to leave space for top_info
    return file_path
