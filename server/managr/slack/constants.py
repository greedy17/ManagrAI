from django.conf import settings

SLACK_API_ROOT = "https://slack.com/api/"
SLACK_OAUTH_AUTHORIZE_ROOT = "https://slack.com/oauth/v2/authorize"


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

# Action IDs of different interactive UI in the Managr Slack App
DEFAULT_ACTION_ID = "ACTION_ID"
ZOOM_MEETING__GREAT = "ZOOM_MEETING__GREAT"
ZOOM_MEETING__NOT_WELL = "ZOOM_MEETING__NOT_WELL"
ZOOM_MEETING__NOT_WELL = "ZOOM_MEETING__CANT_TELL"
ZOOM_MEETING__DIFFERENT_OPPORTUNITY = "ZOOM_MEETING__DIFFERENT_OPPORTUNITY"
GET_ORGANIZATION_STAGES = "GET_ORGANIZATION_STAGES"
GET_LEAD_FORECASTS = "GET_LEAD_FORECASTS"
GET_ORGANIZATION_ACTION_CHOICES = "GET_ORGANIZATION_ACTION_CHOICES"
GET_USER_OPPORTUNITIES = "GET_USER_OPPORTUNITIES"
SHOW_REMINDER_CONTACTS = "SHOW_REMINDER_CONTACTS"

