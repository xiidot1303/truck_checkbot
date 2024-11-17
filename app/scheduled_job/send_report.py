import io
import asyncio
from datetime import datetime, timedelta

from telegram import InputFile

from bot.models import ReportGroup
from app.views.task import create_task_report
from bot.services.driver_service import get_report_group
from bot.utils.bot_functions import driver_app, send_newsletter
from app.services.task_service import filter_completed_tasks_by_date_range


async def async_list(tasks):
    for task in tasks:
        yield task


async def send_report():
    now = datetime.now()
    today = now.strftime("%d.%m.%Y")
    yesterday = (now - timedelta(days=1)).strftime("%d.%m.%Y")

    tasks = await filter_completed_tasks_by_date_range(yesterday, today)
    group: ReportGroup = await get_report_group()
    async for task in tasks:
        file_report = io.BytesIO()
        wb = await create_task_report(yesterday, today, tasks=async_list([task]))
        wb.save(file_report)
        file_report.seek(0)

        driver = await task.get_driver
        car = await task.get_car

        await send_newsletter(
            driver_app.bot,
            group.tg_id_2,
            f"{driver}\n{car}",
            document=InputFile(file_report, filename=f"{now.strftime('%Y_%m_%d')}_.xlsx")
        )

        await asyncio.sleep(5)


def sync_send_report():
    asyncio.run(send_report())
