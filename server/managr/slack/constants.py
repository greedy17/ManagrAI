from django.conf import settings

SLACK_API_ROOT = "https://slack.com/api/"
SLACK_OAUTH_AUTHORIZE_ROOT = "https://slack.com/oauth/v2/authorize"

if settings.USE_SLACK:
    SLACK_SIGNING_SECRET = settings.SLACK_SIGNING_SECRET
    SLACK_APP_VERSION = settings.SLACK_APP_VERSION

# https://api.slack.com/methods/oauth.v2.access
OAUTH_V2_ACCESS = "oauth.v2.access"

# https://api.slack.com/methods/conversations.open
CONVERSATIONS_OPEN = "conversations.open"

# https://api.slack.com/methods/chat.postMessage
POST_MESSAGE = "chat.postMessage"

# https://api.slack.com/methods/views.open

VIEWS_OPEN = "views.open"

VIEWS_UPDATE = "views.update"

# https://api.slack.com/methods/chat.getPermalink
CHAT_GET_PERMALINK = "chat.getPermalink"

# https://api.slack.com/methods/chat.update
CHAT_UPDATE = "chat.update"

WORKSPACE_SCOPES = [
    "app_mentions:read",
    "channels:join",
    "channels:read",
    "chat:write",
    "chat:write.public",
    "commands",
    "im:history",
    "im:write",
    "incoming-webhook",
    "links:read",
    "links:write",
    "mpim:history",
    "mpim:read",
    "mpim:write",
    "team:read",
    "users:read",
    "users:read.email",
]

USER_SCOPES = ["identity.basic"]

# Link Types to determine which type of OAuth link to generate
WORKSPACE = "WORKSPACE"
USER = "USER"
OAUTH_LINK_TYPES = [WORKSPACE, USER]

TOKEN_TYPE_BOT = "bot"

# Interactive payload types
BLOCK_ACTIONS = "block_actions"
BLOCK_SUGGESTION = "block_suggestion"
VIEW_SUBMISSION = "view_submission"
VIEW_CLOSED = "view_closed"

#
ZOOM_MEETING__PROCESS_MEETING_SENTIMENT = "ZOOM_MEETING__PROCESS_MEETING_SENTIMENT"

# Action IDs of different interactive UI in the Managr Slack App
DEFAULT_ACTION_ID = "ACTION_ID"
ZOOM_MEETING__GREAT = "ZOOM_MEETING__GREAT"
ZOOM_MEETING__NOT_WELL = "ZOOM_MEETING__NOT_WELL"
ZOOM_MEETING__CANT_TELL = "ZOOM_MEETING__CANT_TELL"
ZOOM_MEETING__DIFFERENT_OPPORTUNITY = "ZOOM_MEETING__DIFFERENT_OPPORTUNITY"
GET_ORGANIZATION_STAGES = "GET_ORGANIZATION_STAGES"
GET_OPPORTUNITY_FORECASTS = "GET_OPPORTUNITY_FORECASTS"
GET_ORGANIZATION_ACTION_CHOICES = "GET_ORGANIZATION_ACTION_CHOICES"
GET_USER_OPPORTUNITIES = "GET_USER_OPPORTUNITIES"
SHOW_REMINDER_CONTACTS = "SHOW_REMINDER_CONTACTS"
SHOW_LEAD_CONTACTS = "SHOW_LEAD_CONTACTS"
SHOW_LEAD_LOGS = "SHOW_LEAD_LOGS"
SHOW_MEETING_SCORE_COMPONENTS = "SHOW_MEETING_SCORE_COMPONENTS"
SHOW_LEAD_SCORE_COMPONENTS = "SHOW_LEAD_SCORE_COMPONENTS"
ZOOM_MEETING__VIEW_MEETING_CONTACTS = "VIEW_MEETING_CONTACTS"
ZOOM_MEETING__EDIT_CONTACT = "EDIT_MEETING_CONTACT"
ZOOM_MEETING__UPDATE_CONTACT = "UPDATE_MEETING_CONTACT"
ZOOM_MEETING__REMOVE_CONTACT = "REMOVE_MEETING_CONTACT"
ZOOM_MEETING__UPDATE_FORECAST_SELECTION = "UPDATE_FORECAST_SELECTION"


## Customizable Slack forms exist for resources listed here and can only be one of each type

OPPORTUNITY_CREATE_FORM = "Opportunity.CREATE"
OPPORTUNITY_UPDATE_FORM = "Opportunity.UPDATE"
OPPORTUNITY_MEETING_REVIEW_FORM = "Opportunity.MEETING_REVIEW"
ACCOUNT_CREATE_FORM = "Account.CREATE"
ACCOUNT_UPDATE_FORM = "Account.UPDATE"
ACCOUNT_MEETING_REVIEW_FORM = "Account.MEETING_REVIEW"

FORM_RESOURCE_OPPORTUNITY = "Opportunity"
FORM_RESOURCE_ACCOUNT = "Account"

FORM_RESOURCES = (
    (FORM_RESOURCE_OPPORTUNITY, "Opportunity"),
    (FORM_RESOURCE_ACCOUNT, "Account"),
)

FORM_TYPE_CREATE = "CREATE"
FORM_TYPE_UPDATE = "UPDATE"
FORM_TYPE_MEETING_REVIEW = "MEETING_REVIEW"

INITIAL_FORMS = [
    OPPORTUNITY_CREATE_FORM,
    OPPORTUNITY_UPDATE_FORM,
    OPPORTUNITY_MEETING_REVIEW_FORM,
    ACCOUNT_CREATE_FORM,
    ACCOUNT_UPDATE_FORM,
    ACCOUNT_MEETING_REVIEW_FORM,
]

FORM_TYPES = (
    (FORM_TYPE_CREATE, "Create"),
    (FORM_TYPE_UPDATE, "Update"),
    (FORM_TYPE_MEETING_REVIEW, "Meeting Review"),
)
