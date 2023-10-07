import scrapy
import logging
import datetime
from ..models import NewsSource
from ..serializers import ArticleSerializer
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher

logger = logging.getLogger("managr")


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
            # if source.last_scraped:
            for anchor in article_links:
                article_url = url + anchor.xpath("@href").extract_first()
                yield scrapy.Request(
                    article_url, callback=self.parse_article, cb_kwargs={"source": source}
                )
            # else:
            #     first_article = article_links[0]
            #     article_url = url + first_article.xpath("@href").extract_first()
            #     yield scrapy.Request(
            #         article_url, callback=self.process_new_article_url, cb_kwargs={"source": source}
            #     )
        else:
            self.process_new_url(source, response)
        self.urls_processed += 1

    def parse_article(self, response, source):
        meta_tag_selectors = [
            "title.//meta[contains(@property, 'title')]/@content",
            "description.//meta[contains(@property, 'description')]/@content",
            "publish_date.//meta[contains(@property, 'published')]/@content",
            "image_url.//meta[@property='og:image']/@content",
            "author.//*[@rel='author']/text()",
        ]
        meta_tag_data = {"link": response.url, "source": source.id}
        for tag in meta_tag_selectors:
            key, path = tag.split(".")
            selector = response.xpath(path).get()
            meta_tag_data[key] = selector
        article_tags = response.xpath("(//*[contains(@class, 'article')])[1]//p/text()").getall()
        full_article = ""
        for article in article_tags:
            full_article += article
        meta_tag_data["content"] = full_article
        try:
            serializer = ArticleSerializer(data=meta_tag_data)
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
            data_attributes = {}
            for key, value in link.attrib.items():
                if key.startswith("data-"):
                    data_attributes[key] = value
            scrape_dict[idx] = {"href": href, "data_attributes": data_attributes}
        source.scrape_data["main_page"] = scrape_dict
        source.last_scraped = datetime.datetime.now()
        source.save()
        return

    def process_new_article_url(self, response, source):
        meta_tag_selectors = [
            "title.//meta[contains(@property, 'title')]/@content",
            "description.//meta[contains(@property, 'description')]/@content",
            "publish_date.//meta[contains(@property, 'published')]/@content",
            "image.//meta[@property='og:image']/@content",
            "author.//*[@rel='author']/text()",
        ]
        meta_tag_data = {}
        for tag in meta_tag_selectors:
            key, path = tag.split(".")
            selector = response.xpath(path).get()
            meta_tag_data[key] = selector
        article_tags = response.xpath("(//*[contains(@class, 'article')])[1]//p/text()").getall()
        full_article = ""
        for article in article_tags:
            full_article += article
        meta_tag_data["content"] = full_article
        # source.scrape_data["article_data"] = article_data
        # source.save()
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
    return
