import scrapy
import logging
import datetime
from django.utils import timezone
from django.conf import settings
from ..models import NewsSource
from ..serializers import ArticleSerializer
from dateutil import parser
from ..utils import get_domain, extract_date_from_text, news_aggregator_check
from .. import constants as comms_consts

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
        "//meta[contains(@itemprop,'date')]/@content",
        "//meta[contains(@property, 'publish')]/@content",
        "//meta[contains(@name, '-date')]/@content",
        "//time/@dateTime",
        "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'publish')]/text()",
    ],
    "image_url": ["//meta[@property='og:image']/@content"],
}


def data_cleaner(data):
    try:
        content = data.pop("content")
        date = data.pop("publish_date")
        parsed_date = parser.parse(date)
        content = content.replace("\n", " ").replace("\t", " ").replace("  ", "")
        data["content"] = content
        data["publish_date"] = parsed_date
    except KeyError:
        return False
    return data


class NewsSpider(scrapy.Spider):
    name = "news_spider"

    custom_settings = {
        "DOWNLOAD_DELAY_RANDOMIZE": True,
        "DOWNLOAD_DELAY": 2,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware": 100,
        },
        "AUTOTHROTTLE_ENABLED": True,
        "USER_AGENT": "Mozilla/5.0 (compatible; managr-webcrawler/1.0; +https://managr.ai/documentation)",
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_DIR": settings.HTTPCACHE_DIR,
    }

    def __init__(self, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs.get("start_urls")
        self.urls_processed = 0

    def parse(self, response):
        url = response.url
        domain = get_domain(url)
        source = NewsSource.objects.get(domain__contains=domain)
        if source.last_scraped and source.article_link_attribute is not None:
            regex = source.create_search_regex()
            article_links = response.xpath(regex)
            do_not_track_str = ",".join(comms_consts.DO_NOT_TRACK_LIST)
            if source.last_scraped and source.article_link_attribute:
                for anchor in article_links:
                    article_url = anchor.xpath("@href").extract_first()
                    for word in comms_consts.DO_NOT_INCLUDE_WORDS:
                        if word in article_url:
                            continue
                    article_domain = get_domain(article_url)
                    if (len(article_domain) and article_domain not in do_not_track_str) or not len(
                        article_domain
                    ):
                        if "https" not in article_url:
                            article_url = url + article_url
                        current_datetime = datetime.datetime.now()
                        source.last_scraped = timezone.make_aware(
                            current_datetime, timezone.get_current_timezone()
                        )
                        source.save()
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
                if key == "publish_date" and "text" in path:
                    selector = extract_date_from_text(selector)
                if selector is not None:
                    meta_tag_data[key] = selector
                    break
        article_tag_list = ["article", "story", "content"]
        article_tags = None
        for tag in article_tag_list:
            tags = response.xpath(f"(//*[contains(@class, '{tag}')])//p//text()").getall()
            if len(tags):
                article_tags = tags
                break
        full_article = ""
        cleaned_data = None
        if article_tags is not None:
            for article in article_tags:
                full_article += article
            meta_tag_data["content"] = full_article
        try:
            if "content" in meta_tag_data.keys():
                cleaned_data = data_cleaner(meta_tag_data)
                if cleaned_data:
                    serializer = ArticleSerializer(data=cleaned_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    raise Exception()
            else:
                logger.info(f"No content for article: {response.url}")
                return
        except Exception as e:
            logger.info(str(e))
            source.error_log.append(f"{str(e)} - data: {meta_tag_data}")
            source.save()
        return

    def process_new_url(self, source, response):
        anchor_tags = response.css("a")
        site_name = response.xpath("//meta[contains(@property, 'site_name')]/@content").get()
        scrape_dict = {}
        is_news_aggregator = news_aggregator_check(anchor_tags, source.domain)
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
        source.site_name = site_name
        source.is_active = is_news_aggregator
        source.last_scraped = datetime.datetime.now()
        source.save()
        return

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url, headers={"Referer": "https://www.google.com"}, callback=self.parse
            )
