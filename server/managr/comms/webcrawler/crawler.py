import scrapy
import logging
import datetime
import time
import json
from scrapy import signals
from scrapy.exceptions import CloseSpider, IgnoreRequest
import scrapy.spiders
import twisted
from twisted.internet.error import ConnectionLost, TimeoutError, DNSLookupError, ConnectionDone
from scrapy.spidermiddlewares.httperror import HttpError
from django.utils import timezone
from django.conf import settings
from managr.core.models import CrawlerReport
from django.db import IntegrityError
from . import constants as crawler_consts
from ..models import NewsSource, Article
from ..serializers import ArticleSerializer
from urllib.parse import urlparse, parse_qs
from dateutil import parser
from managr.api.emails import send_html_email
from copy import copy

from ..utils import (
    get_domain,
    extract_date_from_text,
    potential_link_check,
    complete_url,
)
from .. import constants as comms_consts

logger = logging.getLogger("managr")


def check_values(href):
    found_value = None
    found_attribute = None
    for value_set in crawler_consts.COMMON_SELECTORS["value"]:
        value, attribute = value_set.split(".")
        if value == "year":
            year = datetime.datetime.now().year
            if f"/{year}/" in href:
                found_value = value
                found_attribute = attribute
                break
        elif value != "year" and value in href:
            found_value = f"value,{value}"
            found_attribute = attribute
            break
    return found_value, found_attribute


def check_classes(classes_str):
    found_value = None
    found_attribute = None
    class_list = classes_str.split(" ")
    for class_set in crawler_consts.COMMON_SELECTORS["class"]:
        class_value, attribute = class_set.split(".")
        if class_value in class_list:
            found_value = f"class,{class_value}"
            found_attribute = attribute
    return found_value, found_attribute


def common_selectors_check(source):
    check = False
    selector = None
    attribute = None
    for dataset in source.scrape_data.values():
        href = dataset["href"]
        classes = dataset["classes"]
        if classes:
            found_class, found_attribute = check_classes(classes)
            if found_class:
                selector = found_class
                attribute = found_attribute
            else:
                found_value, found_attribute = check_values(href)
                if found_value:
                    selector = found_value
                    attribute = found_attribute
        if selector:
            source.article_link_selector = selector
            source.article_link_attribute = attribute
            check = True
            break
    return check


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
    except TypeError as e:
        return f"Error cleaning data: {data}"
    except KeyError as e:
        return f"Error cleaning data: {data}"
    except parser.ParserError as e:
        return f"Error cleaning data: {data}"
    return data


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
        self.first_only = kwargs.get("first_only")
        self.test = kwargs.get("test")
        self.no_report = kwargs.get("no_report")
        self.article_only = kwargs.get("article_only")
        self.urls_processed = 0
        self.articles_to_process = 0
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

    def get_site_name(self, response):
        xpaths = [
            "//meta[contains(@property, 'og:site_name')]/@content",
            "//meta[contains(@property,'og:url')]/@content",
        ]
        site_name = response.request.url
        for xpath in xpaths:
            site_name = response.xpath(xpath).get()
            if site_name:
                break
        return site_name

    def get_site_icon(self, response):
        xpath = "//link[@rel='icon']/@href"
        icon_href = response.xpath(xpath).get()
        if icon_href:
            if icon_href[0] == "/":
                icon_href = response.request.url + icon_href
        return icon_href

    def parse(self, response):
        original_check = response.meta.get("redirect_urls", [])
        if self.print_response:
            for attribute in response.attributes:
                print(attribute, ": ", getattr(response, attribute))
                print("----------------------------------")
        if response.status == 403:
            self.blocked_urls += 1
        url = original_check[0] if original_check else response.request.url
        if url[len(url) - 1] == "/":
            url = url[: len(url) - 1]
        if "api.scraperapi.com" in url:
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)
            url = params.get("url")[0]
        try:
            source = self.sources.get(domain=url)
            if response.status == 500:
                source = self.update_source(source.id, use_scrape_api=False)
                return
            if response.status == 403:
                source = self.update_source(source.id, use_scrape_api=True)
                return
        except NewsSource.DoesNotExist:
            original_urls = response.meta.get("redirect_urls", [])
            if len(original_urls):
                original_url = original_urls[0]
                sources = self.sources.filter(domain=original_url)
                if len(sources):
                    source = sources.first()
                    source = self.update_source(
                        source.id,
                        is_crawling=False,
                    )
            return
        if source.article_link_attribute is not None:
            if not source.article_link_regex:
                regex = source.create_search_regex()
                source = self.update_source(source.id, article_link_regex=regex)
            else:
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
                if len(article_links) and (self.first_only or self.test):
                    article_links = article_links[:4]
                for anchor in article_links:
                    classes = anchor.xpath("@class").get()
                    skip = False
                    article_url = anchor.xpath("@href").extract_first()
                    if article_url is None:
                        continue
                    for word in comms_consts.DO_NOT_INCLUDE_WORDS:
                        if word in article_url:
                            skip = True
                            break
                    if classes:
                        for class_word in comms_consts.NON_VIABLE_CLASSES:
                            if class_word in classes:
                                skip = True
                                break
                    if skip:
                        continue
                    article_domain = get_domain(article_url)
                    if (len(article_domain) and article_domain not in do_not_track_str) or not len(
                        article_domain
                    ):
                        article_url = complete_url(article_url, source.domain)
                        if source.use_scrape_api:
                            article_url = f"http://api.scraperapi.com/?api_key={comms_consts.SCRAPER_API_KEY}&url={article_url}&render=true"
                        self.articles_to_process += 1
                        yield scrapy.Request(
                            article_url,
                            callback=self.parse_article,
                            headers=crawler_consts.SCRAPPY_HEADERS,
                            errback=self.handle_error,
                            cb_kwargs={"source": source},
                        )
                if source.site_name is None and response.status != 403:
                    site_name = self.get_site_name(response)
                    source.site_name = site_name
                if source.icon is None and response.status < 300:
                    icon_href = self.get_site_icon(response)
                    source.icon = icon_href
        else:
            self.process_new_url(source, response)
        self.urls_processed += 1
        return

    def parse_article(self, response, source=False):
        xpath_copy = copy(crawler_consts.XPATH_STRING_OBJ)
        url = response.url
        if "api.scraperapi.com" in response.url:
            parsed_url = urlparse(response.url)
            params = parse_qs(parsed_url.query)
            url = params.get("url")[0]
        if source is False:
            try:
                instance = Article.objects.get(link=url)
                source = instance.source
            except Article.DoesNotExist:
                instance = None
                try:
                    domain = get_domain(url, True)
                    source = NewsSource.objects.get(domain__contains=domain)
                except NewsSource.DoesNotExist:
                    logger.exception(f"Failed to find source with domain: {domain}")
                    return
        meta_tag_data = {"link": url, "source": source.id}
        article_selectors = source.article_selectors()
        fields_dict = {}
        article_tags = None
        if source.selectors_defined:
            for key in article_selectors.keys():
                path = article_selectors[key]
                if "//script" in path:
                    script_path = path.split("|")[0]
                    selector = response.xpath(script_path).get()
                else:
                    selector = response.xpath(path).getall()
                if "//script" in path:
                    data_path = path.split("|")[1:]
                    for i, v in enumerate(data_path):
                        try:
                            integer_value = int(v)
                            data_path[i] = integer_value
                        except ValueError:
                            continue
                    try:
                        data = json.loads(selector)
                        selector_value = data
                        for path in data_path:
                            selector_value = selector_value[path]
                        selector = [selector_value]
                    except Exception as e:
                        print(e)
                        selector = []
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
                    try:
                        selector = response.xpath(path).get()
                    except ValueError as e:
                        selector = None
                        print(f"ERROR ({e})\n{url}\n{key}: -{path}-")
                    if key == "publish_date":
                        if "text" in path and selector is not None:
                            selector = extract_date_from_text(selector)
                        if "text" not in path:
                            try:
                                parser.parse(selector)
                            except TypeError as e:
                                selector = None
                            except Exception as e:
                                print(e)
                                continue
                    if selector is not None:
                        fields_dict[key] = path
                        meta_tag_data[key] = selector
                        break
                if key not in meta_tag_data.keys() or not len(meta_tag_data[key]):
                    meta_tag_data[key] = None
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
        else:
            meta_tag_data["content"] = None
        try:
            if "content" in meta_tag_data.keys():
                cleaned_data = data_cleaner(meta_tag_data)
                if isinstance(cleaned_data, dict):
                    if self.article_only and instance:
                        serializer = ArticleSerializer(instance=instance, data=cleaned_data)
                    else:
                        serializer = ArticleSerializer(data=cleaned_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    raise Exception(cleaned_data)
            else:
                logger.info(f"No content for article: {response.url}")

        except IntegrityError as e:
            return
        except Exception as e:
            self.error_log.append(f"{url}|{str(e)}")
            if source.error_log is None or len(source.error_log) <= 5:
                error = source.add_error(f"{str(e)}")
                source = self.update_source(source.id, error_log=error)
        if len(fields_dict):
            path_dict = {}
            for key in fields_dict.keys():
                path = fields_dict[key]
                field = crawler_consts.XPATH_TO_FIELD[key]
                path_dict[field] = path
            source = self.update_source(source.id, **path_dict)
        self.urls_processed += 1
        self.articles_to_process -= 1
        return

    # def parse_article(self, response, source=False):
    #     xpath_copy = copy(crawler_consts.XPATH_STRING_OBJ)
    #     url = response.url
    #     if "api.scraperapi.com" in response.url:
    #         parsed_url = urlparse(response.url)
    #         params = parse_qs(parsed_url.query)
    #         url = params.get("url")[0]
    #     if source is False:
    #         try:
    #             instance = Article.objects.get(link=url)
    #             source = instance.source
    #         except Article.DoesNotExist:
    #             instance = None
    #             try:
    #                 domain = get_domain(url, True)
    #                 source = NewsSource.objects.get(domain__contains=domain)
    #             except NewsSource.DoesNotExist:
    #                 logger.exception(f"Failed to find source with domain: {domain}")
    #                 return
    #     meta_tag_data = {"link": url, "source": source.id}
    #     if self.article_only:
    #         meta_tag_data["id"] = source.id
    #     article_selectors = source.article_selectors()
    #     fields_dict = {}
    #     article_tags = None
    #     if source.selectors_defined:
    #         for key in article_selectors.keys():
    #             path = article_selectors[key]
    #             if "//script" in path:
    #                 script_path = path.split("|")[0]
    #                 selector = response.xpath(script_path).get()
    #             else:
    #                 selector = response.xpath(path).getall()
    #             if "//script" in path:
    #                 data_path = path.split("|")[1:]
    #                 for i, v in enumerate(data_path):
    #                     try:
    #                         integer_value = int(v)
    #                         data_path[i] = integer_value
    #                     except ValueError:
    #                         continue
    #                 try:
    #                     data = json.loads(selector)
    #                     selector_value = data
    #                     for path in data_path:
    #                         selector_value = selector_value[path]
    #                     selector = [selector_value]
    #                 except Exception as e:
    #                     print(e)
    #                     selector = []
    #             if len(selector) and key != "content" and key != "publish_date":
    #                 selector = ",".join(selector)
    #             if key == "publish_date":
    #                 if isinstance(selector, list) and len(selector):
    #                     selector = selector[0]
    #                 selector = extract_date_from_text(selector)
    #             if key == "content":
    #                 article_tags = selector
    #                 continue
    #             if selector is not None:
    #                 meta_tag_data[key] = selector
    #             else:
    #                 meta_tag_data[key] = "N/A"
    #     else:
    #         for key in xpath_copy.keys():
    #             if article_selectors[key] is not None:
    #                 xpath_copy[key] = [article_selectors[key]]
    #             for path in xpath_copy[key]:
    #                 selector = response.xpath(path).get()
    #                 if key == "publish_date":
    #                     if "text" in path and selector is not None:
    #                         selector = extract_date_from_text(selector)
    #                     if "text" not in path:
    #                         try:
    #                             parser.parse(selector)
    #                         except Exception as e:
    #                             print(e)
    #                             continue
    #                 if selector is not None:
    #                     fields_dict[key] = path
    #                     meta_tag_data[key] = selector
    #                     break
    #             if key not in meta_tag_data.keys() or not len(meta_tag_data[key]):
    #                 meta_tag_data[key] = None
    #         article_tag_list = ["article", "story", "content"]
    #         article_xpaths = ["//article//p//text()"]
    #         for a in article_tag_list:
    #             article_xpaths.append(
    #                 f"//*[contains(@class, '{a}') or contains(@id, '{a}') and .//p]//p//text()"
    #             )
    #         if article_selectors["content"] is not None:
    #             article_xpaths = [article_selectors["content"]]
    #         for tag in article_xpaths:
    #             tags = response.xpath(tag).getall()
    #             if len(tags):
    #                 fields_dict["content"] = tag
    #                 article_tags = tags
    #                 break
    #     meta_tag_data["content"] = article_tags
    #     if len(fields_dict):
    #         for key in fields_dict.keys():
    #             path = fields_dict[key]
    #             field = crawler_consts.XPATH_TO_FIELD[key]
    #             setattr(source, field, path)
    #         source.save()
    #     self.urls_processed += 1
    #     yield meta_tag_data

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
        xpath = (
            "//body//a["
            + "(starts-with(@href, '/') or starts-with(@href, 'https'))"
            + f" and not({exclude_classes})"
            + f" and not({exclude_words})"
            + "]"
        )
        anchor_tags = response.xpath(xpath)
        scrape_dict = {}
        for idx, link in enumerate(anchor_tags):
            href = link.css("::attr(href)").get()
            is_potential_link = potential_link_check(href, source.domain)
            if is_potential_link:
                try:
                    parent = (
                        response.xpath(f"//a[@href='{href}']/parent::*").css("::attr(class)").get()
                    )
                except ValueError:
                    continue
                classes = link.css("::attr(class)").get()
                data_attributes = {}
                for key, value in link.attrib.items():
                    if key.startswith("data-"):
                        data_attributes[key] = value
                scrape_dict[idx] = {
                    "href": href,
                    "data_attributes": data_attributes,
                    "classes": classes,
                    "parent_classes": parent,
                }
        site_name = self.get_site_name(response)
        source = self.update_source(source.id, scrape_data=scrape_dict, site_name=site_name)
        selectors_check = common_selectors_check(source)
        return

    def get_sources(self):
        current_datetime = datetime.datetime.now()
        last_scraped = timezone.make_aware(current_datetime, timezone.get_current_timezone())
        sources = NewsSource.objects.filter(domain__in=self.start_urls)
        sources.update(last_scraped=last_scraped)
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
        timeout = self.settings.getint("DOWNLOAD_TIMEOUT")
        scrape_api_sources = list(
            self.sources.filter(use_scrape_api=True).values_list("domain", flat=True)
        )
        for url in self.start_urls:
            callback = self.parse_article if self.article_only else self.parse
            try:
                if url in scrape_api_sources:
                    url = f"http://api.scraperapi.com/?api_key={comms_consts.SCRAPER_API_KEY}&url={url}&render=true"
                    timeout = 300
                yield scrapy.Request(
                    url,
                    headers=crawler_consts.SCRAPPY_HEADERS,
                    callback=callback,
                    errback=self.handle_error,
                    meta={"download_timeout": timeout},
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
        self.first_only = kwargs.get("first_only")
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
        print(response)
        if response.status == 403:
            print(response.body)
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
            article_check = source.newest_article_date()
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
