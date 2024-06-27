import json
import httpx
import time
import logging
import pytz
import uuid
from rest_framework import (
    mixins,
    viewsets,
)
from django.http import JsonResponse
from asgiref.sync import async_to_sync, sync_to_async
from pytz import timezone
from datetime import datetime, timedelta
from newspaper import Article, ArticleException
from managr.api.models import ExpiringTokenAuthentication
from rest_framework.response import Response
from rest_framework import (
    permissions,
    mixins,
    status,
    viewsets,
)
from urllib.parse import urlencode
from dateutil import parser
from django.shortcuts import redirect
from rest_framework.decorators import action
from . import constants as comms_consts
from .models import (
    Search,
    TwitterAccount,
    Pitch,
    Process,
    InstagramAccount,
    Discovery,
    Journalist,
    EmailTracker,
)
from .models import Article as InternalArticle
from .models import WritingStyle, EmailAlert, JournalistContact
from managr.core.models import User
from managr.comms import exceptions as comms_exceptions
from .tasks import (
    emit_process_website_domain,
    emit_send_news_summary,
    emit_send_social_summary,
    emit_share_client_summary,
    _add_jounralist_to_db,
)
from .serializers import (
    SearchSerializer,
    PitchSerializer,
    EmailAlertSerializer,
    ProcessSerializer,
    TwitterAccountSerializer,
    InstagramAccountSerializer,
    WritingStyleSerializer,
    DiscoverySerializer,
    EmailTrackerSerializer,
    JournalistContactSerializer,
)
from managr.core import constants as core_consts
from managr.utils.client import Variable_Client
from managr.utils.misc import decrypt_dict
from managr.core import exceptions as open_ai_exceptions
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from managr.comms.utils import (
    generate_config,
    normalize_article_data,
    get_domain,
    extract_pdf_text,
    convert_pdf_from_url,
    extract_email_address,
    google_search,
)
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from managr.comms.tasks import emit_get_meta_account_info
from managr.api.emails import send_html_email
from newspaper.article import ArticleException

logger = logging.getLogger("managr")


def getclips(request):
    try:
        user = User.objects.get(id=request.GET.get("user_id"))
        has_error = False
        search = request.GET.get("search", False)
        boolean = request.GET.get("boolean", False)
        date_to = request.GET.get("date_to", False)
        date_from = request.GET.get("date_from", False)
        if "journalist:" in search:
            internal_articles = InternalArticle.search_by_query(search, date_to, date_from, True)
            articles = normalize_article_data([], internal_articles)
            return {"articles": articles, "string": search}
        if not boolean:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_QUERY_STRING(search)
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email,
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
            logger.info(1)
            query_input = r.get("choices")[0].get("message").get("content")
            news_res = Search.get_clips(query_input, date_to, date_from)
            articles = news_res["articles"]
        else:
            news_res = Search.get_clips(boolean, date_to, date_from)
            logger.info(1)
            articles = news_res["articles"]
            query_input = boolean
        logger.info(2)
        articles = [article for article in articles if article["title"] != "[Removed]"]
        logger.info(3)
        internal_articles = InternalArticle.search_by_query(query_input, date_to, date_from)
        logger.info(4)
        articles = normalize_article_data(articles, internal_articles)
        logger.info(5)
        return {"articles": articles, "string": query_input}

    except Exception as e:
        has_error = True
        logger.exception(e)
        return {"error": str(e)}


@require_http_methods(["GET"])
@permission_classes([permissions.IsAuthenticated])
@async_to_sync
async def get_clips(request, *args, **kwargs):
    response = await sync_to_async(getclips)(request)
    return JsonResponse(data=response)


def add_timezone_and_convert_to_utc(datetime_str, user_timezone):
    user_timezone_obj = timezone(user_timezone)
    localized_datetime = user_timezone_obj.localize(
        datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f")
    )
    utc_time = pytz.utc
    converted_datetime = localized_datetime.astimezone(utc_time)
    return converted_datetime


class PRSearchViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = SearchSerializer

    def get_queryset(self):
        return Search.objects.filter(user__organization=self.request.user.organization)

    def get_all_searches(self):
        return Search.objects.filter(organization=self.request.user.organization)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        data["user"] = str(user.id)
        try:
            serializer = SearchSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_data = serializer.data
            # serializer.instance.update_boolean()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_201_CREATED, data=response_data)

    def update(self, request, *args, **kwargs):
        search = Search.objects.get(id=request.data.get("id"))
        all_keys = [key for key, value in request.data.items()]
        keys = [key for key in all_keys]
        try:
            for field in keys:
                setattr(search, field, request.data[field])
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        search.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(
    #     methods=["get"],
    #     permission_classes=[permissions.IsAuthenticated],
    #     detail=False,
    #     url_path="clips",
    # )
    # async def get_clips(self, request, *args, **kwargs):
    #     return await getclips(request)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="summary",
    )
    def get_summary(self, request, *args, **kwargs):
        user = request.user
        if user.has_hit_summary_limit:
            return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        clips = request.data.get("clips")
        search = request.data.get("search")
        instructions = request.data.get("instructions", False)
        company = request.data.get("company")
        if "journalist:" in search:
            instructions = comms_consts.JOURNALIST_INSTRUCTIONS(company)
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0
        while True:
            try:
                res = Search.get_summary(
                    request.user, token_amount, timeout, clips, search, instructions, True
                )
                message = res.get("choices")[0].get("message").get("content").replace("**", "*")
                user.add_meta_data("news_summaries")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"summary": message})

        return Response(data={"summary": message})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="article-summary",
    )
    def get_article_summary(self, request, *args, **kwargs):
        user = request.user
        if user.has_hit_summary_limit:
            return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        url = request.data["params"]["url"]
        search = request.data["params"]["search"]
        instructions = request.data["params"]["instructions"]
        length = request.data["params"]["length"]
        has_error = False
        attempts = 1
        token_amount = 2000
        timeout = 60.0
        while True:
            try:
                article_res = Article(url, config=generate_config())
                article_res.download()
                article_res.parse()
                text = article_res.text.replace("\n", "")
                open_ai_url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_ARTICLE_SUMMARY(
                    datetime.now().date(), text, search, length, instructions, True
                )
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    "You are a VP of Communications",
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        open_ai_url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                r = open_ai_exceptions._handle_response(r)
                message = r.get("choices")[0].get("message").get("content").replace("**", "*")
                user.add_meta_data("article_summaries")
                task = emit_process_website_domain(url, user.organization.name)
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2500:
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
            except ArticleException:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "We could not access that url"},
                )
            except Exception as e:
                has_error = True
                message = f"Unknown exception: {e}"
                logger.exception(e)
                break
        if has_error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"summary": message})

        return Response(data={"summary": message})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="regenerate-article-summary",
    )
    def regenerate_article_summary(self, request, *args, **kwargs):
        user = request.user
        if user.has_hit_summary_limit:
            return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        url = request.data["params"]["url"]
        original_summary = request.data["params"]["summary"]
        instructions = request.data["params"]["instructions"]
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0
        while True:
            try:
                article_res = Article(url, config=generate_config())
                article_res.download()
                article_res.parse()
                text = article_res.text
                open_ai_url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_REGENERATE_ARTICLE(
                    text,
                    original_summary,
                    instructions,
                )
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    "You are a VP of Communications",
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        open_ai_url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                r = open_ai_exceptions._handle_response(r)
                message = r.get("choices")[0].get("message").get("content").replace("**", "*")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
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
            except ArticleException:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "We could not access that url"},
                )
            except Exception as e:
                has_error = True
                message = f"Unknown exception: {e}"
                logger.exception(e)
                break
        if has_error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"summary": message})

        return Response(data={"summary": message})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="generate-content",
    )
    def generate_content(self, request, *args, **kwargs):
        user = request.user
        if user.has_hit_summary_limit:
            return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        url = request.data["params"]["url"]
        instructions = request.data["params"]["instructions"]
        style = request.data["params"]["style"]
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0
        while True:
            try:
                article_res = Article(url, config=generate_config())
                article_res.download()
                article_res.parse()
                article = article_res.text

                open_ai_url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_GENERATE_CONTENT(
                    datetime.now().date(), article, "", instructions
                )
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    "You are a VP of Communications",
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        open_ai_url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                r = open_ai_exceptions._handle_response(r)
                message = r.get("choices")[0].get("message").get("content").replace("**", "*")

                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
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
            except ArticleException:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "We could not access that url"},
                )
            except Exception as e:
                has_error = True
                message = f"Unknown exception: {e}"
                logger.exception(e)
                break
        if has_error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"summary": message})

        return Response(data={"content": message})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="web-summary",
    )
    def get_web_summary(self, request, *args, **kwargs):
        user = request.user
        if user.has_hit_summary_limit:
            return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        news_url = request.data["params"]["url"]
        instructions = request.data["params"]["instructions"]
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0
        while True:
            try:
                article_res = Article(news_url, config=generate_config())
                article_res.download()
                article_res.parse()
                text = article_res.text
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_WEB_SUMMARY(
                    datetime.now().date(),
                    text,
                    instructions,
                )
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    "You are a VP of Communications",
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                r = open_ai_exceptions._handle_response(r)
                message = r.get("choices")[0].get("message").get("content").replace("**", "*")
                user.add_meta_data("article_summaries")
                task = emit_process_website_domain(url, user.organization.name)
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
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
            except ArticleException:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "We could not access that url"},
                )
            except Exception as e:
                has_error = True
                message = f"Unknown exception: {e}"
                logger.exception(e)
                break
        if has_error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"summary": message})
        return Response(data={"summary": message})

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="tweets",
    )
    def get_tweets(self, request, *args, **kwargs):
        user = User.objects.get(id=request.GET.get("user_id"))
        twitter_account = user.twitter_account
        has_error = False
        search = request.GET.get("search")
        query_input = None
        next_token = False
        tweet_list = []
        attempts = 1
        while True:
            try:
                if attempts >= 10:
                    break
                if query_input is None:
                    url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                    prompt = comms_consts.OPEN_AI_TWITTER_SEARCH_CONVERSION(search)
                    body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                        user.email,
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
                    query_input = query_input.replace("AND", " ")
                    query_input = query_input + " lang:en -is:retweet"
                    if "from:" not in query_input:
                        query_input = query_input + " is:verified"
                tweet_res = twitter_account.get_tweets(query_input, next_token)
                tweets = tweet_res.get("data", None)
                includes = tweet_res.get("includes", None)
                attempts += 1
                if tweets:
                    if "next_token" in tweet_res["meta"].keys():
                        next_token = tweet_res["meta"]["next_token"]
                    user_data = tweet_res["includes"].get("users")
                    for tweet in tweets:
                        if len(tweet_list) > 39:
                            break
                        for user in user_data:
                            if user["id"] == tweet["author_id"]:
                                if user["public_metrics"]["followers_count"] > 1000:
                                    tweet["user"] = user
                                    tweet_list.append(tweet)
                                break

                else:
                    if len(tweet_list):
                        break
                    return Response(
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        data={"error": f"No results for {query_input}", "string": query_input},
                    )
                if len(tweet_list) < 40 and tweets:
                    continue
                break
            except KeyError as e:
                logger.exception(e)
                return Response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    data={"error": f"No results for {query_input}", "string": query_input},
                )
            except comms_exceptions.TooManyRequestsError:
                if len(tweet_list):
                    break
                else:
                    return Response(
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        data={
                            "error": f"We've hit an issue contacting Twitter for {query_input}",
                            "string": query_input,
                        },
                    )
            except Exception as e:
                print(1)
                has_error = True
                logger.exception(e)
                tweet_res = e
                break
        if has_error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": tweet_res})
        query_input = query_input.replace("-is:retweet", "").replace("is:verified", "")
        return Response({"tweets": tweet_list, "string": query_input, "includes": includes})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="tweet-summary",
    )
    def get_tweet_summary(self, request, *args, **kwargs):
        user = request.user
        if user.has_hit_summary_limit:
            return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        tweets = request.data.get("tweets")
        search = request.data.get("search")
        instructions = request.data.get("instructions", False)
        twitter_account = user.twitter_account
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0
        while True:
            try:
                res = twitter_account.get_summary(
                    request.user, token_amount, timeout, tweets, search, instructions, True
                )
                message = res.get("choices")[0].get("message").get("content").replace("**", "*")
                user.add_meta_data("tweet_summaries")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"summary": message})

        return Response(data={"summary": message})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="suggestions",
    )
    def get_suggestions(self, request, *args, **kwargs):
        user = request.user
        name = user.first_name
        company = user.organization
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0
        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_SEARCH_SUGGESTIONS(name, company)
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    "You are a VP of Communications",
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                res = open_ai_exceptions._handle_response(r)
                message = res.get("choices")[0].get("message").get("content").replace("**", "*")
                user.add_meta_data("news_summaries")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
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
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"suggestions": message}
            )

        return Response(data={"suggestions": message})

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="generate-link",
    )
    def generate_link(self, request, *args, **kwargs):
        search = Search.objects.get(id=request.GET.get("id"))
        link = search.generate_shareable_link()
        return Response(data={"link": link})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="email-summary",
    )
    def share_email_summary(self, request, *args, **kwargs):
        summary = request.data.get("summary", "N/A")
        clips = request.data.get("clips", [])
        logger.info(request.user.email)
        logger.info(summary)
        logger.info(clips)
        emit_share_client_summary(summary, clips, request.user.email)
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="recipients",
    )
    def edit_recipients(self, request, *args, **kwargs):
        recipient = request.data.get("recipient")
        search_id = request.data.get("search_id")
        action = request.data.get("action")
        search = Search.objects.get(id=search_id)
        if action == "ADD":
            search.add_recipient(recipient)
        else:
            search.remove_recipient(recipient)
        return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes(
    [
        permissions.AllowAny,
    ]
)
def get_shared_summary(request, encrypted_param):
    decrypted_dict = decrypt_dict(encrypted_param)
    created_at = datetime.strptime(decrypted_dict.get("created_at"), "%Y-%m-%d %H:%M:%S.%f")
    time_difference = datetime.now() - created_at
    twenty_four_hours = timedelta(hours=24)
    if time_difference > twenty_four_hours:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    search = Search.objects.get(id=decrypt_dict["id"])
    return Response(data={"summary": search.summary})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def upload_link(request):
    url = request.data["params"]["url"]
    try:
        article_res = Article(url, config=generate_config())
        article_res.download()
        article_res.parse()

        title = article_res.title
        author = article_res.authors
        image = article_res.top_image
        date = article_res.publish_date
        text = article_res.meta_description
        domain = get_domain(url)
        article = {}
        article = {
            "title": title,
            "source": domain,
            "author": author,
            "image_url": image,
            "publish_date": date,
            "description": text,
            "link": url,
        }
        emit_process_website_domain(url, request.user.organization.name)
    except Exception as e:
        logger.exception(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(data=article)


class PitchViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = PitchSerializer

    def get_queryset(self):
        return Pitch.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            readSerializer = self.serializer_class(instance=serializer.instance)
        except Exception as e:
            logger.exception(f"Error validating data for pitch <{e}>")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_201_CREATED, data=readSerializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.request.data
        serializer = self.serializer_class(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="generate",
    )
    def generate_pitch(self, request, *args, **kwargs):
        user = request.user
        if user.has_hit_summary_limit:
            return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        type = request.data.get("type")
        instructions = request.data.get("instructions")
        style = request.data.get("style")
        pitch_id = request.data.get("pitch_id", False)
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0

        while True:
            try:
                res = Pitch.generate_pitch(user, type, instructions, style, token_amount, timeout)
                pitch = res.get("choices")[0].get("message").get("content")
                if pitch_id:
                    saved_pitch = Pitch.objects.get(id=pitch_id)
                    saved_pitch.generate_pitch = pitch
                    saved_pitch.save()
                user.add_meta_data("pitches")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
                    has_error = True

                    message = "Token amount error"
                    break
                else:
                    token_amount += 500
                    continue
            except httpx.ReadTimeout as e:
                print(e)
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})
        return Response({"pitch": pitch})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="regenerate",
    )
    def get_regenerated_pitch(self, request, *args, **kwargs):
        user = request.user
        instructions = request.data.get("instructions")
        pitch = request.data.get("pitch")
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0

        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_PTICH_DRAFT_WITH_INSTRUCTIONS(pitch, instructions)
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                r = open_ai_exceptions._handle_response(r)
                pitch = r.get("choices")[0].get("message").get("content")
                user.add_meta_data("pitches")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
                    has_error = True

                    message = "Token amount error"
                    break
                else:
                    token_amount += 500
                    continue
            except httpx.ReadTimeout as e:
                print(e)
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})
        return Response({"pitch": pitch})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="learn",
    )
    def learn_writing_style(self, request, *args, **kwargs):
        user = request.user
        example = request.data["params"]["example"]
        title = request.data["params"]["title"]
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0

        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_LEARN_WRITING_STYLE_PROMPT(example)
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                r = open_ai_exceptions._handle_response(r)
                style = r.get("choices")[0].get("message").get("content")
                writing_dict = {"title": title, "style": style, "user": request.user}
                WritingStyle.objects.create(**writing_dict)
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
                    has_error = True

                    message = "Token amount error"
                    break
                else:
                    token_amount += 500
                    continue
            except httpx.ReadTimeout as e:
                print(e)
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})
        return Response({"style": style})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="delete-style",
    )
    def delete_writing_style(self, request, *args, **kwargs):
        style_id = request.data["params"]["style_id"]
        style = WritingStyle.objects.get(id=style_id)
        style.delete()
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="journalists",
    )
    def find_journalist(self, request, *args, **kwargs):
        user = request.user
        # if user.has_hit_summary_limit:
        #     return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        type = request.data.get("type")
        beat = request.data.get("beat")
        location = request.data.get("location")
        content = request.data.get("content")
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0

        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_FIND_JOURNALISTS(type, beat, location, content)
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                res = open_ai_exceptions._handle_response(r)

                journalists = res.get("choices")[0].get("message").get("content")

                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
                    has_error = True

                    message = "Token amount error"
                    break
                else:
                    token_amount += 500
                    continue
            except httpx.ReadTimeout as e:
                print(e)
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})
        return Response({"journalists": journalists})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="feedback",
    )
    def get_feedback(self, request, *args, **kwargs):
        user = request.user
        type = request.data.get("type")
        audience = request.data.get("audience")
        objective = request.data.get("objective")
        feedback = request.data.get("feedback")
        content = request.data.get("content")
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0

        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_GENERATE_FEEDBACK(
                    type, audience, objective, feedback, content
                )
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                res = open_ai_exceptions._handle_response(r)

                feedback = res.get("choices")[0].get("message").get("content")

                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
                    has_error = True

                    message = "Token amount error"
                    break
                else:
                    token_amount += 500
                    continue
            except httpx.ReadTimeout as e:
                print(e)
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})
        return Response({"feedback": feedback})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="regenerate-feedback",
    )
    def regenerate_with_feedback(self, request, *args, **kwargs):
        user = request.user
        feedback = request.data.get("feedback")
        content = request.data.get("content")
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0

        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.REGENERATE_CONTENT_WITH_FEEDBACK(content, feedback)
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                res = open_ai_exceptions._handle_response(r)

                feedback = res.get("choices")[0].get("message").get("content")

                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
                    has_error = True

                    message = "Token amount error"
                    break
                else:
                    token_amount += 500
                    continue
            except httpx.ReadTimeout as e:
                print(e)
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})
        return Response({"feedback": feedback})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="rewrite",
    )
    def rewrite_pitch(self, request, *args, **kwargs):
        user = request.user
        original = request.data.get("original")
        bio = request.data.get("bio")

        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0

        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_REWRITE_PTICH(original, bio, user.first_name)
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                r = open_ai_exceptions._handle_response(r)
                pitch = r.get("choices")[0].get("message").get("content")
                user.add_meta_data("emailDraft")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
                    has_error = True

                    message = "Token amount error"
                    break
                else:
                    token_amount += 500
                    continue
            except httpx.ReadTimeout as e:
                print(e)
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})
        return Response({"pitch": pitch})


class EmailAlertViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = EmailAlertSerializer

    def get_queryset(self):
        return EmailAlert.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        datetime = request.data.pop("run_at")
        converted_datetime = add_timezone_and_convert_to_utc(datetime, request.user.timezone)
        request.data["run_at"] = converted_datetime
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            readSerializer = self.serializer_class(instance=serializer.instance)
        except Exception as e:
            logger.exception(f"Error validating data for email alert <{e}>")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_201_CREATED, data=readSerializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.request.data
        serializer = self.serializer_class(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="test-alert",
    )
    def test_email_alert(self, request, *args, **kwargs):
        alert_id = request.data.get("alert_id")
        social = request.data.get("social")
        if social:
            print("In Social")
            emit_send_social_summary(alert_id, str(datetime.now()))
        else:
            emit_send_news_summary(alert_id, str(datetime.now()))
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="get-email-alerts",
    )
    def get_email_alerts(self, request, *args, **kwargs):
        alerts = EmailAlert.objects
        serialized = EmailAlertSerializer(alerts, many=True)
        return Response(data=serialized.data, status=status.HTTP_200_OK)


class ProcessViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = ProcessSerializer

    def get_queryset(self):
        return Process.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            readSerializer = self.serializer_class(instance=serializer.instance)
        except Exception as e:
            logger.exception(f"Error validating data for detials <{e}>")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_201_CREATED, data=readSerializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.request.data
        serializer = self.serializer_class(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="run",
    )
    def run_process(self, request, *args, **kwargs):
        user = request.user
        type = request.data.get("type")
        summary = request.data.get("summary")
        details = request.data.get("details")
        process_id = request.data.get("process_id")
        style = request.data.get("style")

        #         style = """
        #         The author's style is formal yet personal, employing a tone of gratitude and excitement. They use first-person narrative, making the text relatable and engaging. The structure is chronological, starting with the present and moving to past achievements, ending with a hopeful look to the future. The author uses sophisticated vocabulary and complex sentence structures, demonstrating a high level of education and professionalism.
        # The author establishes credibility by mentioning specific names, roles, and institutions, and by expressing gratitude towards mentors and colleagues. They avoid promotional language, focusing instead on personal growth and learning opportunities.
        # Guidelines for replicating this style:
        # 1. Use a formal yet personal tone, employing first-person narrative.
        # 2. Structure the text chronologically, linking past, present, and future.
        # 3. Use sophisticated vocabulary and complex sentence structures.
        # 4. Establish credibility by mentioning specific names, roles, and institutions.
        # 5. Express gratitude and excitement about learning and growth opportunities.
        # 6. Avoid promotional language, focusing on informative and trustworthy discourse.
        #         """

        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0

        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.RUN_PROCESS(datetime.now(), type, summary, details, style)
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                res = open_ai_exceptions._handle_response(r)

                content = res.get("choices")[0].get("message").get("content")

                user.add_meta_data("assist")

                if process_id:
                    process = Process.objects.get(id=process_id)
                    process.generated_content = content
                    process.save()
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
                    has_error = True

                    message = "Token amount error"
                    break
                else:
                    token_amount += 500
                    continue
            except httpx.ReadTimeout as e:
                print(e)
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})
        return Response({"content": content})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_twitter_request_token(request):
    res = TwitterAccount.get_token(request)
    return Response(res)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_twitter_auth_link(request):
    link = TwitterAccount.get_authorization(request.token)
    return Response({"link": link})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_twitter_authentication(request):
    user = request.user
    data = request.data
    access_token = TwitterAccount.authenticate(data.get("oauth_token"), data.get("oauth_verifier"))
    data = {
        "user": user.id,
        "access_token": access_token.get("oauth_token"),
        "access_token_secret": access_token.get("oauth_token_secret"),
    }
    existing = TwitterAccount.objects.filter(user=request.user).first()
    if existing:
        serializer = TwitterAccountSerializer(data=data, instance=existing)
    else:
        serializer = TwitterAccountSerializer(data=data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()

    except Exception as e:
        logger.exception(str(e))
        return Response(data={"success": False})
    return Response(data={"success": True})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_instagram_request_token(request):
    res = InstagramAccount.get_token(request)
    return Response(res)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_instagram_authentication(request):
    user = request.user
    data = request.data
    access_token_response = InstagramAccount.authenticate(data.get("code"))
    access_token_response["user"] = user.id
    existing = InstagramAccount.objects.filter(user=request.user).first()
    if existing:
        serializer = InstagramAccountSerializer(data=access_token_response, instance=existing)
    else:
        serializer = InstagramAccountSerializer(data=access_token_response)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        emit_get_meta_account_info(str(user.id))
    except Exception as e:
        logger.exception(str(e))
        return Response(data={"success": False})
    return Response(data={"success": True})


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def revoke_instagram_auth(request):
    user = request.user
    ig_account = InstagramAccount.objects.filter(user=user)
    try:
        ig_account.delete()
    except Exception as e:
        return Response({"error": str(e)})
    return Response(data={"success": True})


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def revoke_twitter_auth(request):
    user = request.user
    twitter_account = TwitterAccount.objects.filter(user=user)
    try:
        twitter_account.delete()
    except Exception as e:
        return Response({"error": str(e)})
    return Response(data={"success": True})


def redirect_from_twitter(request):
    verifier = request.GET.get("oauth_verifier", False)
    token = request.GET.get("oauth_token", False)
    q = urlencode({"state": "TWITTER", "oauth_verifier": verifier, "code": "code", "token": token})
    if not verifier:
        err = {"error": "there was an error"}
        err = urlencode(err)
        return redirect(f"{comms_consts.TWITTER_FRONTEND_REDIRECT}?{err}")
    return redirect(f"{comms_consts.TWITTER_FRONTEND_REDIRECT}?{q}")


def redirect_from_instagram(request):
    code = request.GET.get("code", False)
    q = urlencode({"state": "INSTAGRAM", "code": code})
    if not code:
        err = {"error": "there was an error"}
        err = urlencode(err)
        return redirect(f"{comms_consts.TWITTER_FRONTEND_REDIRECT}?{err}")
    return redirect(f"{comms_consts.TWITTER_FRONTEND_REDIRECT}?{q}")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def upload_pdf(request):
    user = request.user
    url = request.data.get("url", None)
    pdf_file = request.FILES.get("pdf_file", None)
    instructions = request.data.get("instructions", "Create a summary")
    if pdf_file:
        text, images = extract_pdf_text(pdf_file)
    else:
        text, images = convert_pdf_from_url(url)
    if not len(text):
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            data={"error": "No text could be extract from the uploaded PDF"},
        )
    has_error = False
    attempts = 1
    token_amount = 4000
    timeout = 60.0
    while True:
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_GENERATE_PDF_SUMMARY(
                datetime.now().date(), instructions, text
            )
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email,
                prompt,
                token_amount=token_amount,
                top_p=0.1,
            )
            with Variable_Client(timeout) as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            res = open_ai_exceptions._handle_response(r)

            content = res.get("choices")[0].get("message").get("content")
            # if len(images):
            #     prompt = comms_consts.OPEN_AI_IMAGE_CONTENT(
            #         images, "Generate a summary of the images", token_amount
            #     )
            #     with Variable_Client(timeout) as client:
            #         r = client.post(
            #             url,
            #             data=json.dumps(prompt),
            #             headers=core_consts.OPEN_AI_HEADERS,
            #         )
            #     res = open_ai_exceptions._handle_response(r)
            #     print(res)
            break
        except open_ai_exceptions.StopReasonLength:
            logger.exception(
                f"Retrying again due to token amount, amount currently at: {token_amount}"
            )
            if token_amount <= 8000:
                has_error = True

                message = "Token amount error"
                break
            else:
                token_amount += 1000
                continue
        except httpx.ReadTimeout as e:
            print(e)
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
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})
    return Response({"content": content})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_writing_styles(request):
    # if request.data.get("all_styles", False):
    #     writing_styles = WritingStyle.objects.filter(
    #         user__organization=request.user.organization
    #     )
    # else:
    #     writing_styles = WritingStyle.objects.filter(
    #         user=request.user
    #     )
    #     print('why...')
    writing_styles = WritingStyle.objects.filter(user__organization=request.user.organization)
    serializer = WritingStyleSerializer(writing_styles, many=True)  # Serialize the queryset

    return Response(serializer.data)


class DiscoveryViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = DiscoverySerializer

    def get_queryset(self):
        return Discovery.objects.filter(user__organization=self.request.user.organization)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            readSerializer = self.serializer_class(instance=serializer.instance)
        except Exception as e:
            logger.exception(f"Error validating data for details <{e}>")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_201_CREATED, data=readSerializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.request.data
        serializer = self.serializer_class(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="run",
    )
    def run_discovery(self, request, *args, **kwargs):
        user = request.user
        # if user.has_hit_summary_limit:
        #     return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        type = request.data.get("type")
        beat = request.data.get("beat")
        location = request.data.get("location")
        content = request.data.get("content")
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0
        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.DISCOVER_JOURNALIST(type, beat, location, content)
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    "You are a VP of Communications",
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                res = open_ai_exceptions._handle_response(r)

                message = res.get("choices")[0].get("message").get("content").replace("**", "*")
                user.add_meta_data("discovery")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=message)

        return Response(data=message)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="email",
    )
    def send_email(self, request, *args, **kwargs):
        user = request.user
        subject = request.data.get("subject")
        body = request.data.get("body").replace("[Your Name]", f"\n\n{user.full_name}")
        recipient = request.data.get("recipient")
        name = request.data.get("name")
        bcc = request.data.get("bcc")
        context = {"body": body}
        message_id = f"{uuid.uuid4()}-{user.email}"
        try:
            send_html_email(
                subject,
                "core/email-templates/user-email.html",
                f"{user.full_name} <{user.email}>",
                [recipient],
                context=context,
                bcc_emails=bcc,
                headers={
                    "Reply-To": f"{user.full_name} <{user.first_name}.{user.last_name}@mg.managr.ai>",
                    "X-Managr-Id": message_id,
                    "Message-ID": message_id,
                },
                user=user,
            )
            user.add_meta_data("emailSent")
            serializer = EmailTrackerSerializer(
                data={
                    "user": user.id,
                    "recipient": recipient,
                    "body": body,
                    "subject": subject,
                    "message_id": message_id,
                    "name": name,
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer.instance.add_activity("sent")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.exception(str(e))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="verify",
    )
    def verify_email(self, request, *args, **kwargs):
        user = request.user
        journalist = request.data.get("journalist")
        outlet = request.data.get("publication")
        email = request.data.get("email")
        name_list = journalist.strip().split(" ")
        db_check = []
        if len(journalist) > 2:
            first = name_list[0]
            last = name_list[len(name_list) - 1]
        else:
            first = name_list[0]
            last = name_list[1]
        try:
            email_check = Journalist.objects.filter(email=email)
            if len(email_check):
                db_check = email_check
            else:
                name_check = Journalist.objects.filter(
                    first_name=first, last_name=last, outlet=outlet
                )
                if len(name_check):
                    db_check = name_check
            if len(db_check):
                internal_journalist = db_check.first()
                return Response(
                    status=status.HTTP_200_OK,
                    data={
                        "is_valid": internal_journalist.verified,
                        "email": internal_journalist.email,
                    },
                )
            else:
                score = Journalist.verify_email(email)
                is_valid = True if score >= 85 else False
                if is_valid is False:
                    r = Journalist.email_finder(first, last, outlet=outlet)
                    score = r["score"]
                    if score is None:
                        score = 0
                    is_valid = True if score >= 85 else False
                    if r["email"] is not None:
                        email = r["email"]
                        request.data["email"] = email
                        request.data["publication"] = r["company"]
                request.data["accuracy_score"] = score
                user.add_meta_data("verify")
                _add_jounralist_to_db(request.data, is_valid)
                return Response(
                    status=status.HTTP_200_OK, data={"is_valid": is_valid, "email": email}
                )
        except Exception as e:
            logger.exception(str(e))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="web-context",
    )
    def journalist_web_context(self, request, *args, **kwargs):
        user = request.user
        journalist = request.data.get("journalist")
        outlet = request.data.get("outlet")
        content = request.data.get("content")
        company = request.data.get("company")
        search = request.data.get("search")
        query = f"{journalist} AND {outlet}"
        google_results = google_search(query)
        if len(google_results) == 0:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={"error": "No results could be found."},
            )
        results = google_results["results"]
        images = google_results["images"]
        art = Article(results[0]["link"], config=generate_config())
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
        token_amount = 1000
        timeout = 60.0
        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                if search:
                    prompt = comms_consts.OPEN_AI_RESULTS_PROMPT(journalist, results, company, text)
                else:
                    prompt = comms_consts.OPEN_AI_DISCOVERY_RESULTS_PROMPT(
                        journalist, results, content, text
                    )
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    "You are a VP of Communications",
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                res = open_ai_exceptions._handle_response(r)

                message = res.get("choices")[0].get("message").get("content").replace("**", "*")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=message)

        return Response(data={"summary": message, "images": images})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="draft",
    )
    def draft_pitch(self, request, *args, **kwargs):
        user = request.user
        username = request.data.get("user")
        org = request.data.get("org")
        bio = request.data.get("bio")
        style = request.data.get("style")
        author = request.data.get("author")
        outlet = request.data.get("outlet")
        headline = request.data.get("headline")
        description = request.data.get("description")
        date = request.data.get("date")
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0
        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_EMAIL_JOURNALIST(
                    username, org, style, bio, author, outlet, headline, description, date
                )
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    "You are a VP of Communications",
                    token_amount=token_amount,
                    top_p=0.1,
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                res = open_ai_exceptions._handle_response(r)

                message = res.get("choices")[0].get("message").get("content").replace("**", "*")
                user.add_meta_data("emailDraft")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 2000:
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=message)

        return Response(data=message)


@api_view(["POST"])
@permission_classes([])
def mailgun_webhooks(request):
    event_data = request.data["event-data"]
    message_id = event_data["message"]["headers"]["message-id"]
    event_type = event_data["event"]
    try:
        tracker = EmailTracker.objects.get(message_id=message_id)
        if event_type == "opened":
            last_log = tracker.activity_log[len(tracker.activity_log) - 1]
            event, time = last_log.split("|")
            if event == "opened":
                message_timestamp = event_data["timestamp"]
                datetime_obj = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f")
                unix_time = datetime_obj.timestamp()
                if unix_time - message_timestamp < 60:
                    Response(status=status.HTTP_202_ACCEPTED)
                else:
                    tracker.opens += 1
            else:
                tracker.opens += 1
        elif event_type == "delivered":
            tracker.received = True
        elif event_type == "failed":
            tracker.failed = True
        elif event_type == "clicked":
            tracker.clicks += 1
        tracker.save()
        tracker.add_activity(event_type)
    except EmailTracker.DoesNotExist:
        return Response(status=status.HTTP_202_ACCEPTED)
    except Exception as e:
        logger.exception(f"{e}, {message_id}\n{event_data}")
    return Response(status=status.HTTP_202_ACCEPTED)


@api_view(["POST"])
@permission_classes([])
def email_recieved_webhook(request):
    subject = request.POST.get("Subject")
    email_html = request.POST.get("stripped-html")
    to_email = request.POST.get("To")
    to_email = extract_email_address(to_email)
    from_email = request.POST.get("From")
    from_email = extract_email_address(from_email)
    name, domain = to_email.split("@")
    first, last = name.split(".")
    original_subject = subject.replace("Re: ", "")
    user = User.objects.get(first_name=first, last_name=last)
    try:
        print(subject, from_email, user)
        trackers = EmailTracker.objects.filter(recipient__icontains=from_email, user=user)
        filtered_trackers = [email for email in trackers if email.subject in original_subject]
        if len(filtered_trackers):
            tracker = filtered_trackers[0]
            tracker.replies += 1
            tracker.recieved = True
            tracker.save()
            tracker.add_activity("reply")
    except Exception as e:
        print(e)
    email = send_html_email(
        subject,
        "core/email-templates/reply-email.html",
        from_email,
        user.email,
        {"html": email_html},
    )
    return Response(status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
@permission_classes([])
def get_email_tracking(request):
    user = request.user
    trackers = EmailTracker.objects.filter(user__organization=user.organization).order_by(
        "-datetime_created"
    )
    serialized = EmailTrackerSerializer(trackers, many=True)
    rate_data = EmailTracker.get_user_rates(user.id)
    return Response(data={"trackers": serialized.data, "rates": rate_data})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_web_summary(request):
    user = request.user
    query = request.data.get("query")
    res = google_search(query)
    results = res["results"]
    art = Article(results[0]["link"], config=generate_config())
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
    token_amount = 1000
    timeout = 60.0
    while True:
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_WEB_SUMMARY(results, text)
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email,
                prompt,
                "You are a VP of Communications",
                token_amount=token_amount,
                top_p=0.1,
            )
            with Variable_Client(timeout) as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            res = open_ai_exceptions._handle_response(r)

            message = res.get("choices")[0].get("message").get("content").replace("**", "*")
            break
        except open_ai_exceptions.StopReasonLength:
            if token_amount <= 2000:
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
                break
            else:
                attempts += 1
                continue
        except Exception as e:
            has_error = True
            message = f"Unknown exception: {e}"
            break
    if has_error:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=message)
    return Response(data={"message": message})


class JournalistContactViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = JournalistContactSerializer

    def get_queryset(self):
        contacts = JournalistContact.objects.for_user(user=self.request.user)
        if self.request.data.get("tag", False):
            tag = self.request.get("tag")
            return contacts.filter(tags__contains=[tag])
        else:
            return contacts

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="modify_tags",
    )
    def modify_tags(self, request, *args, **kwargs):
        id = request.data.get("id")
        tag = request.data.get("tag")
        modifier = request.data.get("modifier")
        JournalistContact.modify_tags(id, tag, modifier)
        Response(status=status.HTTP_200_OK)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="tag_list",
    )
    def get_tag_list(self, request, *args, **kwargs):
        user = request.user
        tags = JournalistContact.get_tags_by_user(user)
        return Response(status=status.HTTP_200_OK, data={"tags": tags})
