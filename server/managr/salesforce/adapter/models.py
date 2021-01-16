import json
import pytz
import requests
from datetime import datetime
from urllib.parse import urlencode, quote_plus
from requests.exceptions import HTTPError

from managr.utils.client import HttpClient

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

    def revoke(self):
        # if a token is already expired a 400 error occurs we can ignore that
        client.post(sf_consts.REVOKE_URI, {"token": self.access_token})
        client.post(sf_consts.REVOKE_URI, {"token": self.refresh_token})

    @property
    def as_dict(self):
        return vars(self)
