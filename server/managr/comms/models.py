import json
import logging
from django.db import models
from managr.core.models import TimeStampModel
from managr.core import constants as core_consts
from managr.utils.client import Variable_Client
from managr.core import exceptions as open_ai_exceptions
logger = logging.getLogger("managr")

class Search(TimeStampModel):
    user = models.OneToOneField(
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

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.email} - {self.name}"

    def update_boolean(self):
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = core_consts.OPEN_AI_NEWS_BOOLEAN_CONVERSION(self.input_text)
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                self.user.email, prompt, token_amount=500, top_p=0.1,
            )
            with Variable_Client() as client:
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
                r = open_ai_exceptions._handle_response(r)
                query_input = r.get("choices")[0].get("message").get("content")
                self.search_boolean = query_input
        except Exception as e:
            logger.exception(e)
        return self.save()