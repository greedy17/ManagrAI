import datetime
from django.core.management.base import BaseCommand
from managr.comms.models import NewsSource
from managr.comms.tasks import _run_spider_batch, _check_spider_status


class Command(BaseCommand):
    help = "Batch Spiders to run"

    def handle(self, *args, **options):
        schedule = datetime.datetime.now() + datetime.timedelta(hours=3)
        batch_size = 50
        news = NewsSource.domain_list(True, False)
        for i in range(0, len(news), batch_size):
            batch = news[i : i + batch_size]
            batch_url_list = ",".join(batch)
            _run_spider_batch(batch_url_list)
        _check_spider_status(schedule=schedule)
