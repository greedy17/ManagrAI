from django.conf import settings


TOKEN_INFO_URI = "oauth/v1/access-tokens"
REFRESH_TOKEN_URI = "oauth/v1/token"

HUBSPOT_PROPERTIES_URI = "crm/v3/properties/"
RESOURCE_SYNC_COMPANY = "Company"
RESOURCE_SYNC_CONTACT = "Contact"
RESOURCE_SYNC_DEAL = "Deal"
HUBSPOT_URL_RESOURCE_MAP = {
    RESOURCE_SYNC_COMPANY: "companies",
    RESOURCE_SYNC_CONTACT: "contacts",
    RESOURCE_SYNC_DEAL: "deals",
}
HUBSPOT_API_VERSION = 3
HUBSPOT_OBJECT_FIELDS = "OBJECT_FIELDS"
HUBSPOT_FIELD_SYNC = "HUBSPOT_FIELD_SYNC"
HUBSPOT_RESOURCE_SYNC = "HUBSPOT_RESOURCE_SYNC"
HUBSPOT_FIELD_SYNC_QUEUE = "HUBSPOT_FIELD_SYNC"
HUBSPOT_RESOURCE_SYNC_QUEUE = "HUBSPOT_RESOURCE_SYNC"

HUBSPOT_QUERY_LIMIT = 100
if settings.USE_HUBSPOT:
    BASE_URL = settings.HUBSPOT_BASE_URL
    CLIENT_ID = settings.HUBSPOT_CLIENT_ID
    CLIENT_SECRET = settings.HUBSPOT_SECRET
    REDIRECT_URI = settings.HUBSPOT_REDIRECT_URI
    AUTHORIZATION_URI = "https://app.hubspot.com/oauth/authorize"
    AUTHENTICATION_URI = "https://api.hubapi.com/oauth/v1/token"

    if settings.IN_DEV:
        HUBSPOT_FRONTEND_REDIRECT = "http://localhost:8080/settings/integrations"
    elif settings.IN_STAGING:
        HUBSPOT_FRONTEND_REDIRECT = "https://staging.managr.ai/settings/integrations"
    else:
        HUBSPOT_FRONTEND_REDIRECT = "https://app.managr.ai/settings/integrations"
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
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "client_secret": CLIENT_SECRET,
    }
    AUTHENTICATION_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
    AUTHORIZATION_QUERY_PARAMS = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "scopes": URL_SCOPES,
        "state": "HUBSPOT",
    }

    HUBSPOT_REQUEST_HEADERS = lambda token: {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def HUBSPOT_PIPELINES_URI(pipeline_id):
    return f"{BASE_URL}/crm/v{HUBSPOT_API_VERSION}/pipelines/Deal/{pipeline_id}"


def HUBSPOT_RESOURCE_URI(resource):
    return f"{BASE_URL}/crm/v{HUBSPOT_API_VERSION}/objects/{resource}/"


def HUBSPOT_SEARCH_URI(resource):
    return (
        f"{BASE_URL}/crm/v{HUBSPOT_API_VERSION}/objects/{HUBSPOT_URL_RESOURCE_MAP[resource]}/search"
    )


def HUBSPOT_ASSOCIATIONS_READ_URI(resource, associated_resource):
    return f"{BASE_URL}/crm/v{HUBSPOT_API_VERSION}/associations/{HUBSPOT_URL_RESOURCE_MAP[resource]}/{HUBSPOT_URL_RESOURCE_MAP[associated_resource]}/batch/read"


def HUBSPOT_OBJECTS_URI(
    resource, fields, childRelationshipFields=[], additional_filters=[], limit=HUBSPOT_QUERY_LIMIT,
):
    fields = set(fields)
    url = f"{BASE_URL}/crm/v{HUBSPOT_API_VERSION}/objects/{resource}?limit={limit}&properties={','.join(fields)}"
    return url


def HUBSPOT_OWNERS_URI(email):
    return f"{BASE_URL}/crm/v3/owners?email={email}"


def HUBSPOT_SEARCH_BODY(fields, filters, limit):
    fields = set(fields)
    return {"properties": list(fields), "filters": filters, "limit": limit}


def HUBSPOT_PIPELINE_URI(resource):
    return f"{BASE_URL}/crm/v3/pipelines/{resource}"
