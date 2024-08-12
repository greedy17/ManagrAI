import scrapy
import logging
import datetime
import time
import json
from scrapy import signals
from django.utils import timezone
from django.conf import settings
from managr.core.models import CrawlerReport
from django.db import IntegrityError
from ..models import NewsSource, Article
from ..serializers import ArticleSerializer
from dateutil import parser
from managr.api.emails import send_html_email
from copy import copy

from ..utils import (
    get_domain,
    extract_date_from_text,
    potential_link_check,
    extract_base_domain,
    complete_url,
)
from .. import constants as comms_consts

logger = logging.getLogger("managr")

XPATH_STRING_OBJ = {
    "title": ["//meta[contains(@property, 'title')]/@content"],
    "author": [
        "//*[contains(@class,'gnt_ar_by')]/a/text()",
        "//*[@class='article__author']/text()",
        "//meta[contains(@name,'author')]/@content",
        "//*[@rel='author']/text()",
        "//*[contains(@class,'author-name') and string-length() > 2]//text()",
    ],
    "description": ["//meta[contains(@property, 'description')]/@content"],
    "publish_date": [
        "//*[contains(@class,'gnt_ar_dt')]/@aria-label",
        "//body//time/@datetime | //body//time/@dateTime | //body//time/text()",
        "//meta[contains(@itemprop,'date')]/@content",
        "//meta[contains(translate(@property, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'modified') or contains(translate(@property, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'published')]/@content",
        "//meta[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'modified') or contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'published')]/@content",
        "//meta[contains(@name, 'date')]/@content",
        "(//*[contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'date')])[last()]//text()",
        f"//body//*[not(self::script) and not(self::p) and (contains(text(),', {datetime.datetime.now().year}') or contains(text(),'{datetime.datetime.now().year},'))]",
        "//body//*[not(self::script) and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'publish')]/text()",
    ],
    "image_url": ["//meta[@property='og:image']/@content"],
}

XPATH_TO_FIELD = {
    "title": "article_title_selector",
    "author": "author_selector",
    "description": "description_selector",
    "publish_date": "date_published_selector",
    "image_url": "image_url_selector",
    "content": "article_content_selector",
}


def data_cleaner(data):
    try:
        content = data.pop("content")
        date = data.pop("publish_date")
        parsed_date = parser.parse(date)
        content = content.replace("\n", " ").replace("\t", " ").replace("  ", "")
        data["author"] = (
            data["author"].replace("\n", "").replace(" and ", ",").replace("By ,", "").strip()
        )
        authors = data["author"].split(",")
        author = authors[0]
        data["author"] = author
        data["content"] = content
        data["publish_date"] = parsed_date
        if len(data["title"]) > 150:
            data["title"] = data["title"][:145] + "..."
    except KeyError as e:
        return str(e)
    except parser.ParserError as e:
        return str(e)
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
        "HTTPCACHE_EXPIRATION_SECS": 43200,
        "LOG_LEVEL": settings.SCRAPY_LOG_LEVEL,
    }

    def __init__(self, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs.get("start_urls")
        self.first_only = kwargs.get("first_only")
        self.test = kwargs.get("test")
        self.no_report = kwargs.get("no_report")
        self.article_only = kwargs.get("article_only")
        self.urls_processed = 0
        self.error_log = []
        self.start_time = time.time()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NewsSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed_handler, signal=signals.spider_closed)
        return spider

    def spider_closed_handler(self, spider):
        if self.no_report:
            return
        report = CrawlerReport.objects.all().order_by("-datetime_created").first()
        seconds = int((time.time() - self.start_time))
        # minutes = 0
        # if seconds >= 60:
        #     minutes = round((seconds / 60), 0)
        # completed_in = f"{seconds} seconds" if minutes == 0 else f"{minutes} minutes"
        # report_data = {
        #     "start_urls": len(self.start_urls),
        #     "urls_processed": self.urls_processed,
        #     "seconds": str(seconds),
        #     "time": completed_in,
        #     "errors": self.error_log,
        # }
        report_str = ",".join(self.error_log)
        report.task_times.append(seconds)
        report.error_log.append(report_str)
        report.start_url_counts.append(len(self.start_urls))
        report.total_url_counts.append(self.urls_processed)
        report.save()
        return
        # self.generate_report(report_data)

    def generate_report(self, data):
        try:
            send_html_email(
                f"Managr Crawler Report",
                "core/email-templates/crawler-email.html",
                settings.DEFAULT_FROM_EMAIL,
                ["zach@mymanagr.com"],
                context=data,
            )
        except Exception as e:
            logger.exception(e)
        return

    def get_site_name(self, response):
        site_name = response.xpath(
            "//meta[contains(@property,'og:url') or contains(@property, 'og:site_name')]/@content"
        ).getall()
        if len(site_name) > 1:
            return site_name[1]
        elif not len(site_name):
            return response.request.url
        if isinstance(site_name, list):
            site_name = site_name[0]
        return site_name

    def parse(self, response):
        url = response.request.url
        if url[len(url) - 1] == "/":
            url = url[: len(url) - 1]
        try:
            source = NewsSource.objects.get(domain=url)
        except NewsSource.DoesNotExist:
            original_urls = response.meta.get("redirect_urls", [])
            if len(original_urls):
                original_url = original_urls[0]
                sources = NewsSource.objects.filter(domain=original_url)
                if len(sources):
                    source = sources.first()
                    source.is_active = False
                    current_datetime = datetime.datetime.now()
                    source.last_scraped = timezone.make_aware(
                        current_datetime, timezone.get_current_timezone()
                    )
                    source.save()
            return
        if source.article_link_attribute is not None:
            regex = source.create_search_regex()
            article_links = response.xpath(regex)
            do_not_track_str = ",".join(comms_consts.DO_NOT_TRACK_LIST)
            if source.last_scraped and source.article_link_attribute:
                if len(article_links) and (self.first_only or self.test):
                    article_links = [article_links[0]]
                for anchor in article_links:
                    skip = False
                    article_url = anchor.xpath("@href").extract_first()
                    if article_url is None:
                        continue
                    for word in comms_consts.DO_NOT_INCLUDE_WORDS:
                        if word in article_url:
                            skip = True
                            break
                    if skip:
                        continue
                    article_domain = get_domain(article_url)
                    if (len(article_domain) and article_domain not in do_not_track_str) or not len(
                        article_domain
                    ):
                        article_url = complete_url(article_url, source.domain)

                        yield scrapy.Request(
                            article_url,
                            callback=self.parse_article,
                            headers={"Referer": "https://www.google.com"},
                            cb_kwargs={"source": source},
                        )
                if source.site_name is None:
                    site_name = self.get_site_name(response)
                    source.site_name = site_name
                current_datetime = datetime.datetime.now()
                source.last_scraped = timezone.make_aware(
                    current_datetime, timezone.get_current_timezone()
                )
                source.save()
        else:
            self.process_new_url(source, response)
        self.urls_processed += 1
        return

    def parse_article(self, response, source=False):
        xpath_copy = copy(XPATH_STRING_OBJ)
        if source is False:
            instance = Article.objects.get(link=response.url)
            source = instance.source
        meta_tag_data = {"link": response.url, "source": source.id}
        article_selectors = source.article_selectors()
        fields_dict = {}
        article_tags = None
        if source.selectors_defined:
            for key in article_selectors.keys():
                selector = response.xpath(article_selectors[key]).getall()
                if len(selector) and key != "content" and key != "publish_date":
                    selector = ",".join(selector)
                if key == "publish_date":
                    if isinstance(selector, list) and len(selector):
                        selector = selector[0]
                    selector = extract_date_from_text(selector)
                if key == "content":
                    article_tags = selector
                    continue
                if selector is not None:
                    meta_tag_data[key] = selector
                else:
                    meta_tag_data[key] = "N/A"
        else:
            for key in xpath_copy.keys():
                if article_selectors[key] is not None:
                    xpath_copy[key] = [article_selectors[key]]
                for path in xpath_copy[key]:
                    selector = response.xpath(path).get()
                    if key == "publish_date":
                        if "text" in path and selector is not None:
                            selector = extract_date_from_text(selector)
                        if "text" not in path:
                            try:
                                parser.parse(selector)
                            except Exception as e:
                                print(e)
                                continue
                    if selector is not None:
                        fields_dict[key] = path
                        meta_tag_data[key] = selector
                        break
                if key not in meta_tag_data.keys() or not len(meta_tag_data[key]):
                    meta_tag_data[key] = "N/A"
            article_tag_list = ["article", "story", "content"]
            article_xpaths = ["//article//p//text()"]
            for a in article_tag_list:
                article_xpaths.append(
                    f"//*[contains(@class, '{a}') or contains(@id, '{a}') and .//p]//p//text()"
                )
            if article_selectors["content"] is not None:
                article_xpaths = [article_selectors["content"]]
            for tag in article_xpaths:
                tags = response.xpath(tag).getall()
                if len(tags):
                    fields_dict["content"] = tag
                    article_tags = tags
                    break
        full_article = ""
        cleaned_data = None
        if article_tags is not None:
            for article in article_tags:
                article = article.replace("\n", "").strip()
                full_article += article
            meta_tag_data["content"] = full_article
        try:
            if "content" in meta_tag_data.keys():
                cleaned_data = data_cleaner(meta_tag_data)
                if isinstance(cleaned_data, dict):
                    if self.article_only:
                        serializer = ArticleSerializer(instance=instance, data=cleaned_data)
                    else:
                        serializer = ArticleSerializer(data=cleaned_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    serializer.instance.update_search_vector()
                else:
                    raise Exception(cleaned_data)
            else:
                logger.info(f"No content for article: {response.url}")
                return
        except IntegrityError:
            return
        except Exception as e:
            print(e)
            self.error_log.append(f"URL: {source.domain} | Error: {str(e)}")
            if source.error_log is None or len(source.error_log) <= 5:
                source.add_error(f"{str(e)} {meta_tag_data}\n")
        if len(fields_dict):
            for key in fields_dict.keys():
                path = fields_dict[key]
                field = XPATH_TO_FIELD[key]
                setattr(source, field, path)
            source.save()
            source.crawling
        self.urls_processed += 1
        return

    def process_new_url(self, source, response):
        exclude_classes_list = ["menu", "-nav"]
        exclude_classes = " or ".join(
            f"contains(@class, '{word}')" for word in exclude_classes_list
        )
        exclude_word_list = [
            "/about",
            "/terms",
            "-policy",
            "/privacy",
            "/careers",
            "/accessibility",
            "/category",
        ]
        exclude_words = " or ".join(f"contains(@href, '{word}')" for word in exclude_word_list)
        anchor_tags = response.xpath(
            "//body//a["
            + "(starts-with(@href, '/') or starts-with(@href, 'https'))"
            + f" and not({exclude_classes})"
            + f" and not({exclude_words})"
            + "]"
        )
        scrape_dict = {}
        for idx, link in enumerate(anchor_tags):
            href = link.css("::attr(href)").get()
            is_potential_link = potential_link_check(href, source.domain)
            if is_potential_link:
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
        source.site_name = self.get_site_name(response)
        current_datetime = datetime.datetime.now()
        source.last_scraped = timezone.make_aware(current_datetime, timezone.get_current_timezone())
        source.save()
        return

    def start_requests(self):
        self.total_urls = len(self.start_urls)
        for url in self.start_urls:
            callback = self.parse_article if self.article_only else self.parse
            try:
                yield scrapy.Request(
                    url, headers={"Referer": "https://www.google.com"}, callback=callback
                )
            except Exception as e:
                self.error_log.append(str(e))


class SubstackSpider(scrapy.Spider):
    name = "substack_spider"

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
        "HTTPCACHE_EXPIRATION_SECS": 43200,
        "LOG_LEVEL": settings.SCRAPY_LOG_LEVEL,
    }

    def __init__(self, *args, **kwargs):
        super(SubstackSpider, self).__init__(*args, **kwargs)
        self.start_url = kwargs.get("start_url")

    def parse(self, response):
        article_links = response.xpath("//div[@class='reader2-page-body']/div/div")
        print(article_links)
        return {"results": article_links}
