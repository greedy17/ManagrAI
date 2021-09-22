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
from .exceptions import SalesloftAPIException, TokenExpired
from managr.organization.models import Organization

from managr.salesforce.adapter.models import ActivityAdapter

from managr.core import constants as core_consts
from . import constants as salesloft_consts

from managr.slack.helpers import block_builders

logger = logging.getLogger("managr")

client = HttpClient().client


class SalesloftAuthAdapter:
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
            logger.info(f"{error_data}")
            error_check = error_data.get("error_param", None)
            error_param = error_check if error_check else error_data.get("errors")
            kwargs = {
                "status_code": status_code,
                "error_param": error_param,
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
        data = {}
        data["organization"] = org.id
        data["access_token"] = auth_data["access_token"]
        data["refresh_token"] = auth_data["refresh_token"]
        data["admin"] = managr_user_id
        data["token_generated_date"] = timezone.now()
        return cls(**data)

    def get_users(self, page=1):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        res = client.get(
            f"{salesloft_consts.SALESLOFT_BASE_URI}/{salesloft_consts.USERS}", headers=headers
        )
        return SalesloftAuthAdapter._handle_response(res)

    def get_cadences(self, page=1):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        query = urlencode({"include_paging_counts": True, "page": page})
        res = client.get(
            f"{salesloft_consts.SALESLOFT_BASE_URI}/{salesloft_consts.CADENCES}?{query}",
            headers=headers,
        )
        return SalesloftAuthAdapter._handle_response(res)

    def get_accounts(self, page=1):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        query = urlencode({"include_paging_counts": True, "page": page})
        res = client.get(
            f"{salesloft_consts.SALESLOFT_BASE_URI}/{salesloft_consts.ACCOUNTS}?{query}",
            headers=headers,
        )
        return SalesloftAuthAdapter._handle_response(res)

    def get_people(self, page=1):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        query = urlencode({"include_paging_counts": True, "page": page})
        res = client.get(
            f"{salesloft_consts.SALESLOFT_BASE_URI}/{salesloft_consts.PEOPLE}?{query}",
            headers=headers,
        )
        return SalesloftAuthAdapter._handle_response(res)

    def refresh(self):
        query = salesloft_consts.REAUTHENTICATION_QUERY_PARAMS(self.refresh_token)
        query = urlencode(query)
        res = client.post(f"{salesloft_consts.AUTHENTICATION_URI}?{query}")

        return SalesloftAuthAdapter._handle_response(res)

    def revoke(self):
        salesloft_account = SalesloftAccount.objects.get(id=self.id)
        try:
            salesloft_account.delete()
            return logger.info(f"Succefully deleted account {salesloft_account}")
        except Exception as e:
            logger.exception(f"Failed to delete account {salesloft_account},{e}")


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
    token_generated_date = models.DateTimeField(null=True, blank=True)
    admin = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="salesloft_admin", blank=True, null=True
    )

    objects = SalesloftAuthAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Auth account for {self.organization} owned by {self.admin.email}"

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return SalesloftAuthAdapter(**data)

    def regenerate_token(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        helper = SalesloftAuthAdapter(**data)
        res = helper.refresh()
        self.token_generated_date = timezone.now()
        self.access_token = res.get("access_token", None)
        self.refresh_token = res.get("refresh_token", None)
        self.save()


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

    def __str__(self):
        return f"Salesloft Account for {self.user.email}"

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return SalesloftAuthAdapter(**data)


class CadenceQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(owner__organization=user.organization_id)
        else:
            return self.none()


class CadenceAdapter:
    def __init__(self, **kwargs):
        self.cadence_id = kwargs.get("cadence_id", None)
        self.name = kwargs.get("name", None)
        self.owner = kwargs.get("owner", None)
        self.is_team_cadence = kwargs.get("is_team_cadence", None)
        self.is_shared = kwargs.get("is_shared", None)
        self.created_at = kwargs.get("created_at", None)
        self.updated_at = kwargs.get("updated_at", None)

    @property
    def as_dict(self):
        return vars(self)

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
            logger.info(f"{error_data}")
            error_check = error_data.get("error_param", None)
            error_param = error_check if error_check else error_data.get("errors")
            kwargs = {
                "status_code": status_code,
                "error_param": error_param,
            }

            SalesloftAPIException(HTTPError(kwargs), fn_name)
        return data

    @classmethod
    def create_cadence(cls, cadence_data):
        try:
            owner = cadence_data["owner"]
            slacc = SalesloftAccount.objects.get(salesloft_id=owner["id"])
            data = {}
            data["cadence_id"] = cadence_data["id"]
            data["name"] = cadence_data["name"]
            data["owner"] = slacc.id
            data["is_team_cadence"] = cadence_data["team_cadence"]
            data["is_shared"] = cadence_data["shared"]
            data["created_at"] = dateutil.parser.isoparse(cadence_data["created_at"])
            data["updated_at"] = dateutil.parser.isoparse(cadence_data["updated_at"])
            return cls(**data)
        except ObjectDoesNotExist:
            return None

    def add_membership(self, person_id, access_token):
        headers = salesloft_consts.SALESLOFT_REQUEST_HEADERS(access_token)
        query = urlencode({"person_id": person_id, "cadence_id": self.cadence_id})
        res = client.post(
            f"{salesloft_consts.SALESLOFT_BASE_URI}/{salesloft_consts.ADD_TO_CADENCE}?{query}",
            headers=headers,
        )
        return CadenceAdapter._handle_response(res)


class Cadence(TimeStampModel):
    cadence_id = models.IntegerField()
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        "SalesloftAccount",
        related_name="cadences",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    is_team_cadence = models.BooleanField()
    is_shared = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = CadenceQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Cadence {self.name} owned by {self.owner}"

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return CadenceAdapter(**data)

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.id))


class SLAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(owner__organization=user.organization_id)
        else:
            return self.none()


class SLAccountAdapter:
    def __init__(self, **kwargs):
        self.account_id = kwargs.get("account_id", None)
        self.name = kwargs.get("name", None)
        self.created_at = kwargs.get("created_at", None)
        self.updated_at = kwargs.get("updated_at", None)
        self.owner = kwargs.get("owner", None)

    @property
    def as_dict(self):
        return vars(self)

    @classmethod
    def create_slaccount(cls, account_data):
        try:
            owner = account_data["owner"]
            slacc = SalesloftAccount.objects.get(salesloft_id=owner["id"])
            data = {}
            data["account_id"] = account_data["id"]
            data["name"] = account_data["name"]
            data["owner"] = slacc.id
            data["created_at"] = dateutil.parser.isoparse(account_data["created_at"])
            data["updated_at"] = dateutil.parser.isoparse(account_data["updated_at"])
            return cls(**data)
        except ObjectDoesNotExist:
            return None


class SLAccount(TimeStampModel):
    account_id = models.IntegerField()
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    owner = models.ForeignKey(
        "SalesloftAccount",
        related_name="sl_accounts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    objects = SLAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"SLAccount {self.name} owned by {self.owner}"


class PeopleQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(owner__organization=user.organization_id)
        else:
            return self.none()


class PeopleAdapter:
    def __init__(self, **kwargs):
        self.people_id = kwargs.get("people_id", None)
        self.first_name = kwargs.get("first_name", None)
        self.last_name = kwargs.get("last_name", None)
        self.full_name = kwargs.get("full_name", None)
        self.email = kwargs.get("email", None)
        self.account = kwargs.get("account", None)
        self.owner = kwargs.get("owner", None)
        self.created_at = kwargs.get("created_at", None)
        self.updated_at = kwargs.get("updated_at", None)

    @property
    def as_dict(self):
        return vars(self)

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
            logger.info(f"{error_data}")
            error_check = error_data.get("error_param", None)
            error_param = error_check if error_check else error_data.get("errors")
            kwargs = {
                "status_code": status_code,
                "error_param": error_param,
            }

            SalesloftAPIException(HTTPError(kwargs), fn_name)
        return data

    @classmethod
    def create_people(cls, people_data):
        try:
            owner = people_data["owner"]
            account = people_data["account"]
            slacc_id = None
            acc_id = None
            if owner:
                slacc = SalesloftAccount.objects.get(salesloft_id=owner["id"])
                slacc_id = slacc.id
            if account:
                acc = SLAccount.objects.get(account_id=account["id"])
                acc_id = acc.id
            data = {}
            data["people_id"] = people_data["id"]
            data["first_name"] = people_data["first_name"]
            data["last_name"] = people_data["last_name"]
            data["full_name"] = people_data["display_name"]
            data["email"] = people_data["email_address"]
            data["owner"] = slacc_id
            data["account"] = acc_id
            data["created_at"] = dateutil.parser.isoparse(people_data["created_at"])
            data["updated_at"] = dateutil.parser.isoparse(people_data["updated_at"])
            return cls(**data)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def create_in_salesloft(access_token, data):
        headers = salesloft_consts.SALESLOFT_REQUEST_HEADERS(access_token)
        res = client.post(
            f"{salesloft_consts.SALESLOFT_BASE_URI}/{salesloft_consts.PEOPLE}",
            headers=headers,
            data=json.dumps(data),
        )
        return PeopleAdapter._handle_response(res)


class People(TimeStampModel):
    people_id = models.IntegerField()
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    account = models.ForeignKey(
        "SLAccount", related_name="people", on_delete=models.CASCADE, blank=True, null=True,
    )
    owner = models.ForeignKey(
        "SalesloftAccount", related_name="people", on_delete=models.SET_NULL, blank=True, null=True,
    )

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def as_slack_option(self):
        return block_builders.option(self.full_name, str(self.id))
