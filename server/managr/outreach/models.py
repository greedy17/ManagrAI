from django.db.models.fields.related import ForeignKey
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

from . import constants as outreach_consts

from managr.slack.helpers import block_builders

logger = logging.getLogger("managr")

client = HttpClient().client


class OutreachAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(auth_account__organization=user.organization)
        else:
            return self.none()


class OutreachAccountAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.outreach_id = kwargs.get("outreach_id", None)
        self.user = kwargs.get("user", None)
        self.mailbox = kwargs.get("mailbox", None)
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.token_generated_date = kwargs.get("token_generated_date", None)

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
            error_param = error_data.get("title", None)
            kwargs = {
                "status_code": status_code,
                "error_param": error_param,
            }

            OutreachAPIException(HTTPError(kwargs), fn_name)
        return data

    @staticmethod
    def get_authorization():
        query = urlencode(outreach_consts.AUTHORIZATION_QUERY_PARAMS)
        return f"{outreach_consts.AUTHORIZATION_URI}?{query}"

    @staticmethod
    def get_auth_token(code: str):
        query = outreach_consts.AUTHENTICATION_QUERY_PARAMS(code)
        query = urlencode(query)
        r = client.post(f"{outreach_consts.AUTHENTICATION_URI}?{query}",)
        return OutreachAccountAdapter._handle_response(r)

    def refresh(self):
        query = outreach_consts.REAUTHENTICATION_QUERY_PARAMS(self.refresh_token)
        query = urlencode(query)
        res = client.post(f"{outreach_consts.AUTHENTICATION_URI}?{query}")

        return OutreachAccountAdapter._handle_response(res)

    def revoke(self):
        outreach_account = OutreachAccount.objects.get(id=self.id)
        try:
            outreach_account.delete()
            return logger.info(f"Succefully deleted account {outreach_account}")
        except Exception as e:
            logger.exception(f"Failed to delete account {outreach_account},{e}")

    @classmethod
    def get_basic_user(cls, access_token):
        headers = outreach_consts.OUTREACH_REQUEST_HEADERS(access_token)
        res = client.get(f"{outreach_consts.OUTREACH_BASE_URI}", headers=headers)
        return OutreachAccountAdapter._handle_response(res)

    @classmethod
    def get_mailbox(cls, access_token, user_id):
        headers = outreach_consts.OUTREACH_REQUEST_HEADERS(access_token)
        query = urlencode({"filter[user][id]": user_id})
        res = client.get(f"{outreach_consts.OUTREACH_BASE_URI}/mailboxes?{query}", headers=headers,)
        return OutreachAccountAdapter._handle_response(res)

    @classmethod
    def create_account(cls, code, managr_user_id):
        user = User.objects.get(id=managr_user_id)
        try:
            auth_data = cls.get_auth_token(code)
            user_data = cls.get_basic_user(auth_data["access_token"])
            mailbox = cls.get_mailbox(auth_data["access_token"], user_data["meta"]["user"]["id"])
            data = {}
            data["outreach_id"] = user_data["meta"]["user"]["id"]
            data["user"] = user.id
            data["mailbox"] = mailbox["data"][0]["id"]
            data["access_token"] = auth_data["access_token"]
            data["refresh_token"] = auth_data["refresh_token"]
            data["token_generated_date"] = datetime.now()
            return cls(**data)
        except ObjectDoesNotExist:
            return None

    def get_sequences(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        query = urlencode({"filter[owner][id]": self.outreach_id})
        res = client.get(f"{outreach_consts.OUTREACH_BASE_URI}/sequences?{query}", headers=headers,)
        return OutreachAccountAdapter._handle_response(res)

    def get_accounts(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        query = urlencode({"filter[owner][id]": self.outreach_id, "page[limit]": 250})
        res = client.get(f"{outreach_consts.OUTREACH_BASE_URI}/accounts?{query}", headers=headers,)
        return OutreachAccountAdapter._handle_response(res)

    def get_prospects(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        query = urlencode(
            {"filter[owner][id]": self.outreach_id, "page[limit]": 250, "sort": "-updatedAt"}
        )
        res = client.get(f"{outreach_consts.OUTREACH_BASE_URI}/prospects?{query}", headers=headers,)
        return OutreachAccountAdapter._handle_response(res)


class OutreachAccount(TimeStampModel):
    user = models.OneToOneField(
        "core.User",
        on_delete=models.CASCADE,
        related_name="outreach_account",
        blank=True,
        null=True,
    )
    outreach_id = models.IntegerField()
    mailbox = models.IntegerField(null=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_generated_date = models.DateTimeField(null=True, blank=True)

    objects = OutreachAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Outreach Account for {self.user.email}"

    @property
    def as_dict(self):
        return vars(self)

    @property
    def helper_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return OutreachAccountAdapter(**data)

    def regenerate_token(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        helper = OutreachAccountAdapter(**data)
        res = helper.refresh()
        self.token_generated_date = timezone.now()
        self.access_token = res.get("access_token", None)
        self.refresh_token = res.get("refresh_token", None)
        self.save()


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
            owner = sequence_data["relationships"]["owner"]["data"]["id"]
            outreach_account = OutreachAccount.objects.get(outreach_id=owner)
            data = {}
            data["sequence_id"] = sequence_data["id"]
            data["name"] = sequence_data["attributes"]["name"]
            data["owner"] = outreach_account.id
            data["created_at"] = dateutil.parser.isoparse(sequence_data["attributes"]["createdAt"])
            data["updated_at"] = dateutil.parser.isoparse(sequence_data["attributes"]["updatedAt"])
            return cls(**data)
        except ObjectDoesNotExist:
            return None

    def add_membership(self, person_id, access_token):
        headers = outreach_consts.OUTREACH_REQUEST_HEADERS(access_token)
        query = urlencode({"prospect_id": person_id, "sequence_id": self.sequence_id})
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


class AccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(owner__organization=user.organization_id)
        else:
            return self.none()


class AccountAdapter:
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
    def create_account(cls, account_data):
        try:
            owner = account_data["relationships"]["owner"]["data"]["id"]
            outreach_account = OutreachAccount.objects.get(outreach_id=owner)
            data = {}
            data["account_id"] = account_data["id"]
            data["name"] = account_data["attributes"]["name"]
            data["owner"] = outreach_account.id
            data["created_at"] = dateutil.parser.isoparse(account_data["attributes"]["createdAt"])
            data["updated_at"] = dateutil.parser.isoparse(account_data["attributes"]["updatedAt"])
            return cls(**data)
        except ObjectDoesNotExist:
            return None


class Account(TimeStampModel):
    account_id = models.IntegerField()
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    owner = models.ForeignKey(
        "OutreachAccount",
        related_name="outreach_accounts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    objects = AccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Account {self.name} owned by {self.owner}"


class ProspectQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(owner__organization=user.organization_id)
        else:
            return self.none()


class ProspectAdapter:
    def __init__(self, **kwargs):
        self.prospect_id = kwargs.get("prospect_id", None)
        self.full_name = kwargs.get("full_name", None)
        self.email = kwargs.get("email", None)
        self.account = kwargs.get("account", None)
        self.contact_id = kwargs.get("contact_id", None)
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
    def create_prospect(cls, prospects_data, contact_id, email):
        try:
            owner = prospects_data["relationships"]["owner"]["data"]["id"]
            account = prospects_data["relationships"]["account"]["data"]["id"]
            owner_id = OutreachAccount.objects.filter(outreach_id=owner).first()
            account_id = Account.objects.filter(account_id=account).first()
            data = {}
            data["prospect_id"] = prospects_data["id"]
            data["full_name"] = prospects_data["attributes"]["name"]
            data["email"] = email
            data["owner"] = owner_id.id
            data["contact_id"] = contact_id
            data["account"] = account_id.id if account_id else None
            data["created_at"] = dateutil.parser.isoparse(prospects_data["attributes"]["createdAt"])
            data["updated_at"] = dateutil.parser.isoparse(prospects_data["attributes"]["updatedAt"])
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
    prospect_id = models.IntegerField()
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    contact_id = models.ForeignKey(
        "organization.Contact", on_delete=models.SET_NULL, related_name="prospect", null=True
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    account = models.ForeignKey(
        "Account", related_name="prospects", on_delete=models.CASCADE, blank=True, null=True,
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
