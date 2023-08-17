import json
import os
import logging
from datetime import datetime
from django.db import models
from managr.core.models import TimeStampModel
from managr.core import constants as core_consts
from . import constants as comms_consts
from .exceptions import _handle_response as _handle_news_response, TwitterApiException
from managr.utils.client import Variable_Client
from managr.utils.sites import get_site_url
from managr.core import exceptions as open_ai_exceptions
from managr.utils.misc import encrypt_dict
from urllib.parse import urlencode
import base64
import hashlib

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

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.email} - {self.name}"

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
    def get_clips(cls, search_boolean):
        news_url = (
            comms_consts.NEW_API_URI
            + "/"
            + comms_consts.NEW_API_EVERYTHING_URI(urlencode({"q": search_boolean}))
        )
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

    def get_tweets(self, query):
        url = comms_consts.TWITTER_BASE_URI + comms_consts.TWITTER_RECENT_TWEETS_URI
        params = {
            "query": query,
            "max_results": 10,
            "expansions": "author_id,attachments.media_keys",
            "user.fields": "username, name,profile_image_url, public_metrics, verified, location",
            "tweet.fields": "created_at",
            "media.fields": "url",
            "sort_order": "relevancy",
        }
        headers = comms_consts.TWITTER_API_HEADERS
        with Variable_Client() as client:
            response = client.get(url, headers=headers, params=params)
            res = self._handle_response(response)
        return res

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
        return auth_url, CODE_VERIFIER

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
