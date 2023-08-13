import json
import httpx
import logging
from rest_framework import (
    mixins,
    viewsets,
)
from datetime import datetime, timedelta
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
from .models import Search
from managr.core.models import User
from .serializers import SearchSerializer
from managr.core import constants as core_consts
from managr.utils.client import Variable_Client
from managr.utils.misc import decrypt_dict
from managr.core import exceptions as open_ai_exceptions
from rest_framework.decorators import (
    api_view,
    permission_classes,
)

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
    serializer_class = SearchSerializer

    def get_queryset(self):
        return Search.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        data["user"] = str(user.id)
        try:
            serializer = SearchSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_data = serializer.data
            serializer.instance.update_boolean()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_201_CREATED, data=response_data)

    def update(self, request, *args, **kwargs):
        search = Search.objects.get(id=request.data.get("id"))
        try:
            search.update(
                input_text=request.data.get("input_text"),
                instructions=request.data.get("instructions"),
            )
            search.update_boolean()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="clips",
    )
    def get_clips(self, request, *args, **kwargs):
        user = User.objects.get(id=request.GET.get("user_id"))
        has_error = False
        search = request.GET.get("search")
        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = core_consts.OPEN_AI_NEWS_BOOLEAN_CONVERSION(search)
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
                news_res = Search.get_clips(query_input)
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
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="summary",
    )
    def get_summary(self, request, *args, **kwargs):
        clips = request.data.get("clips")
        search = request.data.get("search")
        instructions = request.data.get("instructions", False)
        has_error = False
        attempts = 1
        token_amount = 500
        timeout = 60.0
        while True:
            try:
                res = Search.get_summary(
                    request.user, token_amount, timeout, clips, search, instructions, True
                )
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
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"summary": message})

        return Response(data={"summary": message})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="article-summary",
    )
    def get_article_summary(self, request, *args, **kwargs):
        url = request.data["params"]["url"]
        search = request.data["params"]["search"]
        instructions = request.data["params"]["instructions"]
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
                datetime.now().date(), text, search, instructions
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
