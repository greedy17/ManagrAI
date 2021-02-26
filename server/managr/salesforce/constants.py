from django.conf import settings
from urllib.parse import urlencode


SF_API_VERSION = settings.SALESFORCE_API_VERSION

# SF COMMON URIS - Mostly Used for Auth

BASE_URL = settings.SALESFORCE_BASE_URL
AUTHORIZATION_URI = f"{BASE_URL}/services/oauth2/authorize"
AUTHENTICATION_URI = f"{BASE_URL}/services/oauth2/token"
REVOKE_URI = f"{BASE_URL}/services/oauth2/revoke"
REFRESH_URI = f"{BASE_URL}/services/oauth2/token"

# SF CUSTOM URIS - Used to retrieve data

CUSTOM_BASE_URI = f"/services/data/{SF_API_VERSION}"
SALESFORCE_QUERY_LIMIT = 500
SALESFORCE_FIELDS_URI = lambda resource: f"{CUSTOM_BASE_URI}/ui-api/object-info/{resource}"
SALESFORCE_PICKLIST_URI = (
    lambda resource_uri, record_type_id: f"{resource_uri}/picklist-values/{record_type_id}"
)


# SF CUSTOM URI QUERIES
def SALSFORCE_RESOURCE_QUERY_URI(
    owner_id,
    resource,
    fields,
    childRelationshipFields=[],
    additional_filters=[],
    limit=SALESFORCE_QUERY_LIMIT,
):
    url = f"{CUSTOM_BASE_URI}/query/?q=SELECT {','.join(fields)}"
    if len(childRelationshipFields):
        for rel, v in childRelationshipFields.items():
            url += f", (SELECT {','.join(v['fields'])} FROM {rel} {' '.join(v['attrs'])})"
    url = f"{url} FROM {resource} WHERE OwnerId = '{owner_id}'"
    if len(additional_filters):
        for f in additional_filters:
            url = f"{url} {f} "

    return f"{url} order by CreatedDate limit {limit}"


def SF_COUNT_URI(resource, owner_id):
    url = f"{CUSTOM_BASE_URI}/query/?q=SELECT COUNT () from {resource}"
    if owner_id:
        url = f"{url} WHERE OwnerId = '{owner_id}'"
    return url


SALESFORCE_VALIDATION_QUERY = (
    lambda resource: f"{CUSTOM_BASE_URI}/tooling/query/?q=Select Id,Active,Description,ErrorMessage From ValidationRule where EntityDefinition.DeveloperName = '{resource}' AND Active = true"
)

# SF HEADERS
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
SALESFORCE_JSON_HEADER = {"Content-Type": "application/json"}
SALESFORCE_BEARER_AUTH_HEADER = lambda x: dict(Authorization=f"Bearer {x}")


RESOURCE_SYNC_ACCOUNT = "Account"
RESOURCE_SYNC_OPPORTUNITY = "Opportunity"
RESOURCE_SYNC_CONTACT = "Contact"
SALESFORCE_RESOURCE_TASK = "Task"

SALESFORCE_OBJECT_FIELDS = "OBJECT_FIELDS"
SALESFORCE_PICKLIST_VALUES = "PICKLIST_VALUES"
SALESFORCE_VALIDATIONS = "VALIDATIONS"

SALESFORCE_RESOURCE_SYNC_QUEUE = "SALESFORCE_RESOURCE_SYNC"


SALESFORCE_USER_REQUEST_HEADERS = lambda token: dict(Authorization=f"Bearer {token}")


OPPORTUNITY_CONTACT_ROLE_FIELDS = [
    # if a user has access to the contactrole we can assume they have access
    # to the id field (and most likely the role field, and contactid field)
    "Id",
    "Role",
    "ContactId",
]

OPPORTUNITY_HISTORY_FIELDS = ["Id", "CreatedDate"]
OPPORTUNITY_HISTORY_ATTRS = ["LIMIT 1"]


OPPORTUNITY_CONTACT_ROLES = "OpportunityContactRoles"
OPPORTUNITY_HISTORIES = "OpportunityHistories"
OPP_CHILD_RELATIONSHIPS = [
    # Users have access to different fields
    # we are looking for these to add as a subquery
    # if they exist we can use them
    OPPORTUNITY_CONTACT_ROLES,
    OPPORTUNITY_HISTORIES,  # last stage update comes from this object
]


STANDARD_CONTACT_FIELDS = [
    # standard fields that we save as part of our db's rather than metadata
    "Id",
    "Email",
]
STANDARD_OPP_FIELDS = [
    # standard fields that we save as part of our db's rather than metadata
    "Id",
    "Name",
    "Amount",
    "ForecastCategoryName",
    "AccountId",
    "LastActivityDate",
    "StageName",
    "CloseDate",
    "OwnerId",
]


STANDARD_ACCOUNT_FIELDS = ["Id", "Name", "Type", "ParentId", "Website", "PhotoUrl"]


"""
u = custom uri
r = resource 
k = resource id

"""
SALESFORCE_WRITE_URI = lambda u, r, k: f"{u}{CUSTOM_BASE_URI}/sobjects/{r}/{k}"


SALESFORCE_RESOURCE_OPPORTUNITY_CONTACT_ROLE = "OpportunityContactRole"

SALESFORCE_CONTACT_VIEW_URI = lambda u, k: f"{u}/lightning/r/Contact/{k}/view"

