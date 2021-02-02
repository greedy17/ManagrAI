from django.conf import settings
from urllib.parse import urlencode


BASE_URL = settings.SALESFORCE_BASE_URL
SF_API_VERSION = settings.SALESFORCE_API_VERSION

AUTHORIZATION_URI = f"{BASE_URL}/services/oauth2/authorize"
AUTHENTICATION_URI = f"{BASE_URL}/services/oauth2/token"
REVOKE_URI = f"{BASE_URL}/services/oauth2/revoke"
REFRESH_URI = f"{BASE_URL}/services/oauth2/token"
CLIENT_ID = settings.SALESFORCE_CONSUMER_KEY
CLIENT_SECRET = settings.SALESFORCE_SECRET
SCOPES = settings.SALESFORCE_SCOPES
REDIRECT_URL = settings.SALESFORCE_REDIRECT_URL

AUTHENTICATION_BODY = lambda code: {
    "grant_type": "authorization_code",
    "Content-type": "application/x-www-form-urlencoded",
    "code": code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URL,
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
        "redirect_uri": REDIRECT_URL,
        "response_type": "code",
        "scope": SCOPES,
        "state": "SALESFORCE",
    }
)

# temporary mapping for fields (in future each org will have their own mappings)
MAPPING_FROM_API = (
    ("ID", "id"),
    ("TITLE", "id"),
    ("AMOUNT", "id"),
    ("FORECAST_CATEGORY", "id"),
    ("EXPECTED_CLOSE_DATE", "id"),
    ("PRIMARY_DESCRIPTION", "id"),
    ("NEXT_STEP", "id"),
)


RESOURCE_SYNC_ACCOUNT = "ACCOUNT"
RESOURCE_SYNC_OPPORTUNITY = "OPPORTUNITY"
RESOURCE_SYNC_STAGE = "STAGE"

SALESFORCE_RESOURCE_SYNC_QUEUE = "SALESFORCE_RESOURCE_SYNC"

SALESFORCE_QUERY_LIMIT = 100

SALESFORCE_USER_REQUEST_HEADERS = lambda token: dict(Authorization=f"Bearer {token}")
SALSFORCE_ACCOUNT_QUERY_URI = f"/services/data/{SF_API_VERSION}/query/?q=SELECT Id, Name, Type, ParentId, Website, PhotoUrl from Account order by CreatedDate limit {SALESFORCE_QUERY_LIMIT}"
SALSFORCE_STAGE_QUERY_URI = f"/services/data/{SF_API_VERSION}/query/?q=SELECT id, MasterLabel, ForecastCategory, ApiName, IsActive, SortOrder, IsClosed, IsWon, Description from OpportunityStage order by CreatedDate limit {SALESFORCE_QUERY_LIMIT}"
SALSFORCE_OPP_QUERY_URI = f"/services/data/{SF_API_VERSION}/query/?q=SELECT Id, AccountId, Name, Description, StageName, Amount, CloseDate, Type, NextStep, LeadSource, ForecastCategory, OwnerId, LastActivityDate, (SELECT Contact.Id, Contact.FirstName, Contact.LastName,  Contact.Email, Contact.MobilePhone, Contact.Phone, Contact.Title FROM OpportunityContactRoles), (SELECT CreatedDate FROM OpportunityHistories limit 1) FROM Opportunity order by CreatedDate limit {SALESFORCE_QUERY_LIMIT}"


SALSFORCE_ACCOUNT_QUERY_URI_COUNT = (
    f"/services/data/{SF_API_VERSION}/query/?q=SELECT COUNT () from Account"
)
SALSFORCE_STAGE_QUERY_URI_COUNT = (
    f"/services/data/{SF_API_VERSION}/query/?q=SELECT COUNT () from OpportunityStage"
)
SALSFORCE_OPP_QUERY_URI_COUNT = (
    f"/services/data/{SF_API_VERSION}/query/?q=SELECT COUNT () from Opportunity"
)

SALESFORCE_JSON_HEADER = {"Content-Type": "application/json"}
SALESFORCE_BEARER_AUTH_HEADER = lambda x: dict(Authorization=f"Bearer {x}")
"""
u = custom uri
r = resource 
k = resource id

"""
SALESFORCE_WRITE_URI = lambda u, r, k: f"{u}/services/data/{SF_API_VERSION}/sobjects/{r}/{k}"

SALESFORCE_RESOURCE_OPPORTUNITY = "Opportunity"
SALESFORCE_RESOURCE_OPPORTUNITY_CONTACT_ROLE = "OpportunityContactRole"
SALESFORCE_RESOURCE_CONTACT = "Contact"
SALESFORCE_RESOURCE_TASK = "Task"

SALESFORCE_CONTACT_VIEW_URI = lambda u, k: f"{u}/lightning/r/Contact/{k}/view"

