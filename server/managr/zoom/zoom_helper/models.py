import json
import requests
from urllib.parse import urlencode
from requests.exceptions import HTTPError

from managr.zoom.zoom_helper import constants as zoom_model_consts


class ZoomAcct:
    def __init__(self, managr_id, zoom_id, **kwargs):
        return

    def refresh_token(self):
        return

    @staticmethod
    def get_authorization():
        query = urlencode(zoom_model_consts.AUTHORIZATION_QUERY_PARAMS)
        return f"{zoom_model_consts.AUTHORIZATION_URI}?{query}"

    @classmethod
    def create_account(cls, code):
        query = zoom_model_consts.AUTHENTICATION_QUERY_PARAMS(code)
        query = urlencode(query)

        r = requests.post(
            f"{zoom_model_consts.AUTHENTICATION_URI}?{query}",
            headers=dict(Authorization=(f"Basic {zoom_model_consts.APP_BASIC_TOKEN}")),
        )
        data = r.json()

        return cls("test", "test")

