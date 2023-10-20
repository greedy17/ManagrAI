from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from managr.comms.webcrawler.crawler import NewsSpider
from managr.comms.models import NewsSource


class Command(BaseCommand):
    help = "Run your Scrapy spider"

    def add_arguments(self, parser):
        parser.add_argument("url", nargs="?", type=str, help="The URL to scrape (optional)")

    def handle(self, *args, **options):
        url = options.get("url", False)
        if url:
            urls = [url]
        else:
            urls = NewsSource.domain_list()
        process = CrawlerProcess()
        process.crawl(NewsSpider, start_urls=urls)
        process.start()
