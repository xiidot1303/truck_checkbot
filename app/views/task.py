from app.views import *
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from app.services.task_service import *

async def task_report_by_date(request):
    # Create a new workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active

    # Define column headers (based on your data)
    headers = [
        ["Period", "Yo'nalish", "Mashina", "Haydovchi", "Mashina skladda bo'lishi", "", "", "Yuk ortilishi tugatilishi", "", "", "Manzilga yetib borish jarayoni", "", "", "Filialning yukni tushirish jarayoni", "", "", "Mashinaning zavodga qaytib kelishi", "", "", "Grafikdan jami kechikish"],
        ["", "", "", "", "Grafik", "Fact", "Farq", "Grafik", "Fact", "Farq",
        "Grafik", "Fact", "Farq", "Grafik", "Fact", "Farq", "Grafik", "Fact", "Farq", "Grafikdan jami kechikish"]
        ]

    # Add the headers to the worksheet
    for header in headers:
        ws.append(header)
    
    # Query the database
    tasks = await filter_completed_tasks()  # Replace 'YourModel' with your actual model name

    # Example: Add your tasks to the worksheet
    last_period = date(1900, 1, 1)
    async for task in tasks:
        task: Task
        async for taskdepot in task.depots.filter(): 
            taskdepot: TaskDepot
            row_data = [
                task.created_at.strftime("%d.%m.%Y") if last_period != task.created_at.date() else "", 
                taskdepot.branch, 
                await task.get_car, await task.get_driver
            ]
            async for event in task.events.filter():
                event: TaskEvent
                data = [
                    await event.spend_time,
                    event.duration_norm,
                    await event.difference_with_norm
                ]
                row_data += data
            ws.append(row_data)

        last_period = task.created_at.date()
    # Style the headers
    header_font = Font(bold=True)
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Set column widths for better readability
    column_widths = [12, 12, 12, 20, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 18]
    for i, width in enumerate(column_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Save the workbook to a response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="schedule_report.xlsx"'
    wb.save(response)
    return response