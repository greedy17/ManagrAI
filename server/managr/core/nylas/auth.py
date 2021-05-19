import base64
import requests
from requests.exceptions import HTTPError
from urllib.parse import urlencode

from .. import constants as core_consts


def gen_auth_url(email, scopes=core_consts.ALL_SCOPES_STR):
    """Generate the redirect URL that should kick off the Nylas OAuth flow."""
    query = dict(
        redirect_uri=core_consts.NYLAS_OAUTH_CALLBACK_URL,
        response_type="code",
        login_hint=email,
        state="NYLAS",
        scopes=scopes,
        client_id=core_consts.NYLAS_CLIENT_ID,
    )
    params = urlencode(query)
    return f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.EMAIL_AUTH_URI}?{params}"


def get_access_token(code):
    """gets access token from code"""
    base64_secret = base64.b64encode(core_consts.NYLAS_CLIENT_SECRET.encode("ascii")).decode(
        "utf-8"
    )
    headers = dict(Authorization=f"Basic {base64_secret}")
    data = dict(
        client_id=core_consts.NYLAS_CLIENT_ID,
        client_secret=core_consts.NYLAS_CLIENT_SECRET,
        grant_type="authorization_code",
        code=code,
    )
    """
        Nylas returns a 400 error with a text that is all html
        Usually this means the code is already in use (aka failed authentication flow and we cannot get the token anymore)
        Or it is expired/invalid
    """

    res = requests.post(
        f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.EMAIL_AUTH_TOKEN_URI}",
        data=data,
        headers=headers,
    )
    if res.status_code == 200:
        return res.json()["access_token"]
    elif res.status_code == 400:
        raise HTTPError(res.status_code)
    else:
        """most likely an error with our account or their server"""
        raise HTTPError(res.status_code)


def get_account_details(token):
    """gets account details from token to store in db"""
    headers = dict(Authorization=f"Bearer {token}")
    res = requests.get(
        f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.EMAIL_ACCOUNT_URI}", headers=headers,
    )
    return res.json()


def revoke_access_token(token):
    """function to revoke access token
    mostly used for billing if a user changes smtp or is removed
    """
    headers = dict(Authorization=f"Bearer {token}")
    res = requests.post(
        f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.EMAIL_AUTH_TOKEN_REVOKE_URI}",
        headers=headers,
    )

    # returns {success:True} on success
    # if a 401 error is thrown then we have incorrect token stored
    # we return the 401 error and revoke all access tokens when a new one is created
    if res.status_code == 200:
        return res
    elif res.status_code == 401:
        """access token was not verified (aka does not exist) and we have a sync mismatch"""
        raise HTTPError(res.status_code)
    else:
        """most likely an error with our account or their server"""
        raise HTTPError()


def revoke_all_access_tokens(account_id, keep_token=""):
    """
    This function will remove all access tokens for accounts that have more than one
    we will be calling this in case of a 401 on revoke (meaning we have out of sync data)
    and every 24 hours with a cron job
    manager will be charged for duplicates
    """
    password = ""
    auth_string = f"{core_consts.NYLAS_CLIENT_SECRET}:{password}"
    base64_secret = base64.b64encode(auth_string.encode("ascii")).decode("utf-8")
    headers = dict(Authorization=f"Basic {base64_secret}")
    data = dict(keep_access_token=keep_token)

    res = requests.post(
        f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.EMAIL_REVOKE_ALL_TOKENS_URI(account_id)}",
        headers=headers,
        data=data,
    )
    if res.status_code == 200:
        return res.json()
    elif res.status_code == 404:
        """the user has no tokens to revoke"""
        raise HTTPError(res.status_code)
    else:
        """most likely an error with our account or their server"""
        raise HTTPError()
    return
