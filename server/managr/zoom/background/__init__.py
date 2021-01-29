import logging
import json

import pytz
from datetime import datetime
from background_task import background

from django.db.models import F, Q, Count
from django.utils import timezone

from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets import get_block_set
from managr.organization.models import Contact
from managr.opportunity.models import Opportunity
from managr.salesforce.adapter.models import ContactAdapter


from .. import constants as zoom_consts
from ..zoom_helper import auth as zoom_auth
from ..zoom_helper import constants as zoom_model_consts
from ..zoom_helper.models import ZoomAcct, ZoomMtg
from ..models import ZoomAuthAccount, ZoomMeeting, MeetingReview
from ..serializers import (
    ZoomAuthRefSerializer,
    ZoomAuthSerializer,
    ZoomMeetingWebhookSerializer,
    ZoomMeetingSerializer,
)


def _split_first_name(name):
    if name and len(name):
        name_parts = name.split(" ")
        if len(name_parts):
            return name_parts[0]


def _split_last_name(name):
    if name and len(name):
        name_parts = name.split(" ")
        if len(name_parts) > 1:

            return "".join(name_parts[1:])


def emit_process_past_zoom_meeting(user_id, meeting_uuid):
    return _get_past_zoom_meeting_details(user_id, meeting_uuid)


def emit_kick_off_slack_interaction(user_id, managr_meeting_id):
    return _kick_off_slack_interaction(user_id, managr_meeting_id)


def emit_save_meeting_review_data(managr_meeting_id, data):
    return _save_meeting_review_data(managr_meeting_id, data)


@background(schedule=0)
def _get_past_zoom_meeting_details(user_id, meeting_uuid, original_duration):
    zoom_account = ZoomAuthAccount.objects.filter(user__id=user_id).first()
    if zoom_account and not zoom_account.is_revoked:
        # emit the process
        meeting = zoom_account.helper_class.get_past_meeting(meeting_uuid)
        meeting = meeting.get_past_meeting_participants(zoom_account.access_token)
        meeting.original_duration = original_duration
        zoom_participants = meeting.as_dict.get("participants", None)
        # remove duplicates
        participants = []
        for participant in zoom_participants:
            if participant not in participants:
                participants.append(participant)

        if participants:
            user = zoom_account.user
            participant_emails = set(
                [participant.get("user_email", None) for participant in participants]
            )

            opportunity = Opportunity.objects.filter(
                contacts__email__in=participant_emails,
            ).first()
            meeting_contacts = []
            if opportunity:
                existing_contacts = Contact.objects.filter(
                    email__in=participant_emails, user__organization__id=user.organization.id
                ).exclude(email=user.email)
                # convert all contacts to model representation and remove from array
                for contact in existing_contacts:
                    meeting_contacts.append(contact.adapter_class.as_dict)
                    for index, participant in enumerate(participants):
                        if (
                            participant["user_email"] == contact.email
                            or participant["user_email"] == user.email
                        ):
                            del participants[index]

                meeting_contacts = [
                    *list(
                        map(
                            lambda contact: ContactAdapter(**contact).as_dict,
                            list(
                                map(
                                    lambda participant: dict(
                                        email=participant["user_email"],
                                        first_name=_split_first_name(participant["name"]),
                                        last_name=_split_last_name(participant["name"]),
                                    ),
                                    participants,
                                ),
                            ),
                        ),
                    ),
                    *meeting_contacts,
                ]

                # push to sf

                # for v1 will only be able to assign to one opportunity
                meeting.opportunity = opportunity.id
                meeting.participants = meeting_contacts
                serializer = ZoomMeetingSerializer(data=meeting.as_dict)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                # emit the event to start slack interaction
                emit_kick_off_slack_interaction(user_id, str(serializer.instance.id))


@background(schedule=0)
def _kick_off_slack_interaction(user_id, managr_meeting_id):
    # get meeting
    meeting = ZoomMeeting.objects.filter(id=managr_meeting_id).first()
    if meeting:
        # get user
        user = meeting.zoom_account.user
        org = user.organization.id
        opportunity = meeting.opportunity.id

        if hasattr(user, "slack_integration"):
            user_slack_channel = user.slack_integration.channel
            slack_org_access_token = user.organization.slack_integration.access_token
            block_set = get_block_set(
                "zoom_meeting_initial",
                {
                    "o": str(org),
                    "u": str(user.id),
                    "opp": str(opportunity),
                    "m": managr_meeting_id,
                },
            )
            res = slack_requests.send_channel_message(
                user_slack_channel, slack_org_access_token, block_set=block_set
            )
            meeting.current_interaction = 1
            meeting.notification_attempts = meeting.notification_attempts + 1
            meeting.save()


@background(schedule=0)
def _save_meeting_review_data(managr_meeting_id, data):
    data = json.loads(data)

    meeting = ZoomMeeting.objects.filter(id=managr_meeting_id).first()
    meeting.interaction_status = zoom_consts.MEETING_INTERACTION_STATUS_COMPLETE
    meeting.is_closed = True
    meeting.save()
    if not hasattr(meeting, "meeting_review"):
        date = data.get("close_date", None)
        if date:
            ## make it aware by adding utc
            date = datetime.strptime(date, "%Y-%m-%d")
            date = pytz.utc.localize(date)
        obj = dict()
        obj["meeting"] = meeting
        obj["meeting_type"] = data.get("meeting_type", None)
        obj["forecast_category"] = data.get("forecast_category", None)
        obj["stage"] = data.get("stage", None)
        obj["description"] = data.get("description", None)
        obj["next_step"] = data.get("next_step", None)
        obj["close_date"] = date
        obj["sentiment"] = data.get("sentiment", None)
        obj["amount"] = data.get("amount", None)

        meeting_review = MeetingReview.objects.create(**obj)

