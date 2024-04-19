import math
from django.core.management.base import BaseCommand
from managr.comms.models import NewsSource
from managr.comms.tasks import _run_spider_batch


class Command(BaseCommand):
    help = "Batch Spiders to run"

    def handle(self, *args, **options):
        batch_size = 200
        news = NewsSource.domain_list(True, False)
        for i in range(0, len(news), batch_size):
            batch = news[i : i + batch_size]
            batch_url_list = ",".join(batch)
            _run_spider_batch(batch_url_list)
