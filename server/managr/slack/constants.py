SLACK_API_ROOT = "https://slack.com/api/"
SLACK_OAUTH_AUTHORIZE_ROOT = "https://slack.com/oauth/v2/authorize"

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

# Action IDs of different interactive UI in the Managr Slack App
ZOOM_MEETING__GREAT = "ZOOM_MEETING__GREAT"
ZOOM_MEETING__NOT_WELL = "ZOOM_MEETING__NOT_WELL"
GET_ORGANIZATION_STAGES = "GET_ORGANIZATION_STAGES"
GET_LEAD_FORECASTS = "GET_LEAD_FORECASTS"
GET_ORGANIZATION_ACTION_CHOICES = "GET_ORGANIZATION_ACTION_CHOICES"
