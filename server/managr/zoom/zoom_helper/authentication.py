from rest_framework import authentication
from rest_framework import exceptions


from managr.zoom.zoom_helper import constants as zoom_helper_consts


class ZoomWebhookAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization", None)
        return token == zoom_helper_consts.ZOOM_WEBHOOK_TOKEN

