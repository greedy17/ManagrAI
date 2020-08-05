from django.conf import settings

from managr.utils.misc import get_site_url

USE_NYLAS = settings.USE_NYLAS
NYLAS_CLIENT_ID = settings.NYLAS_CLIENT_ID if USE_NYLAS else None
NYLAS_CLIENT_SECRET = settings.NYLAS_CLIENT_SECRET if USE_NYLAS else None
NYLAS_OAUTH_CALLBACK_URL = settings.NYLAS_OAUTH_CALLBACK_URL if USE_NYLAS else None
NYLAS_API_BASE_URL = "https://api.nylas.com"
EMAIL_AUTH_URI = "oauth/authorize"
EMAIL_AUTH_TOKEN_URI = "oauth/token"
EMAIL_AUTH_TOKEN_REVOKE_URI = "oauth/revoke"
EMAIL_ACCOUNT_URI = "account"
SEND_EMAIL_URI = "send"


<<<<<<< HEAD
=======
USE_TWILIO = settings.USE_TWILIO
ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID if USE_TWILIO else None
AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN if USE_TWILIO else None
TWILIO_MESSAGE_STATUS_CALLBACK_URL = f'{settings.TWILIO_BASE_CALLBACK_URL}/api/twilio/callback/messages/status/' if USE_TWILIO else None
TWILIO_MESSAGE_RECEIVED_CALLBACK_URL = f'{settings.TWILIO_BASE_CALLBACK_URL}/api/twilio/callback/messages' if USE_TWILIO else None


>>>>>>> develop
# OAuth permission scopes to request from Nylas
SCOPE_EMAIL_READ_ONLY = "email.read_only"
SCOPE_EMAIL_SEND = "email.send"
ALL_SCOPES = [
    SCOPE_EMAIL_READ_ONLY,
    SCOPE_EMAIL_SEND,
]
ALL_SCOPES_STR = ", ".join(ALL_SCOPES)

NYLAS_WEBHOOK_TYPE_MSG_CREATED = 'message.created'
NYLAS_WEBHOOK_TYPE_MSG_OPENED = 'message.opened'
NYLAS_WEBHOOK_OBJECT_MESSAGE = 'message'
NYLAS_WEBHOOK_OBJECT_METADATA = 'metadata'
NYLAS_WEBHOOK_TYPES = (
    (NYLAS_WEBHOOK_TYPE_MSG_CREATED, 'Message Created',),
    (NYLAS_WEBHOOK_TYPE_MSG_OPENED, 'Message Opened',),

)
NYLAS_WEBHOOK_OBJECTS = (
    (NYLAS_WEBHOOK_OBJECT_MESSAGE, 'message'),
    (NYLAS_WEBHOOK_OBJECT_METADATA, 'metadata'),

)


def EMAIL_REVOKE_ALL_TOKENS_URI(account_id):
    return f"a/{NYLAS_CLIENT_ID}/accounts/{account_id}/revoke-all/"


ACCOUNT_TYPE_LIMITED = "LIMITED"
ACCOUNT_TYPE_MANAGER = "MANAGER"
ACCOUNT_TYPE_INTEGRATION = "INTEGRATION"
ACCOUNT_TYPES = ((ACCOUNT_TYPE_LIMITED, "LIMITED"), (ACCOUNT_TYPE_MANAGER,
                                                     "MANAGER"), (ACCOUNT_TYPE_INTEGRATION, "INTEGRATION"))

STATE_ACTIVE = "ACTIVE"
STATE_INACTIVE = "INACTIVE"
STATE_INVITED = "INVITED"
STATE_CHOCIES = (
    (STATE_ACTIVE, "Active"),
    (STATE_INACTIVE, "Inactive"),
    (STATE_INVITED, "Invited"),
)

SERVICE_TYPE_NULL = None
SERVICE_TYPE_EMAIL = "EMAIL"
SERVICE_TYPE_EXTERNAL_API = "EXTERNAL"
SERVICE_TYPES = ((SERVICE_TYPE_EMAIL, "Email"),
                 (SERVICE_TYPE_EXTERNAL_API, "External"), (SERVICE_TYPE_NULL, None))
