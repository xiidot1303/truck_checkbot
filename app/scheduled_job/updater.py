from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from app.scheduled_job import one_c_job
from asgiref.sync import async_to_sync

class jobs:
    scheduler = BackgroundScheduler(timezone='Asia/Tashkent')
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)
    # scheduler.add_job(one_c_job.update_depots, 'interval', minutes=20)
    scheduler.add_job(one_c_job.update_cars, 'interval', minutes=20)
