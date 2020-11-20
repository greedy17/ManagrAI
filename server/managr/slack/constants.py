SLACK_API_ROOT = "https://slack.com/api/"
SLACK_OAUTH_AUTHORIZE_ROOT = "https://slack.com/oauth/v2/authorize"

# https://api.slack.com/methods/oauth.v2.access
OAUTH_V2_ACCESS = "oauth.v2.access"

# https://api.slack.com/methods/conversations.open
CONVERSATIONS_OPEN = "conversations.open"

# https://api.slack.com/methods/chat.postMessage
POST_MESSAGE = "chat.postMessage"

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
