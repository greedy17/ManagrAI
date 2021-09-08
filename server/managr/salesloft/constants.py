import base64
import json
import requests

from urllib.parse import urlencode
from django.conf import settings

from requests.exceptions import HTTPError


from managr.utils.misc import get_site_url

if settings.USE_SALESLOFT:

    CLIENT_ID = settings.SALESLOFT_CLIENT_ID
    REDIRECT_URI = settings.SALESLOFT_REDIRECT_URI
    CLIENT_SECRET = settings.SALESLOFT_SECRET

    AUTHENTICATION_URI = "https://accounts.salesloft.com/oauth/token"
    AUTHORIZATION_URI = "https://accounts.salesloft.com/oauth/authorize"
    SALESLOFT_BASE_URI = "https://api.salesloft.com/v2"
    if settings.IN_DEV:
        SALESLOFT_FRONTEND_REDIRECT = "http://localhost:8080/settings/integrations"

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
