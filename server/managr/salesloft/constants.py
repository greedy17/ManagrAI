import base64
import json
import requests

from urllib.parse import urlencode
from django.conf import settings

from requests.exceptions import HTTPError


from managr.utils.misc import get_site_url

if settings.USE_SALESLOFT:

    CLIENT_ID = setting.SALESLOFT_CLIENT_ID
    REDIRECT_URI = setting.SALESLOFT_REDIRECT_URI

    AUTHENTICATION_URI = "https://accounts.salesloft.com/oauth/token"
    AUTHORIZATION_URI = "https://accounts.salesloft.com/oauth/authorize"

    AUTHORIZATION_QUERY_PARAMS = {
        "client_id": CLIENT_ID,
        "redirect_uri": RED,
        "response_type": "code",
    }

    AUTHENTICATION_QUERY_PARAMS = lambda code, context, scope: {
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "YOUR_REDIRECT_URI",
        "context": context,
        "scope": scope,
    }
