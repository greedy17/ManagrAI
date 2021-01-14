from django.conf import settings
from urllib.parse import urlencode

if settings.USE_SALESFORCE:
    BASE_URL=settings.SALESFORCE_BASE_URL

    AUTHORIZATION_URI=f"{BASE_URL}/services/oauth2/authorize"
    AUTHENTICATION_URI=f'{BASE_URL}/services/oauth2/token'
    CLIENT_ID = settings.SALESFORCE_CONSUMER_KEY
    CLIENT_SECRET = settings.SALESFORCE_SECRET
    SCOPES = settings.SALESFORCE_SCOPES
    REDIRECT_URL=settings.SALESFORCE_REDIRECT_URL

    AUTHENTICATION_BODY=lambda code: {
        'grant_type':'authorization_code',
        'Content-type':'application/x-www-form-urlencoded',
        'code':code, 
        'client_id':CLIENT_ID,
        'client_secret':CLIENT_SECRET,
        'redirect_uri':REDIRECT_URL,
    }
    AUTHENTICATION_HEADERS={
        "Content-Type":"application/x-www-form-urlencoded"
    }
    AUTHORIZATION_QUERY=urleoncode{
        "client_id":CLIENT_ID,
        "client_secret":CLIENT_SECRET,
        "redirect_uri":REDIRECT_URL,
        "response_type":"code",
        "scope":SCOPES
    }