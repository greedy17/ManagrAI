import logging
import json

import pytz
from datetime import datetime
from background_task import background

from django.db.models import F, Q, Count
from django.utils import timezone


from managr.zoom.zoom_helper import auth as zoom_auth
from managr.zoom.zoom_helper import constants as zoom_model_consts
from managr.zoom.zoom_helper.models import ZoomAcct, ZoomMtg
from managr.zoom.models import ZoomAuthAccount, ZoomMeeting, MeetingReview
from managr.zoom.serializers import (
    ZoomAuthRefSerializer,
    ZoomAuthSerializer,
    ZoomMeetingWebhookSerializer,
    ZoomMeetingSerializer,
)
from managr.zoom import constants as zoom_consts
from managr.core.nylas.emails import send_system_email
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets import get_block_set
from managr.organization.models import Contact


def _send_slack_int_email(user):
    # when checking slack notification settings, if the user has opted to
    # receive slack notifs but has not integrated slack send them an email (assuming their org has set it up)
    # reminding them to set up slack

    recipient = [{"name": user.full_name, "email": user.email}]
    message = {
        "subject": "Enable Slack",
        "body": "You have opted to receive Slack Notifications, please integrate slack so you can receive them",
    }
    send_system_email(recipient, message)


def emit_process_past_zoom_meeting(user_id, meeting_uuid):
    return _get_past_zoom_meeting_details(user_id, meeting_uuid)


def emit_kick_off_slack_interaction(user_id, managr_meeting_id):
    return _kick_off_slack_interaction(user_id, managr_meeting_id)


def emit_save_meeting_review_data(managr_meeting_id, data):
    return _save_meeting_review_data(managr_meeting_id, data)


@background(schedule=0)
def _get_past_zoom_meeting_details(user_id, meeting_uuid):
    zoom_account = ZoomAuthAccount.objects.filter(user__id=user_id).first()
    if zoom_account:
        # emit the process
        meeting = zoom_account.helper_class.get_past_meeting(meeting_uuid)
        meeting = meeting.get_past_meeting_participants(zoom_account.access_token)
        participants = meeting.as_dict.get("participants", None)
        if participants:
            user = zoom_account.user
            participant_emails = [
                participant.get("user_email", None) for participant in participants
            ]
            lead = user.claimed_leads.filter(
                linked_contacts__email__in=participant_emails
            ).first()
            meeting_contacts = []
            for contact in participants:
                contact_email = contact.get("user_email", None)
                if contact_email and contact_email != user.email:

                    c, created = Contact.objects.for_user(user).get_or_create(
                        email=contact["user_email"].lower(),
                        defaults={
                            "account": lead.account,
                            "organization": lead.account.organization,
                        },
                    )

                    if created:
                        if contact["name"]:
                            name_items = contact["name"].split(" ")
                            c.first_name = name_items[0]
                            if len(name_items) > 1:
                                c.last_name = " ".join(name_items[1:])
                            c.save()
                        lead.linked_contacts.add(c)
                    meeting_contacts.append(c.id)

            # for v1 will only be able to assign to one lead
            if lead:
                meeting.lead = lead.id
                meeting.participants = set(meeting_contacts)
                serializer = ZoomMeetingSerializer(data=meeting.as_dict)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                # emit the event to start slack interaction
                emit_kick_off_slack_interaction(user_id, str(serializer.instance.id))


@background(schedule=0)
def _kick_off_slack_interaction(user_id, managr_meeting_id):
    # get meeting
    meeting = ZoomMeeting.objects.filter(id=managr_meeting_id).first()
    if not meeting:
        return
    # get user
    user = meeting.zoom_account.user
    org = user.organization.id
    lead = meeting.lead.id

    if user.send_email_to_integrate_slack:
        _send_slack_int_email(user)
        return
    if hasattr(user, "slack_integration"):
        user_slack_channel = user.slack_integration.channel
        slack_org_access_token = user.organization.slack_integration.access_token
        block_set = get_block_set(
            "zoom_meeting_initial",
            {"o": str(org), "u": str(user.id), "l": str(lead), "m": managr_meeting_id},
        )
        slack_requests.send_channel_message(
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
        date = data.get("expected_close_date", None)
        if date:
            ## make it aware by adding utc
            date = datetime.strptime(date, "%Y-%m-%d")
            date = pytz.utc.localize(date)
        obj = dict()
        obj["meeting"] = meeting
        obj["meeting_type"] = data.get("meeting_type", None)
        obj["forecast_strength"] = data.get("forecast", None)
        obj["update_stage"] = data.get("stage", None)
        obj["description"] = data.get("description", None)
        obj["next_steps"] = data.get("next_steps", None)
        obj["updated_close_date"] = date
        obj["sentiment"] = data.get("sentiment", None)
        obj["amount"] = data.get("amount", None)

        MeetingReview.objects.create(**obj)
        # send slack notification when it is ready

