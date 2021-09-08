import jwt
import pytz
import math
import logging
import json

from datetime import datetime
from django.db import models
from django.utils import timezone
from urllib.parse import urlencode
from requests.exceptions import HTTPError

from django.contrib.postgres.fields import JSONField, ArrayField
from django.core.exceptions import ObjectDoesNotExist

from managr.core.models import TimeStampModel, User
from managr.utils.client import HttpClient
from .exceptions import SalesloftAPIException
from managr.organization.models import Organization

from managr.salesforce.adapter.models import ActivityAdapter

from managr.core import constants as core_consts
from . import constants as salesloft_consts

logger = logging.getLogger("managr")

client = HttpClient().client


class SalesloftAuthAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.organization = kwargs.get("organization", None)
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.admin = kwargs.get("admin", None)

    @property
    def as_dict(self):
        return vars(self)

    @staticmethod
    def get_authorization():
        query = urlencode(salesloft_consts.AUTHORIZATION_QUERY_PARAMS)
        return f"{salesloft_consts.AUTHORIZATION_URI}?{query}"

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError
        elif response.status_code == 200 or response.status_code == 201:
            try:
                data = response.json()
            except Exception as e:
                SalesloftAPIException(e, fn_name)
            except json.decoder.JSONDecodeError as e:
                return logger.error(f"An error occured with a zoom integration, {e}")
        else:
            status_code = response.status_code
            error_data = response.json()
            error_param = error_data.get("error", None)
            error_message = error_data.get("message", None)
            error_code = error_data.get("code", None)
            kwargs = {
                "status_code": status_code,
                "error_code": error_code,
                "error_param": error_param,
                "error_message": error_message,
            }

            SalesloftAPIException(HTTPError(kwargs), fn_name)
        return data

    @staticmethod
    def get_auth_token(code: str, context: str, scope: str):
        query = salesloft_consts.AUTHENTICATION_QUERY_PARAMS(code, context, scope)
        query = urlencode(query)
        r = client.post(f"{salesloft_consts.AUTHENTICATION_URI}?{query}",)
        return SalesloftAuthAdapter._handle_response(r)

    @classmethod
    def create_auth_account(cls, code: str, context: str, scope: str, managr_user_id):
        user = User.objects.get(id=managr_user_id)
        org = Organization.objects.get(id=user.organization.id)
        auth_data = cls.get_auth_token(code, context, scope)
        # user_data = cls._get_user_data(auth_data["access_token"])
        data = {}
        data["organization"] = org.id
        data["access_token"] = auth_data["access_token"]
        data["refresh_token"] = auth_data["refresh_token"]
        data["admin"] = managr_user_id
        return cls(**data)

    def refresh_access_token(self):
        query = salesloft_consts.REAUTHENTICATION_QUERY_PARAMS(self.refresh_token)
        query = urlencode(query)
        ## error handling here

        r = client.post(
            f"{salesloft_consts.AUTHENTICATION_URI}?{query}",
            headers=dict(Authorization=(f"Basic {salesloft_consts.APP_BASIC_TOKEN}")),
        )
        return SalesloftAuthAdapter._handle_response(r)

    def get_all_users(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        print(headers)
        res = client.get(f"{salesloft_consts.SALESLOFT_BASE_URI}/users.json", headers=headers)
        return SalesloftAuthAdapter._handle_response(res)


class SalesloftAuthAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(organization=user.organization)
        else:
            self.none()


class SalesloftAuthAccount(TimeStampModel):
    organization = models.OneToOneField(
        "organization.Organization",
        related_name="salesloft_auth_account",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    admin = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="salesloft_admin", blank=True, null=True
    )
    objects = SalesloftAuthAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return SalesloftAuthAdapter(**data)


class SalesloftAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(auth_account__organization=user.organization)
        else:
            return self.none()


class SalesloftAccountAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.auth_account = kwargs.get("auth_account", None)
        self.user = kwargs.get("user", None)
        self.salesloft_id = kwargs.get("salesloft_id", None)
        self.guid = kwargs.get("guid", None)
        self.is_active = kwargs.get("is_active", None)
        self.email = kwargs.get("email", None)
        self.team_id = kwargs.get("team_id", None)

    @property
    def as_dict(self):
        return vars(self)

    @classmethod
    def create_account(cls, user_data, auth_account_id):
        try:
            user = User.objects.get(email=user_data["email"])
            team = user_data["team"]
            data = {}
            data["auth_account"] = auth_account_id
            data["user"] = user.id
            data["salesloft_id"] = user_data["id"]
            data["guid"] = user_data["guid"]
            data["is_active"] = user_data["active"]
            data["email"] = user_data["email"]
            data["team_id"] = team["id"]
            return cls(**data)
        except ObjectDoesNotExist:
            return None


class SalesloftAccount(TimeStampModel):
    auth_account = models.ForeignKey(
        "SalesloftAuthAccount",
        related_name="users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    user = models.OneToOneField(
        "core.User",
        on_delete=models.CASCADE,
        related_name="salesloft_account",
        blank=True,
        null=True,
    )
    salesloft_id = models.IntegerField()
    guid = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    email = models.EmailField()
    team_id = models.IntegerField(blank=True)

    objects = SalesloftAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return SalesloftAuthAdapter(**data)
