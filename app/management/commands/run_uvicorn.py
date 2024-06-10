from django.core.management.base import BaseCommand
from bot.driver.control.updater import application as driver_app
import asyncio
import signal
import uvicorn
from config import PORT

# This function will be called when a shutdown signal is received
def handle_shutdown(signal, frame):
    print("Received shutdown signal")
    # Stop the event loop
    loop = asyncio.get_event_loop()
    loop.stop()

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

async def serve():
    config = uvicorn.Config("core.asgi:application", host="127.0.0.1", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    # await server.serve()
    async with driver_app:
        await driver_app.start()
        await server.serve()
        await driver_app.stop()


class Command(BaseCommand):
    help = 'Start uvicron server'

    def handle(self, *args, **options):
        asyncio.run(
            serve()
        )
