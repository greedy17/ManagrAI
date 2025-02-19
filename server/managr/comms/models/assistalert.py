import logging
import re
from datetime import datetime, timedelta

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.utils.functional import cached_property

from managr.comms import constants as comms_consts
from managr.core.models import TimeStampModel

logger = logging.getLogger("managr")


class AssistAlert(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="assist_alerts",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    type = models.CharField(choices=comms_consts.ALERT_TYPES, max_length=50, default="EMAIL")
    title = models.CharField(max_length=255)
    run_at = models.DateTimeField()
    search = models.ForeignKey(
        "Search",
        related_name="alerts",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    thread = models.ForeignKey(
        "Thread",
        related_name="threads",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    recipients = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    meta_data = JSONField(
        default=dict,
        null=True,
        blank=True,
    )

    @cached_property
    def search_type(self):
        if hasattr(self, "search"):
            return self.search.type
        return self.thread.search.type

    @cached_property
    def search_boolean(self):
        search = self.search if hasattr(self, "search") else self.thread.search
        if not search.search_boolean or search.search_boolean == search.input_text:
            updated_boolean = search.update_boolean()
            return updated_boolean
        return search.search_boolean

    @cached_property
    def instructions(self):
        return self.meta_data.get("project", None)

    @cached_property
    def last_sent(self):
        return self.meta_data.get("last_sent", None)

    def delete(self, *args, **kwargs):
        self.search.delete()
        self.thread.delete
        self.delete()
        return super().delete(AssistAlert, *args, **kwargs)

    def add_recipient(self, email):
        new_recipients = self.recipients.append(email)
        remove_duplicates = list(set(new_recipients))
        self.recipients = remove_duplicates
        return self.save()

    def remove_recipient(self, email):
        remove_index = self.recipients.index(email)
        self.recipients.pop(remove_index)
        return self.save()

    def update_thread_data(self, for_dev=False):
        from managr.comms.models import Article, Search
        from managr.comms.utils import normalize_article_data

        project = self.thread.meta_data.get("project", "")
        if self.search.search_boolean == self.search.input_text:
            self.search.update_boolean()
        boolean = self.search.search_boolean
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        clips = self.search.get_clips(boolean, end_time, start_time)["articles"]
        try:
            clips = [article for article in clips if article["title"] != "[Removed]"]
            internal_articles = Article.search_by_query(boolean, str(end_time), str(start_time))
            normalized_clips = normalize_article_data(clips, internal_articles, False)
            descriptions = [clip["description"] for clip in normalized_clips]
            if for_dev:
                print(f"Current Boolean: {boolean}")
                print(f"Clips ({len(clips)}): {clips}")
                print("------------------------------")
                print(f"Internal Clips ({len(internal_articles)}): {internal_articles}")
                print("------------------------------")
            res = Search.get_summary(
                self.user,
                2000,
                60.0,
                descriptions,
                self.search.instructions,
                False,
                False,
                project,
                False,
                self.search.instructions,
                True,
            )
            if for_dev:
                print(f"Chat response: {res}")
            else:
                message = res.get("choices")[0].get("message").get("content").replace("**", "*")
                message = re.sub(r"\*(.*?)\*", r"<strong>\1</strong>", message)
                message = re.sub(
                    r"\[(.*?)\]\((.*?)\)", r'<a href="\2" target="_blank">\1</a>', message
                )
                self.thread.meta_data["articlesFiltered"] = normalized_clips
                self.thread.meta_data["filteredArticles"] = normalized_clips
                self.thread.meta_data["summary"] = message
                self.thread.meta_data["summaries"] = []
                self.thread.save()
        except Exception as e:
            print(str(e))
        return
