from django.conf import settings
from urllib.parse import urlencode

AUTHORIZATION_URI = "https://app.hubspot.com/oauth/authorize"
AUTHENTICATION_URI = "https://api.hubapi.com/oauth/v1/token"

if settings.USE_HUBSPOT:
    BASE_URL = settings.HUBSPOT_BASE_URL
    CLIENT_ID = settings.HUBSPOT_CLIENT_ID
    CLIENT_SECRET = settings.HUBSPOT_SECRET
    REDIRECT_URI = settings.HUBSPOT_REDIRECT_URI
    SCOPES = [
        "crm.objects.contacts.read",
        "crm.objects.contacts.write",
        "crm.objects.companies.write",
        "crm.schemas.contacts.read",
        "crm.objects.companies.read",
        "crm.objects.deals.read",
        "crm.objects.deals.write",
        "crm.schemas.companies.read",
        "crm.schemas.companies.write",
        "crm.schemas.contacts.write",
        "crm.schemas.deals.read",
        "crm.schemas.deals.write",
        "crm.objects.owners.read",
    ]
    URL_SCOPES = " ".join(SCOPES)
    AUTHENTICATION_BODY = lambda code: {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }
    REAUTHENTICATION_BODY = lambda refresh_token: {
        "grant_type": "refresh_token",
        "Content-type": "application/x-www-form-urlencoded",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    AUTHENTICATION_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
    AUTHORIZATION_QUERY = urlencode(
        {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "scopes": URL_SCOPES,
            "state": "HUBSPOT",
        }
    )

    HUBSPOT_REQUEST_HEADERS = lambda token: {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
