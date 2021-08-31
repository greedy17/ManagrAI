import jwt
import pytz
import math
import logging

from datetime import datetime
from django.db import models
from django.utils import timezone
from urllib.parse import urlencode
from requests.exceptions import HTTPError

from django.contrib.postgres.fields import JSONField, ArrayField

from managr.core.models import TimeStampModel
from managr.utils.client import HttpClient
from .exceptions import SalesloftAPIException

from managr.salesforce.adapter.models import ActivityAdapter

from managr.core import constants as core_consts
from . import constants as salesloft_consts

logger = logging.getLogger("managr")

client = HttpClient().client


class SalesloftAuthAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            if user.type == core_consts.ACCOUNT_TYPE_MANAGER:
                return self.filter(user__organization=user.organization)
            elif user.type == core_consts.ACCOUNT_TYPE_REP:
                return self.filter(user=user)
            else:
                return self.none()


class SalesloftAuthAccount(TimeStampModel):
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="salesloft_account"
    )
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)

    objects = SalesloftAuthAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

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
        print(r)

    @classmethod
    def create_account(cls, code: str, context: str, scope: str, managr_user_id):
        auth_data = cls.get_auth_token(code, context, scope)
        user_data = cls._get_user_data(auth_data["access_token"])
        data = {**auth_data, **user_data}
        data["user"] = str(managr_user_id)

        return cls(**data)
