

NYLAS_API_BASE_URL = "https://api.nylas.com"
EMAIL_AUTH_CALLBACK_URL = "http://localhost:5000/api/connect-email"
EMAIL_AUTH_URI = "oauth/authorize"
NYLAS_CLIENT_ID = "2th0vp5dkvmc1lkcvf41quqkf"
NYLAS_CLIENT_SECRET = "5jvvtb1zg8vuha4rxgqbqvfjj"
EMAIL_AUTH_TOKEN_URI = "oauth/token"
EMAIL_AUTH_TOKEN_REVOKE_URI = "oauth/revoke"
EMAIL_ACCOUNT_URI = "account"
SCOPE_EMAIL_READ_ONLY = "email.read_only"


def EMAIL_REVOKE_ALL_TOKENS_URI(account_id):
    return f'a/{NYLAS_CLIENT_ID}/accounts/{account_id}/revoke-all/'
