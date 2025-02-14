import json
import logging
import random
import re
from copy import copy
from datetime import datetime
from urllib.parse import urlparse

import pytz
import requests
from dateutil import parser
from lxml import etree

from managr.comms.utils import (
    check_classes,
    check_values,
    complete_url,
    extract_date_from_text,
    find_key,
    potential_link_check,
)
from managr.comms.webcrawler.constants import (
    EXCLUDE_CLASSES,
    HOMEPAGE_ANCHOR_TAG_XPATH,
    TIMEZONE_DICT,
    URL_DATE_PATTERN,
    XPATH_STRING_OBJ,
    XPATH_TO_FIELD,
)

logger = logging.getLogger("managr")


class ArticleExtractor:
    """
    Extracts needed values from article. We currently save title, description, publish_date,
    link, image_url, author, and content.
    Attributes:
        source (NewsSource): Source the scraper is currently on, will always have a value
        article (ScrapyResponse): Direct response from the scrapy request.
        link (str): Url of the article scraped
        article_instance (Article): If the requests was a rescrape of a saved article, this
                                    will be an instance of Article.
        selectors (dict): This is the dict of article xpaths saved on the source.
        error (str/None): Used for any errors that happen, only one error will happen
                          before we return.
        saved (bool): Used in parse_article of scrapy spider. Sets to True on successful
                      save to the DB
    """

    def __init__(self, source, article, selectors, article_instance=None):
        self.source = source
        self.article = article
        self.link = article.url
        self.article_instance = article_instance
        self.selectors = selectors
        self.error = None
        self.saved = False
        self.set_selectors(selectors)
        self.parse()

    def set_selectors(self, selector_dict):
        """Sets selector attributes for all values we collect from the selectors"""
        for key, value in selector_dict.items():
            setattr(self, f"{key}_selector", value)
            setattr(self, key, None)
        return

    @property
    def article_values(self):
        """Returns the current article values set on the extractor"""
        return {
            "author": self.author,
            "publish_date": self.publish_date,
            "title": self.title,
            "content": self.content,
            "image_url": self.image_url,
            "description": self.description,
            "link": self.link,
            "source": self.source.id,
        }

    @property
    def has_valid_values(self):
        """Checks if any values are None in article_values. There will either be a value or be None"""
        for v in self.article_values.values():
            if v is None:
                return False
        return True

    def parse(self):
        """This is the main function of the Extractor. Loops through each of the parse function of our
        needed article values. If the has_valid_values check fails to be True after, it automatically
        returns as this means on of the xpaths needs to be fixed. Otherwise we clean the parsed values.
        If those values are valid, we try to save the article."""
        parse_methods = [
            "parse_title",
            "parse_author",
            "parse_publish_date",
            "parse_content",
            "parse_image_url",
            "parse_description",
        ]
        for parse_method in parse_methods:
            method = getattr(self, parse_method, None)
            if callable(method):
                method()
        if not self.has_valid_values:
            self.error = "Error parsing values from article: {}".format(self.article_values)
            return
        self.clean_data()
        if self.has_valid_values:
            self.save_article()
        return

    # These next function are the individual functions for each article value.
    def parse_author(self):
        if "//script" in self.author_selector:
            author_value = self.extract_script(self.author_selector)
        else:
            author_value = self.extract_value(self.author_selector)
        self.author = author_value
        return

    def parse_publish_date(self):
        if "//script" in self.publish_date_selector:
            selector_value = self.extract_script(self.publish_date_selector)
        else:
            selector_value = self.extract_value(self.publish_date_selector)
        # This function checks if the date is a valid date/format.
        if selector_value is not None:
            selector_value = extract_date_from_text(selector_value, TIMEZONE_DICT)
        print(selector_value)
        self.publish_date = selector_value
        return

    def parse_content(self):
        selector_value = self.extract_value(self.content_selector, True)
        p_list = []
        content_value = None
        if selector_value is not None:
            for p in selector_value:
                p = p.replace("\n", "").strip()
                p_list.append(p)
            content_value = " ".join(p_list)
        self.content = content_value
        return

    def parse_image_url(self):
        self.image_url = self.extract_value(self.image_url_selector)
        return

    def parse_description(self):
        self.description = self.extract_value(self.description_selector)
        return

    def parse_title(self):
        self.title = self.extract_value(self.title_selector)
        return

    def extract_script(self, path):
        """This is for any xpaths for the ld+json script. The value of the path contains
        both the xpath and the keys to get to the approriate value (publish date or author)
        separated by pipes between the keys. Any values that are integers are for indexes of a list
        within the script data."""
        path = path.split("|")
        selector_path = path[0]
        data_path = path[1:]
        selector = self.article.xpath(selector_path).getall()
        for i, v in enumerate(data_path):
            try:
                integer_value = int(v)
                data_path[i] = integer_value
            except ValueError:
                continue
        try:
            data = json.loads(selector.lower())
            data_value = data
            for path in data_path:
                data_value = data_value[path]
            selector_value = data_value.title()
        except Exception as e:
            self.error = "Error ({}) extracting script with path {}".format(e, path)
            selector_value = None
        return selector_value

    def extract_value(self, path, multi=False):
        """Extracts the value from the path. Since some article values like content have
        multiple values that need to be saved, The multi arg determine if we only extract
        the first value from the returned list or return all. If the xpath is bad and no values
        are extracted, we return None."""
        selector_value = self.article.xpath(path).getall()
        if len(selector_value):
            if multi:
                return selector_value
            return selector_value[0]
        return None

    def clean_data(self):
        """This function is mainly for making sure the extracted values are indeed the type of value
        we want and to make sure it will save correctly into the database. News sites have a huge
        variety of ways they display certain data such as publish date."""
        # We set a now variable to make sure the date extracted is not a future date.
        now = datetime.now(pytz.timezone("America/New_York"))
        try:
            # Since some of the tz info from sites are not valid in Django we insert the correct variations
            parsed_date = parser.parse(self.publish_date, tzinfos=TIMEZONE_DICT)
            if not parsed_date.tzinfo:
                # Sets timezone to EST if it's not included from the site.
                parsed_date = parsed_date.astimezone(pytz.timezone("America/New_York"))
            self.publish_date = None if parsed_date > now else parsed_date

            # These next lines are for cleaning up the text returned and making sure we only save the main author.
            self.content = self.content.replace("\n", " ").replace("\t", " ").replace("  ", "")
            author = self.author.replace("\n", "").replace(" and ", ",").replace("By ,", "").strip()
            authors = author.split(",")
            self.author = authors[0]
            if len(self.title) > 150:
                self.title = self.title[:145]
        except (TypeError, KeyError, parser.ParserError) as e:
            self.error = "{} Error cleaning data: {}".format(type(e).__name__, self.article_values)
        except Exception as e:
            self.error = "Unknown Error () cleaning data: {}".format(e, self.article_values)
        return

    def save_article(self):
        from managr.comms.serializers import ArticleSerializer

        try:
            if self.article_instance:
                serializer = ArticleSerializer(
                    instance=self.article_instance, data=self.article_values
                )
            else:
                serializer = ArticleSerializer(data=self.article_values)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            self.saved = True
        except Exception as e:
            self.error = "Error saving article: {}".format(e)
            self.saved = False
        return


class SourceExtractor:
    def __init__(self, response, source):
        self.response = response
        self.source = source
        self.error = None
        self.set_source_values()

    def set_source_values(self):
        self.use_scrape_api = False
        self.site_name = self.source.site_name
        self.icon = self.source.icon
        self.domain = self.source.domain
        self.sitemap = self.source.sitemap
        self.scrape_data = self.source.scrape_data
        self.article_link_selector = self.source.article_link_selector
        self.article_link_attribute = self.source.article_link_attribute
        self.data_attribute_key = self.source.data_attribute_key
        self.data_attribute_value = self.source.data_attribute_value
        self.author_selector = self.source.author_selector
        self.date_published_selector = self.source.date_published_selector
        self.article_title_selector = self.source.article_title_selector
        self.article_content_selector = self.source.article_content_selector
        self.image_url_selector = self.source.image_url_selector
        self.description_selector = self.source.description_selector
        self.article_link_regex = self.source.article_link_regex

    def parse(self):
        if self.response.status >= 400:
            self.use_scrape_api = True
        else:
            self.site_name = self.get_site_name()
            self.icon = self.get_site_icon()
            url = self.validate_url()
            if url != self.domain:
                self.domain == url
            self.scrape_data = self.get_article_link_data()
            self.check_if_date_format()
            if not self.article_link_attribute:
                self.common_selectors_check()
            self.article_link_regex = self.create_search_regex()
        self.save_source_data()
        return self.source

    def save_source_data(self):
        source_data = [
            "site_name",
            "icon",
            "domain",
            "sitemap",
            "scrape_data",
            "use_scrape_api",
            "article_link_selector",
            "article_link_attribute",
            "data_attribute_key",
            "data_attribute_value",
            "article_link_regex",
        ]
        for field in source_data:
            value = getattr(self, field)
            setattr(self.source, field, value)
        self.source.save()
        self.source.refresh_from_db()
        return

    def save_article_selectors(self):
        article_selectors = [
            "author_selector",
            "date_published_selector",
            "article_title_selector",
            "article_content_selector",
            "image_url_selector",
            "description_selector",
        ]
        for selector in article_selectors:
            value = getattr(self, selector)
            setattr(self.source, selector, value)
        self.source.save()
        self.source.refresh_from_db()
        return

    def common_selectors_check(self):
        for dataset in self.scrape_data.values():
            href = dataset["href"]
            classes = dataset["classes"]
            if classes:
                found_class, found_attribute = check_classes(classes)
                if found_class:
                    self.article_link_selector = found_class
                    self.article_link_attribute = found_attribute
                    break
            found_value, found_attribute = check_values(href)
            if found_value:
                self.article_link_selector = found_value
                self.article_link_attribute = found_attribute
                break
        return

    def validate_url(self):
        og_domain = self.domain
        response_url = self.response.url
        validated_url = response_url
        if og_domain not in response_url:
            if response_url[0] == "/":
                validated_url = og_domain + response_url
            if self.response.status >= 300:
                redirect_urls = self.response.meta.get("redirect_urls", [])
                if redirect_urls:
                    if og_domain not in redirect_urls[0]:
                        validated_url = redirect_urls[0]
                        self.error = "New URL found for {}: {}".format(og_domain, validated_url)
        return validated_url

    def get_site_name(self):
        xpaths = ["//meta[contains(@property, 'og:site_name')]/@content", "//title/text()"]
        site_url = urlparse(self.response.request.url).netloc.strip("www.")
        site_name = site_url
        for xpath in xpaths:
            found = self.response.xpath(xpath).get()
            if found:
                site_name = found
                break
        return site_name

    def get_site_icon(self):
        xpath = "//link[contains(@href,'.ico')]/@href"
        icon_href = self.response.xpath(xpath).get()
        if icon_href:
            if icon_href[0] == "/":
                icon_href = self.response.request.url + icon_href
        else:
            return None
        return icon_href

    def get_article_link_data(self):
        anchor_tags = self.response.xpath(HOMEPAGE_ANCHOR_TAG_XPATH)
        scrape_dict = {}
        for idx, link in enumerate(anchor_tags):
            href = link.css("::attr(href)").get()
            updated_url = complete_url(href, self.domain)
            is_potential_link = potential_link_check(updated_url, self.domain)
            if is_potential_link:
                parent = (
                    self.response.xpath(f"//a[@href='{href}']/parent::*").css("::attr(class)").get()
                )
                if parent:
                    for word in EXCLUDE_CLASSES:
                        if word in parent:
                            is_potential_link = False
                            break
                if not is_potential_link:
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
        return scrape_dict

    def selector_processor(self):
        selector_split = self.article_link_selector.split(",")
        selector_type = selector_split[0]
        if selector_type == "year":
            selector = "contains(@href, '{}')".format(str(datetime.now().year))
        if selector_type == "value":
            if "|" in selector_split[1]:
                selector = ""
                values = selector_split[1].split("|")
                for idx, value in enumerate(values):
                    selector += "contains(@href, '{}')".format(value)
                    if idx != len(values) - 1:
                        selector += " or "
            else:
                selector = "contains(@href, '{}')".format(selector_split[1])
        if selector_type == "class":
            if "|" in selector_split[1]:
                selector = ""
                values = selector_split[1].split("|")
                for idx, value in enumerate(values):
                    if "=" in value:
                        value = value.replace("=", "")
                        selector += "@class='{}'".format(value)
                    else:
                        selector += "contains(@class, '{}')".format(value)
                    if idx != len(values) - 1:
                        selector += " or "
            else:
                if "=" in selector_split[1]:
                    value = selector_split[1].replace("=", "")
                    selector = "@class='{value}'".format(value)
                else:
                    selector = "contains(@class, '{}')".format(selector_split[1])
        return selector

    def check_sitemap(self):
        try:
            sitemap_url = f"{self.domain}/sitemap.xml"
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                tree = etree.fromstring(response.content)
                for sitemap in tree.xpath(
                    "//xmlns:sitemap/xmlns:loc",
                    namespaces={"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"},
                ):
                    loc = sitemap.text
                    if "news.xml" in loc:
                        sitemap_url = loc
                        break
                self.sitemap = sitemap_url
            else:
                robots_url = f"{self.domain}/robots.txt"
                response = requests.get(robots_url, timeout=10)
                if response.status_code == 200:
                    if "Sitemap" in response.text:
                        sitemap_url = response.text.split("Sitemap: ")[1].strip().split("\n")[0]
                        self.sitemap = sitemap_url
                    else:
                        return "No sitemap found"
        except Exception as e:
            return "No sitemap found"
        return

    def check_if_date_format(self):
        urls = [u["href"] for u in self.scrape_data.values()]
        if len(urls) == 0:
            return self
        sample_size = max(1, len(urls) // 10)
        sample = random.sample(urls, sample_size)
        matches = []
        pattern = re.compile(URL_DATE_PATTERN)
        for url in sample:
            try:
                m = pattern.search(url)
                if m:
                    matches.append(m.groups())
            except Exception as e:
                continue
        if matches:
            is_date = len(matches) / len(sample) >= 0.5
            year, month, day = matches[0]
            for v in [year, month, day]:
                if v is None or v.isdigit():
                    continue
                else:
                    return self
            logger.info("{} ({})".format((len(matches) / len(sample)), "{year}/{month}/{day}"))
            if is_date:
                self.article_link_selector = "year"
                self.article_link_attribute = "a"
                return
        return

    def add_selectors(self):
        url = self.response.url
        xpath_copy = copy(XPATH_STRING_OBJ)
        fields_dict = {}
        article_selectors = self.source.article_selectors
        for key in xpath_copy.keys():
            if article_selectors[key] is not None:
                xpath_copy[key] = [article_selectors[key]]
            for path in xpath_copy[key]:
                try:
                    selector = self.response.xpath(path).getall()
                except ValueError as e:
                    selector = None
                    self.error = "ERROR ({})\n{}\n{}: -{}-".format(e, url, key, path)
                if selector:
                    if key == "publish_date" and "//script" not in path:
                        if "text" in path:
                            selector = extract_date_from_text(selector, TIMEZONE_DICT)
                        else:
                            try:
                                check_if_date = parser.parse(selector, tzinfos=TIMEZONE_DICT)
                            except TypeError as e:
                                selector = None
                            except Exception as e:
                                continue
                    if "//script" in path:
                        if isinstance(selector, list):
                            selector = [json.loads(a.lower()) for a in selector]
                        script_key = "name" if key == "author" else "datepublished"
                        key_path = find_key(selector, script_key)
                        if key_path is not None:
                            if isinstance(selector, list):
                                path = f"({path})[{int(key_path[1])+ 1}]{key_path[2:]}"
                            else:
                                path = path + key_path
                        else:
                            selector = None
                else:
                    selector = None
                if selector is not None:
                    fields_dict[key] = path
                    break
        if len(fields_dict):
            for key in fields_dict.keys():
                path = fields_dict[key]
                field = XPATH_TO_FIELD[key]
                setattr(self, field, path)
        self.save_article_selectors()
        return self.source, self.source.article_selectors

    def create_search_regex(self):
        current_year = str(datetime.now().year)
        if self.article_link_regex is not None:
            if self.article_link_selector == "year" and current_year in self.article_link_regex:
                return self.article_link_regex
            elif self.article_link_selector != "year":
                return self.article_link_regex
        # add the link selector
        attribute_list = self.article_link_attribute.split(",")
        regex = "//body//" + attribute_list[0]
        if self.article_link_selector or self.data_attribute_key:
            regex += "["
        # check for data attribute
        if self.data_attribute_key:
            if self.data_attribute_value is not None:
                regex += f"@{self.data_attribute_key}='{self.data_attribute_value}'"
            else:
                regex += f"@{self.data_attribute_key}"
        # check for link attribute
        if self.article_link_selector:
            selector = self.selector_processor()
            if "@data" in regex:
                regex += f" and {selector}"
            else:
                regex += selector
            regex += "]"
        if len(attribute_list) > 1:
            regex += f"//{attribute_list[1]}[1]"
        return regex
