from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from managr.comms.webcrawler.crawler import NewsSpider
from managr.comms.models import NewsSource
from managr.comms.utils import remove_api_sources


class Command(BaseCommand):
    help = "Run your Scrapy spider"

    def add_arguments(self, parser):
        parser.add_argument("url", nargs="?", type=str, help="The URL to scrape (optional)")
        parser.add_argument(
            "--active",
            action="store_true",
            help="Scrape only the sources that are fully filled out",
        )
        parser.add_argument(
            "--new",
            action="store_true",
            help="Used for articles that have no attribute yet. Combine with active flag to run only active sources with their attribute filled in.",
        )
        parser.add_argument(
            "--test",
            action="store_true",
            help="Combine with active flag, this will only run the first anchor tag pulled to test all of the active sources quickly.",
        )

    def handle(self, *args, **options):
        url = options.get("url", False)
        new = options["new"]
        if url:
            urls = [url]
        else:
            remove_api_sources()
            scrape_ready = True if options["active"] else False
            urls = NewsSource.domain_list(scrape_ready, new)
        first_only = True if (options["active"] and options["new"]) else False
        process = CrawlerProcess()
        process.crawl(NewsSpider, start_urls=urls, first_only=first_only, test=options["test"])
        process.start()
