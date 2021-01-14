import json
import pytz
import requests
from datetime import datetime
from urllib.parse import urlencode, quote_plus
from requests.exceptions import HTTPError

from managr.utils.client import HttpClient
from .. import constants as sf_consts

client = HttpClient().client


class SalesforceAuthAccountAdapter:
    def __init__(self, **kwargs):
        self.id = self.kwargs.get("id", None)
        self.access_token = self.kwargs.get("access_token", None)
        self.refresh_token = self.kwargs.get("refresh_token", None)
        self.signature = self.kwargs.get("signature", None)
        self.scope = self.kwargs.get("scope", None)
        self.id_token = self.kwargs.get("id_token", None)
        self.instance_url = self.kwargs.get("instance_url", None)
        self.salesforce_id = self.kwargs.get("salesforce_id", None)
        self.user = self.kwargs.get("user", None)

    @classmethod
    def create_account(cls, code, user_id):
        res = cls.authenticate(code)
        data = cls.from_api(res, user_id)

        return cls(**data)

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
            f"{sf_consts.AUTHENITCATION_URI}",
            data,
            headers=sf_consts.AUTHENTICATION_HEADERS,
        )

        return res

