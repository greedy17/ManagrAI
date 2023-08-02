import json
import logging
from rest_framework import (
    mixins,
    viewsets,
)
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
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="clips",
    )
    def get_clips(self, request, *args, **kwargs):
        search = request.data.get("search")
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

        return Response(data={"articles": articles})
