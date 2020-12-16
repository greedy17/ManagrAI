import json
import requests
from urllib.parse import urlencode, quote_plus
from requests.exceptions import HTTPError
from datetime import datetime

from . import constants as zoom_model_consts
from .exceptions import ZoomAPIException


class ZoomMtg:
    def __init__(self, **kwargs):
        self.id = kwargs.get("meeting_managr_id", None)
        self.zoom_account = kwargs.get("zoom_account", None)
        self.account_id = kwargs.get("account_id", None)
        self.operator = kwargs.get("operator", None)
        self.meeting_id = kwargs.get("meeting_id", None)
        self.meeting_uuid = kwargs.get("meeting_uuid", None)
        self.host_id = kwargs.get("host_id", None)
        self.topic = kwargs.get("topic", None)
        self.type = kwargs.get("type", None)
        self.start_time = kwargs.get("start_time", None)
        self.end_time = kwargs.get("end_time", None)
        self.timezone = kwargs.get("timezone", None)
        self.duration = kwargs.get("duration", None)
        self.occurences = kwargs.get("occurences", None)
        self.operator_id = kwargs.get("operator_id", None)
        self.operation = kwargs.get("operation", None)
        self.participants = kwargs.get("participants", None)
        self.review = kwargs.get("review", None)
        self.participants_count = kwargs.get("participants_count", None)
        self.total_minutes = kwargs.get("total_minutes", None)

    @classmethod
    def from_webhook(cls, payload):
        obj = payload.pop("object", None)
        if obj:
            payload = {**payload, **obj}

        meeting_uuid = payload.pop("uuid", None)
        meeting_id = payload.pop("id", None)
        payload["meeting_uuid"] = meeting_uuid
        payload["meeting_id"] = meeting_id

        return cls(**payload)

    def get_past_meeting_participants(self, access_token):
        meeting_id_double_encoded = quote_plus(quote_plus(self.meeting_uuid))
        url = f"{zoom_model_consts.ZOOM_API_ENDPOINT}/past_meetings/{meeting_id_double_encoded}/participants"
        # TODO check if access_token is expired and refresh PB 11/20/20
        headers = dict(Authorization=(f"Bearer {access_token}"))
        r = requests.get(url, headers=headers)
        data = ZoomAcct._handle_response(r)
        self.participants = data.get("participants", None)
        return self

    @property
    def as_dict(self):
        return vars(self)


class ZoomAcct:
    def __init__(self, **kwargs):
        self.user = kwargs.get("user", None)
        self.zoom_id = kwargs.get("zoom_id", None)
        self.id = kwargs.get("id", None)
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.token_type = kwargs.get("token_type", None)
        self.first_name = kwargs.get("first_name", None)
        self.last_name = kwargs.get("last_name", None)
        self.email = kwargs.get("email", None)
        self.type = kwargs.get("type", None)
        self.role_name = kwargs.get("role_name", None)
        self.personal_meeting_url = kwargs.get("personal_meeting_url", None)
        self.timezone = kwargs.get("timezone", None)
        self.verified = kwargs.get("verified", None)
        self.dept = kwargs.get("dept", None)
        self.pic_url = kwargs.get("pic_url", None)
        self.pmi = kwargs.get("pmi", None)
        self.use_pmi = kwargs.get("use_pmi", None)
        self.host_key = kwargs.get("host_key", None)
        self.jid = kwargs.get("jid", None)
        self.account_id = kwargs.get("account_id", None)
        self.language = kwargs.get("language", None)
        self.phone_country = kwargs.get("phone_country", None)
        self.status = kwargs.get("status", None)
        self.token_generated_date = datetime.now()
        self.token_scope = kwargs.get("scope", None)

    def get_past_meeting(self, meeting_id):
        meeting_id_double_encoded = quote_plus(quote_plus(meeting_id))
        url = f"{zoom_model_consts.ZOOM_API_ENDPOINT}/past_meetings/{meeting_id_double_encoded}"
        # TODO check if access_token is expired and refresh PB 11/20/20
        headers = dict(Authorization=(f"Bearer {self.access_token}"))
        r = requests.get(url, headers=headers)
        data = ZoomAcct._handle_response(r)
        meeting_uuid = data.pop("uuid", None)
        meeting_id = data.pop("id", None)
        # Rename uuid and uid so that they fit the django model and are not confused with django id's
        data["meeting_uuid"] = meeting_uuid
        data["meeting_id"] = meeting_id
        data["zoom_account"] = str(self.id)
        return ZoomMtg(**data)

    @property
    def as_dict(self):
        return vars(self)

    def refresh_access_token(self):
        query = zoom_model_consts.REAUTHENTICATION_QUERY_PARAMS(self.refresh_token)
        query = urlencode(query)
        ## error handling here

        r = requests.post(
            f"{zoom_model_consts.AUTHENTICATION_URI}?{query}",
            headers=dict(Authorization=(f"Basic {zoom_model_consts.APP_BASIC_TOKEN}")),
        )
        return ZoomAcct._handle_response(r)

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError

        elif response.status_code == 200:
            try:
                data = response.json()
            except Exception as e:
                ZoomAPIException(e, fn_name)
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
                ZoomAPIException(e, fn_name)
        return data

    @staticmethod
    def get_authorization():
        query = urlencode(zoom_model_consts.AUTHORIZATION_QUERY_PARAMS)
        return f"{zoom_model_consts.AUTHORIZATION_URI}?{query}"

    @staticmethod
    def get_auth_token(code: str):
        query = zoom_model_consts.AUTHENTICATION_QUERY_PARAMS(code)
        query = urlencode(query)
        r = requests.post(
            f"{zoom_model_consts.AUTHENTICATION_URI}?{query}",
            headers=dict(Authorization=(f"Basic {zoom_model_consts.APP_BASIC_TOKEN}")),
        )

        return ZoomAcct._handle_response(r)

    @staticmethod
    def _get_user_data(token: str):

        r = requests.get(
            f"{zoom_model_consts.ZOOM_API_ENDPOINT}/users/me",
            headers=dict(Authorization=(f"Bearer {token}")),
        )
        return ZoomAcct._handle_response(r)

    @classmethod
    def create_account(cls, code: str, managr_user_id):
        auth_data = cls.get_auth_token(code)
        user_data = cls._get_user_data(auth_data["access_token"])
        data = {**auth_data, **user_data}
        data["user"] = str(managr_user_id)

        zoom_id = data.pop("id", None)
        data["zoom_id"] = zoom_id

        return cls(**data)

    def revoke(self):
        r = requests.post(
            f"{zoom_model_consts.BASE_AUTH_URI}revoke?token={self.access_token}",
            headers=dict(Authorization=(f"Basic {zoom_model_consts.APP_BASIC_TOKEN}")),
        )

        return ZoomAcct._handle_response(r)
