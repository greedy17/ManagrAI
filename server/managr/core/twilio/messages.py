
from twilio.rest import Client

from django.conf import settings
from rest_framework.exceptions import APIException, PermissionDenied

from managr.core import constants as core_consts


client = Client(core_consts.ACCOUNT_SID, core_consts.AUTH_TOKEN)


def _handle_twilio_response(response):
    """ Function to generate a Json object from Nylas's server.
    Returns either the JSON object or raises an error.
    Eventually we can extend this to clean and serialize the data."""
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise APIException(
            detail="401 Unauthorized Response from Twilio server",
            code=response.status_code,
        )
    elif response.status_code == 400:
        raise APIException(
            detail="400 Bad Request response from Twilio server",
            code=response.status_code,
        )
    else:
        raise APIException(detail="Error from Twilio server",
                           code=response.status_code)


def send_message(body, sender, recepient):
    message = client.messages \
        .create(
            body=body,
            from_=sender,
            to=recepient,
            # callback url will return the created message to add to the log
            status_callback=core_consts.TWILIO_MESSAGE_CALLBACK_URL
        )
    return message


def create_new_account(phone_number):
    # status_callback_method and sms_method are set to POST by default but can be changed
    try:
        incoming_phone_number = client.incoming_phone_numbers \
            .create(phone_number=phone_number,
                    sms_url=core_consts.TWILIO_MESSAGE_RECEIVED_CALLBACK_URL,
                    status_callback=core_consts.TWILIO_MESSAGE_CALLBACK_URL,

                    )
    except Exception as e:
        message = e.msg
        status = e.status
        raise APIException(
            detail=f'Error From Twilio Server, {message}', code=status)

    return incoming_phone_number


def list_messages(sender, recipient, limit=25):
    """ 
        helper function to list messages 
        messages on the front end are listed by lead
        however if a user feels as though we have missed a message
        we offer an option to search for messages from themselves to 
        a specific lead contact 

    """
    # TODO:- Pari Will have to work on pagination 07/23/20
    try:
        messages = client.messages.list(
            from_=sender,
            to=recipient,
            limit=limit,
        )
    except Exception as e:
        message = e.msg
        status = e.status
        raise APIException(
            detail=f'Error From Twilio Server, {message}', code=status)

    return messages


def list_available_numbers(region="DC", country="US", zipcode=None):
    """ method to retrieve a list of available phone numbers from twilio"""
    try:
        available_numbers = client.available_phone_numbers(
            country_code=country, region=region).mobile.list(limit=25)

    except Exception as e:
        message = e.msg
        status = e.status
        raise APIException(
            detail=f'Error From Twilio Server, {message}', code=status)

    return available_numbers


#from managr.core.twilio.messages import send_message
#send_message('test', "+15005550006", "+18572056014")
# class TwilioException404(APIException):
#    status_code = 404
