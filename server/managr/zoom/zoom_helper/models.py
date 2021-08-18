import logging
import json
from datetime import datetime
from urllib.parse import urlencode, quote_plus
from requests.exceptions import HTTPError

from django.utils import timezone

from managr.utils.client import HttpClient

from . import constants as zoom_model_consts
from .exceptions import ZoomAPIException

client = HttpClient().client
logger = logging.getLogger("managr")


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
        self.original_duration = kwargs.get("original_duration", None)

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
        r = client.get(url, headers=headers)
        data = ZoomAcct._handle_response(r)
        self.participants = data.get("participants", None)
        return self

    @property
    def as_dict(self):
        return vars(self)

    @property
    def start_time_timestamp(self):
        return int(timezone.datetime.fromisoformat(self.start_time.replace("Z", "")).timestamp())

    @property
    def end_time_timestamp(self):
        return int(timezone.datetime.fromisoformat(self.end_time.replace("Z", "")).timestamp())


class ZoomAcct:
    def __init__(self, **kwargs):
        self.user = kwargs.get("user", None)
        self.zoom_id = kwargs.get("zoom_id", None)
        self.id = kwargs.get("id", None)
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.token_type = kwargs.get("token_type", None)
        self.email = kwargs.get("email", None)
        self.type = kwargs.get("type", None)
        self.role_name = kwargs.get("role_name", None)
        self.timezone = kwargs.get("timezone", None)
        self.host_key = kwargs.get("host_key", None)

        self.account_id = kwargs.get("account_id", None)
        self.language = kwargs.get("language", None)

        self.status = kwargs.get("status", None)
        self.token_generated_date = datetime.now()
        self.token_scope = kwargs.get("scope", None)

    def get_past_meeting(self, meeting_id):
        meeting_id_double_encoded = quote_plus(quote_plus(meeting_id))
        url = f"{zoom_model_consts.ZOOM_API_ENDPOINT}/past_meetings/{meeting_id_double_encoded}"
        # TODO check if access_token is expired and refresh PB 11/20/20
        headers = dict(Authorization=(f"Bearer {self.access_token}"))
        r = client.get(url, headers=headers)
        data = ZoomAcct._handle_response(r)
        meeting_uuid = data.pop("uuid", None)
        meeting_id = data.pop("id", None)
        # Rename uuid and uid so that they fit the django model and are not confused with django id's
        data["meeting_uuid"] = meeting_uuid
        data["meeting_id"] = meeting_id
        data["zoom_account"] = str(self.id)
        return ZoomMtg(**data)

    def schedule_meeting(self, topic, date, time, duration):
        url = f"{zoom_model_consts.ZOOM_API_ENDPOINT}/users/{self.zoom_id}/meetings"
        headers = dict(Authorization=(f"Bearer {self.access_token}"))
        data = {
            "topic": f"{topic}",
            "type": 2,
            "start_time": f"{date}T{time}:00",
            "duration": f"{duration}",
        }
        r = client.post(url, json.dumps(data), headers=headers)
        response_data = self._handle_response(r)
        return response_data

    @property
    def as_dict(self):
        return vars(self)

    def refresh_access_token(self):
        query = zoom_model_consts.REAUTHENTICATION_QUERY_PARAMS(self.refresh_token)
        query = urlencode(query)
        ## error handling here

        r = client.post(
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

            ZoomAPIException(HTTPError(kwargs), fn_name)
        return data

    @staticmethod
    def get_authorization():
        query = urlencode(zoom_model_consts.AUTHORIZATION_QUERY_PARAMS)
        return f"{zoom_model_consts.AUTHORIZATION_URI}?{query}"

    @staticmethod
    def get_auth_token(code: str):
        query = zoom_model_consts.AUTHENTICATION_QUERY_PARAMS(code)
        query = urlencode(query)
        r = client.post(
            f"{zoom_model_consts.AUTHENTICATION_URI}?{query}",
            headers=dict(Authorization=(f"Basic {zoom_model_consts.APP_BASIC_TOKEN}")),
        )

        return ZoomAcct._handle_response(r)

    @staticmethod
    def _get_user_data(token: str):

        r = client.get(
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
        r = client.post(
            f"{zoom_model_consts.BASE_AUTH_URI}revoke?token={self.access_token}",
            headers=dict(Authorization=(f"Basic {zoom_model_consts.APP_BASIC_TOKEN}")),
        )

        return ZoomAcct._handle_response(r)

    @staticmethod
    def compliance_api(obj):
        """
        When app_deauth webhook is registered post data deletion to zoom compliance
        data = https://marketplace.zoom.us/docs/api-reference/data-compliance/data-compliance/compliance
        """
        headers = {
            "Authorization": f"Basic {zoom_model_consts.APP_BASIC_TOKEN}",
            "Cache-Control": "no-cache",
        }
        data = {
            "user_id": obj.get("user_id"),
            "client_id": obj.get("client_id"),
            "account_id": obj.get("account_id"),
            "deauthorization_event_received": obj,
            "compliance_completed": True,
        }
        r = client.post(
            f"{zoom_model_consts.ZOOM_COMPLIANCE_API}", json.dumps(data), headers=headers
        )
        logger.info(f"Compiance API: {r.json()}")

        return ZoomAcct._handle_response(r)
