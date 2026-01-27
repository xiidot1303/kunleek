from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from app.scheduled_job import *
from bot.scheduled_job import mailing
from bot.services.redis_service import save_langs_to_redis
from asgiref.sync import async_to_sync
from app.scheduled_job import billz_job

class jobs:
    scheduler = BackgroundScheduler(timezone='Asia/Tashkent')
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)
    # scheduler.add_job(, 'interval', minutes=5)
    scheduler.add_job(
        async_to_sync(mailing.send_message), 
        'interval', minutes=5)
    scheduler.add_job(save_langs_to_redis, 'interval', minutes=20)

    # scheduler.add_job(billz_job.fetch_categories, 'interval', minutes=120)
    scheduler.add_job(billz_job.fetch_products, 'interval', minutes=2)
    scheduler.add_job(billz_job.fetch_shops, 'interval', minutes=20)
