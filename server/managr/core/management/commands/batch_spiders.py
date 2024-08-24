from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from managr.core.models import CrawlerReport
from managr.comms.models import NewsSource
from managr.comms.tasks import _run_spider_batch
from managr.slack.helpers.utils import send_to_error_channel


class Command(BaseCommand):
    help = "Batch Spiders to run"

    def add_arguments(self, parser):
        parser.add_argument("batch_size", nargs="?", type=int, help="The URL to scrape (optional)")

    def handle(self, *args, **options):
        batch_size = options["batch_size"] if options["batch_size"] is not None else 10
        news = NewsSource.domain_list(True, False)
        report = CrawlerReport.objects.create()
        d = datetime.now()
        counter = 0
        for i in range(0, len(news), int(batch_size)):
            counter += 1
            batch = news[i : i + batch_size]
            batch_url_list = ",".join(batch)
            _run_spider_batch(batch_url_list, priority=-1)
        send_to_error_channel(
            f"Crawler started at: {d.time().hour}:{d.time().minute}, total tasks: {counter}",
            None,
            "crawler",
            f"Crawler Update {settings.ENVIRONMENT}",
            str(report.id),
        )
