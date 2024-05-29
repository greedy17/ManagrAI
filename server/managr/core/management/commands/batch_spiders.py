from django.core.management.base import BaseCommand
from managr.core.models import CrawlerReport
from managr.comms.models import NewsSource
from managr.comms.tasks import _run_spider_batch


class Command(BaseCommand):
    help = "Batch Spiders to run"

    def add_arguments(self, parser):
        parser.add_argument("batch_size", nargs="?", type=int, help="The URL to scrape (optional)")

    def handle(self, *args, **options):
        batch_size = options["batch_size"] if options["batch_size"] is not None else 10
        news = NewsSource.domain_list(True, False)
        report = CrawlerReport.objects.create()
        for i in range(0, len(news), int(batch_size)):
            batch = news[i : i + batch_size]
            batch_url_list = ",".join(batch)
            _run_spider_batch(batch_url_list, priority=-1)
