import io
import asyncio
from datetime import datetime, timedelta

from telegram import InputFile

from bot.models import ReportGroup
from app.views.task import create_task_report
from bot.services.driver_service import get_report_group
from bot.utils.bot_functions import driver_app, send_newsletter

async def send_report():
    now = datetime.now()
    today = now.strftime("%d.%m.%Y")
    yesterday = (now - timedelta(days=1)).strftime("%d.%m.%Y")

    file_report = io.BytesIO()
    wb = await create_task_report(yesterday, today)
    wb.save(file_report)
    file_report.seek(0)

    group: ReportGroup = await get_report_group()
    await send_newsletter(
        driver_app.bot,
        group.tg_id_2,
        None,
        document=InputFile(file_report, filename=f"{now.strftime('%Y_%m_%d')}_.xlsx")
    )


def sync_send_report():
    asyncio.run(send_report())
