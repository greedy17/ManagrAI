import json
import os
import logging
import base64
import hashlib
import httpx
import pytz
import math
import re
from datetime import datetime, timedelta
from dateutil import parser
from django.db import models
from managr.core.models import TimeStampModel
from django.db.models.constraints import UniqueConstraint
from newspaper import ArticleException
from newspaper import Article as ExternalArticle
from managr.core import constants as core_consts
from . import constants as comms_consts
from managr.slack.helpers import block_builders
from .exceptions import (
    _handle_response as _handle_news_response,
    TwitterApiException,
    InstagramApiException,
)
from managr.utils.client import Variable_Client
from managr.utils.sites import get_site_url
from managr.core import exceptions as open_ai_exceptions
from managr.utils.misc import encrypt_dict
from urllib.parse import urlencode, urlparse
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex
from requests_oauthlib import OAuth1Session, OAuth2Session
from oauthlib.oauth2 import OAuth2Error
from collections import Counter
from django.conf import settings

logger = logging.getLogger("managr")


class Search(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="news_search",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    input_text = models.TextField(null=True, blank=True)
    search_boolean = models.TextField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    type = models.CharField(choices=comms_consts.SEARCH_TYPE_CHOICES, max_length=50, default="NEWS")
    meta_data = JSONField(
        default=dict,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.user.email}"

    def update_boolean(self):
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = core_consts.OPEN_AI_NEWS_BOOLEAN_CONVERSION(self.input_text)
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                self.user.email,
                prompt,
                token_amount=500,
                top_p=0.1,
            )
            with Variable_Client() as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            r = open_ai_exceptions._handle_response(r)
            query_input = r.get("choices")[0].get("message").get("content")
            self.search_boolean = query_input
        except Exception as e:
            logger.exception(e)
        return self.save()

    @classmethod
    def get_summary(
        cls,
        user,
        tokens,
        timeout,
        clips,
        input_text,
        previous,
        is_follow__up,
        company,
        trending,
        instructions=False,
        for_client=False,
    ):
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        elma = core_consts.ELMA

        if is_follow__up:
            prompt = comms_consts.SUMMARY_FOLLOW_UP(
                datetime.now().date(), clips, previous, company, elma, instructions, trending
            )
        else:
            prompt = (
                comms_consts.OPEN_AI_NEWS_CLIPS_SUMMARY(
                    datetime.now().date(),
                    clips,
                    input_text,
                    company,
                    elma,
                    trending,
                    instructions,
                    for_client,
                )
                if for_client
                else comms_consts.OPEN_AI_NEWS_CLIPS_SLACK_SUMMARY(
                    datetime.now().date(), clips, input_text, previous, instructions, for_client
                )
            )

        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email,
            prompt,
            temperature=0.1,
            top_p=0.1,
            # model="o1-mini",
        )
        with Variable_Client(timeout) as client:
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        return open_ai_exceptions._handle_response(r)

    @classmethod
    def get_summary_email(
        cls, user, tokens, timeout, clips, input_text, instructions=False, for_client=False
    ):
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        elma = core_consts.ELMA
        project = ""

        prompt = (
            comms_consts.OPEN_AI_NEWS_CLIPS_SUMMARY_EMAIL(
                datetime.now().date(), clips, input_text, elma, project, instructions, for_client
            )
            if for_client
            else comms_consts.OPEN_AI_NEWS_CLIPS_SLACK_SUMMARY(
                datetime.now().date(), clips, input_text, instructions, for_client
            )
        )
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email,
            prompt,
            "You are a VP of Communications",
            top_p=0.1,
            # model="o1-mini",
        )
        with Variable_Client(timeout) as client:
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        return open_ai_exceptions._handle_response(r)

    @classmethod
    def get_clips(cls, search_boolean, date_to=False, date_from=False, is_report=False):
        page_size = 40
        if is_report:
            page_size = 100
        query = {"q": search_boolean, "excludeDomains": ",".join(comms_consts.EXCLUDE_DOMAINS)}
        if date_to:
            query["to"] = date_to
            query["from"] = date_from
        endpoint = (
            comms_consts.NEW_API_EVERYTHING_QUERY_URI(urlencode(query)) + f"&pageSize={page_size}"
        )
        news_url = comms_consts.NEW_API_URI + "/" + endpoint
        with Variable_Client() as client:
            new_res = client.get(news_url, headers=comms_consts.NEWS_API_HEADERS)
        return _handle_news_response(new_res)

    @classmethod
    def no_results(cls, user, boolean):
        timeout = 60.0
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI

        prompt = comms_consts.OPEN_AI_NO_RESULTS(boolean)
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user,
            prompt,
            top_p=0.1,
            # model="o1-mini",
        )
        with Variable_Client(timeout) as client:
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        return open_ai_exceptions._handle_response(r)

    def generate_shareable_link(self):
        date = str(datetime.now())
        data = {"created_at": date, "id": str(self.id)}
        encrypted_data = encrypt_dict(data)
        base_url = get_site_url()
        return f"{base_url}/shared/{encrypted_data}"


class TwitterAuthAccountAdapter:
    def __init__(self, **kwargs):
        self.user = kwargs.get("user", None)
        self.access_token = kwargs.get("access_token", None)
        self.display_name = kwargs.get("display_name", None)

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError

        elif response.status_code == 200 or response.status_code == 201:
            try:
                data = response.json()
            except json.decoder.JSONDecodeError as e:
                return logger.error(f"An error occured with a nylas integration, {e}")
            except Exception as e:
                print(str(e))
                TwitterApiException(e)

        else:
            status_code = response.status_code
            error_data = response.json()
            error_param = error_data.get("errors", None)
            error_message = error_data.get("message", None)
            error_code = error_data.get("code", None)
            kwargs = {
                "status_code": status_code,
                "error_code": error_code,
                "error_param": error_param,
                "error_message": error_message,
            }
            return TwitterApiException(kwargs)
        return data

    def get_request_url():
        params = urlencode({"oauth_callback": comms_consts.TWITTER_REDIRECT_URI})
        return f"{comms_consts.TWITTER_BASE_URI}{comms_consts.TWITTER_REQUEST_TOKEN_URI}?{params}"

    def get_tweets(self, query, next_token=False):
        url = comms_consts.TWITTER_BASE_URI + comms_consts.TWITTER_RECENT_TWEETS_URI
        params = {
            "query": query,
            "max_results": 50,
            "expansions": "author_id,attachments.media_keys",
            "user.fields": "username,name,profile_image_url,public_metrics,verified,location,url",
            "tweet.fields": "created_at",
            "media.fields": "url,variants",
            "sort_order": "relevancy",
        }
        if next_token:
            params["next_token"] = next_token
        headers = comms_consts.TWITTER_API_HEADERS
        with Variable_Client() as client:
            response = client.get(url, headers=headers, params=params)
            return self._handle_response(response)

    def get_summary(
        self,
        user,
        tokens,
        timeout,
        tweets,
        input_text,
        project,
        instructions=False,
        for_client=False,
    ):
        elma = core_consts.ELMA
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        prompt = comms_consts.OPEN_AI_TWITTER_SUMMARY(
            datetime.now().date(), tweets, input_text, project, elma, for_client
        )
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email,
            prompt,
            "You are a VP of Communications",
            token_amount=tokens,
            top_p=0.1,
        )
        with Variable_Client(timeout) as client:
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        return open_ai_exceptions._handle_response(r)

    @classmethod
    def get_authorization_link(cls):
        CODE_VERIFIER = os.urandom(32)
        CODE_CHALLENGE = (
            base64.urlsafe_b64encode(hashlib.sha256(CODE_VERIFIER).digest())
            .rstrip(b"=")
            .decode("utf-8")
        )
        auth_params = {
            "response_type": "code",
            "client_id": comms_consts.TWITTER_CLIENT_ID,
            "redirect_uri": comms_consts.TWITTER_REDIRECT_URI,
            "scope": " ".join(comms_consts.TWITTER_SCOPES),
            "state": "TWITTER",
            "code_challenge_method": "S256",
            "code_challenge": CODE_CHALLENGE,
        }
        auth_url = comms_consts.TWITTER_AUTHORIZATION_URI + "?" + urlencode(auth_params)
        return auth_url, str(CODE_VERIFIER)

    @classmethod
    def get_access_token(cls, code, verifier):
        params = {
            "grant-type": "authorization_code",
            "code": code,
            "client_id": comms_consts.TWITTER_CLIENT_ID,
            "redirect_uri": comms_consts.TWITTER_REDIRECT_URI,
            "code_verifier": verifier,
        }
        url = comms_consts.TWITTER_ACCESS_TOKEN_URI + "?" + urlencode(params)
        with Variable_Client() as client:
            res = client.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"})
        return cls._handle_response(res)


class Pitch(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="pitches",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    instructions = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=300, null=True, blank=True)
    audience = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    generated_pitch = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.email} - {self.name}"

    @classmethod
    def generate_pitch(cls, user, type, instructions, style, tokens, timeout):
        elma = core_consts.ELMA
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        # style = user.writing_style if user.writing_style else False
        prompt = comms_consts.OPEN_AI_PITCH(datetime.now().date(), type, instructions, elma, style)
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(user.email, prompt, model="o1-mini")
        with Variable_Client(timeout) as client:
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        return open_ai_exceptions._handle_response(r)


class NewsSource(TimeStampModel):
    domain = models.CharField(max_length=255, unique=True)
    site_name = models.CharField(max_length=255, blank=True, null=True)
    sitemap = models.CharField(max_length=255, blank=True, null=True)
    last_scraped = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_crawling = models.BooleanField(default=False)
    is_stopped = models.BooleanField(default=False)
    use_scrape_api = models.BooleanField(default=False)
    posting_frequency = models.IntegerField(default=0)
    scrape_type = models.CharField(
        choices=[("HTML", "HTML"), ("SITEMAP", "Sitemap"), ("XML", "XML")],
        max_length=50,
        default="HTML",
    )
    access_count = JSONField(default=dict, null=True, blank=True)
    icon = models.TextField(null=True, blank=True)
    # Web Scraping Fields
    category_link_selector = models.CharField(max_length=255, blank=True, null=True)
    category_name_attribute = models.CharField(max_length=50, blank=True, null=True)
    category_mapping = JSONField(
        blank=True,
        null=True,
        help_text="JSON mapping of website categories to application categories",
    )
    article_link_selector = models.CharField(max_length=255, blank=True, null=True)
    article_link_attribute = models.CharField(max_length=50, blank=True, null=True)
    article_link_prefix = models.URLField(blank=True, null=True)
    article_link_regex = models.CharField(max_length=500, blank=True, null=True)
    data_attribute_key = models.CharField(max_length=255, blank=True, null=True)
    data_attribute_value = models.CharField(max_length=255, blank=True, null=True)
    date_published_selector = models.CharField(max_length=255, blank=True, null=True)
    date_published_format = models.CharField(max_length=255, blank=True, null=True)
    article_title_selector = models.CharField(max_length=255, blank=True, null=True)
    article_content_selector = models.CharField(max_length=255, blank=True, null=True)
    author_selector = models.CharField(max_length=255, blank=True, null=True)
    description_selector = models.CharField(max_length=255, blank=True, null=True)
    image_url_selector = models.CharField(max_length=255, blank=True, null=True)
    scrape_data = JSONField(default=dict, null=True, blank=True)
    error_log = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.domain

    class Meta:
        ordering = ["-datetime_created"]

    def article_selectors(self):
        return {
            "author": self.author_selector,
            "publish_date": self.date_published_selector,
            "title": self.article_title_selector,
            "content": self.article_content_selector,
            "image_url": self.image_url_selector,
            "description": self.description_selector,
            "content": self.article_content_selector,
        }

    @property
    def selectors_defined(self):
        selector_obj = self.article_selectors()
        for value in selector_obj.values():
            if value is None:
                return False
        return True

    def selector_processor(self):
        selector_split = self.article_link_selector.split(",")
        selector_type = selector_split[0]
        if selector_type == "year":
            selector = f"contains(@href, '{str(datetime.now().year)}')"
        if selector_type == "value":
            if "|" in selector_split[1]:
                selector = ""
                values = selector_split[1].split("|")
                for idx, value in enumerate(values):
                    selector += f"contains(@href, '{value}')"
                    if idx != len(values) - 1:
                        selector += " or "
            else:
                selector = f"contains(@href, '{selector_split[1]}')"
        if selector_type == "class":
            if "|" in selector_split[1]:
                selector = ""
                values = selector_split[1].split("|")
                for idx, value in enumerate(values):
                    if "=" in value:
                        value = value.replace("=", "")
                        selector += f"@class='{value}'"
                    else:
                        selector += f"contains(@class, '{value}')"
                    if idx != len(values) - 1:
                        selector += " or "
            else:
                if "=" in selector_split[1]:
                    value = selector_split[1].replace("=", "")
                    selector = f"@class='{value}'"
                else:
                    selector = f"contains(@class, '{selector_split[1]}')"
        return selector

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
            regex += f"/{attribute_list[1]}[1]"
        self.article_link_regex = regex
        self.save()
        return regex

    def transfer_dict(self):
        return dict(
            domain=self.domain,
            site_name=self.site_name,
            last_scraped=str(self.last_scraped),
            article_link_selector=self.article_link_selector,
            article_link_attribute=self.article_link_attribute,
            article_link_regex=self.article_link_regex,
            data_attribute_key=self.data_attribute_key,
            data_attribute_value=self.data_attribute_value,
            date_published_selector=self.date_published_selector,
            author_selector=self.author_selector,
            article_content_selector=self.article_content_selector,
            is_active=self.is_active,
            article_title_selector=self.article_title_selector,
            image_url_selector=self.image_url_selector,
            description_selector=self.description_selector,
        )

    @property
    def crawling(self):
        article_check = Article.objects.filter(source=self)
        if len(article_check):
            self.is_crawling = True
            self.save()
            return self.is_crawling
        return False

    @classmethod
    def get_stopped_sources(cls, include_date=False):
        news = NewsSource.objects.filter(
            is_crawling=True, is_active=True, is_stopped=True
        ).values_list("domain", flat=True)
        stopped_sources = list(news)
        return stopped_sources

    @classmethod
    def domain_list(cls, scrape_ready=False, new=False, type="HTML", run_now=False):
        six_hours = datetime.now() - timedelta(hours=6)
        active_sources = cls.objects.filter(is_active=True, scrape_type=type)
        if scrape_ready and new:
            active_sources = active_sources.filter(
                article_link_selector__isnull=False, article_link_regex__isnull=True
            )
        # filters sources that are already scrapping
        elif scrape_ready and not new:
            if settings.IN_DEV or run_now:
                active_sources = active_sources.filter(is_crawling=True)
            else:
                active_sources = active_sources.filter(is_crawling=True, is_stopped=False).filter(
                    last_scraped__lt=six_hours
                )
        # filters sources that were just added and don't have scrape data yet
        elif not scrape_ready and new:
            active_sources = active_sources.filter(article_link_attribute__isnull=True)
        source_list = [source.domain for source in active_sources]
        return source_list

    @classmethod
    def problem_urls(cls):
        d = datetime.now().date()
        news = NewsSource.objects.filter(last_scraped__date=d, is_active=False).values_list(
            "domain", flat=True
        )
        return list(news)

    def newest_article_date(self):
        articles = self.articles.all().order_by("-publish_date")
        if articles:
            newest_article_date = articles.first().publish_date
            return newest_article_date
        return None

    def add_error(self, error):
        if self.error_log:
            self.error_log += error
        else:
            self.error_log = error
        return self.save()

    def sync_journalists(self):
        from managr.comms.serializers import JournalistSerializer

        parsed_domain = urlparse(self.domain)
        domain = parsed_domain.netloc
        articles = self.articles.all().values_list("author", flat=True)
        author_set = list(set(articles))
        for a in author_set:
            if "staff" in a.lower() or self.site_name in a or "The " in a:
                continue
            try:
                if " and " in a:
                    author_list = a.split(" and ")
                else:
                    author_list = a.split(",")
            except ValueError as e:
                print(f"{a} - {e}")
                continue
            for author in author_list:
                try:
                    author_names = author.split(" ")
                    if len(author_names) == 2:
                        first = author_names[0]
                        last = author_names[1]
                    elif len(author_names) == 3:
                        first = author_names[0]
                        if "II" in author_names[2]:
                            last = author_names[1]
                        else:
                            last = author_names[2]
                    else:
                        first = author_names[0]
                        last = author_names[1:]
                    journalist_check = Journalist.objects.filter(first_name=first, last_name=last)
                    if len(journalist_check):
                        continue
                    response = Journalist.email_finder(domain, first, last)
                    if "score" in response.keys() and response["score"] is not None:
                        is_valid = (
                            False
                            if response["verification"]["status"] in ["invalid", "unknown"]
                            else True
                        )
                        data = {
                            "verified": is_valid,
                            "first_name": response["first_name"],
                            "last_name": response["last_name"],
                            "email": response["email"],
                            "outlet": response["company"],
                            "accuracy_score": response["score"],
                            "number_of_sources": len(response["sources"]),
                        }
                        serializer = JournalistSerializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                    else:
                        print(f"Failed to find journalist: {response}")
                except ValueError as e:
                    print(f"Failed to split author name: {author} - {e}")
                except Exception as e:
                    print(f"{author} - {e}")
                    continue
        return

    def calculate_posting_frequency(self):
        alpha = 0.3
        publish_dates = list(self.articles.all().values_list("publish_date", flat=True))
        parsed_dates = []
        for date in publish_dates:
            try:
                parsed_dates.append(datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S.%f"))
            except ValueError:
                parsed_dates.append(datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S"))
        unique_dates = sorted({date.date() for date in parsed_dates})
        if len(unique_dates) <= 1:
            return f"Not enough articles synced for {source.domain}"
        time_diffs = [
            (unique_dates[i] - unique_dates[i - 1]).days for i in range(1, len(unique_dates))
        ]
        if len(time_diffs):
            ema = time_diffs[0]
            for diff in time_diffs[1:]:
                ema = alpha * diff + (1 - alpha) * ema
            self.posting_frequency = math.ceil(ema)
        else:
            print(f"Unique: {unique_dates}\nTime Diffs: {time_diffs}")
        return self.save()

    def check_if_stopped(self):
        if self.posting_frequency == 0:
            return
        newest_article = self.newest_article_date()
        if newest_article:
            article_date = newest_article.date()
            today = datetime.now().date()
            days_since_last_article = (today - article_date).days
            if days_since_last_article > self.posting_frequency:
                self.is_stopped = True
                if days_since_last_article > 30:
                    self.is_active = False
            else:
                self.is_stopped = False
        self.save()
        return self.is_stopped


class Article(TimeStampModel):
    title = models.CharField(max_length=150)
    description = models.TextField(null=True)
    author = models.CharField(max_length=150, blank=True, null=True)
    publish_date = models.DateTimeField()
    link = models.CharField(max_length=255)
    image_url = models.CharField(max_length=500)
    source = models.ForeignKey(
        "comms.NewsSource", on_delete=models.CASCADE, related_name="articles"
    )
    content = models.TextField()
    content_search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=["content_search_vector"]),
            models.Index(fields=["-publish_date"]),
        ]
        constraints = [UniqueConstraint(fields=["source", "title"], name="unique_article")]

    def update_search_vector(self):
        try:
            self.content_search_vector = SearchVector("content")
            self.save()
        except Exception as e:
            return str(e)
        return True

    def fields_to_dict(self, internal_flag=True):
        site_name = (
            self.source.site_name if hasattr(self.source, "site_name") else self.source.domain
        )
        fields = dict(
            title=self.title,
            description=self.description,
            author=self.author,
            publish_date=str(self.publish_date),
            link=self.link,
            image_url=self.image_url,
            source={"name": site_name, "icon": self.source.icon},
        )
        if internal_flag:
            fields["i"] = True
        return fields

    @classmethod
    def search_by_query(
        cls, boolean_string, date_to=False, date_from=False, author=False, for_report=False
    ):
        from managr.comms.utils import boolean_search_to_query, boolean_search_to_searchquery

        date_to_date_obj = parser.parse(date_to)
        day_incremented = date_to_date_obj + timedelta(days=1)
        day_incremented_str = str(day_incremented)
        date_range_articles = Article.objects.filter(
            publish_date__range=(date_from, day_incremented_str)
        )
        if author:
            boolean_string = boolean_string.replace("journalist:", "").strip()
            articles = date_range_articles.filter(author__icontains=boolean_string)
        else:
            converted_boolean = boolean_search_to_query(boolean_string)
            articles = date_range_articles.filter(converted_boolean)
            # articles = date_range_articles.annotate(search=SearchVector("content")).filter(
            #     search=converted_boolean
            # )
        if for_report:
            articles = articles[:100]
        else:
            articles = articles[:20]
        return list(articles)


class WritingStyle(models.Model):
    style = models.TextField()
    title = models.TextField()
    user = models.ForeignKey(
        "core.User",
        related_name="writing_styles",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

    @property
    def as_slack_option(self):
        return block_builders.option(self.title[:74], str(self.id))


class AssistAlert(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="assist_alerts",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    type = models.CharField(choices=comms_consts.ALERT_TYPES, max_length=50, default="EMAIL")
    title = models.CharField(max_length=255)
    run_at = models.DateTimeField()
    search = models.ForeignKey(
        "Search",
        related_name="alerts",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    thread = models.ForeignKey(
        "Thread",
        related_name="threads",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    recipients = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    meta_data = JSONField(
        default=dict,
        null=True,
        blank=True,
    )

    def add_recipient(self, email):
        new_recipients = self.recipients.append(email)
        remove_duplicates = list(set(new_recipients))
        self.recipients = remove_duplicates
        return self.save()

    def remove_recipient(self, email):
        remove_index = self.recipients.index(email)
        self.recipients.pop(remove_index)
        return self.save()

    def update_thread_data(self, for_dev=False):
        from managr.comms.utils import normalize_article_data

        project = self.thread.meta_data.get("project", "")
        if self.search.search_boolean == self.search.input_text:
            self.search.update_boolean()
        boolean = self.search.search_boolean
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        clips = self.search.get_clips(boolean, end_time, start_time)["articles"]
        try:
            clips = [article for article in clips if article["title"] != "[Removed]"]
            internal_articles = Article.search_by_query(boolean, str(end_time), str(start_time))
            normalized_clips = normalize_article_data(clips, internal_articles, False)
            descriptions = [clip["description"] for clip in normalized_clips]
            if for_dev:
                print(f"Current Boolean: {boolean}")
                print(f"Clips ({len(clips)}): {clips}")
                print("------------------------------")
                print(f"Internal Clips ({len(internal_articles)}): {internal_articles}")
                print("------------------------------")
            res = Search.get_summary(
                self.user,
                2000,
                60.0,
                descriptions,
                self.search.instructions,
                False,
                False,
                project,
                False,
                self.search.instructions,
                True,
            )
            if for_dev:
                print(f"Chat response: {res}")
            else:
                message = res.get("choices")[0].get("message").get("content").replace("**", "*")
                message = re.sub(r"\*(.*?)\*", r"<strong>\1</strong>", message)
                message = re.sub(
                    r"\[(.*?)\]\((.*?)\)", r'<a href="\2" target="_blank">\1</a>', message
                )
                self.thread.meta_data["articlesFiltered"] = normalized_clips
                self.thread.meta_data["filteredArticles"] = normalized_clips
                self.thread.meta_data["summary"] = message
                self.thread.meta_data["summaries"] = []
                self.thread.save()
        except Exception as e:
            print(str(e))
        return


class Process(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="process",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    search_id = models.CharField(max_length=255)
    type = models.TextField(null=True, blank=True)
    details = models.TextField()
    style = models.TextField(null=True, blank=True)
    generated_content = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["name"]


class TwitterAccount(TimeStampModel):
    user = models.OneToOneField(
        "core.User",
        related_name="twitter_account",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    access_token = models.CharField(max_length=255, null=True)
    access_token_secret = models.CharField(max_length=255, null=True)
    display_name = models.CharField(max_length=255, null=True)

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError

        elif response.status_code == 200 or response.status_code == 201:
            try:
                data = response.json()
            except json.decoder.JSONDecodeError as e:
                return logger.error(f"An error occured with a nylas integration, {e}")
            except Exception as e:
                TwitterApiException(e)

        else:
            print(vars(response))
            status_code = response.status_code
            error_data = response.json()
            error_param = error_data.get("errors", None)
            error_message = error_data.get("message", None)
            error_code = error_data.get("code", None)
            kwargs = {
                "status_code": status_code,
                "error_code": error_code,
                "error_param": error_param,
                "error_message": error_message,
            }
            return TwitterApiException(kwargs)
        return data

    def get_tweets(self, query, next_token=False):
        url = comms_consts.TWITTER_BASE_URI + comms_consts.TWITTER_RECENT_TWEETS_URI
        params = {
            "query": query,
            "max_results": 50,
            "expansions": "author_id,attachments.media_keys",
            "user.fields": "username,name,profile_image_url,public_metrics,verified,location,url",
            "tweet.fields": "created_at",
            "media.fields": "url,variants",
            "sort_order": "relevancy",
        }
        if next_token:
            params["next_token"] = next_token
        headers = comms_consts.TWITTER_API_HEADERS
        with Variable_Client() as client:
            response = client.get(url, headers=headers, params=params)
            return self._handle_response(response)

    @classmethod
    def get_summary(
        cls,
        user,
        tokens,
        timeout,
        tweets,
        input_text,
        company,
        instructions=False,
        for_client=False,
    ):
        elma = core_consts.ELMA
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        if "from:" in input_text:
            instructions = comms_consts.TWITTER_USERNAME_INSTRUCTIONS(company)
        prompt = comms_consts.OPEN_AI_TWITTER_SUMMARY(
            datetime.now().date(), tweets, input_text, company, elma, for_client
        )
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email,
            prompt,
            "You are a VP of Communications",
            token_amount=tokens,
            top_p=0.1,
        )
        with Variable_Client(timeout) as client:
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        return open_ai_exceptions._handle_response(r)

    def get_summary_follow_up(self, user, tokens, timeout, previous, tweets, project, instructions):
        elma = core_consts.ELMA
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI

        prompt = comms_consts.TWITTER_SUMMARY_FOLLOW_UP(
            datetime.now().date(),
            tweets,
            previous,
            project,
            elma,
            instructions,
        )

        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email,
            prompt,
            "You are a VP of Communications",
            token_amount=tokens,
            top_p=0.1,
        )
        with Variable_Client(timeout) as client:
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        return open_ai_exceptions._handle_response(r)

    def no_results(cls, user, boolean):
        timeout = 60.0
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI

        prompt = comms_consts.OPEN_AI_NO_RESULTS(boolean)
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user,
            prompt,
            top_p=0.1,
            # model="o1-mini",
        )
        with Variable_Client(timeout) as client:
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        return open_ai_exceptions._handle_response(r)

    def adapter(self):
        return TwitterAuthAccountAdapter(
            **{
                "user": self.user,
                "access_token": self.access_token,
                "display_name": self.display_name,
            }
        )

    @staticmethod
    def get_authorization(token):
        query = urlencode(comms_consts.TWITTER_TOKEN_PARAMS(token))
        return f"{comms_consts.TWITTER_AUTHORIZATION_URI}?{query}"

    @staticmethod
    def get_token(request):
        client = OAuth1Session(
            comms_consts.TWITTER_API_KEY,
            comms_consts.TWITTER_API_SECRET,
            callback_uri=comms_consts.TWITTER_REDIRECT_URI,
        )
        request_token = client.fetch_request_token(comms_consts.TWITTER_REQUEST_TOKEN_URI)
        authorization = client.authorization_url(comms_consts.TWITTER_AUTHORIZATION_URI)
        request_token["link"] = authorization
        return request_token

    @staticmethod
    def authenticate(request_token, verifier):
        client = OAuth1Session(
            comms_consts.TWITTER_API_KEY, comms_consts.TWITTER_API_SECRET, request_token
        )
        try:
            access_token = client.fetch_access_token(
                comms_consts.TWITTER_ACCESS_TOKEN_URI, verifier
            )
            return access_token
        except OAuth2Error:
            return "Invalid authorization code"


class InstagramAccount(TimeStampModel):
    user = models.OneToOneField(
        "core.User",
        related_name="instagram_account",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    facebook_id = models.CharField(max_length=255, null=True)
    instagram_id = models.CharField(max_length=255, null=True)
    access_token = models.TextField(null=True)
    display_name = models.CharField(max_length=255, null=True)
    hashtag_list = ArrayField(models.CharField(max_length=255), default=list)

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError

        elif response.status_code == 200 or response.status_code == 201:
            try:
                data = response.json()
            except json.decoder.JSONDecodeError as e:
                return logger.error(f"An error occured with a nylas integration, {e}")
            except Exception as e:
                InstagramApiException(e)

        else:
            status_code = response.status_code
            error_json = response.json()
            error_data = error_json.get("error", None)
            error_message = error_data.get("error_user_title", None)
            error_param = error_data.get("message", None)
            error_code = error_data.get("code", None)
            kwargs = {
                "status_code": status_code,
                "error_code": error_code,
                "error_param": error_param,
                "error_message": error_message,
            }
            return InstagramApiException(kwargs)
        return data

    # def check_for_hashtag(self, ht):
    #     for hashtag_str in self.hashtag_list:
    #         if ht in hashtag_str:
    #             hashtag, date, id = ht.split(".")
    #             return id
    #     return False

    def check_for_hashtag(self, ht):
        for hashtag_str in self.hashtag_list:
            if ht in hashtag_str:
                parts = hashtag_str.split(".")
                if len(parts) == 3:
                    hashtag, date, _id = parts
                    return _id
        return None

    def add_hashtag(self, hashtag, hashtag_id):
        date = str(datetime.now().date())
        hashtag_str = f"{hashtag}.{date}.{hashtag_id}"
        self.hashtag_list.append(hashtag_str)
        return self.save()

    def get_posts(self, hashtag_id, date_to, date_from, next_token=False):
        date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
        date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
        to_unix = int(date_to_obj.timestamp())
        from_unix = int(date_from_obj.timestamp()) + 86400
        url = comms_consts.INSTAGRAM_TOP_MEDIA_URI(hashtag_id)
        params = comms_consts.INSTAGRAM_MEDIA_PARAMS(self.instagram_id, to_unix, from_unix)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        with Variable_Client() as client:
            r = client.get(url, headers=headers, params=params)
            r = InstagramAccount._handle_response(r)
            return r

    def get_summary(self, user, tokens, timeout, posts, instructions=False, for_client=False):
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        prompt = comms_consts.OPEN_AI_INSTAGRAM_SUMMARY(
            datetime.now().date(), posts, instructions, for_client
        )
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email,
            prompt,
            "You are a VP of Communications",
            token_amount=tokens,
            top_p=0.1,
        )
        with Variable_Client(timeout) as client:
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        return open_ai_exceptions._handle_response(r)

    @staticmethod
    def get_long_lived_token(access_token):
        url = "https://graph.facebook.com/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "fb_exchange_token": access_token,
            "client_secret": comms_consts.INSTAGRAM_APP_SECRET,
            "client_id": comms_consts.INSTAGRAM_APP_KEY,
        }
        encoded_url = url + "?" + urlencode(params)
        with Variable_Client() as client:
            r = client.get(encoded_url)
            r = InstagramAccount._handle_response(r)
        token = r["access_token"]
        return token

    @staticmethod
    def get_token(request):
        client = OAuth2Session(
            comms_consts.INSTAGRAM_APP_KEY,
            redirect_uri=comms_consts.INSTAGRAM_REDIRECT_URI,
            scope=comms_consts.INSTAGRAM_SCOPES,
        )
        authorization_url, _ = client.authorization_url(
            comms_consts.INSTAGRAM_AUTHORIZATION_URI,
            state="INSTAGRAM",
        )
        return {"link": authorization_url}

    @staticmethod
    def authenticate(code):
        client = OAuth2Session(
            comms_consts.INSTAGRAM_APP_KEY, redirect_uri=comms_consts.INSTAGRAM_REDIRECT_URI
        )
        try:
            token = client.fetch_token(
                comms_consts.INSTAGRAM_ACCESS_TOKEN_URI,
                code=code,
                client_secret=comms_consts.INSTAGRAM_APP_SECRET,
                include_client_id=comms_consts.INSTAGRAM_APP_KEY,
            )
            # response = {"access_token": token["access_token"]}
            access_token = token["access_token"]
            long_lived_token = InstagramAccount.get_long_lived_token(access_token)
            response = {"access_token": long_lived_token}
            return response

        except OAuth2Error as e:
            print(e)
            return str(e)

    def get_account_id(self):
        url = comms_consts.INSTAGRAM_ACCOUNTS_URI
        headers = {"Authorization": f"Bearer {self.access_token}"}
        with Variable_Client() as client:
            r = client.get(url, headers=headers)
            r = InstagramAccount._handle_response(r)
        data = r["data"]
        id = data[0]["id"]
        return id

    def get_instagram_account_id(self, account_id):
        url = (
            comms_consts.INSTAGRAM_GRAPH_BASE_URL
            + account_id
            + "?fields=instagram_business_account"
        )
        headers = {"Authorization": f"Bearer {self.access_token}"}
        with Variable_Client() as client:
            r = client.get(url, headers=headers)
            r = InstagramAccount._handle_response(r)
        account = r["instagram_business_account"]
        id = account["id"]
        return id

    def get_hashtag_id(self, hashtag):
        hashtag_check = self.check_for_hashtag(hashtag)
        if hashtag_check:
            return hashtag_check
        else:
            url = comms_consts.INSTAGRAM_HASHTAG_SEARCH_URI
            params = urlencode({"user_id": self.instagram_id, "q": hashtag})
            headers = {"Authorization": f"Bearer {self.access_token}"}
            url = url + "?" + params
            with Variable_Client() as client:
                r = client.get(url, headers=headers)
                r = InstagramAccount._handle_response(r)
            id = r["data"][0]["id"]
            self.add_hashtag(hashtag, id)
            return id


class Discovery(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="discoveries",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    beat = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    list = models.TextField(null=True, blank=True)
    results = JSONField(default=dict, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.email} - {self.name}"


class Journalist(TimeStampModel):
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    outlet = models.CharField(max_length=255)
    verified = models.BooleanField(default=False)
    date_verified = models.DateTimeField(blank=True, null=True)
    beats = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    coverage_type = models.CharField(
        choices=comms_consts.COVERAGE_TYPE_CHOICES, max_length=50, default="BOTH"
    )
    accuracy_score = models.IntegerField(default=0)
    number_of_sources = models.IntegerField(default=0)
    status = models.CharField(
        choices=comms_consts.JOURNALIST_CHOICES, max_length=100, default="OTHER"
    )
    needs_review = models.BooleanField(default=False)
    review_details = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["last_name"]

    def __str__(self):
        return f"{self.email} - {self.outlet}"

    @property
    def as_object(self):
        return {
            "outlet": self.outlet,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
        }

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def verify_email(cls, email):
        url = comms_consts.HUNTER_VERIFY_URI
        params = {"api_key": comms_consts.HUNTER_API_KEY, "email": email}
        encoded_params = urlencode(params)
        url = url + "?" + encoded_params
        with Variable_Client() as client:
            r = client.get(
                url,
            )
            if r.status_code == 200:
                r = r.json()
                score = r["data"]["score"]
                if score is None:
                    score = 0
            else:
                return 0
        return score

    @classmethod
    def email_finder(cls, first_name, last_name, domain=False, outlet=False):
        url = comms_consts.HUNTER_FINDER_URI
        params = {
            "api_key": comms_consts.HUNTER_API_KEY,
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
        }
        if domain:
            params["domain"] = domain
        else:
            params["company"] = outlet
        encoded_params = urlencode(params)
        url = url + "?" + encoded_params
        with Variable_Client() as client:
            r = client.get(
                url,
            )
            r = r.json()
            if "errors" in r.keys():
                return {"score": None, "email": None}
            response = r["data"]
        return response


class EmailTracker(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="emails",
        on_delete=models.CASCADE,
    )
    recipient = models.CharField(max_length=255)
    name = models.CharField(max_length=255, default="N/A")
    subject = models.CharField(max_length=255)
    body = models.TextField()
    cc_recipients = models.TextField(blank=True, null=True)
    bcc_recipients = models.TextField(blank=True, null=True)
    message_id = models.CharField(max_length=255, blank=True, null=True)
    opens = models.IntegerField(default=0)
    replies = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    received = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    activity_log = ArrayField(models.CharField(max_length=255), default=list)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.recipient}: {self.subject}"

    @property
    def is_draft(self):
        if self.activity_log:
            idx = len(self.activity_log) - 1
            first = self.activity_log[idx]
            event, time = first.split("|")
            if event == "draft_created":
                return True
        return False

    def add_activity(self, type):
        timezone = pytz.timezone(self.user.timezone)
        date = datetime.now(pytz.utc)
        date_str = date.astimezone(timezone).isoformat()
        new_item = f"{type}|{date_str}"
        self.activity_log.append(new_item)
        return self.save()

    @classmethod
    def get_user_rates(cls, user_id):
        data = {}
        trackers = cls.objects.filter(user__id=user_id)
        if len(trackers):
            delivered = trackers.filter(received=True)
            failed = trackers.filter(failed=True)
            replies = trackers.filter(replies__gt=0)
            opens = trackers.filter(opens__gt=0)
            delivery_rate = round((len(delivered) / len(trackers)) * 100, 2)
            fail_rate = round((len(failed) / len(trackers)) * 100, 2)
            reply_rate = round((len(replies) / len(trackers)) * 100, 2)
            open_rate = round((len(opens) / len(trackers)) * 100, 2)
            data = {
                "delivery_rate": delivery_rate,
                "fail_rate": fail_rate,
                "reply_rate": reply_rate,
                "open_rate": open_rate,
            }
        return data

    @classmethod
    def _create_email_tracker_data(cls, email):
        from managr.core.models import User
        import random
        import uuid

        user = User.objects.get(email=email)
        open_list = [1, 2, 3]
        booleans = [True, False]
        count = 0
        body = "Test"
        date = str(datetime.now())
        emails = list(Article.objects.filter(author__contains="@").values_list("author", flat=True))
        subject = "Test"
        while count <= 10:
            activity_log = [f"delivered|{date}"]
            data = {}

            received = random.choice(booleans)
            failed = False if received else True
            if received:
                open = random.choice(open_list)
                data["opens"] = open
                data["received"] = received
                data["failed"] = failed
                replied = random.choice(booleans)
                data["replies"] = replied
                activity_log.append(f"open|{date}")
                if replied:
                    activity_log.append(f"replied|{date}")
            else:
                activity_log.append(f"failed|{date}")
            author = random.choice(emails)
            data["recipient"] = author
            data["user"] = user
            data["subject"] = subject
            data["body"] = body
            data["activity_log"] = activity_log
            data["message_id"] = str(uuid.uuid4())
            EmailTracker.objects.create(**data)
            count += 1
        return


class JournalistContactQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user.id)


class JournalistContact(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="j_contacts",
        on_delete=models.CASCADE,
    )
    journalist = models.ForeignKey(
        "comms.Journalist",
        on_delete=models.CASCADE,
    )
    tags = ArrayField(models.CharField(max_length=255), default=list)
    bio = models.TextField(blank=True, null=True)
    email = models.CharField(blank=True, null=True, max_length=255)
    outlet = models.CharField(blank=True, null=True, max_length=255)
    images = ArrayField(models.TextField(), default=list)
    notes = ArrayField(JSONField(), default=list, blank=True, null=True)

    class Meta:
        unique_together = ("user", "journalist")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"{self.user} - {self.journalist}"

    objects = JournalistContactQuerySet.as_manager()

    @classmethod
    def get_tags_by_user(cls, user):
        tags_query = cls.objects.filter(user=user)
        tag_list = []
        for contact in tags_query:
            tag_list.extend(contact.tags)
        tag_counts = Counter(tag_list)
        tags_with_count = [{"name": tag, "count": count} for tag, count in tag_counts.items()]

        return tags_with_count

    @classmethod
    def modify_tags(cls, id, tag, modifier):
        contact = cls.objects.get(id=id)
        if modifier == "add":
            tags = contact.tags
            tags.append(tag)
            contact.tags = list(set(tags))
        else:
            contact.tags.remove(tag)
        return contact.save()

    def generate_bio(self):
        from managr.comms.utils import google_search, generate_config

        query = f"Journalist AND {self.journalist.full_name} AND {self.journalist.outlet}"
        google_results = google_search(query)
        if len(google_results) == 0:
            return False
        results = google_results["results"]
        images = google_results["images"]
        art = ExternalArticle(results[0]["link"], config=generate_config())
        try:
            art.download()
            art.parse()
            text = art.text
        except ArticleException:
            text = ""
        except Exception:
            text = ""
        has_error = False
        attempts = 1
        token_amount = 2000
        timeout = 60.0
        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_DISCOVERY_RESULTS_PROMPT(
                    self.journalist.full_name, results, self.journalist.outlet, text
                )
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    self.user.email,
                    prompt,
                    "You are a VP of Communications",
                    token_amount=token_amount,
                    top_p=0.1,
                    response_format={"type": "json_object"},
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                res = open_ai_exceptions._handle_response(r)
                message = res.get("choices")[0].get("message").get("content")
                message = json.loads(message)
                bio = message.get("bio")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 3000:
                    has_error = True
                    message = "Token amount error"
                    break
                else:
                    token_amount += 500
                    continue
            except httpx.ReadTimeout as e:
                timeout += 30.0
                if timeout >= 120.0:
                    has_error = True
                    message = "Read timeout issue"
                    logger.exception(f"Read timeout from Open AI {e}")
                    break
                else:
                    attempts += 1
                    continue
            except Exception as e:
                has_error = True
                message = f"Unknown exception: {e}"
                logger.exception(e)
                break
        if has_error:
            return False
        self.bio = bio
        self.images = images
        self.save()
        return True


class CompanyDetails(models.Model):
    details = models.TextField()
    title = models.TextField()
    user = models.ForeignKey(
        "core.User",
        related_name="company_details",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Company Detail"
        verbose_name_plural = "Company Details"

    @property
    def as_slack_option(self):
        return block_builders.option(self.title[:74], str(self.id))


class Thread(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="threads",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    title = models.TextField()
    meta_data = JSONField(default=dict)

    @property
    def current_index(self):
        message_idxs = list(self.messages.all().values_list("index", flat=True))
        if message_idxs:
            return max(message_idxs)
        else:
            return None

    def add_message(self, message_text, role="SYSTEM"):
        curr_idx = self.current_index()
        if curr_idx:
            data = dict(body=message_text, index=(curr_idx + 1), role=role, thread=self)
            try:
                message = ThreadMessage.objects.create(**data)
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": True, "data": message.as_dict()}

    def generate_url(self):
        date = str(datetime.now())
        data = {"created_at": date, "id": str(self.id)}
        encrypted_data = encrypt_dict(data)
        base_url = get_site_url()
        return f"{base_url}/summaries/{encrypted_data}"


class ThreadMessage(TimeStampModel):
    body = models.TextField(blank=True, null=True)
    thread = models.ForeignKey(
        "Thread",
        related_name="messages",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    role = models.CharField(choices=comms_consts.MESSAGE_TYPES, max_length=50, default="SYSTEM")
    index = models.PositiveIntegerField(default=0)
    meta_data = JSONField(default=dict)

    class Meta:
        ordering = ["index"]
        constraints = [UniqueConstraint(fields=["thread", "index"], name="unique_message")]

    def as_dict(self):
        return dict(body=self.body, thread=str(self.thread.id), role=self.role, index=self.index)
