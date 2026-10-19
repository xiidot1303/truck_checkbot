from app.views import *
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from app.services.task_service import *
from django.db.models import Q


def format_fact_time(fact_time, schedule_datetime) -> str:
    # show day offset from the schedule date, e.g. "12:32 (+1)"
    if not fact_time:
        return ""
    result = fact_time.strftime('%H:%M')
    if schedule_datetime:
        day_offset = (fact_time.date() - schedule_datetime.date()).days
        if day_offset:
            result += f" ({day_offset:+d})"
    return result

# index of the first cell of each event in the report row
EVENT_COLUMNS = {
    'arrive_to_factory': 4,  # E
    'placing_in_warehouse': 7,  # H
    'in_factory': 10,  # K
    'arrive_to_depot': 16,  # Q
    'in_depot': 22,  # W
    'back_to_factory': 28,  # AC
}
EVENTS_LAST_COLUMN = 31  # AE

# summary tables under the main table: event type -> (table key, group by driver or branch)
SUMMARY_EVENTS = {
    'arrive_to_factory': ('driver_arrive', 'driver'),
    'in_depot': ('unloading', 'branch'),
    'arrive_to_depot': ('cargo_arrive', 'branch'),
}
SUMMARY_TABLES = [
    # (table key, title, first column)
    ('driver_arrive', "Хайдовчи йетиб бориш норматив буйича", 2),  # B
    ('unloading', "Юк тушириш норматив буйича", 8),  # H
    ('cargo_arrive', "Юк йетиб бориши норматив буйича", 14),  # N
]


def write_summary_table(ws, start_row: int, start_col: int, title: str, rows: dict):
    # rows: name -> [early hours, late hours]
    # layout: name (2 merged cells) | олдин | кечикиш
    border = Border(left=Side(style='thin'), right=Side(style='thin'),
                    top=Side(style='thin'), bottom=Side(style='thin'))
    title_fill = PatternFill(start_color="dce6f1", end_color="dce6f1", fill_type="solid")
    total_fill = PatternFill(start_color="ffff00", end_color="ffff00", fill_type="solid")

    ws.cell(row=start_row, column=start_col, value=title).font = Font(bold=True)
    for col in range(start_col, start_col + 4):
        ws.cell(row=start_row, column=col).fill = title_fill
    ws.merge_cells(start_row=start_row, start_column=start_col, end_row=start_row, end_column=start_col + 3)

    ws.cell(row=start_row + 1, column=start_col + 2, value="олдин")
    ws.cell(row=start_row + 1, column=start_col + 3, value="кечикиш")

    row = start_row + 2
    total_late = 0
    for name, (early, late) in rows.items():
        ws.cell(row=row, column=start_col, value=name)
        ws.merge_cells(start_row=row, start_column=start_col, end_row=row, end_column=start_col + 1)
        ws.cell(row=row, column=start_col + 2, value=round(early, 2))
        ws.cell(row=row, column=start_col + 3, value=round(late, 2))
        for col in range(start_col, start_col + 4):
            ws.cell(row=row, column=col).border = border
        total_late += late
        row += 1

    total_cell = ws.cell(row=row, column=start_col + 3, value=round(total_late, 2))
    total_cell.fill = total_fill
    total_cell.border = border


async def task_report_by_date(request):
    start_date = request.GET.get('created_at__range__gte')
    end_date = request.GET.get('created_at__range__lte')
    start_date = "10.10.2020" if not start_date or start_date == 'None' else start_date
    end_date = "10.10.2100" if not end_date or end_date == 'None' else end_date

    wb = await create_task_report(start_date, end_date)

    # Save the workbook to a response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="schedule_report.xlsx"'
    wb.save(response)
    return response


async def create_task_report(start_date: str, end_date: str, is_complete: bool = None, tasks=None) -> Workbook:
    # Create a new workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active

    # Define column headers (based on your data)
    headers = [
        ["Period", "Yo'nalish", "Mashina", "Haydovchi", "Haydovchi zavodga kelishi", "", "",
         "Avtomobilning tayyor mahsulotlar omboriga qo'yish", "", "",
         "Yuk ortilishi boshlanishi", "", "", "Yuk ortilishi tugatilishi", "", "", 
         "Manzilga yo'lga chiqqan vaqti", "", "", "Manzilga yetib borgan vaqti", "", "", 
         "Filialning yuk tushirish boshlanishi", "", "", "Filialning yuk tushirish tugatilishi", "", "",
         "Mashinaning zavodga qaytib kelishi", "", "", 
         "Fors-major", "", "", "Grafikdan jami kechikish"
        ],
        ["", "", "", "", "Grafik", "Fact", "Farq", "Grafik", "Fact", "Farq", 
         "Grafik", "Fact", "Farq", "Grafik", "Fact", "Farq", "Grafik", "Fact", "Farq", 
         "Grafik", "Fact", "Farq", "Grafik", "Fact", "Farq", 
         "Grafik", "Fact", "Farq", "Grafik", "Fact", "Farq", 
         "Remont", "Avariya", "Zapravka", ""]
    ]

    # Add the headers to the worksheet
    for header in headers:
        ws.append(header)

    # Query the database
    if not tasks:
        tasks = await filter_completed_tasks_by_date_range(start_date, end_date, is_complete=is_complete)

    # Example: Add your tasks to the worksheet
    last_period = date(1900, 1, 1)
    # summary: table key -> {driver or branch: [early hours, late hours]}
    summary = {key: {} for key, _, _ in SUMMARY_TABLES}
    # events without depot are repeated for every depot of the task, count them once
    summary_counted_events = set()
    async for task in tasks:
        task: Task
        async for taskdepot in task.depots.filter():
            taskdepot: Depot
            driver = await task.get_driver
            row_data = [
                task.created_at.strftime("%d.%m.%Y") if last_period != task.created_at.date() else "",
                taskdepot.branch,
                await task.get_car, driver
            ]
            summary_groups = {'driver': driver, 'branch': taskdepot.branch or ""}
            for key, group in SUMMARY_EVENTS.values():
                summary[key].setdefault(summary_groups[group], [0, 0])
            is_milktanker = await task.is_task_car_milktanker
            # every event has fixed cells in the row, so missing events don't shift the columns
            row_data += [""] * (EVENTS_LAST_COLUMN - len(row_data))
            last_event = None
            async for event in task.events.filter(
                Q(depot=taskdepot) | Q(depot=None)
            ).order_by('id'):
                event: TaskEvent
                # in_depot of milktanker is not shown in report
                if is_milktanker and event.event_type == 'in_depot':
                    continue
                has_schedule = bool(event.end_time and event.schedule_datetime)
                difference = await event.difference_with_schedule if has_schedule else ""
                if event.event_type in ['in_factory', 'in_depot', 'arrive_to_depot']:
                    # insert double data start and end times
                    data = [
                        "",
                        event.start_time.strftime('%H:%M') if event.start_time else "",
                        "",

                        event.schedule_datetime.strftime("%H:%M") if event.schedule_datetime else "",
                        format_fact_time(event.end_time, event.schedule_datetime),
                        difference
                    ]
                else:
                    data = [
                        event.schedule_datetime.strftime("%H:%M") if event.schedule_datetime else "",
                        format_fact_time(event.end_time, event.schedule_datetime),
                        difference
                    ]
                column = EVENT_COLUMNS[event.event_type]
                row_data[column:column + len(data)] = data

                if has_schedule and event.event_type in SUMMARY_EVENTS and event.id not in summary_counted_events:
                    summary_counted_events.add(event.id)
                    key, group = SUMMARY_EVENTS[event.event_type]
                    # positive difference - early, negative - late
                    summary[key][summary_groups[group]][0 if difference > 0 else 1] += difference

                # the latest completed event shows the accumulated delay of the whole trip
                if has_schedule and (not last_event or event.end_time > last_event.end_time):
                    last_event = event

            # set force majeures of the task (hours)
            force_majeures = [
                fm async for fm in task.forcemajeures.filter(spend_time__isnull=False)
            ]
            force_majeures_by_type = {}
            for fm in force_majeures:
                force_majeures_by_type[fm.type] = force_majeures_by_type.get(fm.type, 0) + fm.spend_time / 60
            for fm_type in ['repair', 'accident', 'refueling']:
                row_data += [round(force_majeures_by_type[fm_type], 2) if force_majeures_by_type.get(fm_type) else ""]

            # total delay = delay of the latest event minus force majeures happened before it
            if last_event:
                delay = min(await last_event.difference_with_schedule, 0)
                excused = sum(
                    fm.spend_time / 60 for fm in force_majeures
                    if fm.end_time and fm.end_time <= last_event.end_time
                )
                total_delay = round(min(delay + excused, 0), 2)
            else:
                total_delay = ""
            row_data += [total_delay]
            ws.append(row_data)

        last_period = task.created_at.date()
    # Style the headers
    header_font = Font(bold=True)
    for col in range(1, 33):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Set column widths for better readability
    column_widths = [12, 12, 12, 20, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 
                     11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 25]
    for i, width in enumerate(column_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Merge cells
    ws.merge_cells(start_row=1, start_column=5, end_row=1, end_column=7)
    ws.merge_cells(start_row=1, start_column=8, end_row=1, end_column=10)
    ws.merge_cells(start_row=1, start_column=11, end_row=1, end_column=13)
    ws.merge_cells(start_row=1, start_column=14, end_row=1, end_column=16)
    ws.merge_cells(start_row=1, start_column=17, end_row=1, end_column=19)
    ws.merge_cells(start_row=1, start_column=20, end_row=1, end_column=22)
    ws.merge_cells(start_row=1, start_column=23, end_row=1, end_column=25)
    ws.merge_cells(start_row=1, start_column=26, end_row=1, end_column=28)
    ws.merge_cells(start_row=1, start_column=29, end_row=1, end_column=31)
    ws.merge_cells(start_row=1, start_column=32, end_row=1, end_column=34)

    ws.merge_cells(start_row=1, start_column=1, end_row=2, end_column=1)
    ws.merge_cells(start_row=1, start_column=2, end_row=2, end_column=2)
    ws.merge_cells(start_row=1, start_column=3, end_row=2, end_column=3)
    ws.merge_cells(start_row=1, start_column=4, end_row=2, end_column=4)
    ws.merge_cells(start_row=1, start_column=35, end_row=2, end_column=35)

    # Define border style
    border_style = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    # Apply borders to the entire table
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            cell.border = border_style

    # color the fields
    for row in range(1, ws.max_row + 1):
        for col in range(5, 8):  # Columns E, F, G
            ws.cell(row=row, column=col).fill = PatternFill(start_color="e2f0d9", end_color="e2f0d9", fill_type="solid")
        for col in range(8, 11):  # Columns H, I, J
            ws.cell(row=row, column=col).fill = PatternFill(start_color="dae3f4", end_color="dae3f4", fill_type="solid")
        for col in range(11, 17):  # Columns K, L, M, N, O, P
            ws.cell(row=row, column=col).fill = PatternFill(start_color="ffdae3", end_color="ffdae3", fill_type="solid")
        for col in range(17, 23):  # Columns Q, R, S, T, U, V
            ws.cell(row=row, column=col).fill = PatternFill(start_color="f4ffda", end_color="f4ffda", fill_type="solid")
        for col in range(23, 29):  # Columns W, X, Y, Z, AA, AB
            ws.cell(row=row, column=col).fill = PatternFill(start_color="e5d6ff", end_color="e5d6ff", fill_type="solid")
        for col in range(29, 32):  # Columns AC, AD, AE
            ws.cell(row=row, column=col).fill = PatternFill(start_color="e2f0d9", end_color="e2f0d9", fill_type="solid")
        for col in range(32, 35):  # Columns AF, AG, AH
            ws.cell(row=row, column=col).fill = PatternFill(start_color="dae3f4", end_color="dae3f4", fill_type="solid")
        for col in range(35, 36):  # Columns AI
            ws.cell(row=row, column=col).fill = PatternFill(start_color="fffbe5", end_color="fffbe5", fill_type="solid")

    # summary tables under the main table (added after styling so they keep their own style)
    summary_start_row = ws.max_row + 3
    for key, title, start_col in SUMMARY_TABLES:
        write_summary_table(ws, summary_start_row, start_col, title, summary[key])

    return wb
