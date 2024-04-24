import datetime
from django.core.management.base import BaseCommand
from managr.comms.models import NewsSource
from managr.comms.tasks import _run_spider_batch, _check_spider_status


class Command(BaseCommand):
    help = "Batch Spiders to run"

    def add_arguments(self, parser):
        parser.add_argument("batch_size", nargs="?", type=str, help="The URL to scrape (optional)")

    def handle(self, *args, **options):
        batch_size = options.get("batch_size", 10)
        schedule = datetime.datetime.now() + datetime.timedelta(hours=3)
        news = NewsSource.domain_list(True, False)
        for i in range(0, len(news), int(batch_size)):
            batch = news[i : i + batch_size]
            batch_url_list = ",".join(batch)
            _run_spider_batch(batch_url_list)
        _check_spider_status(batch_size, schedule=schedule)
