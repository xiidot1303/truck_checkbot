from django.core.management.base import BaseCommand
from bot.driver.control.updater import delete_webhook as driver_bot_delete_webhook
from bot.depot_manager.control.updater import delete_webhook as depot_manager_bot_delete_webhook
import asyncio

class Command(BaseCommand):
    help = 'Command that delete webhook'

    def add_arguments(self, parser):
        # Adding a positional argument
        parser.add_argument('bot', type=str, help='Bot name')

    def handle(self, *args, **options):
        bot = options['bot']
        if bot == 'driver':
            asyncio.run(
                driver_bot_delete_webhook()
            )
        elif bot == 'depot_manager':
            asyncio.run(
                depot_manager_bot_delete_webhook()
            )
        else:
            print("Bot not found")