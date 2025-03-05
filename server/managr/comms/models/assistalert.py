import json
import logging
import re
from datetime import datetime, timedelta, timezone

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.utils.functional import cached_property

from managr.comms import constants as comms_consts
from managr.comms.utils import (
    alternate_google_search,
    get_bluesky_data,
    get_tweet_data,
    get_youtube_data,
    merge_sort_dates,
    normalize_article_data,
)
from managr.core import constants as core_consts
from managr.core import exceptions as open_ai_exceptions
from managr.core.models import TimeStampModel
from managr.core.utils import Variable_Client

logger = logging.getLogger("managr")


def update_news_alert_data(alert_id):
    from managr.comms.models import Article as InternalArticle
    from managr.comms.models import Search

    alert = AssistAlert.objects.get(id=alert_id)
    thread = alert.thread
    project = alert.thread.meta_data.get("project", "")
    boolean = alert.search_boolean
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    clips = alert.thread.search.get_clips(boolean, end_time, start_time)["articles"]
    clips = [article for article in clips if article["title"] != "[Removed]"]
    internal_articles = InternalArticle.search_by_query(boolean, str(end_time), str(start_time))
    normalized_clips = normalize_article_data(clips, internal_articles, False)
    descriptions = [clip["description"] for clip in normalized_clips]
    res = Search.get_summary(
        alert.user,
        2000,
        60.0,
        descriptions,
        alert.thread.search.instructions,
        False,
        False,
        project,
        False,
        alert.thread.search.instructions,
        True,
    )
    message = res.get("choices")[0].get("message").get("content").replace("**", "*")
    message = re.sub(r"\*(.*?)\*", r"<strong>\1</strong>", message)
    message = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" target="_blank">\1</a>', message)
    thread.meta_data["articlesFiltered"] = normalized_clips
    thread.meta_data["filteredArticles"] = normalized_clips
    thread.meta_data["summary"] = message
    thread.meta_data["summaries"] = []
    thread.save()


def update_omni_alert_data(alert_id):
    from managr.comms.models import Article as InternalArticle

    alert = AssistAlert.objects.get(id=alert_id)
    user = alert.user
    thread = alert.thread
    search_boolean = alert.search_boolean
    social_switcher = {
        "youtube": get_youtube_data,
        "twitter": get_tweet_data,
        "bluesky": get_bluesky_data,
    }
    max = 0
    social_values = ["youtube", "bluesky"]
    if user.has_twitter_integration:
        max = 20
        social_values.append("twitter")
    else:
        max = 25
    date_now = datetime.now(timezone.utc)
    date_to = str(date_now.date())
    date_from = str((date_now - timedelta(hours=24)).date())
    social_data_dict = {"twitter": []}
    for value in social_values:
        data_func = social_switcher[value]
        social_data = data_func(
            search_boolean, max=max, user=user, date_from=date_from, date_to=date_to
        )
        if "error" in social_data.keys():
            social_data_dict[value] = []
            continue
        else:
            social_data_dict[value] = merge_sort_dates(social_data["data"], "created_at")
    internal_articles = InternalArticle.search_by_query(
        search_boolean, str(date_to), str(date_from)
    )
    normalized_clips = normalize_article_data([], internal_articles, False)[:31]
    google_results = alternate_google_search(search_boolean, 5, True)["results"]
    sorted_social_data = []
    sorted_social_data.extend(social_data_dict["twitter"][:5])
    sorted_social_data.extend(social_data_dict["bluesky"][:7])
    sorted_social_data.extend(social_data_dict["youtube"][:6])
    sorted_social_data = merge_sort_dates(sorted_social_data, "created_at")
    omniResults = [*normalized_clips, *sorted_social_data, *google_results]
    for i, r in enumerate(omniResults):
        r["citationIndex"] = i
    url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
    prompt = comms_consts.OPEN_AI_OMNI_SUMMARY(
        date_now,
        alert.thread.search.input_text,
        normalized_clips,
        social_data_dict["twitter"][:5],
        social_data_dict["youtube"][:6],
        social_data_dict["bluesky"][:7],
        google_results,
        thread.meta_data["project"],
    )

    body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
        user.email,
        prompt,
        "You are a VP of Communications",
        top_p=0.1,
    )
    with Variable_Client(30) as client:
        r = client.post(
            url,
            data=json.dumps(body),
            headers=core_consts.OPEN_AI_HEADERS,
        )
    res = open_ai_exceptions._handle_response(r)
    message = res.get("choices")[0].get("message").get("content").replace("**", "*")
    message = re.sub(r"\*(.*?)\*", r"<strong>\1</strong>", message)
    message = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" target="_blank">\1</a>', message)
    thread.meta_data["summary"] = message
    thread.meta_data["summaries"] = []
    thread.meta_data["omniSocial"] = sorted_social_data
    thread.meta_data["omniNews"] = normalized_clips
    thread.meta_data["omniWeb"] = google_results
    thread.meta_data["omniResults"] = omniResults
    thread.save()
    return


def update_social_alert_data(alert_id):
    from managr.comms.models import TwitterAccount

    alert = AssistAlert.objects.get(id=alert_id)
    user = alert.user
    thread = alert.thread
    search_boolean = alert.search_boolean
    social_switcher = {
        "youtube": get_youtube_data,
        "twitter": get_tweet_data,
        "bluesky": get_bluesky_data,
    }
    max = 0
    social_values = ["youtube", "bluesky"]
    if user.has_twitter_integration:
        max = 20
        social_values.append("twitter")
    else:
        max = 25
    date_now = datetime.now(timezone.utc)
    date_to = str(date_now.date())
    date_from = str((date_now - timedelta(hours=24)).date())
    email_data = {}
    social_data_list = []
    for value in social_values:
        data_func = social_switcher[value]
        social_data = data_func(
            search_boolean, max=max, user=user, date_from=date_from, date_to=date_to
        )
        if "error" in social_data.keys():
            continue
        else:
            social_data_list.extend(social_data["data"])
    sorted_social_data = merge_sort_dates(social_data_list, "created_at")
    res = TwitterAccount.get_summary(
        alert.user,
        2000,
        60.0,
        sorted_social_data,
        search_boolean,
        alert.instructions,
        False,
    )
    message = res.get("choices")[0].get("message").get("content").replace("**", "*")
    message = re.sub(r"\*(.*?)\*", r"<strong>\1</strong>", message)
    message = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" target="_blank">\1</a>', message)
    thread.meta_data["tweets"] = sorted_social_data
    thread.meta_data["summary"] = message
    thread.meta_data["summaries"] = []
    if user.has_twitter_integration:
        if "tweetMedia" in email_data.keys():
            thread.meta_data["tweetMedia"] = email_data["media"]
        if "includes" in email_data.keys():
            thread.meta_data["includes"] = email_data["includes"]
    thread.save()


update_switcher = {
    "OMNI": update_omni_alert_data,
    "SOCIAL": update_social_alert_data,
    "NEWS": update_news_alert_data,
}


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
        return self.thread.search.type

    @cached_property
    def search_boolean(self):
        search = self.thread.search
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
        try:
            update_func = update_switcher[self.thread.search.type]
            update_func(self.id)
        except Exception as e:
            print(str(e))
        return
