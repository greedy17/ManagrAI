import base64
import json
import requests

from urllib.parse import urlencode
from django.conf import settings

from requests.exceptions import HTTPError


from managr.utils.misc import get_site_url

if settings.USE_ZOOM:

    CLIENT_ID = settings.ZOOM_CLIENT_ID

    BASE_AUTH_URI = "https://zoom.us/oauth/"
    AUTHORIZATION_URI = "https://zoom.us/oauth/authorize"
    AUTHENTICATION_URI = "https://zoom.us/oauth/token"
    ZOOM_API_ENDPOINT = "https://api.zoom.us/v2"
    ZOOM_WEBHOOK_TOKEN = settings.ZOOM_WEBHOOK_TOKEN
    uri = get_site_url()
    # must be same as on zoom app
    REDIRECT_URI = settings.ZOOM_REDIRECT_URI

    if settings.IN_DEV:
        MEETING_WEBHOOK = "https://thinknimble.ngrok.io/api/zoom/webhooks/meetings/"
        TOKEN_REDIRECT_URI = "https://thinknimble.ngrok.io/api/zoom/webhooks/auth/"
        ZOOM_FRONTEND_REDIRECT = "http://localhost:8080/settings/zoom-integration"
    else:
        MEETING_WEBHOOK = f"{uri}api/zoom/webhooks/meetings/"
        TOKEN_REDIRECT_URI = f"{uri}api/zoom/webhooks/auth/"
        ZOOM_FRONTEND_REDIRECT = f"{uri}/settings/zoom-integration"

    AUTHORIZATION_QUERY_PARAMS = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    }
    AUTHENTICATION_QUERY_PARAMS = lambda x: {
        "grant_type": "authorization_code",
        "code": x,
        "redirect_uri": REDIRECT_URI,
    }
    REAUTHENTICATION_QUERY_PARAMS = lambda x: {
        "grant_type": "refresh_token",
        "refresh_token": x,
    }

    ZOOM_CLIENT_ID = settings.ZOOM_CLIENT_ID
    ZOOM_SECRET = settings.ZOOM_SECRET

    APP_BASIC_TOKEN = base64.b64encode(
        f"{ZOOM_CLIENT_ID}:{ZOOM_SECRET}".encode("ascii")
    ).decode("utf-8")

