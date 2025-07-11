from django.core.management.base import BaseCommand
from app.scheduled_job.updater import jobs

class Command(BaseCommand):
    help = 'Run scheduled jobs'

    def handle(self, *args, **kwargs):
        jobs.scheduler.start()
        self.stdout.write(self.style.SUCCESS('Successfully started scheduled jobs'))

        import time
        try:
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            jobs.scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS('Scheduler stopped!'))