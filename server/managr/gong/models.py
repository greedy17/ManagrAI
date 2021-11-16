from django.db import models
import jwt
import pytz
import math
import logging
import json
import dateutil.parser

from datetime import datetime
from django.db import models
from django.utils import timezone
from urllib.parse import urlencode
from requests.exceptions import HTTPError

from django.contrib.postgres.fields import JSONField, ArrayField
from django.core.exceptions import ObjectDoesNotExist

from managr.core.models import TimeStampModel, User
from managr.utils.client import HttpClient
from .exceptions import GongAPIException, TokenExpired
from managr.organization.models import Organization

from managr.core import constants as core_consts
from . import constants as gong_consts

from managr.slack.helpers import block_builders

logger = logging.getLogger("managr")

client = HttpClient().client


class GongAuthAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.organization = kwargs.get("organization", None)
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.token_generated_date = kwargs.get("token_generated_date", None)
        self.admin = kwargs.get("admin", None)

    @property
    def as_dict(self):
        return vars(self)

    @staticmethod
    def get_authorization():
        query = urlencode(gong_consts.AUTHORIZATION_QUERY_PARAMS)
        return f"{gong_consts.AUTHORIZATION_URI}?{query}"

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError
        elif response.status_code == 200:
            try:
                data = response.json()
            except Exception as e:
                GongAPIException(e, fn_name)
            except json.decoder.JSONDecodeError as e:
                return logger.error(f"An error occured with a zoom integration, {e}")
        else:
            status_code = response.status_code
            error_data = response.json()
            error_check = error_data.get("error_param", None)
            error_param = error_check if error_check else error_data.get("errors")
            kwargs = {
                "status_code": status_code,
                "error_param": error_param,
            }
            GongAPIException(HTTPError(kwargs), fn_name)
        return data

    @staticmethod
    def get_auth_token(code: str):
        query = urlencode(gong_consts.AUTHENTICATION_QUERY_PARAMS(code))
        headers = {"Authorization": f"Basic {gong_consts.GONG_BASIC_TOKEN}"}
        r = client.post(f"{gong_consts.AUTHENTICATION_URI}?{query}", headers=headers)
        return GongAuthAdapter._handle_response(r)

    @classmethod
    def create_auth_account(cls, code: str, managr_user_id):
        user = User.objects.get(id=managr_user_id)
        org = Organization.objects.get(id=user.organization.id)
        auth_data = cls.get_auth_token(code)
        data = {}
        data["organization"] = org.id
        data["access_token"] = auth_data["access_token"]
        data["refresh_token"] = auth_data["refresh_token"]
        data["admin"] = managr_user_id
        data["token_generated_date"] = timezone.now()
        return cls(**data)

    def get_users(self, cursor):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        url = f"{gong_consts.GONG_BASE_URI}/{gong_consts.USERS}"
        if cursor:
            url += "?" + urlencode({"cursor": cursor})
        res = client.get(url, headers=headers)
        return GongAuthAdapter._handle_response(res)

    def get_calls(self, start, end):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        body = {
            "filter": {"fromDateTime": start, "toDateTime": end},
            "contentSelector": {
                "context": "Extended",
                "exposedFields": {
                    "collaboration": {"publicComments": True},
                    "content": {
                        "pointsOfInterest": True,
                        "structure": True,
                        "topics": True,
                        "trackers": True,
                    },
                    "interaction": {
                        "personInteractionStats": True,
                        "questions": True,
                        "speakers": True,
                        "video": True,
                    },
                    "media": True,
                    "parties": True,
                },
            },
        }
        res = client.post(
            f"{gong_consts.GONG_BASE_URI}/{gong_consts.CALLS_EXTENSIVE}",
            json.dumps(body),
            headers=headers,
        )
        return GongAuthAdapter._handle_response(res)

    def check_for_current_call(self, date):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        body = {
            "filter": {"fromDateTime": date},
            "contentSelector": {
                "context": "Extended",
                "exposedFields": {
                    "collaboration": {"publicComments": True},
                    "content": {
                        "pointsOfInterest": True,
                        "structure": True,
                        "topics": True,
                        "trackers": True,
                    },
                    "interaction": {
                        "personInteractionStats": True,
                        "questions": True,
                        "speakers": True,
                        "video": True,
                    },
                    "media": True,
                    "parties": True,
                },
            },
        }
        res = client.post(
            f"{gong_consts.GONG_BASE_URI}/{gong_consts.CALLS_EXTENSIVE}",
            json.dumps(body),
            headers=headers,
        )
        return GongAuthAdapter._handle_response(res)

    def refresh(self):
        query = gong_consts.REAUTHENTICATION_QUERY_PARAMS(self.refresh_token)
        query = urlencode(query)
        res = client.post(f"{gong_consts.AUTHENTICATION_URI}?{query}")

        return GongAuthAdapter._handle_response(res)

    def revoke(self):
        gong_account = GongAuthAccount.objects.get(id=self.id)
        try:
            gong_account.delete()
            return logger.info(f"Succefully deleted account {gong_account}")
        except Exception as e:
            logger.exception(f"Failed to delete account {gong_account},{e}")


class GongAuthAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(organization=user.organization)
        else:
            self.none()


class GongAuthAccount(TimeStampModel):
    organization = models.OneToOneField(
        "organization.Organization",
        related_name="gong_auth_account",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_generated_date = models.DateTimeField(null=True, blank=True)
    admin = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="gong_admin", blank=True, null=True
    )

    objects = GongAuthAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Auth account for {self.organization} owned by {self.admin.email}"

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return GongAuthAdapter(**data)

    def regenerate_token(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        helper = GongAuthAdapter(**data)
        res = helper.refresh()
        self.token_generated_date = timezone.now()
        self.access_token = res.get("access_token", None)
        self.refresh_token = res.get("refresh_token", None)
        self.save()


class GongAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(auth_account__organization=user.organization)
        else:
            return self.none()


class GongAccountAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.auth_account = kwargs.get("auth_account", None)
        self.user = kwargs.get("user", None)
        self.gong_id = kwargs.get("gong_id", None)
        self.guid = kwargs.get("guid", None)
        self.is_active = kwargs.get("is_active", None)
        self.email = kwargs.get("email", None)

    @property
    def as_dict(self):
        return vars(self)

    @classmethod
    def create_account(cls, user_data, auth_account_id):
        try:
            emails = user_data["emailAliases"]
            emails.append(user_data["emailAddress"])
            user = User.objects.filter(email__in=emails).first()
            if user:
                data = {}
                data["auth_account"] = auth_account_id
                data["user"] = user.id
                data["gong_id"] = user_data["id"]
                data["is_active"] = user_data["active"]
                data["email"] = user_data["emailAddress"]
                return cls(**data)
            else:
                return None
        except ObjectDoesNotExist:
            return None


class GongAccount(TimeStampModel):
    auth_account = models.ForeignKey(
        "GongAuthAccount", related_name="users", on_delete=models.CASCADE, blank=True, null=True,
    )
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="gong_account", blank=True, null=True,
    )
    gong_id = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    email = models.EmailField()

    objects = GongAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Gong Account for {self.user.email}"

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return GongAuthAdapter(**data)


class GongCallQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(user__organization=user.organization)
        else:
            return self.none()


class GongCallAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.auth_account = kwargs.get("auth_account", None)
        self.crm = kwargs.get("crm", None)
        self.crm_id = kwargs.get("crm_id", None)
        self.gong_id = kwargs.get("gong_id", None)
        self.client_id = kwargs.get("client_id", None)
        self.client_system = kwargs.get("client_system", None)
        self.scheduled_date = kwargs.get("scheduled_date", None)

    @property
    def as_dict(self):
        return vars(self)

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError
        elif response.status_code == 200:
            try:
                data = response.json()
            except Exception as e:
                GongAPIException(e, fn_name)
            except json.decoder.JSONDecodeError as e:
                return logger.error(f"An error occured with a zoom integration, {e}")
        else:
            status_code = response.status_code
            error_data = response.json()
            error_check = error_data.get("error_param", None)
            error_param = error_check if error_check else error_data.get("errors")
            kwargs = {
                "status_code": status_code,
                "error_param": error_param,
            }

            GongAPIException(HTTPError(kwargs), fn_name)
        return data

    @classmethod
    def create_call(cls, call_data, auth_account_id):
        meta_data = call_data.get("metaData")
        context_data = call_data.get("context")
        auth_account = GongAuthAccount.objects.get(id=auth_account_id)
        schedule_date = dateutil.parser.parse(meta_data.get("scheduled")).date()
        opp_data = (
            [d for d in context_data[0].get("objects") if d["objectType"] == "Opportunity"]
            if len(context_data)
            else {}
        )
        opp = opp_data[0] if len(opp_data) else None
        data = {}
        data["auth_account"] = auth_account.id
        data["crm"] = context_data[0].get("system", None) if len(context_data) else None
        data["crm_id"] = opp.get("objectId") if opp else None
        data["gong_id"] = meta_data.get("id")
        data["client_id"] = meta_data.get("clientUniqueId", None)
        data["client_system"] = meta_data.get("system", None)
        data["scheduled_date"] = schedule_date
        return cls(**data)

    def get_call_details(self, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        body = {
            "filter": {"callIds": [self.gong_id],},
            "contentSelector": {
                "context": "Extended",
                "contextTiming": ["Now"],
                "exposedFields": {
                    "collaboration": {"publicComments": True},
                    "content": {
                        "pointsOfInterest": True,
                        "structure": True,
                        "topics": True,
                        "trackers": True,
                    },
                    "interaction": {
                        "personInteractionStats": True,
                        "questions": True,
                        "speakers": True,
                        "video": True,
                    },
                    "media": True,
                    "parties": True,
                },
            },
        }
        res = client.post(
            f"{gong_consts.GONG_BASE_URI}/{gong_consts.CALLS_EXTENSIVE}",
            json.dumps(body),
            headers=headers,
        )
        return GongCallAdapter._handle_response(res)


class GongCall(TimeStampModel):
    auth_account = models.ForeignKey(
        "GongAuthAccount", related_name="calls", on_delete=models.CASCADE, blank=True, null=True,
    )
    crm_id = models.CharField(max_length=100, null=True)
    crm = models.CharField(max_length=50, null=True)
    gong_id = models.CharField(max_length=30, null=True)
    client_system = models.CharField(max_length=50, null=True)
    client_id = models.CharField(max_length=50, null=True)
    scheduled_date = models.DateField(null=True)

    objects = GongCallQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return GongCallAdapter(**data)

    @property
    def as_slack_option(self):
        return block_builders.option(self.scheduled_date, str(self.id))
