from nylas import APIClient
from managr.core import constants as core_consts


SCOPE_EMAIL_READ_ONLY = "email.read_only"
SCOPES = (SCOPE_EMAIL_READ_ONLY,)
nylas = APIClient(core_consts.NYLAS_CLIENT_ID, core_consts.NYLAS_CLIENT_SECRET)


def gen_auth_url(callback_url, email, magic_token, scopes=SCOPE_EMAIL_READ_ONLY):
    return nylas.authentication_url(callback_url, login_hint=email, state=magic_token, scopes=scopes)


def get_email_auth_token(code):
    """ generates an access_token from the user code """
    ACCESS_TOKEN = nylas.token_for_code(code)
    nylas_account = APIClient(
        core_consts.NYLAS_CLIENT_ID, core_consts.NYLAS_CLIENT_SECRET, ACCESS_TOKEN)
    return nylas_account
