import base64
import hashlib
import json
import logging
import os
from datetime import datetime
from urllib.parse import urlencode

from django.contrib.postgres.fields import ArrayField
from django.db import models
from oauthlib.oauth2 import OAuth2Error
from requests_oauthlib import OAuth1Session, OAuth2Session

from managr.comms import constants as comms_consts
from managr.comms.exceptions import TwitterApiException
from managr.core import constants as core_consts
from managr.core import exceptions as open_ai_exceptions
from managr.core.models import TimeStampModel
from managr.utils.client import Variable_Client

logger = logging.getLogger("managr")


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

    def get_tweets(self, query, date_from, date_to, next_token=False):
        url = comms_consts.TWITTER_BASE_URI + comms_consts.TWITTER_RECENT_TWEETS_URI
        params = {
            "query": query,
            "max_results": 100,
            "expansions": "author_id,attachments.media_keys",
            "user.fields": "username,name,profile_image_url,public_metrics,verified,location,url",
            "tweet.fields": "created_at",
            "media.fields": "url,variants",
            "sort_order": "relevancy",
            "start_time": date_from,
            "end_time": date_to,
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
        model="gpt-4o",
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
            model=model,
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
