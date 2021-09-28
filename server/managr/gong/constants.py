import base64
import json
import requests

from urllib.parse import urlencode
from django.conf import settings

from requests.exceptions import HTTPError

from managr.utils.misc import get_site_url

USERS = "users"
USERS_SCOPE = "api:users:read"
CALLS_SCOPE = "api:calls:read:extensive"
GONG_SCOPES = [USERS_SCOPE, CALLS_SCOPE]
SCOPES_STRING = " ".join(GONG_SCOPES)

if settings.USE_GONG:

    CLIENT_ID = settings.GONG_CLIENT_ID
    REDIRECT_URI = settings.GONG_REDIRECT_URI
    CLIENT_SECRET = settings.GONG_SECRET
    GONG_BASE_URI = settings.GONG_BASE_URL

    AUTHENTICATION_URI = "https://app.gong.io/oauth2/generate-token"
    AUTHORIZATION_URI = "https://app.gong.io/oauth2/authorize"

    if settings.IN_DEV:
        GONG_FRONTEND_REDIRECT = "http://localhost:8080/settings/integrations"
    elif settings.IN_STAGING:
        GONG_FRONTEND_REDIRECT = "https://staging.managr.ai/settings/integrations"
    else:
        GONG_FRONTEND_REDIRECT = "https://app.managr.ai/settings/integrations"

    AUTHORIZATION_QUERY_PARAMS = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES_STRING,
        "state": "GONG",
    }

    AUTHENTICATION_QUERY_PARAMS = lambda code: {
        "client_id": CLIENT_ID,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    REFRESH_QUERY_PARAMS = lambda token: {
        "grant_type": "refresh_token",
        "refresh_token": token,
    }

    GONG_BASIC_TOKEN = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("ascii")).decode(
        "utf-8"
    )

