from django.conf import settings
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess

from managr.comms.models import NewsSource
from managr.comms.utils import remove_api_sources, send_url_batch
from managr.comms.webcrawler.crawler import NewsSpider, XMLSpider


class Command(BaseCommand):
    help = "Run your Scrapy spider"

    def add_arguments(self, parser):
        parser.add_argument("url", nargs="?", type=str, help="The URL to scrape (optional)"),
        parser.add_argument(
            "--remove_url", nargs="?", type=str, help="URLs to remove from the cache"
        )
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
        parser.add_argument(
            "--noreport",
            action="store_true",
            help="Won't run the report after the crawler runs",
        )
        parser.add_argument(
            "--rescrape",
            action="store_true",
            help="Rescrapes the scrape data of the source",
        )
        parser.add_argument(
            "--article",
            action="store_true",
            help="Runs the spider with parse article instead of parse",
        )
        parser.add_argument(
            "--response",
            action="store_true",
            help="Prints response of the inital url",
        )

    def handle(self, *args, **options):
        url = options.get("url", False)
        new = options["new"]
        ru = options.get("remove_url", False)
        remove_urls = ru.split(",") if ru else []
        response = options.get("response", False)
        html_urls = []
        xml_urls = []
        if url:
            urls = url.split(",")
            if options["article"]:
                html_urls = urls
            else:
                sources = NewsSource.objects.filter(domain__in=urls)
                html_urls = list(
                    sources.filter(scrape_type="HTML", use_scrape_api=False).values_list(
                        "domain", flat=True
                    )
                )
                xml_urls = list(sources.filter(scrape_type="XML").values_list("sitemap", flat=True))
                scraper_urls = list(
                    sources.filter(scrape_type="HTML", use_scrape_api=True).values_list(
                        "domain", flat=True
                    )
                )
        else:
            # remove_api_sources()
            scrape_ready = True if options["active"] else False
            html_urls = NewsSource.domain_list(scrape_ready, new)
            xml_urls = NewsSource.domain_list(scrape_ready, new, type="XML")
            scraper_urls = NewsSource.domain_list(scrape_ready, scrape_api=True)
        process = CrawlerProcess()
        if html_urls:
            process.crawl(
                NewsSpider,
                start_urls=html_urls,
                rescrape=options["rescrape"],
                test=options["test"],
                no_report=options["noreport"],
                article_only=options["article"],
                remove_urls=remove_urls,
                print_response=response,
            )
        if scraper_urls:
            send_url_batch(scraper_urls, True, False)
        process.start()
