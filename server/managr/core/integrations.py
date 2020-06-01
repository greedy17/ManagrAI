
import base64
import json
import requests

from requests.exceptions import HTTPError
from rest_framework.exceptions import APIException
from urllib.parse import urlencode

from managr.core import constants as core_consts

SCOPES = (core_consts.SCOPE_EMAIL_READ_ONLY, core_consts.SCOPE_EMAIL_SEND)


def gen_auth_url(callback_url, email, magic_token, scopes=(', ').join(SCOPES)):

    query = dict(redirect_uri=callback_url, response_type='code',
                 login_hint=email, state=magic_token, scopes=scopes, client_id=core_consts.NYLAS_CLIENT_ID)
    params = urlencode(query)
    return f'{core_consts.NYLAS_API_BASE_URL}/{core_consts.EMAIL_AUTH_URI}?{params}'


def get_access_token(code):
    """ gets access token from code """
    base64_secret = base64.b64encode(
        core_consts.NYLAS_CLIENT_SECRET.encode('ascii')).decode('utf-8')
    headers = dict(Authorization=f'Basic {base64_secret}')
    data = dict(client_id=core_consts.NYLAS_CLIENT_ID,
                client_secret=core_consts.NYLAS_CLIENT_SECRET, grant_type="authorization_code", code=code)
    """
        Nylas returns a 400 error with a text that is all html
        Usually this means the code is already in use (aka failed authentication flow and we cannot get the token anymore)
        Or it is expired/invalid
    """

    res = requests.post(
        f'{core_consts.NYLAS_API_BASE_URL}/{core_consts.EMAIL_AUTH_TOKEN_URI}', data=data, headers=headers)
    if res.status_code == 200:
        return res.json()['access_token']
    elif res.status_code == 400:
        raise HTTPError(res.status_code)
    else:
        """ most likely an error with our account or their server """
        raise HTTPError(res.status_code)


def get_account_details(token):
    """ gets account details from token to store in db """
    headers = dict(Authorization=f'Bearer {token}')
    res = requests.get(
        f'{core_consts.NYLAS_API_BASE_URL}/{core_consts.EMAIL_ACCOUNT_URI}', headers=headers)
    return res.json()


def revoke_access_token(token):
    """ function to revoke access token
        mostly used for billing if a user changes smtp or is removed
    """
    headers = dict(Authorization=f'Bearer {token}')
    res = requests.post(
        f'{core_consts.NYLAS_API_BASE_URL}/{core_consts.EMAIL_AUTH_TOKEN_REVOKE_URI}', headers=headers)

    # returns {success:True} on success
    # if a 401 error is thrown then we have incorrect token stored
    # we return the 401 error and revoke all access tokens when a new one is created
    if res.status_code == 200:
        return res
    elif res.status_code == 401:
        """ access token was not verified (aka does not exist) and we have a sync mismatch"""
        raise HTTPError(res.status_code)
    else:
        """ most likely an error with our account or their server """
        raise HTTPError()


def revoke_all_access_tokens(account_id, keep_token=''):
    """
        This function will remove all access tokens for accounts that have more than one
        we will be calling this in case of a 401 on revoke (meaning we have out of sync data)
        and every 24 hours with a cron job
        manager will be charged for duplicates
    """
    password = ''
    auth_string = f'{core_consts.NYLAS_CLIENT_SECRET}:{password}'
    base64_secret = base64.b64encode(
        auth_string.encode('ascii')).decode('utf-8')
    headers = dict(Authorization=f'Basic {base64_secret}')
    data = dict(keep_access_token=keep_token)

    res = requests.post(
        f'{core_consts.NYLAS_API_BASE_URL}/{core_consts.EMAIL_REVOKE_ALL_TOKENS_URI(account_id)}',
        headers=headers, data=data
    )
    if res.status_code == 200:
        return res.json()
    elif res.status_code == 404:
        """ the user has no tokens to revoke """
        raise HTTPError(res.status_code)
    else:
        """ most likely an error with our account or their server """
        raise HTTPError()
    return


def _generate_nylas_basic_auth_token(user):
    ''' Function to generate the encoded basic auth token required by Nylas
    Details here: https://docs.nylas.com/docs/using-access-tokens
    '''
    password = ''
    if user.email_auth_account is None or user.email_auth_account.access_token is None:
        raise PermissionDenied(detail='User does not have a Nylas access token')

    access_token = user.email_auth_account.access_token
    auth_string = f'{access_token}:{password}'
    base64_secret = base64.b64encode(
        auth_string.encode('ascii')).decode('utf-8')
    return base64_secret


def _return_json_from_nylas_server(response):
    ''' Function to generate a Json object from Nylas's server.
    Returns either the JSON object or raises an error.
    Eventually we can extend this to clean and serialize the data.'''
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise APIException(detail='401 Unauthorized Response from Nylas server',
                           code=response.status_code)
    elif response.status_code == 400:
        raise APIException(detail='400 Bad Request response from Nylas server',
                           code=response.status_code)
    else:
        raise APIException(detail='Error from Nylas server',
                           code=response.status_code)


def _return_nylas_headers(user):
    ''' Function to generate the basic headers required by Nylas
    Details here: https://docs.nylas.com/docs/using-access-tokens'''
    headers = dict(Authorization=(f'Basic {_generate_nylas_basic_auth_token(user)}'))
    return headers


def retrieve_user_threads(user, to_email):
    """ Use Nylas to retrieve threads for a specific user
    """
    request_url = f'{core_consts.NYLAS_API_BASE_URL}/threads/'
    headers = _return_nylas_headers(user)
    # TODO: Make pagination variable.
    params = {'limit': 10}
    if to_email:
        params['to'] = to_email
    response = requests.get(request_url, params=params, headers=headers)
    json_response = _return_json_from_nylas_server(response)
    return json_response


def retrieve_messages(user, thread_id):
    """ Use Nylas to retrieve messages from specific threads ids.
    """
    request_url = f'{core_consts.NYLAS_API_BASE_URL}/messages/'
    headers = _return_nylas_headers(user)
    # TODO: Make pagination variable.
    params = {'limit': 10, 'thread_id': thread_id}
    response = requests.get(request_url, params=params, headers=headers)
    json_response = _return_json_from_nylas_server(response)
    return json_response


def send_new_email(sender, recipient_emails, subject='(No Subject)',
                   body='(This email was left blank)',
                   cc_emails=[], bcc_emails=[],
                   reply_to_message_id=None,):
    """ Use Nylas to send emails, pass in the user from which it will send
        simple version

        PARAMS:
        sender: The User object of the sender of the email.
        recipient_email: An array of contact objects for the To field.
            Contact objects must be in the format {"name": NAME, "email": EMAIL}.
        cc_email: An array of contact objects for the CC field.
            Contact objects must be in the format {"name": NAME, "email": EMAIL}.
        bcc_email: An array of contact objects for the BCC field.
            Contact objects must be in the format {"name": NAME, "email": EMAIL}.
        subject: A string for the subject of the email.
        body: A string for the body of the email.

    """
    from_info = [{
        "name": sender.full_name,
        "email": sender.email
    }]

    email_info = {
        'from': from_info,
        'to': recipient_emails,
        'subject': subject,
        'body': body
    }
    if reply_to_message_id:
        email_info['reply_to_message_id'] = reply_to_message_id

    if cc_emails:
        email_info['cc'] = cc_emails

    if bcc_emails:
        email_info['bcc'] = bcc_emails

    data = json.dumps(email_info)
    # Note: The documentation says that this endpoint requires a bearer token, but we
    # are using a basic auth token here. I think this may be a mistake in the documentation.
    # But, if this fails, this could be why.
    headers = _return_nylas_headers(sender)
    response = requests.post(
        f'{core_consts.NYLAS_API_BASE_URL}/{core_consts.SEND_EMAIL_URI}',
        data=data, headers=headers)

    return _return_json_from_nylas_server(response)


def send_new_email_legacy(auth, sender, receipient, message):
    """ Use Nylas to send emails, pass in the user from which it will send
        simple version
        NOTE: I AM KEEPING THIS HERE TO SUPPORT A LEGACY VIEW. WE CAN REPLACE
        THIS WITH SEND_NEW_EMAIL() ABOVE AND IT WILL WORK.
    """
    token = auth
    from_info = [sender]  # {'name':'','email':''}
    to_info = receipient
    subject = message.get('subject', None)
    body = message.get('body', None)
    headers = dict(Authorization=(f'Bearer {token}'))
    data = json.dumps({'from': from_info, 'to': to_info,
                       "subject": subject, "body": body})

    response = requests.post(
        f'{core_consts.NYLAS_API_BASE_URL}/{core_consts.SEND_EMAIL_URI}', data=data, headers=headers)

    return _return_json_from_nylas_server(response)
