from rest_framework import authentication
from rest_framework import exceptions

from managr.core.models import WebhookAuthUser
from managr.zoom.zoom_helper import constants as zoom_helper_consts


class ZoomWebhookAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization", None)
        if token != zoom_helper_consts.ZOOM_WEBHOOK_TOKEN:
            raise exceptions.AuthenticationFailed("Invalid token header")

        user = WebhookAuthUser()
        return user, None
