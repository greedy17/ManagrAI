import scrapy
import logging
import datetime
from ..models import NewsSource
from ..serializers import ArticleSerializer
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from dateutil import parser

logger = logging.getLogger("managr")

XPATH_STRING_OBJ = {
    "title": ["//meta[contains(@property, 'title')]/@content"],
    "author": [
        "//meta[@name='author']/@content",
        "//meta[contains(@name,'author')]/@content",
        "//*[@rel='author']/text()",
    ],
    "description": ["//meta[contains(@property, 'description')]/@content"],
    "publish_date": [
        "//meta[contains(@property, 'published')]/@content",
        "//meta[contains(@name, 'date')]/@content",
    ],
    "image_url": ["//meta[@property='og:image']/@content"],
}


def data_cleaner(data):
    content = data.pop("content")
    date = data.pop("publish_date")
    parsed_date = parser.parse(date)
    content = content.replace("\n", " ").replace("\t", " ").replace("  ", "")
    data["content"] = content
    data["publish_date"] = parsed_date
    return data


class NewsSpider(scrapy.Spider):
    name = "news_spider"

    custom_settings = {
        "DOWNLOAD_DELAY_RANDOMIZE": True,  # Enable randomization
        "DOWNLOAD_DELAY": 2,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware": 100,
        },
        "AUTOTHROTTLE_ENABLED": True,
        "USER_AGENT": "Mozilla/5.0 (compatible; managr-webcrawler/1.0; +https://managr.ai/documentation)",
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
            if source.last_scraped:
                for anchor in article_links:
                    article_url = anchor.xpath("@href").extract_first()
                    if "https" not in article_url:
                        article_url = url + article_url
                    yield scrapy.Request(
                        article_url,
                        callback=self.parse_article,
                        headers={"Referer": "https://www.google.com"},
                        cb_kwargs={"source": source},
                    )
        else:
            self.process_new_url(source, response)
        self.urls_processed += 1

    def parse_article(self, response, source):
        meta_tag_data = {"link": response.url, "source": source.id}
        for key in XPATH_STRING_OBJ.keys():
            for path in XPATH_STRING_OBJ[key]:
                selector = response.xpath(path).get()
                if selector is not None:
                    meta_tag_data[key] = selector
                    break
        article_tags = response.xpath("(//*[contains(@class, 'article')])[1]//p/text()").getall()
        full_article = ""
        for article in article_tags:
            full_article += article
        meta_tag_data["content"] = full_article
        try:
            cleaned_data = data_cleaner(meta_tag_data)
            serializer = ArticleSerializer(data=cleaned_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            logger.exception(f"Failed to save article :{e}\nData: {meta_tag_data}")
        return

    def process_new_url(self, source, response):
        anchor_tags = response.css("a")
        scrape_dict = {}
        for idx, link in enumerate(anchor_tags):
            href = link.css("::attr(href)").get()
            classes = link.css("::attr(class)").get()
            data_attributes = {}
            for key, value in link.attrib.items():
                if key.startswith("data-"):
                    data_attributes[key] = value
            scrape_dict[idx] = {
                "href": href,
                "data_attributes": data_attributes,
                "classes": classes,
            }
        source.scrape_data = scrape_dict
        source.last_scraped = datetime.datetime.now()
        source.save()
        return

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url, headers={"Referer": "https://www.google.com"}, callback=self.parse
            )

    def spider_closed_handler(self, spider, reason):
        if self.urls_processed == len(self.start_urls):
            self.logger.info("All URLs processed. Stopping the spider.")
            self.crawler.engine.close_spider(spider, "All URLs processed")
        else:
            self.logger.info(
                f"Not all URLs processed. ({self.urls_processed}/{len(self.start_urls)})"
            )


def run_spider(url):
    process = CrawlerProcess()
    try:
        process.crawl(NewsSpider, start_urls=url)
        process.start()
    finally:
        process.stop()
    return
