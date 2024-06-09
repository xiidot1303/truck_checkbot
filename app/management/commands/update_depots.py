from django.core.management.base import BaseCommand
from app.scheduled_job.one_c_job import update_depots

class Command(BaseCommand):
    help = 'Command for updating depots by getting data from 1C'

    def handle(self, *args, **options):
        update_depots()
        print("depots are updated succesfully")