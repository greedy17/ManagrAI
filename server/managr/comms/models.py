import json
import os
import logging
import base64
import hashlib
from datetime import datetime, timedelta
from django.db import models
from managr.core.models import TimeStampModel
from django.db.models.constraints import UniqueConstraint
from managr.core import constants as core_consts
from . import constants as comms_consts
from .exceptions import _handle_response as _handle_news_response, TwitterApiException
from managr.utils.client import Variable_Client
from managr.utils.sites import get_site_url
from managr.core import exceptions as open_ai_exceptions
from dateutil import parser
from managr.utils.misc import encrypt_dict
from urllib.parse import urlencode
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex

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
        cls, user, tokens, timeout, clips, input_text, instructions=False, for_client=False
    ):
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        prompt = comms_consts.OPEN_AI_NEWS_CLIPS_SUMMARY(
            datetime.now().date(), clips, input_text, instructions, for_client
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
    def get_clips(cls, search_boolean, date_to=False, date_from=False):
        query = {"q": search_boolean, "excludeDomains": ",".join(comms_consts.EXCLUDE_DOMAINS)}
        if date_to:
            query["to"] = date_to
            query["from"] = date_from
        endpoint = comms_consts.NEW_API_EVERYTHING_QUERY_URI(urlencode(query))
        news_url = comms_consts.NEW_API_URI + "/" + endpoint
        with Variable_Client() as client:
            new_res = client.get(news_url, headers=comms_consts.NEWS_API_HEADERS)
        return _handle_news_response(new_res)

    def generate_shareable_link(self):
        date = str(datetime.now())
        data = {"created_at": date, "id": str(self.id)}
        encrypted_data = encrypt_dict(data)
        base_url = get_site_url()
        return f"{base_url}/shared/{encrypted_data}"


class TwitterAuthAccountAdapter:
    def __init__(self, **kwargs):
        self.access_token = kwargs.get("access_token", None)

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
        self, user, tokens, timeout, tweets, input_text, instructions=False, for_client=False
    ):
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        prompt = comms_consts.OPEN_AI_TWITTER_SUMMARY(
            datetime.now().date(), tweets, input_text, instructions, for_client
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


TwitterAuthAccount = TwitterAuthAccountAdapter(
    **{
        "access_token": comms_consts.TWITTER_ACCESS_TOKEN,
    }
)


class Pitch(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="pitches",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    instructions = models.TextField()
    type = models.CharField(max_length=255, null=True, blank=True)
    audience = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    generated_pitch = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.email} - {self.name}"

    @classmethod
    def generate_pitch(cls, user, type, instructions, audience, chars, style, tokens, timeout):
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        # style = user.writing_style if user.writing_style else False
        prompt = comms_consts.OPEN_AI_PITCH(
            datetime.now().date(), type, instructions, audience, chars, style
        )
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email,
            prompt,
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


class NewsSource(TimeStampModel):
    domain = models.CharField(max_length=255, unique=True)
    site_name = models.CharField(max_length=255, blank=True, null=True)
    rss_feed_url = models.URLField(blank=True, null=True)
    last_scraped = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    access_count = JSONField(default=dict, null=True, blank=True)
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
    scrape_data = JSONField(default=dict, null=True, blank=True)
    error_log = ArrayField(models.CharField(max_length=255), default=list, blank=True)

    def __str__(self):
        return self.domain

    def article_selectors(self):
        return {
            "author": self.author_selector,
            "publish_date": self.date_published_selector,
            "title": self.article_title_selector,
            "content": self.article_content_selector,
        }

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
                        selector = f"@class='{value}'"
                    else:
                        selector = f"contains(@class, '{value}')"
                    if idx != len(values) - 1:
                        selector += "or"
            else:
                if "=" in selector_split[1]:
                    value = selector_split[1].replace("=", "")
                    selector = f"@class='{value}'"
                else:
                    selector = f"contains(@class, '{selector_split[1]}')"
        return selector

    def create_search_regex(self):
        current_year = str(datetime.now().year)
        if self.article_link_regex:
            if self.article_link_selector == "year" and current_year in self.article_link_regex:
                return self.article_link_regex
            return self.article_link_regex
        # add the link selector
        attribute_list = self.article_link_attribute.split(",")
        regex = "//body//" + attribute_list[0] + "["
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
            access_count=self.access_count,
            article_link_selector=self.article_link_selector,
            article_link_attribute=self.article_link_attribute,
            article_link_regex=self.article_link_regex,
            data_attribute_key=self.data_attribute_key,
            data_attribute_value=self.data_attribute_value,
            date_published_selector=self.date_published_selector,
            author_selector=self.author_selector,
            article_content_selector=self.article_content_selector,
            is_active=self.is_active,
        )

    @property
    def crawling(self):
        article_check = Article.objects.filter(source=self)
        if len(article_check):
            return True
        return False

    @classmethod
    def domain_list(cls, scrape_ready=False, new=False):
        active_sources = cls.objects.filter(is_active=True).order_by("last_scraped")
        print(len(active_sources))
        # filters sources that have been filled out but haven't been run yet to create the regex and scrape for the first time
        if scrape_ready and new:
            active_sources = active_sources.filter(
                article_link_selector__isnull=False, article_link_regex__isnull=True
            )
        # filters sources that are already scrapping
        elif scrape_ready and not new:
            active_sources = active_sources.filter(article_link_regex__isnull=False)
        # filters sources that were just added and don't have scrape data yet
        elif not scrape_ready and new:
            active_sources = active_sources.filter(article_link_attribute__isnull=True)
        print(len(active_sources))
        source_list = [source.domain for source in active_sources]
        return source_list


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
        ]
        constraints = [UniqueConstraint(fields=["source", "title"], name="unique_article")]

    def update_search_vector(self):
        self.content_search_vector = SearchVector("content")
        return self.save()

    def fields_to_dict(self):
        site_name = (
            self.source.site_name if hasattr(self.source, "site_name") else self.source.domain
        )
        return dict(
            title=self.title,
            description=self.description,
            author=self.author,
            publish_date=str(self.publish_date),
            link=self.link,
            image_url=self.image_url,
            source={"name": site_name},
        )

    @classmethod
    def search_by_query(cls, boolean_string, date_to=False, date_from=False):
        from managr.comms.utils import boolean_search_to_query

        converted_boolean = boolean_search_to_query(boolean_string)
        articles = Article.objects.filter(converted_boolean)
        if date_to:
            date_to_date_obj = parser.parse(date_to)
            day_incremented = date_to_date_obj + timedelta(days=1)
            day_incremented_str = str(day_incremented)
            articles = articles.filter(publish_date__range=(date_from, day_incremented_str))
        if len(articles):
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


class EmailAlert(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="news_alert",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    run_at = models.DateTimeField()
    search = models.ForeignKey(
        "Search",
        related_name="alerts",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    meta_data = JSONField(
        default=dict,
        null=True,
        blank=True,
    )


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
    user = models.ForeignKey(
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

    @staticmethod
    def get_authorization():
        query = urlencode(comms_consts.TWITTER_AUTHORIZATION_QUERY_PARAMS)
        return f"{comms_consts.AUTHORIZATION_URI}?{query}"

    @staticmethod
    def authenticate(code, identifier):
        data = comms_consts.TWITTER_AUTHENTICATION_PARAMS(code, identifier)
        with Variable_Client() as client:
            res = client.post(
                f"{comms_consts.AUTHENTICATION_URI}",
                data=data,
                headers=comms_consts.AUTHENTICATION_HEADERS,
            )
            return TwitterAccount._handle_response(res)
