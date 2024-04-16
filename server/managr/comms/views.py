import json
import httpx
import time
import logging
import pytz
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
from django.shortcuts import redirect
from rest_framework.decorators import action
from . import constants as comms_consts
from .models import Search, TwitterAccount, Pitch, Process, InstagramAccount, Discovery
from .models import Article as InternalArticle
from .models import WritingStyle, EmailAlert
from managr.core.models import User
from managr.comms import exceptions as comms_exceptions
from .tasks import emit_process_website_domain, emit_send_news_summary, emit_share_client_summary
from .serializers import (
    SearchSerializer,
    PitchSerializer,
    EmailAlertSerializer,
    ProcessSerializer,
    TwitterAccountSerializer,
    InstagramAccountSerializer,
    WritingStyleSerializer,
    DiscoverySerializer,
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
    merge_sort_dates,
)
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from managr.comms.tasks import emit_get_meta_account_info

logger = logging.getLogger("managr")


def getclips(request):
    try:
        user = User.objects.get(id=request.GET.get("user_id"))
        has_error = False
        search = request.GET.get("search", False)
        boolean = request.GET.get("boolean", False)
        date_to = request.GET.get("date_to", False)
        date_from = request.GET.get("date_from", False)

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
            query_input = r.get("choices")[0].get("message").get("content")
            news_res = Search.get_clips(query_input, date_to, date_from)
            articles = news_res["articles"]
        else:
            news_res = Search.get_clips(boolean, date_to, date_from)
            articles = news_res["articles"]
            query_input = boolean

        articles = [article for article in articles if article["title"] != "[Removed]"]
        internal_articles = InternalArticle.search_by_query(query_input, date_to, date_from)
        articles = normalize_article_data(articles, internal_articles)

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
        # search = '("Under Armour" OR "Nike" OR "Adidas" OR "Puma" OR "Reebok" OR "Fabletics" OR "Athleta") NOT "Lululemon"'
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
                    query_input = query_input + " lang:en"
                tweet_res = twitter_account.get_tweets(query_input, next_token)
                tweets = tweet_res.get("data", None)
                includes = tweet_res.get("includes", None)
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
                if attempts > 3:
                    return Response(
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        data={
                            "error": f"We've hit an issue contacting Twitter for {query_input}",
                            "string": query_input,
                        },
                    )
                attempts += 1
                retry_after = int(tweet_res.headers.get("Retry-After", 5))
                time.sleep(retry_after)
                continue
            except Exception as e:
                has_error = True
                logger.exception(e)
                tweet_res = e
                break

        if has_error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": tweet_res})
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
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="posts",
    )
    def get_instagram_posts(self, request, *args, **kwargs):
        user = User.objects.get(id=request.GET.get("user_id"))
        date_to = request.GET.get("date_to")
        date_from = request.GET.get("date_from")
        ig_account = user.instagram_account
        has_error = False
        hashtag = request.GET.get("hashtag")
        next_token = False
        post_list = []
        attempts = 1
        while True:
            try:
                id = ig_account.get_hashtag_id(hashtag)
                posts_res = ig_account.get_posts(id, date_to, date_from)
                posts = posts_res["data"]
                post_list = posts
                # post_list = merge_sort_dates(post_list, "timestamp")
                break
            except Exception as e:
                has_error = True
                logger.exception(e)
                ig_res = e
                break

        if has_error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": ig_res})
        return Response(
            {
                "posts": post_list,
            }
        )

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="ig-summary",
    )
    def get_instagram_summary(self, request, *args, **kwargs):
        user = request.user
        if user.has_hit_summary_limit:
            return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        posts = request.data.get("posts")
        for idx, post in enumerate(posts):
            hashtag_idx = post.find("#")
            if hashtag_idx > 0:
                if hashtag_idx == 39:
                    del posts[idx]
                posts[idx] = post[:hashtag_idx]
        instructions = request.data.get("instructions", False)
        ig_account = user.instagram_account
        has_error = False
        attempts = 1
        token_amount = 1000
        timeout = 60.0
        while True:
            try:
                res = ig_account.get_summary(
                    request.user, token_amount, timeout, posts, instructions, True
                )
                message = res.get("choices")[0].get("message").get("content").replace("**", "*")
                user.add_meta_data("ig_summaries")
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
        return Discovery.objects.filter(user=self.request.user)

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
