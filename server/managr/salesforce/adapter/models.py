import json
import pytz
import requests
from datetime import datetime
from urllib.parse import urlencode, quote_plus
from requests.exceptions import HTTPError

from managr.utils.client import HttpClient
from managr.organization import constants as org_consts

from .exceptions import CustomAPIException
from .. import constants as sf_consts

client = HttpClient().client


class SalesforceAuthAccountAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.signature = kwargs.get("signature", None)
        self.scope = kwargs.get("scope", None)
        self.id_token = kwargs.get("id_token", None)
        self.instance_url = kwargs.get("instance_url", None)
        self.salesforce_id = kwargs.get("salesforce_id", None)
        self.user = kwargs.get("user", None)

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError

        elif response.status_code == 200:
            try:
                data = response.json()
            except Exception as e:
                CustomAPIException(e, fn_name)
        else:
            try:
                error_code = response.status_code
                error_data = response.json()
                error_param = error_data.get("error", None)
                error_message = error_data.get("reason", None)
                kwargs = {
                    "error_code": error_code,
                    "error_param": error_param,
                    "error_message": error_message,
                }
                raise HTTPError(kwargs)
            except HTTPError as e:
                CustomAPIException(e, fn_name)
        return data

    @classmethod
    def create_account(cls, code, user_id):
        res = cls.authenticate(code)
        data = cls.from_api(res, user_id)

        return data

    @staticmethod
    def from_api(data, user_id=None):
        salesforce_id = data.pop("id", None)
        data["salesforce_id"] = salesforce_id
        data["user"] = user_id
        return SalesforceAuthAccountAdapter(**data)

    @staticmethod
    def generate_auth_link():
        return f"{sf_consts.AUTHORIZATION_URI}?{sf_consts.AUTHORIZATION_QUERY}"

    @staticmethod
    def authenticate(code):
        data = sf_consts.AUTHENTICATION_BODY(code)
        res = client.post(
            f"{sf_consts.AUTHENTICATION_URI}", data, headers=sf_consts.AUTHENTICATION_HEADERS,
        )

        return SalesforceAuthAccountAdapter._handle_response(res)

    def list_accounts(self, offset):
        url = f"{self.instance_url}{sf_consts.SALSFORCE_ACCOUNT_QUERY_URI}"
        if offset:
            url = f"{url} offset {offset}"
        res = client.get(url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),)

        return self._handle_response(res)

    def list_stages(self, offset):
        url = f"{self.instance_url}{sf_consts.SALSFORCE_STAGE_QUERY_URI}"
        if offset:
            url = f"{url} offset {offset}"
        res = client.get(url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),)

        return self._handle_response(res)

    def get_stage_count(self):
        res = client.get(
            f"{self.instance_url}{sf_consts.SALSFORCE_STAGE_QUERY_URI_COUNT}",
            headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
        )

        return self._handle_response(res)

    def get_account_count(self):
        res = client.get(
            f"{self.instance_url}{sf_consts.SALSFORCE_ACCOUNT_QUERY_URI_COUNT}",
            headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
        )

        return self._handle_response(res)

    def revoke(self):
        # if a token is already expired a 400 error occurs we can ignore that
        client.post(sf_consts.REVOKE_URI, {"token": self.access_token})
        client.post(sf_consts.REVOKE_URI, {"token": self.refresh_token})

    @property
    def as_dict(self):
        return vars(self)


class AccountAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.integration_id = kwargs.get("integration_id", None)
        self.integration_source = kwargs.get("integration_source", None)
        self.name = kwargs.get("name", None)
        self.url = kwargs.get("url", None)
        self.type = kwargs.get("type", None)
        self.organization = kwargs.get("organization", None)
        self.logo = kwargs.get("logo", None)
        self.parent = kwargs.get("parent", None)
        self.parent_integration_id = kwargs.get("parent_integration_id", None)

    @staticmethod
    def from_api(data, organization_id, mapping):
        formatted_data = dict()
        formatted_data["integration_id"] = data.get("Id", "") if data.get("Id", "") else ""
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_SALESFORCE
        formatted_data["name"] = data.get("Name", "") if data.get("Name", "") else ""
        formatted_data["url"] = data.get("Website", "") if data.get("Website", "") else ""
        formatted_data["type"] = data.get("Type", "") if data.get("Type", "") else ""
        formatted_data["logo"] = data.get("PhotoUrl", "") if data.get("PhotoUrl", "") else ""
        formatted_data["parent_integration_id"] = (
            data.get("ParentId", "") if data.get("ParentId", "") else ""
        )
        formatted_data["organization"] = str(organization_id)

        return AccountAdapter(**formatted_data)

    @property
    def as_dict(self):
        return vars(self)


class StageAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.label = kwargs.get("integration_id", None)
        self.integration_source = kwargs.get("integration_source", None)
        self.label = kwargs.get("label", None)
        self.value = kwargs.get("value", None)
        self.is_closed = kwargs.get("is_closed", None)
        self.is_won = kwargs.get("is_won", None)
        self.description = kwargs.get("description", None)
        self.organization = kwargs.get("organization", None)

    @staticmethod
    def from_api(data, organization_id, mapping):
        formatted_data = dict()
        formatted_data["integration_id"] = data.get("Id", "") if data.get("Id", "") else ""
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_SALESFORCE
        formatted_data["label"] = data.get("MasterLabel", "") if data.get("MasterLabel", "") else ""
        formatted_data["value"] = data.get("ApiName", "") if data.get("ApiName", "") else ""
        formatted_data["is_closed"] = data.get("IsClosed", "") if data.get("IsClosed", "") else ""
        formatted_data["is_won"] = data.get("IsWon", "") if data.get("IsWon", "") else ""
        formatted_data["description"] = data.get("Description") if data.get("Description") else ""
        formatted_data["organization"] = str(organization_id)
        return StageAdapter(**formatted_data)

    @property
    def as_dict(self):
        return vars(self)


class OpportunityAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)

    @staticmethod
    def from_api(data, mapping=None, user_id=None):
        ## for version 1 mapping is always the same in future Org's will have custom mappings
        return

    @property
    def as_dict(self):
        return vars(self)
