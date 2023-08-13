import json
import logging
from datetime import datetime
from django.db import models
from managr.core.models import TimeStampModel
from managr.core import constants as core_consts
from . import constants as comms_consts
from .exceptions import _handle_response as _handle_news_response
from managr.utils.client import Variable_Client
from managr.utils.sites import get_site_url
from managr.core import exceptions as open_ai_exceptions
from managr.utils.misc import encrypt_dict
from urllib.parse import urlencode

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
