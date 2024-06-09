from django.core.management.base import BaseCommand
from app.scheduled_job.one_c_job import update_cars

class Command(BaseCommand):
    help = 'Command for updating cars by getting data from 1C'

    def handle(self, *args, **options):
        update_cars()
        print("Cars are updated succesfully")