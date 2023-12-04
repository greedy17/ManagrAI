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
            help="Scrape only the sources that are fully filled out",
        )

    def handle(self, *args, **options):
        url = options.get("url", False)
        if url:
            urls = [url]
        else:
            remove_api_sources()
            scrape_ready = True if options["active"] else False
            new = True if options["new"] else False
            urls = NewsSource.domain_list(scrape_ready, new)
        first_only = True if (options["active"] and options["new"]) else False
        process = CrawlerProcess()
        process.crawl(NewsSpider, start_urls=urls, first_only=first_only)
        process.start()
