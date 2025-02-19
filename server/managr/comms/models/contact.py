import json
from collections import Counter
from datetime import datetime
from urllib.parse import urlencode

import pytz
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from newspaper import Article as ExternalArticle
from newspaper import ArticleException

from managr.comms import constants as comms_consts
from managr.comms.models.scrape import Article
from managr.core import constants as core_consts
from managr.core import exceptions as open_ai_exceptions
from managr.core.models import TimeStampModel
from managr.utils.client import Variable_Client


class Journalist(TimeStampModel):
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    outlet = models.CharField(max_length=255)
    verified = models.BooleanField(default=False)
    date_verified = models.DateTimeField(blank=True, null=True)
    beats = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    coverage_type = models.CharField(
        choices=comms_consts.COVERAGE_TYPE_CHOICES, max_length=50, default="BOTH"
    )
    accuracy_score = models.IntegerField(default=0)
    number_of_sources = models.IntegerField(default=0)
    status = models.CharField(
        choices=comms_consts.JOURNALIST_CHOICES, max_length=100, default="OTHER"
    )
    needs_review = models.BooleanField(default=False)
    review_details = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["last_name"]

    def __str__(self):
        return f"{self.email} - {self.outlet}"

    @property
    def as_object(self):
        return {
            "outlet": self.outlet,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
        }

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def verify_email(cls, email):
        url = comms_consts.HUNTER_VERIFY_URI
        params = {"api_key": comms_consts.HUNTER_API_KEY, "email": email}
        encoded_params = urlencode(params)
        url = url + "?" + encoded_params
        with Variable_Client() as client:
            r = client.get(
                url,
            )
            if r.status_code == 200:
                r = r.json()
                score = r["data"]["score"]
                if score is None:
                    score = 0
            else:
                return 0
        return score

    @classmethod
    def email_finder(cls, first_name, last_name, domain=False, outlet=False):
        url = comms_consts.HUNTER_FINDER_URI
        params = {
            "api_key": comms_consts.HUNTER_API_KEY,
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
        }
        if domain:
            params["domain"] = domain
        else:
            params["company"] = outlet
        encoded_params = urlencode(params)
        url = url + "?" + encoded_params
        with Variable_Client() as client:
            r = client.get(
                url,
            )
            r = r.json()
            if "errors" in r.keys():
                return {"score": None, "email": None}
            response = r["data"]
        return response


class EmailTracker(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="emails",
        on_delete=models.CASCADE,
    )
    recipient = models.CharField(max_length=255)
    name = models.CharField(max_length=255, default="N/A")
    subject = models.CharField(max_length=255)
    body = models.TextField()
    cc_recipients = models.TextField(blank=True, null=True)
    bcc_recipients = models.TextField(blank=True, null=True)
    message_id = models.CharField(max_length=255, blank=True, null=True)
    opens = models.IntegerField(default=0)
    replies = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    received = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    activity_log = ArrayField(models.CharField(max_length=255), default=list)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.recipient}: {self.subject}"

    @property
    def is_draft(self):
        if self.activity_log:
            idx = len(self.activity_log) - 1
            first = self.activity_log[idx]
            event, time = first.split("|")
            if event == "draft_created":
                return True
        return False

    def add_activity(self, type):
        timezone = pytz.timezone(self.user.timezone)
        date = datetime.now(pytz.utc)
        date_str = date.astimezone(timezone).isoformat()
        new_item = f"{type}|{date_str}"
        self.activity_log.append(new_item)
        return self.save()

    @classmethod
    def get_user_rates(cls, user_id):
        data = {}
        trackers = cls.objects.filter(user__id=user_id)
        if len(trackers):
            delivered = trackers.filter(received=True)
            failed = trackers.filter(failed=True)
            replies = trackers.filter(replies__gt=0)
            opens = trackers.filter(opens__gt=0)
            delivery_rate = round((len(delivered) / len(trackers)) * 100, 2)
            fail_rate = round((len(failed) / len(trackers)) * 100, 2)
            reply_rate = round((len(replies) / len(trackers)) * 100, 2)
            open_rate = round((len(opens) / len(trackers)) * 100, 2)
            data = {
                "delivery_rate": delivery_rate,
                "fail_rate": fail_rate,
                "reply_rate": reply_rate,
                "open_rate": open_rate,
            }
        return data

    @classmethod
    def _create_email_tracker_data(cls, email):
        import random
        import uuid

        from managr.core.models import User

        user = User.objects.get(email=email)
        open_list = [1, 2, 3]
        booleans = [True, False]
        count = 0
        body = "Test"
        date = str(datetime.now())
        emails = list(Article.objects.filter(author__contains="@").values_list("author", flat=True))
        subject = "Test"
        while count <= 10:
            activity_log = [f"delivered|{date}"]
            data = {}

            received = random.choice(booleans)
            failed = False if received else True
            if received:
                open = random.choice(open_list)
                data["opens"] = open
                data["received"] = received
                data["failed"] = failed
                replied = random.choice(booleans)
                data["replies"] = replied
                activity_log.append(f"open|{date}")
                if replied:
                    activity_log.append(f"replied|{date}")
            else:
                activity_log.append(f"failed|{date}")
            author = random.choice(emails)
            data["recipient"] = author
            data["user"] = user
            data["subject"] = subject
            data["body"] = body
            data["activity_log"] = activity_log
            data["message_id"] = str(uuid.uuid4())
            EmailTracker.objects.create(**data)
            count += 1
        return


class JournalistContactQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user.id)


class JournalistContact(TimeStampModel):
    user = models.ForeignKey(
        "core.User",
        related_name="j_contacts",
        on_delete=models.CASCADE,
    )
    journalist = models.ForeignKey(
        "comms.Journalist",
        on_delete=models.CASCADE,
    )
    tags = ArrayField(models.CharField(max_length=255), default=list)
    bio = models.TextField(blank=True, null=True)
    email = models.CharField(blank=True, null=True, max_length=255)
    outlet = models.CharField(blank=True, null=True, max_length=255)
    images = ArrayField(models.TextField(), default=list)
    notes = ArrayField(JSONField(), default=list, blank=True, null=True)

    class Meta:
        unique_together = ("user", "journalist")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"{self.user} - {self.journalist}"

    objects = JournalistContactQuerySet.as_manager()

    @classmethod
    def get_tags_by_user(cls, user):
        tags_query = cls.objects.filter(user=user)
        tag_list = []
        for contact in tags_query:
            tag_list.extend(contact.tags)
        tag_counts = Counter(tag_list)
        tags_with_count = [{"name": tag, "count": count} for tag, count in tag_counts.items()]

        return tags_with_count

    @classmethod
    def modify_tags(cls, id, tag, modifier):
        contact = cls.objects.get(id=id)
        if modifier == "add":
            tags = contact.tags
            tags.append(tag)
            contact.tags = list(set(tags))
        else:
            contact.tags.remove(tag)
        return contact.save()

    def generate_bio(self):
        from managr.comms.utils import generate_config, google_search

        query = f"Journalist AND {self.journalist.full_name} AND {self.journalist.outlet}"
        google_results = google_search(query)
        if len(google_results) == 0:
            return False
        results = google_results["results"]
        images = google_results["images"]
        art = ExternalArticle(results[0]["link"], config=generate_config())
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
        token_amount = 2000
        timeout = 60.0
        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_DISCOVERY_RESULTS_PROMPT(
                    self.journalist.full_name, results, self.journalist.outlet, text
                )
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    self.user.email,
                    prompt,
                    "You are a VP of Communications",
                    token_amount=token_amount,
                    top_p=0.1,
                    response_format={"type": "json_object"},
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                res = open_ai_exceptions._handle_response(r)
                message = res.get("choices")[0].get("message").get("content")
                message = json.loads(message)
                bio = message.get("bio")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount <= 3000:
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
            return False
        self.bio = bio
        self.images = images
        self.save()
        return True
