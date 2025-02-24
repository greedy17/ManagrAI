import json
import logging
from datetime import datetime
from urllib.parse import urlencode

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.constraints import UniqueConstraint

from managr.comms import constants as comms_consts
from managr.core import constants as core_consts
from managr.core import exceptions as open_ai_exceptions
from managr.core.models import TimeStampModel
from managr.slack.helpers import block_builders
from managr.utils.client import Variable_Client
from managr.utils.misc import encrypt_dict
from managr.utils.sites import get_site_url

from ..exceptions import _handle_response as _handle_news_response

logger = logging.getLogger("managr")


class CompanyDetails(models.Model):
    details = models.TextField()
    title = models.TextField()
    user = models.ForeignKey(
        "core.User",
        related_name="company_details",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Company Detail"
        verbose_name_plural = "Company Details"

    @property
    def as_slack_option(self):
        return block_builders.option(self.title[:74], str(self.id))


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
            prompt = (
                core_consts.OPEN_AI_QUERY_STRING(self.input_text, self.instructions)
                if self.type == "NEWS"
                else comms_consts.OPEN_AI_TWITTER_SEARCH_CONVERSION(
                    self.input_text, self.instructions
                )
            )
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
            self.search_boolean = query_input.replace('"', "")
        except Exception as e:
            logger.exception(e)
        return self.save()

    @classmethod
    def get_summary(
        cls,
        user,
        tokens,
        timeout,
        clips,
        input_text,
        previous,
        is_follow__up,
        company,
        trending,
        instructions=False,
        for_client=False,
    ):
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        elma = core_consts.ELMA

        if is_follow__up:
            prompt = comms_consts.SUMMARY_FOLLOW_UP(
                datetime.now().date(), clips, previous, company, elma, instructions, trending
            )
        else:
            prompt = (
                comms_consts.OPEN_AI_NEWS_CLIPS_SUMMARY(
                    datetime.now().date(),
                    clips,
                    input_text,
                    company,
                    elma,
                    trending,
                    instructions,
                    for_client,
                )
                if for_client
                else comms_consts.OPEN_AI_NEWS_CLIPS_SLACK_SUMMARY(
                    datetime.now().date(), clips, input_text, previous, instructions, for_client
                )
            )

        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email,
            prompt,
            temperature=0.1,
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
    def get_summary_email(
        cls, user, tokens, timeout, clips, input_text, instructions=False, for_client=False
    ):
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        elma = core_consts.ELMA
        project = ""

        prompt = (
            comms_consts.OPEN_AI_NEWS_CLIPS_SUMMARY_EMAIL(
                datetime.now().date(), clips, input_text, elma, project, instructions, for_client
            )
            if for_client
            else comms_consts.OPEN_AI_NEWS_CLIPS_SLACK_SUMMARY(
                datetime.now().date(), clips, input_text, instructions, for_client
            )
        )
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email,
            prompt,
            "You are a VP of Communications",
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

    @classmethod
    def get_clips(cls, search_boolean, date_to=False, date_from=False, is_report=False):
        page_size = 40
        if is_report:
            page_size = 100
        query = {"q": search_boolean, "excludeDomains": ",".join(comms_consts.EXCLUDE_DOMAINS)}
        if date_to:
            query["to"] = date_to
            query["from"] = date_from
        endpoint = (
            comms_consts.NEW_API_EVERYTHING_QUERY_URI(urlencode(query)) + f"&pageSize={page_size}"
        )
        news_url = comms_consts.NEW_API_URI + "/" + endpoint
        with Variable_Client() as client:
            new_res = client.get(news_url, headers=comms_consts.NEWS_API_HEADERS)
        return _handle_news_response(new_res)

    @classmethod
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

    def generate_shareable_link(self):
        date = str(datetime.now())
        data = {"created_at": date, "id": str(self.id)}
        encrypted_data = encrypt_dict(data)
        base_url = get_site_url()
        return f"{base_url}/shared/{encrypted_data}"


class Thread(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="threads",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    title = models.TextField()
    search = models.ForeignKey(
        Search, related_name="search", on_delete=models.CASCADE, null=True, blank=True
    )
    meta_data = JSONField(default=dict)

    def __str__(self):
        return f"{self.user} - {self.title}"

    @property
    def current_index(self):
        message_idxs = list(self.messages.all().values_list("index", flat=True))
        if message_idxs:
            return max(message_idxs)
        else:
            return None

    def add_message(self, message_text, role="SYSTEM"):
        curr_idx = self.current_index()
        if curr_idx:
            data = dict(body=message_text, index=(curr_idx + 1), role=role, thread=self)
            try:
                message = ThreadMessage.objects.create(**data)
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": True, "data": message.as_dict()}

    def generate_url(self):
        date = str(datetime.now())
        data = {"created_at": date, "id": str(self.id)}
        encrypted_data = encrypt_dict(data)
        base_url = get_site_url()
        return f"{base_url}/summaries/{encrypted_data}"

    def delete(self, *args, **kwargs):
        self.search.delete()
        return super(Thread, self).delete(*args, **kwargs)


class ThreadMessage(TimeStampModel):
    body = models.TextField(blank=True, null=True)
    thread = models.ForeignKey(
        "Thread",
        related_name="messages",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    role = models.CharField(choices=comms_consts.MESSAGE_TYPES, max_length=50, default="SYSTEM")
    index = models.PositiveIntegerField(default=0)
    meta_data = JSONField(default=dict)

    class Meta:
        ordering = ["index"]
        constraints = [UniqueConstraint(fields=["thread", "index"], name="unique_message")]

    def as_dict(self):
        return dict(body=self.body, thread=str(self.thread.id), role=self.role, index=self.index)


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


class Discovery(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="discoveries",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    beat = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    list = models.TextField(null=True, blank=True)
    results = JSONField(default=dict, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.email} - {self.name}"


class Pitch(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="pitches",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    instructions = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=300, null=True, blank=True)
    audience = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    generated_pitch = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.email} - {self.name}"

    @classmethod
    def generate_pitch(cls, user, type, instructions, style, tokens, timeout):
        elma = core_consts.ELMA
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        # style = user.writing_style if user.writing_style else False
        prompt = comms_consts.OPEN_AI_PITCH(datetime.now().date(), type, instructions, elma, style)
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(user.email, prompt, model="o1-mini")
        with Variable_Client(timeout) as client:
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        return open_ai_exceptions._handle_response(r)


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

    @property
    def as_slack_option(self):
        return block_builders.option(self.title[:74], str(self.id))
