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
HUBSPOT_INSTANCE_URL = "https://app.hubspot.com/"

MEETING_REVIEW__UPDATE_RESOURCE = "MEETING_REVIEW_UPDATE_RESOURCE"
MEETING_REVIEW__CREATE_CONTACTS = "MEETING_REVIEW_CREATE_CONTACTS"
MEETING_REVIEW__UPDATE_CONTACTS = "MEETING_REVIEW_UPDATE_CONTACTS"
MEETING_REVIEW__SAVE_CALL_LOG = "MEETING_REVIEW_SAVE_CALL_LOG"
MEETING_REVIEW__ADD_PRODUCTS = "MEETING_REVIEW__ADD_PRODUCTS"

HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE = "HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE"

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
        "oauth",
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


def HUBSPOT_ASSOCIATIONS_CREATE_URI(associate_type, associate_id, to_object, to_object_id):
    return f"{BASE_URL}/crm/v4/objects/{associate_type}/{associate_id}/associations/{HUBSPOT_URL_RESOURCE_MAP[to_object]}/{to_object_id}"


def HUBSPOT_OBJECTS_URI(
    resource, fields, integration_id=None, limit=HUBSPOT_QUERY_LIMIT,
):
    fields = set(fields)
    url = f"{BASE_URL}/crm/v{HUBSPOT_API_VERSION}/objects/{resource}"
    if integration_id:
        url += f"/{integration_id}"
    url += f"?limit={limit}&properties={','.join(fields)}"
    return url


def HUBSPOT_OWNERS_URI(email=None):
    if email and len(email) > 0:
        return f"{BASE_URL}/crm/v3/owners?email={email}"
    return f"{BASE_URL}/crm/v3/owners"


def HUBSPOT_SEARCH_BODY(fields, filter_value, limit=25):
    fields = set(fields)
    return {
        "properties": list(fields),
        "filterGroups": [
            {
                "filters": [
                    {
                        "value": f"*{filter_value}*",
                        "propertyName": "name",
                        "operator": "CONTAINS_TOKEN",
                    }
                ]
            }
        ],
        "limit": limit,
    }


def HUBSPOT_PIPELINE_URI(resource):
    return f"{BASE_URL}/crm/v3/pipelines/{resource}"
