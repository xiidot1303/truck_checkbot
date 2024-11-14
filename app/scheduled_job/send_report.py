import io
import asyncio
from datetime import datetime, timedelta

from telegram import InputFile

from bot.models import ReportGroup
from app.views.task import create_task_report
from bot.services.driver_service import get_report_group
from bot.driver.control.updater import application as driver_app


async def send_report():
    now = datetime.now()
    today = now.strftime("%d.%m.%Y")
    yesterday = (now - timedelta(days=1)).strftime("%d.%m.%Y")

    file_report = io.BytesIO()
    wb = await create_task_report(yesterday, today)
    wb.save(file_report)
    file_report.seek(0)

    group: ReportGroup = await get_report_group()
    await driver_app.bot.send_document(
        group.tg_id_2,
        InputFile(file_report, filename=f"{now.strftime('%Y_%m_%d')}_.xlsx")
    )


def sync_send_report():
    asyncio.run(send_report())
