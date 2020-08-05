
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


def send_message(body, sender, recepient, callback):
    try:
        message = client.messages \
            .create(
                body=body,
                from_=sender,
                to=recepient,
                # callback url will return the created message to add to the log
                status_callback=callback
            )
    except Exception as e:
        message = e.msg
        status = e.status
        raise APIException(
            detail=f'Error From Twilio Server, {message}', code=status)

    return message


def create_new_account(phone_number):
    # status_callback_method and sms_method are set to POST by default but can be changed
    try:
        incoming_phone_number = client.incoming_phone_numbers \
            .create(phone_number=phone_number,
                    sms_url=core_consts.TWILIO_MESSAGE_RECEIVED_CALLBACK_URL,
                    status_callback=core_consts.TWILIO_MESSAGE_STATUS_CALLBACK_URL,
                    )
    except Exception as e:
        message = e.msg
        status = e.status
        raise APIException(
            detail=f'Error From Twilio Server, {message}', code=status)

    return incoming_phone_number.__dict__.get('_properties', None)


def list_messages(sender, recipient, limit=25):
    """ 
        helper function to list messages 
        messages on the front end are listed by lead
        however if a user feels as though we have missed a message
        we offer an option to search for messages from themselves to 
        a specific lead contact 

    """
    # TODO:- Pari Will have to work on pagination 07/23/20
    # TODO:- Pari Will have create class and serializer to class when we decide if we are using convos or not 08/05/20

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
    formatted_messages = [message.__dict__['_properties']
                          for message in messages]
    return formatted_messages


def list_available_numbers(region="DC", country="US", zipcode=None):
    """ method to retrieve a list of available phone numbers from twilio"""
    try:
        available_numbers = client.available_phone_numbers(country).local.list(
            in_region=region if region else ""
        )
        formatted_data = [dict(capabilities=number.capabilities, friendly_name=number.friendly_name,
                               is_country=number.iso_country, locality=number.locality,
                               phone_number=number.phone_number, postal_code=number.postal_code,
                               region=number.region) for number in available_numbers]

    except Exception as e:
        message = e.msg
        status = e.status
        raise APIException(
            detail=f'Error From Twilio Server, {message}', code=status)

    return formatted_data


class TwilioIncomingPhoneNumber:

    def __init__(self, twilioIncomingInstance):
        self.account_sid = twilioIncomingInstance.account_sid
        self.address_sid = twilioIncomingInstance.address_sid
        self.api_version = twilioIncomingInstance.api_version
        self.beta = twilioIncomingInstance.beta
        self.bundle_sid = twilioIncomingInstance.bundle_sid
        self.capabilities = twilioIncomingInstance.capabilities
        self.date_created = twilioIncomingInstance.date_created
        self.date_updated = twilioIncomingInstance.date_updated
        self.emergency_address_sid = twilioIncomingInstance.emergency_address_sid
        self.emergency_status = twilioIncomingInstance.emergency_status
        self.friendly_name = twilioIncomingInstance.friendly_name
        self.identity_sid = twilioIncomingInstance.identity_sid
        self.origin = twilioIncomingInstance.origin
        self.phone_number = twilioIncomingInstance.phone_number
        self.sid = twilioIncomingInstance.sid
        self.sms_application_sid = twilioIncomingInstance.sms_application_sid
        self.sms_fallback_method = twilioIncomingInstance.sms_fallback_method
        self.sms_fallback_url = twilioIncomingInstance.sms_fallback_url
        self.sms_method = twilioIncomingInstance.sms_method
        self.sms_url = twilioIncomingInstance.sms_url
        self.status = twilioIncomingInstance.status
        self.status_callback = twilioIncomingInstance.status_callback
        self.status_callback_method = twilioIncomingInstance.status_callback_method
        self.trunk_sid = twilioIncomingInstance.trunk_sid
        self.uri = twilioIncomingInstance.uri
        self.voice_application_sid = twilioIncomingInstance.voice_application_sid
        self.voice_caller_id_lookup = twilioIncomingInstance.voice_caller_id_lookup
        self.voice_fallback_method = twilioIncomingInstance.voice_fallback_method
        self.voice_fallback_url = twilioIncomingInstance.voice_fallback_url
        self.voice_method = twilioIncomingInstance.voice_method
        self.voice_receive_mode = twilioIncomingInstance.voice_receive_mode
        self.voice_url = twilioIncomingInstance.voice_url

    def as_dict(self):
        return self.__dict__

#from managr.core.twilio.messages import list_messages
# u=User.objects.get(email="testing@thinknimble.com")
#ma = u.message_auth_account
