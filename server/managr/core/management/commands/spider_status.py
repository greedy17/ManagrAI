import datetime
from django.core.management.base import BaseCommand
from managr.comms.models import NewsSource
from managr.comms.tasks import _run_spider_batch
from background_task.models import Task


class Command(BaseCommand):
    help = "Batch Spiders to run"

    def handle(self, *args, **options):
        batch_size = 10
        tasks = Task.objects.filter(task_name="managr.comms.tasks._run_spider_batch")
        locked_tasks = tasks.filter(locked_at__isnull=False)
        if len(locked_tasks):
            dt = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
            for task in locked_tasks:
                seconds_since_locked = dt - task.locked_at
                if seconds_since_locked.seconds >= 1500:
                    # params = task.params()[0]
                    task.delete()
                    # url_list = ",".join(params)
                    # _run_spider_batch(url_list)

        if not len(tasks):
            sources = NewsSource.domain_list(True)
            if len(sources):
                for i in range(0, len(sources), int(batch_size)):
                    batch = sources[i : i + int(batch_size)]
                    batch_url_list = ",".join(batch)
                    _run_spider_batch(batch_url_list)
