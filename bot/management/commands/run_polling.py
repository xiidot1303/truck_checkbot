from django.core.management.base import BaseCommand
from bot.driver.control.updater import application as driver_app
from bot.depot_manager.control.updater import application as depot_manager_app
import asyncio

class Command(BaseCommand):
    help = 'Command to polling bot'

    def add_arguments(self, parser):
        # Adding a positional argument
        parser.add_argument('bot', type=str, help='Bot name')

    def handle(self, *args, **options):
        bot = options['bot']
        if bot == 'driver':
            asyncio.run(
                driver_app.run_polling()
            )
        elif bot == 'depot_manager':
            asyncio.run(
                depot_manager_app.run_polling()
            )
        else:
            print("Bot not found")
        