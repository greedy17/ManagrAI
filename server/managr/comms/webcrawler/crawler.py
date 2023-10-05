import scrapy
import datetime
from ..models import NewsSource
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher


class NewsSpider(scrapy.Spider):
    name = "news_spider"

    custom_settings = {
        "DOWNLOAD_DELAY_RANDOMIZE": True,  # Enable randomization
    }

    def __init__(self, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs.get("start_urls").split(",")
        self.urls_processed = 0
        dispatcher.connect(self.spider_closed_handler, signal=signals.spider_closed)

    def parse(self, response):
        url = response.url
        source = NewsSource.objects.get(domain=url)
        if source.last_scraped:
            regex = source.create_search_regex()
            article_links = response.xpath(regex)
            for anchor in article_links:
                url = anchor.xpath('@href').extract_first()
                yield scrapy.Request(url, callback=self.parse_article)
        else:
            self.process_new_url(source, response, cb_kwargs={'source': source})
        self.urls_processed += 1

    def parse_article(self, response, source):
        # Process the article HTML here
        

    def process_new_url(self, source, response):
        anchor_tags = response.css("a")
        scrape_dict = {}
        for idx, link in enumerate(anchor_tags):
            href = link.css("::attr(href)").get()
            data_attributes = {}
            for key, value in link.attrib.items():
                if key.startswith("data-"):
                    data_attributes[key] = value
            scrape_dict[idx] = {"href": href, "data_attributes": data_attributes}
        source.scrape_data = scrape_dict
        source.last_scraped = datetime.datetime.now()
        source.save()
        return

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def spider_closed_handler(self, spider, reason):
        if self.urls_processed == len(self.start_urls):
            self.logger.info("All URLs processed. Stopping the spider.")
            self.crawler.engine.close_spider(spider, "All URLs processed")
        else:
            self.logger.info(
                f"Not all URLs processed. ({self.urls_processed}/{len(self.start_urls)})"
            )


def run_spider():
    process = CrawlerProcess(
        settings={
            "USER_AGENT": "Mozilla/5.0 (compatible; managr-webcrawler/1.0; +https://managr.ai/documentation)"
        }
    )
    process.crawl(NewsSpider, start_urls="https://www.reuters.com")
    process.start()
