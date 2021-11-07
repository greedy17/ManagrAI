import base64
import json
import requests

from urllib.parse import urlencode
from django.conf import settings

from requests.exceptions import HTTPError


from managr.utils.misc import get_site_url

if settings.USE_OUTREACH:
    ALL_SCOPES = [
        "accounts.read",
        "prospects.read",
        "prospects.write",
        "sequenceStates.read",
        "sequenceStates.write",
        "sequenceSteps.read",
        "sequenceSteps.write",
        "sequences.read",
        "sequences.write",
        "stages.read",
        "stages.write",
        "users.read",
        "users.write",
    ]
    SCOPES = "+".join(ALL_SCOPES)
    CLIENT_ID = settings.OUTREACH_CLIENT_ID
    REDIRECT_URI = settings.OUTREACH_REDIRECT_URI
    CLIENT_SECRET = settings.OUTREACH_SECRET
    OUTREACH_BASE_URI = settings.OUTREACH_BASE_URL

    AUTHENTICATION_URI = "https://api.outreach.io/oauth/token"
    AUTHORIZATION_URI = "https://api.outreach.io/oauth/authorize"

    if settings.IN_DEV:
        OUTREACH_FRONTEND_REDIRECT = "http://localhost:8080/settings/integrations"
    elif settings.IN_STAGING:
        OUTREACH_FRONTEND_REDIRECT = "https://staging.managr.ai/settings/integrations"
    else:
        OUTREACH_FRONTEND_REDIRECT = "https://app.managr.ai/settings/integrations"

    AUTHORIZATION_QUERY_PARAMS = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
    }
    AUTHENTICATION_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

    AUTHENTICATION_QUERY_PARAMS = lambda code: {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    REAUTHENTICATION_QUERY_PARAMS = lambda token: {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": token,
    }

    OUTREACH_REQUEST_HEADERS = lambda token: {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

