import base64
import json
import requests
from requests.exceptions import HTTPError

from rest_framework.exceptions import APIException, PermissionDenied

from django.http import HttpResponse
from django.urls import reverse
from django.template import Context, Template

from managr.utils import sites as site_utils
from managr.lead.models import LeadEmail
from managr.lead import constants as lead_constants
from managr.lead.background import emit_event

from .exceptions import NylasAPIError
from .. import constants as core_consts


def _generate_nylas_basic_auth_token(user):
    """ Function to generate the encoded basic auth token required by Nylas
    Details here: https://docs.nylas.com/docs/using-access-tokens
    """
    password = ""
    if user.email_auth_account is None or user.email_auth_account.access_token is None:
        raise PermissionDenied(
            detail="User does not have a Nylas access token")

    access_token = user.email_auth_account.access_token
    auth_string = f"{access_token}:{password}"
    base64_secret = base64.b64encode(
        auth_string.encode("ascii")).decode("utf-8")
    return base64_secret


def _handle_nylas_response(response):
    """ Function to generate a Json object from Nylas's server.
    Returns either the JSON object or raises an error.
    Eventually we can extend this to clean and serialize the data."""
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise APIException(
            detail="401 Unauthorized Response from Nylas server",
            code=response.status_code,
        )
    elif response.status_code == 400:
        raise APIException(
            detail="400 Bad Request response from Nylas server",
            code=response.status_code,
        )
    else:
        raise APIException(detail="Error from Nylas server",
                           code=response.status_code)


def _return_nylas_headers(user):
    """ Function to generate the basic headers required by Nylas
    Details here: https://docs.nylas.com/docs/using-access-tokens"""
    headers = dict(Authorization=(
        f"Basic {_generate_nylas_basic_auth_token(user)}"))
    return headers


def retrieve_threads(user, to_email=None, any_email=None, page=1, page_size=10):
    """Use the Nylas API to retrieve threads.

    Args:
        user (User):             Access the API on this user's behalf.
        to_email (str):          Retrieve threads addressed to this email.
        any_email (list[str]):   Retrieve threads involving any of these emails.
        page (str, int):         Page of results to access (based on page_size).
        page_size (str, int):    Maximum number of results to retrieve (based on page).
    """
    page = int(page)
    page_size = int(page_size)
    request_url = f"{core_consts.NYLAS_API_BASE_URL}/threads/"
    headers = _return_nylas_headers(user)

    # Set up the request parameters
    params = {"offset": (page - 1) * page_size, "limit": page_size}

    if to_email:
        params["to"] = to_email

    if any_email:
        params["any_email"] = any_email

    response = requests.get(request_url, params=params, headers=headers)
    json_response = _handle_nylas_response(response)

    return json_response


def retrieve_messages(user, thread_id, page=1, page_size=10):
    """Use Nylas to retrieve messages from specific threads ids."""
    request_url = f"{core_consts.NYLAS_API_BASE_URL}/messages/"
    headers = _return_nylas_headers(user)
    params = {
        "offset": (page - 1) * page_size,
        "limit": page_size,
        "thread_id": thread_id,
    }
    response = requests.get(request_url, params=params, headers=headers)
    json_response = _handle_nylas_response(response)

    return json_response


def retrieve_message(user, message_id):
    request_url = f"{core_consts.NYLAS_API_BASE_URL}/messages/{message_id}"
    headers = _return_nylas_headers(user)
    response = requests.get(request_url, headers=headers)
    json_response = _handle_nylas_response(response)
    return json_response


def retrieve_thread(user, thread_id):
    request_url = f"{core_consts.NYLAS_API_BASE_URL}/threads/{thread_id}"
    headers = _return_nylas_headers(user)
    response = requests.get(request_url, headers=headers)
    json_response = _handle_nylas_response(response)
    return json_response


def return_file_id_from_nylas(user, file_object):
    """Use Nylas to generate a file_id for file attachment."""
    headers = _return_nylas_headers(user)
    file_data = {"file": (file_object.name, file_object.file)}
    response = requests.post(
        f"{core_consts.NYLAS_API_BASE_URL}/files/", files=file_data, headers=headers
    )
    json_response = _handle_nylas_response(response)
    return json_response


def download_file_from_nylas(user, file_id):
    """ Use Nylas to download file based on file_id
    """
    # First generate the authorization required for both requests
    headers = _return_nylas_headers(user)
    # First we make a call to nylas to get the file metadata from the file_id
    file_metadata_url = f"{core_consts.NYLAS_API_BASE_URL}/files/{file_id}/"
    r = requests.get(file_metadata_url, headers=headers)

    json_response = r.json()
    file_name = json_response["filename"]
    content_type = json_response["content_type"]

    # Then we make a second call for the file itself.
    file_request_url = f"{core_consts.NYLAS_API_BASE_URL}/files/{file_id}/download/"
    file_response = requests.get(file_request_url, headers=headers)

    response = HttpResponse(content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'
    response.write(file_response.content)

    return response


def render_message(message, context_dict, lb_to_br=False):
    """Render a message, given a dictionary of context.

    Args:
        message (str):           The message to render.
        context_dict (dict):     Dictionary of context variables to find and replace in template.
        lb_to_br (bool):         Convert line breaks to <br> tags. Use this for email bodies that
                                 may have line breaks.
    """
    message = message.replace("\n", "<br />")
    template = Template(message)
    # Set auto-escaping to false, since resources may contain apostrophes, ampersands, etc
    # NOTE: This means message should come from a trusted source; otherwise we are potentially
    #       vulnerable to an HTML or JS injection
    context = Context(context_dict, autoescape=False)
    return template.render(context)


def render_email(
    sender,
    subject="(No Subject)",
    body="(This email has no content.)",
    to=[],
    cc=[],
    bcc=[],
    reply_to_message_id=None,
    file_ids=[],
    variables=None,
):
    """Prepare an email for sending by rendering it with necessary variables.

    Neil: I separated this out so we can know that it's being used the same way in
          both the preview_email and the send_email functions.
    """
    from_info = [{"name": sender.full_name, "email": sender.email}]

    email_info = {
        "from": from_info,
        "to": to,
    }

    # If variables are passed in, render the email body using Django templating.
    if variables:
        email_info["body"] = render_message(body, variables)
        email_info["subject"] = render_message(subject, variables)
    else:
        email_info["body"] = body
        email_info["subject"] = subject

    if reply_to_message_id:
        email_info["reply_to_message_id"] = reply_to_message_id

    if cc:
        email_info["cc"] = cc

    if bcc:
        email_info["bcc"] = bcc

    if len(file_ids) > 0:
        email_info["file_ids"] = file_ids

    return email_info


def send_new_email(
    sender,
    to,
    subject="(No Subject)",
    body="(This email has no content.)",
    cc=[],
    bcc=[],
    reply_to_message_id=None,
    file_ids=[],
    variables=None,
    lead=None,
):
    """Use Nylas to send emails, pass in the user from which it will send.

    Args:
        sender (User):                  The User object of the sender of the email.
        subject (str):                  The subject of the email.
        body (str):                     The body of the email.
        to (list<dict>):                Contacts to receive email. Contacts should be dictionaries
                                        in the format: {"name": NAME, "email": EMAIL}.
        cc_email (list<dict>):          Contacts for the CC field. Contacts must be dictionaries
                                        in the format: {"name": NAME, "email": EMAIL}.
        bcc_email (list<dict>):         Contacts for the BCC field. Contacts must be dictionaries
                                        in the format: {"name": NAME, "email": EMAIL}.
        reply_to_message_id (str):      ID of the Nylas email message to reply to.
        file_ids (list<str>):           List of Nylas File IDs.
        variables (dict):               Context variables used when rendering emails.
    """
    email_info = render_email(
        sender,
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        reply_to_message_id=reply_to_message_id,
        file_ids=file_ids,
        variables=variables,
    )

    # Serialize email data as JSON
    data = json.dumps(email_info)

    # Note: The documentation says that this endpoint requires a bearer token, but we
    # are using a basic auth token here. I think this may be a mistake in the documentation.
    # But, if this fails, this could be why.
    headers = _return_nylas_headers(sender)

    response = requests.post(
        f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.SEND_EMAIL_URI}",
        data=data,
        headers=headers,
    )

    if response.status_code == 200:
        # Create a Lead/Thread connection
        obj = LeadEmail.objects.create(
            created_by=sender, lead=lead, thread_id=response.json()[
                "thread_id"],
        )

        # Emit an EMAIL_SENT event and pass in Lead/Thread record.
        emit_event(lead_constants.EMAIL_SENT, sender, obj)

    return _handle_nylas_response(response)


def generate_preview_email_data(
    sender,
    subject="(No Subject)",
    body="(This email has no content.)",
    to=[],
    cc=[],
    bcc=[],
    reply_to_message_id=None,
    file_ids=[],
    variables=None,
    lead=None,
):
    email_info = render_email(
        sender,
        subject=subject,
        body=body,
        to=to,
        cc=cc,
        bcc=bcc,
        reply_to_message_id=reply_to_message_id,
        file_ids=file_ids,
        variables=variables,
    )

    data = {"subject": email_info["subject"], "body": email_info["body"]}

    return data


def send_new_email_legacy(auth, sender, receipient, message):
    """Use Nylas to send emails, pass in the user from which it will send.

    DEPRECATED, NEIL: I AM KEEPING THIS HERE TO SUPPORT A LEGACY VIEW. WE CAN REPLACE
        THIS WITH SEND_NEW_EMAIL() ABOVE AND IT WILL WORK.
    """
    token = auth
    sender = [sender]  # {'name':'','email':''}
    to = receipient
    subject = message.get("subject", None)
    body = message.get("body", None)
    headers = dict(Authorization=(f"Bearer {token}"))
    data = json.dumps(
        {"from": sender, "to": to, "subject": subject, "body": body}
    )

    response = requests.post(
        f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.SEND_EMAIL_URI}",
        data=data,
        headers=headers,
    )

    return _handle_nylas_response(response)
