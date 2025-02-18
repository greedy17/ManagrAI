import datetime
import logging
import re
import time
from copy import copy
from urllib.parse import parse_qs, urlparse

import scrapy
import scrapy.spiders
import twisted
from dateutil import parser
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from scrapy import signals
from scrapy.exceptions import CloseSpider, IgnoreRequest
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import ConnectionDone, ConnectionLost, DNSLookupError, TimeoutError

from managr.api.emails import send_html_email
from managr.core.models import CrawlerReport

from .. import constants as comms_consts
from ..models import Article, NewsSource
from ..serializers import ArticleSerializer
from ..utils import (
    check_article_validity,
    complete_url,
    data_cleaner,
    extract_date_from_text,
    get_domain,
)
from . import constants as crawler_consts
from .extractor import ArticleExtractor

logger = logging.getLogger("managr")


class NewsSpider(scrapy.Spider):
    name = "news_spider"
    handle_httpstatus_list = [403, 400, 410, 500, 501]
    custom_settings = {
        "FEED_EXPORT_ENCODING": "utf-8",
        "DOWNLOAD_TIMEOUT": 30,
        "RETRY_TIMES": 0,
        "DOWNLOAD_DELAY_RANDOMIZE": True,
        "DOWNLOAD_DELAY": 2,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware": 100,
            "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
            "managr.comms.webcrawler.middleware.ClearCacheMiddleware": 543,
            "managr.comms.webcrawler.middleware.RandomizeHeaderMiddleware": 544,
        },
        "AUTOTHROTTLE_ENABLED": True,
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_DIR": settings.HTTPCACHE_DIR,
        "HTTPCACHE_EXPIRATION_SECS": 43200,
        "LOG_LEVEL": settings.SCRAPY_LOG_LEVEL,
        # "ITEM_PIPELINES": {
        #     "managr.comms.webcrawler.pipelines.BulkInsertPipeline": 1,
        # },
    }

    def __init__(self, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs.get("start_urls")
        self.test = kwargs.get("test")
        self.no_report = kwargs.get("no_report")
        self.article_only = kwargs.get("article_only")
        self.rescrape_data = kwargs.get("rescrape")
        self.urls_processed = 0
        self.articles_to_process = 0
        self.articles_not_saved = 0
        self.error_log = []
        self.start_time = time.time()
        self.blocked_urls = 0
        self.remove_urls = kwargs.get("remove_urls", [])
        self.print_response = kwargs.get("print_response")
        self.sources = self.get_sources()
        self.sources_cache = {source.id: source for source in self.sources}

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
        if report:
            if len(self.error_log):
                report_str = ",".join(self.error_log)
                report.task_times.append(seconds)
                report.error_log.append(report_str)
            else:
                report.error_log.append(f"No errors for task urls {','.join(self.start_urls)}")
            report.start_url_counts.append(len(self.start_urls))
            report.total_url_counts.append(self.urls_processed)
            report.blocked_urls += self.blocked_urls
            report.save()
        for source in self.sources_cache.values():
            current_datetime = datetime.datetime.now()
            source.last_scraped = timezone.make_aware(
                current_datetime, timezone.get_current_timezone()
            )
            source.save()
            if not source.is_crawling:
                source.crawling
            source.check_if_stopped()
        return

    def handle_keyboard_interrupt(self):
        self.logger.info("KeyboardInterrupt detected, preparing to stop spider...")
        self.crawler.engine.close_spider(self, "Manual stop triggered by KeyboardInterrupt")
        raise CloseSpider("Manual stop triggered")

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

    def update_source(self, id, **kwargs):
        # Retrieve the source
        source = self.sources_cache.get(id)
        if not source:
            return None

        # Update attributes
        for key, value in kwargs.items():
            setattr(source, key, value)

        # Cache the updated source
        self.sources_cache[id] = source
        return source

    def parse(self, response, source):
        source = source.initialize(response)
        self.sources_cache[source.id] = source
        if source.article_link_attribute is not None:
            regex = source.article_link_regex
            article_links = response.xpath(regex)
            if len(article_links) < 1:
                self.update_source(
                    source.id,
                    is_crawling=False,
                )
                return
            do_not_track_str = ",".join(comms_consts.DO_NOT_TRACK_LIST)
            if source.last_scraped and source.article_link_attribute:
                if len(article_links) and self.test:
                    article_links = article_links[:4]
                for anchor in article_links:
                    article_url = anchor.xpath("@href").extract_first()
                    valid = check_article_validity(anchor)
                    if not valid:
                        continue
                    article_domain = get_domain(article_url)
                    if (len(article_domain) and article_domain not in do_not_track_str) or not len(
                        article_domain
                    ):
                        article_url = complete_url(article_url, source.domain)
                        self.articles_to_process += 1
                        yield scrapy.Request(
                            article_url,
                            callback=self.parse_article,
                            headers=crawler_consts.SCRAPPY_HEADERS,
                            errback=self.handle_error,
                            cb_kwargs={"source": source},
                        )
        self.urls_processed += 1
        return

    def parse_article(self, response, source=False):
        url = response.url
        instance = None
        if source is False:
            try:
                instance = Article.objects.get(link=url)
                source = instance.source
            except Article.DoesNotExist:
                try:
                    domain = get_domain(url, True)
                    source = NewsSource.objects.get(domain__contains=domain)
                except NewsSource.DoesNotExist:
                    logger.exception(f"Failed to find source with domain: {domain}")
                    return
        source, article_selectors = source.get_selectors(response)
        if source.selectors_defined:
            extractor = ArticleExtractor(source, response, article_selectors, url, instance)
            if not extractor.saved:
                self.error_log.append("{}|{}".format(url, extractor.error))
                error = source.add_error(extractor.error)
                source = self.update_source(source.id, error_log=error)
                self.articles_not_saved += 1
                return
        self.urls_processed += 1
        self.articles_to_process -= 1
        return

    def get_sources(self):
        sources = NewsSource.objects.filter(domain__in=self.start_urls)
        sources.update(error_log="")
        return NewsSource.objects.filter(domain__in=self.start_urls)

    def handle_error(self, failure):
        deactivate = False
        error = ""
        if failure.check(TimeoutError, HttpError):
            deactivate = True
            error = "Request Timeout"
            self.logger.error(f"Timeout error occurred: {failure.request.url}")
        elif failure.check(twisted.web._newclient.ResponseNeverReceived):
            deactivate = True
            error = "Response never received"
            self.logger.error(
                f"SSL Handshake Error occurred: {failure.request.url} - {failure.value}"
            )
        elif failure.check(ConnectionLost, ConnectionDone):
            deactivate = True
            error = "Connection lost"
            self.logger.error(f"Connection lost: {failure.request.url}")
        elif failure.check(DNSLookupError):
            deactivate = True
            error = "DNS Lookup failed"
            self.logger.error(f"DNS Lookup failed: {failure.request.url}")
        elif failure.check(IgnoreRequest):
            self.logger.error(f"Request ignored: {failure.request.url}")
        # Handle generic exceptions or errors
        elif failure.check(Exception):
            self.logger.error(f"Request failed: {failure}")
        else:
            self.logger.error(f"Unexpected error: {failure}")

        if deactivate:
            url = failure.request.url
            if "api.scraperapi.com" in url:
                parsed_url = urlparse(url)
                params = parse_qs(parsed_url.query)
                url = params.get("url")[0]
            source = self.sources.filter(domain=url).first()
            if source:
                self.update_source(source.id, is_active=False, error_log=error)
                return
        return failure

    def start_requests(self):
        self.total_urls = len(self.start_urls)
        if self.article_only:
            callback = self.parse
        elif self.rescrape_data:
            callback = self.process_new_url
        else:
            callback = self.parse
        for url in self.start_urls:
            if not self.article_only:
                cb_kwargs = {"source": self.sources.get(domain=url)}
            else:
                cb_kwargs = {}
            try:
                yield scrapy.Request(
                    url,
                    headers=crawler_consts.SCRAPPY_HEADERS,
                    callback=callback,
                    errback=self.handle_error,
                    cb_kwargs=cb_kwargs,
                )
            except Exception as e:
                self.error_log.append(f"Failed on {url} ({str(e)})")


class SitemapSpider(scrapy.spiders.SitemapSpider):
    name = "sitemap_spider"

    handle_httpstatus_list = [403]
    custom_settings = {
        "DOWNLOAD_DELAY_RANDOMIZE": True,
        "DOWNLOAD_DELAY": 2,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware": 100,
        },
        "AUTOTHROTTLE_ENABLED": True,
        "USER_AGENT": "Mozilla/5.0 (compatible; ManagrCrawler/2.0; +https://managr.ai/documentation; bot-friendly)",
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_DIR": settings.HTTPCACHE_DIR,
        "HTTPCACHE_EXPIRATION_SECS": 43200,
        "LOG_LEVEL": settings.SCRAPY_LOG_LEVEL,
    }

    def __init__(self, *args, **kwargs):
        super(SitemapSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs.get("start_urls")
        self.test = kwargs.get("test")
        self.no_report = kwargs.get("no_report")
        self.article_only = kwargs.get("article_only")
        self.urls_processed = 0
        self.error_log = []
        self.start_time = time.time()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SitemapSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed_handler, signal=signals.spider_closed)
        return spider

    def spider_closed_handler(self, spider):
        if self.no_report:
            return
        report = CrawlerReport.objects.all().order_by("-datetime_created").first()
        seconds = int((time.time() - self.start_time))
        if len(self.error_log):
            report_str = ",".join(self.error_log)
            report.task_times.append(seconds)
            report.error_log.append(report_str)
        else:
            report.error_log.append(f"No errors for task urls {','.join(self.start_urls)}")
        report.start_url_counts.append(len(self.start_urls))
        report.total_url_counts.append(self.urls_processed)
        report.save()
        return

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
        if response.status == 403:
            url = response.request.url
        if url[len(url) - 1] == "/":
            url = url[: len(url) - 1]
        try:
            source = NewsSource.objects.get(sitemap=url)
        except NewsSource.DoesNotExist:
            return
        year = datetime.datetime().now().year
        year_url = source.sitemap + "/" + str(year)
        yield scrapy.Request(
            year_url,
            callback=self.parse_months,
            headers=crawler_consts.SCRAPPY_HEADERS,
            cb_kwargs={"source": source},
        )
        if source.site_name is None:
            site_name = self.get_site_name(response)
            source.site_name = site_name
        current_datetime = datetime.datetime.now()
        source.last_scraped = timezone.make_aware(current_datetime, timezone.get_current_timezone())
        source.save()
        self.urls_processed += 1
        return

    def parse_months(self, response, source):
        date = datetime.datetime()
        current_month = date.month
        months = []
        for i in range(current_month + 1):
            months.append(crawler_consts.MONTH_DAY_TO_NAME[i])
        month_urls = []
        for month in months:
            xpath = f"//a[contains(@href,'{month}')]/@href"
            day_urls = response.xpath(xpath)
            month_urls.extend(day_urls)
        for url in month_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_day,
                headers=crawler_consts.SCRAPPY_HEADERS,
                cb_kwargs={"source": source},
            )

    def parse_day(self, response, source):
        regex = source.create_search_regex()
        article_links = response.xpath(regex)
        do_not_track_str = ",".join(comms_consts.DO_NOT_TRACK_LIST)
        if source.last_scraped and source.article_link_attribute:
            if len(article_links) and self.test:
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
                        headers=crawler_consts.SCRAPPY_HEADERS,
                        cb_kwargs={"source": source},
                    )

                self.urls_processed += 1
        return

    def parse_article(self, response, source=False):
        xpath_copy = copy(crawler_consts.XPATH_STRING_OBJ)
        if source is False:
            instance = Article.objects.get(link=response.url)
            source = instance.source
        meta_tag_data = {"link": response.url, "source": source.id}
        article_selectors = source.article_selectors
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
                else:
                    raise Exception(cleaned_data)
            else:
                logger.info(f"No content for article: {response.url}")
                return
        except IntegrityError:
            return
        except Exception as e:
            print(e)
            self.error_log.append(f"URL: {response.url} ({str(e)})")
            source.add_error(f"{str(e)} {meta_tag_data}\n")
        if len(fields_dict):
            for key in fields_dict.keys():
                path = fields_dict[key]
                field = crawler_consts.XPATH_TO_FIELD[key]
                setattr(source, field, path)
            source.save()
            source.crawling
        self.urls_processed += 1
        return

    def start_requests(self):
        self.total_urls = len(self.start_urls)
        for url in self.start_urls:
            callback = self.parse_article if self.article_only else self.parse
            try:
                yield scrapy.Request(url, headers=crawler_consts.SCRAPPY_HEADERS, callback=callback)
            except Exception as e:
                self.error_log.append(f"Failed on {url} ({str(e)})")


class XMLSpider(scrapy.Spider):
    name = "xml_spider"

    handle_httpstatus_list = [403, 400]
    custom_settings = {
        "DOWNLOAD_DELAY_RANDOMIZE": True,
        "DOWNLOAD_DELAY": 5,
        "AUTOTHROTTLE_ENABLED": True,
        "USER_AGENT": "ScraperAPI (+https://www.scraperapi.com)",
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_DIR": settings.HTTPCACHE_DIR,
        "HTTPCACHE_EXPIRATION_SECS": 43200,
        "LOG_LEVEL": settings.SCRAPY_LOG_LEVEL,
    }

    def __init__(self, *args, **kwargs):
        super(XMLSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs.get("start_urls")
        self.first_only = kwargs.get("first_only")
        self.test = kwargs.get("test")
        self.no_report = kwargs.get("no_report")
        self.article_only = kwargs.get("article_only")
        self.urls_processed = 0
        self.error_log = []
        self.start_time = time.time()
        self.namespaces = {
            "sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9",
        }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(XMLSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed_handler, signal=signals.spider_closed)
        return spider

    def spider_closed_handler(self, spider):
        if self.no_report:
            return
        report = CrawlerReport.objects.all().order_by("-datetime_created").first()
        seconds = int((time.time() - self.start_time))
        if seconds == 0:
            sec_str = (
                f"CRAWLER RAN FOR 0 SECONDS: {self.start_time}/{int(time.time())} {self.start_urls}"
            )
            self.error_log.insert(0, sec_str)
        if len(self.error_log):
            report_str = ",".join(self.error_log)
            report.task_times.append(seconds)
            report.error_log.append(report_str)
        else:
            report.error_log.append(f"No errors for task urls {','.join(self.start_urls)}")
        report.start_url_counts.append(len(self.start_urls))
        report.total_url_counts.append(self.urls_processed)
        report.save()
        return

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
            source = NewsSource.objects.get(sitemap=url)
            article_check = source.newest_article_date
        except NewsSource.DoesNotExist:
            return
        if "rss" in url:
            regex = "//item//link/text()"
            links = response.xpath(regex).getall()
            for link in links:
                new_url = f"http://api.scraperapi.com/?api_key={comms_consts.SCRAPER_API_KEY}&url={link}&render=true"
                yield scrapy.Request(
                    new_url,
                    self.parse_article,
                    headers=crawler_consts.SCRAPPY_HEADERS,
                    cb_kwargs={"source": source},
                )
        else:
            year = datetime.datetime.now().year
            regex = f"//sitemap:loc[contains(text(),'{year}')]/text()"
            if article_check:
                day_links = [response.xpath(regex, namespaces=self.namespaces).get()]
            else:
                day_links = response.xpath(regex, namespaces=self.namespaces).getall()[:3]
            for day in day_links:
                yield scrapy.Request(
                    day,
                    callback=self.parse_day,
                    headers=crawler_consts.SCRAPPY_HEADERS,
                    cb_kwargs={"source": source},
                )
        current_datetime = datetime.datetime.now()
        source.last_scraped = timezone.make_aware(current_datetime, timezone.get_current_timezone())
        source.save()
        self.urls_processed += 1
        return

    def parse_day(self, response, source):
        regex = regex = f"//sitemap:url/sitemap:loc/text()"
        article_links = response.xpath(regex, namespaces=self.namespaces).getall()
        for article in article_links:
            url = f"http://api.scraperapi.com/?api_key={comms_consts.SCRAPER_API_KEY}&url={article}&render=true"
            yield scrapy.Request(
                url,
                callback=self.parse_article,
                cb_kwargs={"source": source},
            )

    def parse_article(self, response, source=False):
        xpath_copy = copy(crawler_consts.XPATH_STRING_OBJ)
        if source is False:
            instance = Article.objects.get(link=response.url)
            source = instance.source
        meta_tag_data = {"link": response.url, "source": source.id}
        article_selectors = source.article_selectors
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
                else:
                    raise Exception(cleaned_data)
            else:
                logger.info(f"No content for article: {response.url}")
                return
        except IntegrityError:
            return
        except Exception as e:
            print(e)
            self.error_log.append(f"URL: {response.url} ({str(e)})")
            if source.error_log is None or len(source.error_log) <= 5:
                source.add_error(f"{str(e)} {meta_tag_data}\n")
        if len(fields_dict):
            for key in fields_dict.keys():
                path = fields_dict[key]
                field = crawler_consts.XPATH_TO_FIELD[key]
                setattr(source, field, path)
        if source.site_name is None:
            site_name = self.get_site_name(response)
            source.site_name = site_name
            source.save()
        if not source.is_crawling:
            source.crawling
        self.urls_processed += 1
        return

    def start_requests(self):
        self.total_urls = len(self.start_urls)
        for url in self.start_urls:
            callback = self.parse_article if self.article_only else self.parse
            try:
                yield scrapy.Request(url, headers=crawler_consts.SCRAPPY_HEADERS, callback=callback)
            except Exception as e:
                self.error_log.append(f"Failed on {url} ({str(e)})")
