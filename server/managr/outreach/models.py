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
from .exceptions import OutreachAPIException, TokenExpired
from managr.organization.models import Organization

from managr.salesforce.adapter.models import ActivityAdapter

from managr.core import constants as core_consts
from . import constants as outreach_consts

from managr.slack.helpers import block_builders

logger = logging.getLogger("managr")

client = HttpClient().client


class OutreachAuthAdapter:
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
        query = urlencode(outreach_consts.AUTHORIZATION_QUERY_PARAMS)
        return f"{outreach_consts.AUTHORIZATION_URI}?{query}"

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError
        elif response.status_code == 200 or response.status_code == 201:
            try:
                data = response.json()
            except Exception as e:
                OutreachAPIException(e, fn_name)
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

            OutreachAPIException(HTTPError(kwargs), fn_name)
        return data

    @staticmethod
    def get_auth_token(code: str, context: str, scope: str):
        query = outreach_consts.AUTHENTICATION_QUERY_PARAMS(code, context, scope)
        query = urlencode(query)
        r = client.post(f"{outreach_consts.AUTHENTICATION_URI}?{query}",)
        return OutreachAuthAdapter._handle_response(r)

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
        query = urlencode({"include_paging_counts": True, "page": page})
        res = client.get(
            f"{outreach_consts.OUTREACH_BASE_URI}/{outreach_consts.USERS}?{query}", headers=headers
        )
        return OutreachAuthAdapter._handle_response(res)

    def get_sequences(self, page=1):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        query = urlencode({"include_paging_counts": True, "page": page})
        res = client.get(
            f"{outreach_consts.OUTREACH_BASE_URI}/{outreach_consts.CADENCES}?{query}",
            headers=headers,
        )
        return OutreachAuthAdapter._handle_response(res)

    def get_accounts(self, page=1):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        query = urlencode({"include_paging_counts": True, "page": page})
        res = client.get(
            f"{outreach_consts.OUTREACH_BASE_URI}/{outreach_consts.ACCOUNTS}?{query}",
            headers=headers,
        )
        return OutreachAuthAdapter._handle_response(res)

    def get_prospects(self, page=1):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        query = urlencode({"include_paging_counts": True, "page": page})
        res = client.get(
            f"{outreach_consts.OUTREACH_BASE_URI}/{outreach_consts.PEOPLE}?{query}",
            headers=headers,
        )
        return OutreachAuthAdapter._handle_response(res)

    def refresh(self):
        query = outreach_consts.REAUTHENTICATION_QUERY_PARAMS(self.refresh_token)
        query = urlencode(query)
        res = client.post(f"{outreach_consts.AUTHENTICATION_URI}?{query}")

        return OutreachAuthAdapter._handle_response(res)

    def revoke(self):
        outreach_account = OutreachAccount.objects.get(id=self.id)
        try:
            outreach_account.delete()
            return logger.info(f"Succefully deleted account {outreach_account}")
        except Exception as e:
            logger.exception(f"Failed to delete account {outreach_account},{e}")


class OutreachAuthAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(organization=user.organization)
        else:
            self.none()


class OutreachAuthAccount(TimeStampModel):
    organization = models.OneToOneField(
        "organization.Organization",
        related_name="outreach_auth_account",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_generated_date = models.DateTimeField(null=True, blank=True)
    admin = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="outreach_admin", blank=True, null=True
    )

    objects = OutreachAuthAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Auth account for {self.organization} owned by {self.admin.email}"

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return OutreachAuthAdapter(**data)

    def regenerate_token(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        helper = OutreachAuthAdapter(**data)
        res = helper.refresh()
        self.token_generated_date = timezone.now()
        self.access_token = res.get("access_token", None)
        self.refresh_token = res.get("refresh_token", None)
        self.save()


class OutreachAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(auth_account__organization=user.organization)
        else:
            return self.none()


class OutreachAccountAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.auth_account = kwargs.get("auth_account", None)
        self.user = kwargs.get("user", None)
        self.outreach_id = kwargs.get("outreach_id", None)
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
            data["outreach_id"] = user_data["id"]
            data["guid"] = user_data["guid"]
            data["is_active"] = user_data["active"]
            data["email"] = user_data["email"]
            data["team_id"] = team["id"]
            return cls(**data)
        except ObjectDoesNotExist:
            return None


class OutreachAccount(TimeStampModel):
    auth_account = models.ForeignKey(
        "OutreachAuthAccount",
        related_name="users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    user = models.OneToOneField(
        "core.User",
        on_delete=models.CASCADE,
        related_name="outreach_account",
        blank=True,
        null=True,
    )
    outreach_id = models.IntegerField()
    guid = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    email = models.EmailField()
    team_id = models.IntegerField(blank=True)

    objects = OutreachAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Outreach Account for {self.user.email}"

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return OutreachAuthAdapter(**data)


class SequenceQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(owner__organization=user.organization_id)
        else:
            return self.none()


class SequenceAdapter:
    def __init__(self, **kwargs):
        self.sequence_id = kwargs.get("sequence_id", None)
        self.name = kwargs.get("name", None)
        self.owner = kwargs.get("owner", None)
        self.is_team_sequence = kwargs.get("is_team_sequence", None)
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
                OutreachAPIException(e, fn_name)
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

            OutreachAPIException(HTTPError(kwargs), fn_name)
        return data

    @classmethod
    def create_sequence(cls, sequence_data):
        try:
            owner = sequence_data["owner"]
            slacc = OutreachAccount.objects.get(outreach_id=owner["id"])
            data = {}
            data["sequence_id"] = sequence_data["id"]
            data["name"] = sequence_data["name"]
            data["owner"] = slacc.id
            data["is_team_sequence"] = sequence_data["team_sequence"]
            data["is_shared"] = sequence_data["shared"]
            data["created_at"] = dateutil.parser.isoparse(sequence_data["created_at"])
            data["updated_at"] = dateutil.parser.isoparse(sequence_data["updated_at"])
            return cls(**data)
        except ObjectDoesNotExist:
            return None

    def add_membership(self, person_id, access_token):
        headers = outreach_consts.OUTREACH_REQUEST_HEADERS(access_token)
        query = urlencode({"person_id": person_id, "sequence_id": self.sequence_id})
        res = client.post(
            f"{outreach_consts.OUTREACH_BASE_URI}/{outreach_consts.ADD_TO_CADENCE}?{query}",
            headers=headers,
        )
        return SequenceAdapter._handle_response(res)


class Sequence(TimeStampModel):
    sequence_id = models.IntegerField()
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        "OutreachAccount",
        related_name="sequences",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    is_team_sequence = models.BooleanField()
    is_shared = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = SequenceQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Sequence {self.name} owned by {self.owner}"

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return SequenceAdapter(**data)

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
            slacc = OutreachAccount.objects.get(outreach_id=owner["id"])
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
        "OutreachAccount",
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


class ProspectQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(owner__organization=user.organization_id)
        else:
            return self.none()


class ProspectAdapter:
    def __init__(self, **kwargs):
        self.prospects_id = kwargs.get("prospects_id", None)
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
                OutreachAPIException(e, fn_name)
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

            OutreachAPIException(HTTPError(kwargs), fn_name)
        return data

    @classmethod
    def create_prospects(cls, prospects_data):
        try:
            owner = prospects_data["owner"]
            account = prospects_data["account"]
            slacc_id = None
            acc_id = None
            if owner:
                slacc = OutreachAccount.objects.get(outreach_id=owner["id"])
                slacc_id = slacc.id
            if account:
                acc = SLAccount.objects.get(account_id=account["id"])
                acc_id = acc.id
            data = {}
            data["prospects_id"] = prospects_data["id"]
            data["first_name"] = prospects_data["first_name"]
            data["last_name"] = prospects_data["last_name"]
            data["full_name"] = prospects_data["display_name"]
            data["email"] = prospects_data["email_address"]
            data["owner"] = slacc_id
            data["account"] = acc_id
            data["created_at"] = dateutil.parser.isoparse(prospects_data["created_at"])
            data["updated_at"] = dateutil.parser.isoparse(prospects_data["updated_at"])
            return cls(**data)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def create_in_outreach(access_token, data):
        headers = outreach_consts.OUTREACH_REQUEST_HEADERS(access_token)
        res = client.post(
            f"{outreach_consts.OUTREACH_BASE_URI}/{outreach_consts.PEOPLE}",
            headers=headers,
            data=json.dumps(data),
        )
        return ProspectAdapter._handle_response(res)


class Prospect(TimeStampModel):
    prospects_id = models.IntegerField()
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    account = models.ForeignKey(
        "SLAccount", related_name="prospects", on_delete=models.CASCADE, blank=True, null=True,
    )
    owner = models.ForeignKey(
        "OutreachAccount",
        related_name="prospects",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def as_slack_option(self):
        return block_builders.option(self.full_name, str(self.id))
