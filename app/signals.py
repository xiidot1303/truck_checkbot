from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import *
from bot.services.notification_service import *
from asgiref.sync import async_to_sync
from bot.driver.control.updater import application as driver_app
from bot.depot_manager.control.updater import application as depot_manager_app

@receiver(post_save, sender=Task)
def task_created(sender, instance, created, **kwargs):
    if created:
        # This code runs after a new Task instance is created
        # send message to driver about new task
        async_to_sync(alert_driver_about_new_task_notification)(driver_app.bot, instance)
        