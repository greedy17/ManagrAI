import json
import datetime
import httpx
import logging
from rest_framework import (
    mixins,
    viewsets,
)
from newspaper import Article
from managr.api.models import ExpiringTokenAuthentication
from rest_framework.response import Response
from rest_framework import (
    permissions,
    mixins,
    status,
    viewsets,
)
from rest_framework.decorators import action
from . import constants as comms_consts
from managr.core import constants as core_consts
from managr.utils.client import Variable_Client
from managr.core import exceptions as open_ai_exceptions
from urllib.parse import urlencode
from .utils import get_news_for_company

logger = logging.getLogger("managr")


class PRSearchViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    authentication_classes = [ExpiringTokenAuthentication]

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="clips",
    )
    def get_clips(self, request, *args, **kwargs):
        search = request.GET.get("search")
        user = request.user
        has_error = False
        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = core_consts.OPEN_AI_NEWS_BOOLEAN_CONVERSION(search)
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email, prompt, token_amount=500, top_p=0.1,
                )
                with Variable_Client() as client:
                    r = client.post(
                        url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,
                    )
                    r = open_ai_exceptions._handle_response(r)
                    query_input = r.get("choices")[0].get("message").get("content")
                    query = urlencode({"q": query_input})
                    news_res = get_news_for_company(query)
                    articles = news_res["articles"]
                    break
            except Exception as e:
                has_error = True
                logger.exception(e)
                articles = e
                break
        if has_error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": articles})

        return Response({"articles": articles, "string": query_input})

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="summary",
    )
    def get_summary(self, request, *args, **kwargs):
        if request.GET.get("clips"):
            clips = request.GET.get("clips")
        else:
            clips = request.GET.getlist("clips[]")
        search = request.GET.get("search")
        instructions = request.GET.get("instructions")
        user = request.user
        has_error = False
        attempts = 1
        token_amount = 500
        timeout = 60.0
        while True:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_NEWS_CLIPS_SUMMARY(
                datetime.datetime.now().date(), clips, search, instructions
            )
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email,
                prompt,
                "You are a VP of Communications",
                token_amount=token_amount,
                top_p=0.1,
            )
            with Variable_Client(timeout) as client:
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
            try:
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
            except Exception as e:
                has_error = True
                message = f"Unknown exception: {e}"
                logger.exception(e)
                break
        if has_error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})

        return Response(data={"summary": message})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="article-summary",
    )
    def get_article_summary(self, request, *args, **kwargs):
        url = request.data['params']["url"]
        search = request.data['params']["search"]
        instructions = request.data['params']["instructions"]
        user = request.user
        article_res = Article(url)
        article_res.download()
        article_res.parse()
        text = article_res.text
        has_error = False
        attempts = 1
        token_amount = 500
        timeout = 60.0
        while True:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_ARTICLE_SUMMARY(
                datetime.datetime.now().date(), text, search,instructions
            )
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email,
                prompt,
                "You are a VP of Communications",
                token_amount=token_amount,
                top_p=0.1,
            )
            with Variable_Client(timeout) as client:
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
            try:
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
            except Exception as e:
                has_error = True
                message = f"Unknown exception: {e}"
                logger.exception(e)
                break
        if has_error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": message})
        return Response(data={"summary": message})
