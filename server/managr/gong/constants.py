import base64
import json
import requests

from urllib.parse import urlencode
from django.conf import settings

from requests.exceptions import HTTPError

from managr.utils.misc import get_site_url

GONG_SCOPES = []

if settings.USE_GONG:

    CLIENT_ID = settings.GONG_CLIENT_ID
    REDIRECT_URI = settings.GONG_REDIRECT_URI
    CLIENT_SECRET = settings.GONG_SECRET
    GONG_BASE_URI = settings.GONG_BASE_URL

    AUTHENTICATION_URI = "https://accounts.GONG.com/oauth/token"
    AUTHORIZATION_URI = "https://app.gong.io/oauth2/authorize"

    if settings.IN_DEV:
        GONG_FRONTEND_REDIRECT = "http://localhost:8080/settings/integrations"
    elif settings.IN_STAGING:
        GONG_FRONTEND_REDIRECT = "https://staging.managr.ai/settings/integrations"
    else:
        GONG_FRONTEND_REDIRECT = "https://app.managr.ai/settings/integrations"

    AUTHORIZATION_QUERY_PARAMS = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
    }
    AUTHENTICATION_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

    AUTHENTICATION_QUERY_PARAMS = lambda code, context, scope: {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "context": context,
        "scope": scope,
    }

    REAUTHENTICATION_QUERY_PARAMS = lambda token: {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": token,
    }

    GONG_REQUEST_HEADERS = lambda token: {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

