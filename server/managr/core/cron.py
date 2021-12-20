import json
import logging
import random
import re
from typing import Any
import uuid
from django.conf import settings
import kronos
import datetime

from django.utils import timezone
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from managr.slack.helpers import block_builders, block_sets

from managr.core import constants as core_consts
from managr.core.models import NylasAuthAccount, User, MeetingPrepInstance
from managr.core.nylas.auth import revoke_access_token
from managr.core.background import (
    check_for_time,
    check_workflows_count,
    emit_process_send_workflow_reminder,
    emit_process_send_meeting_reminder,
    emit_process_send_manager_reminder,
    check_for_uncompleted_meetings,
)

from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets import get_block_set
from managr.slack import constants as slack_const


from managr.zoom.models import ZoomMeeting
from managr.zoom.utils import score_meeting
from managr.slack.helpers.block_sets.meeting_review_block_sets import _initial_interaction_message
from managr.organization.models import Contact
from managr.salesforce.adapter.models import ContactAdapter
from managr.zoom.background import _split_first_name, _split_last_name
from managr.core.calendars import calendar_participants_from_zoom_meeting
from managr.core.serializers import MeetingPrepInstanceSerializer
from managr.opportunity.models import Lead, Opportunity
from managr.organization.models import Account
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.zoom.serializers import ZoomMeetingSerializer
from managr.zoom import constants as zoom_consts
from managr.slack import constants as slack_consts
from managr.salesforce.models import MeetingWorkflow
from managr.slack.helpers.block_builders import divider_block


NOTIFICATION_TITLE_STALLED_IN_STAGE = "Opportunity Stalled in Stage"
NOTIFICATION_TITLE_INACTIVE = "Opportunity Inactive"


NOTIFICATION_TITLE_LAPSED_1 = "Opportunity expected close date lapsed by at least 1 day"
NOTIFICATION_TITLE_LAPSED_14 = "Opportunity expected close date lapsed by at least 14 days"
NOTIFICATION_TITLE_LAPSED_30 = "Opportunity expected close date lapsed by at least 30 days"


logger = logging.getLogger("managr")


def _check_days_lead_expected_close_lapsed(lead_expected_close_date):
    now = timezone.now()
    if (now - lead_expected_close_date).days > 0:
        return (now - lead_expected_close_date).days
    else:
        return 0


def _convert_to_user_friendly_date(date):
    return date.strftime("%m/%d/%Y")


def _has_workflow(user, notification_class, notification_type, resource_id):
    return Notification.objects.filter(
        user=user,
        notification_class=notification_class,
        notification_type=notification_type,
        resource_id=resource_id,
    ).first()


def _send_slack_int_email(user):
    # when checking slack notification settings, if the user has opted to
    # receive slack notifs but has not integrated slack send them an email (assuming their org has set it up)
    # reminding them to set up slack

    recipient = [{"name": user.full_name, "email": user.email}]
    message = {
        "subject": "Enable Slack",
        "body": "You have opted to receive Slack Notifications, please integrate slack so you can receive them",
    }
    return
    # disabling since email is currently not working
    # send_system_email(recipient, message)


# def _create_notification(
#     title, content, notification_type, opportunity, user, notification_class="ALERT"
# ):
#     Notification.objects.create(
#         notify_at=timezone.now(),
#         title=title,
#         notification_type=notification_type,
#         resource_id=str(opportunity.id),
#         notification_class=notification_class,
#         user=user,
#         meta={
#             "id": str(opportunity.id),
#             "title": title,
#             "content": content,
#             "opportunities": [{"id": str(opportunity.id), "title": opportunity.title}],
#         },
#     )


def _process_calendar_details(user_id):
    user = User.objects.get(id=user_id)
    events = user.nylas._get_calendar_data()
    processed_data = []
    # print(events, "This is events")
    # print(len(events), "events")
    for event in events:
        data = {}
        data["title"] = event.get("title", None)
        data["participants"] = event.get("participants", None)
        data["times"] = event.get("when", None)
        processed_data.append(data)
    return processed_data


def meeting_prep(processed_data, user_id, send_slack=True):
    def get_domain(email):
        """Parse domain out of an email"""
        return email[email.index("@") + 1 :]

    user = User.objects.get(id=user_id)
    ignore_emails = user.organization.ignore_emails
    meeting = {}
    # Getting all participants from meetings and all their emails
    all_participants = processed_data.get("participants")
    all_emails = []
    for participant in all_participants:
        participants_email = participant.get("email")
        all_emails.append(participants_email)

    meeting = {}

    # all emails are now in participant_emails

    # Gather Meeting Participants from Zoom and Calendar
    # Gather unique emails from the Zoom Meeting participants
    participants = []
    user = User.objects.get(id=user_id)

    org_email_domain = get_domain(user.email)
    remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
        org_email_domain
    )
    for email in ignore_emails:
        remove_users_with_these_domains_regex = (
            remove_users_with_these_domains_regex + r"|({})".format(email)
        )
    # re.search(remove_users_with_these_domains_regex, p.get("email", ""))
    #### first check if we care about this meeting before going forward

    should_register_this_meeting = [
        p
        for p in all_participants
        if not re.search(remove_users_with_these_domains_regex, p.get("email", ""))
    ]

    if not len(should_register_this_meeting):
        return

    memo = {}
    for p in all_participants:
        if p.get("email", "") not in ["", None, *memo.keys()] and not re.search(
            remove_users_with_these_domains_regex, p.get("email", "")
        ):
            memo[p.get("email")] = len(participants)
            participants.append(p)

    # print(p)
    # If the user has their calendar connected through Nylas, find a
    # matching meeting and gather unique participant emails.
    # calendar_participants = calendar_participants_from_zoom_meeting(meeting, user)

    # Combine the sets of participants. Filter out empty emails, meeting owner, and any
    # emails with domains that match the owner, which are teammates of the owner.
    for p in all_participants:
        if not re.search(remove_users_with_these_domains_regex, p.get("email", "")) and p.get(
            "email", ""
        ) not in ["", None]:
            if p.get("email", "") in memo.keys():
                index = memo[p.get("email")]
                participants[index]["name"] = p.get("name", "")
            else:
                memo[p.get("email")] = len(participants)
                participants.append(p)

    contact_forms = []
    if len(participants):
        # Reduce to set of unique participant emails
        participant_emails = set([p.get("email") for p in participants])
        meeting_contacts = []
    # find existing contacts

    existing_contacts = Contact.objects.filter(
        email__in=participant_emails, owner__organization__id=user.organization.id
    ).exclude(email=user.email)
    # convert all contacts to model representation and remove from array
    for contact in existing_contacts:
        formatted_contact = contact.adapter_class.as_dict

        # create a form for each contact to save to workflow
        meeting_contacts.append(formatted_contact)
        for index, participant in enumerate(participants):
            if participant["email"] == contact.email or participant["email"] == User.email:
                del participants[index]
        # print(meeting_contacts, "This is meeting contacts")
    new_contacts = list(
        filter(
            lambda x: len(x.get("secondary_data", dict())) or x.get("email"),
            list(
                map(
                    lambda participant: {
                        **ContactAdapter(
                            **dict(
                                email=participant["email"],
                                # these will only get stored if lastname and firstname are accessible from sf
                                external_owner=user.salesforce_account.salesforce_id,
                                secondary_data={
                                    "FirstName": _split_first_name(participant["name"]),
                                    "LastName": _split_last_name(participant["name"]),
                                    "Email": participant["email"],
                                },
                            )
                        ).as_dict,
                    },
                    participants,
                ),
            ),
        )
    )

    meeting_contacts = [
        *new_contacts,
        *meeting_contacts,
    ]
    meeting_resource_data = dict(resource_id="", resource_type="")
    opportunity = Opportunity.objects.filter(
        contacts__email__in=participant_emails, owner__id=user.id
    ).first()
    if opportunity:
        meeting_resource_data["resource_id"] = str(opportunity.id)
        meeting_resource_data["resource_type"] = "Opportunity"
    else:
        account = Account.objects.filter(
            contacts__email__in=participant_emails, owner__id=user.id,
        ).first()
        if account:
            meeting_resource_data["resource_id"] = str(account.id)
            meeting_resource_data["resource_type"] = "Account"
        else:
            lead = Lead.objects.filter(email__in=participant_emails, owner__id=user.id).first()
            if lead:
                meeting_resource_data["resource_id"] = str(lead.id)
                meeting_resource_data["resource_type"] = "Lead"

    for contact in meeting_contacts:
        contact["_tracking_id"] = str(uuid.uuid4())
        form_type = (
            slack_consts.FORM_TYPE_UPDATE
            if contact["id"] not in ["", None]
            else slack_consts.FORM_TYPE_CREATE
        )
        template = OrgCustomSlackForm.objects.filter(
            form_type=form_type,
            resource=slack_consts.FORM_RESOURCE_CONTACT,
            organization=user.organization,
        ).first()
        if not template:
            logger.exception(
                f"Unable to find Contact Form template for user {str(user_id)}, email {user.email} cannot create initial form for meeting review"
            )
            contact["_form"] = None
        else:
            # create instance
            form = OrgCustomSlackFormInstance.objects.create(
                user=user,
                template=template,
                resource_id="" if contact.get("id") in ["", None] else contact.get("id"),
            )
            contact_forms.append(form)
            contact["_form"] = str(form.id)
    event_data = processed_data
    processed_data.pop("participants")
    data = {"user": user.id, "participants": meeting_contacts, "event_data": event_data}
    if hasattr(meeting_resource_data, "resource_id"):
        data["resource_id"] = meeting_resource_data["resource_id"]
        data["resource_type"] = meeting_resource_data["resource_type"]
    serializer = MeetingPrepInstanceSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return


def _send_calendar_details(user_id):
    user = User.objects.get(id=user_id)
    processed_data = _process_calendar_details(user_id)
    # processed_data checks to see how many events exists

    blocks = [
        block_builders.header_block("Upcoming Meetings For Today!"),
        {"type": "divider"},
    ]
    for event in processed_data:
        meeting_prep(event, user_id)
    meetings = MeetingPrepInstance.objects.filter(user=user.id).filter(
        datetime_created__gt=datetime.date.today()
    )
    for meeting in meetings:
        blocks = [
            *blocks,
            *block_sets.get_block_set("calendar_reminders_blockset", {"prep_id": str(meeting.id)}),
            {"type": "divider"},
        ]
    # Loop thru processed_data and create block for each one
    if len(meetings):
        try:
            slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                text="Calendar: Meetings for Today",
                block_set=blocks,
            )
        except Exception as e:
            logger.exception(f"Failed to send reminder message to {user.email} due to {e}")


def _generate_notification_key_lapsed(num):
    if num == 1:
        return core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_1_DAY
    if num == 14:
        return core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_14_DAYS
    if num == 30:
        return core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_30_DAYS

    # its not ideal that we are checking against a string, but since these are loaded from the fixture
    # we can assume they will be the same


@kronos.register("0 0 * * *")
def revoke_tokens():
    expire = timezone.now() + datetime.timedelta(days=5)
    """ revokes tokens for email auth accounts in state of sync_error, stopped, invalid """
    nylas_tokens = NylasAuthAccount.objects.filter(
        sync_status__in=core_consts.NYLAS_SYNC_STATUSES_FAILING, last_edited__gte=expire
    ).values_list("access_token", flat=True)
    for token in nylas_tokens:
        revoke_access_token(token)


@kronos.register("*/30 * * * *")
def check_reminders(user_id):
    user = User.objects.get(id=user_id)
    for key in user.reminders.keys():
        if user.reminders[key]:
            check = check_for_time(
                user.timezone,
                core_consts.REMINDER_CONFIG[key]["HOUR"],
                core_consts.REMINDER_CONFIG[key]["MINUTE"],
            )
            if check:
                if key == core_consts.CALENDAR_REMINDER:
                    if hasattr(user, "nylas"):
                        _send_calendar_details(user_id)
                elif key == core_consts.WORKFLOW_REMINDER:
                    if datetime.datetime.today().weekday() == 4:
                        workflows = check_workflows_count(user.id)
                        if workflows["status"] and workflows["workflow_count"] <= 2:
                            emit_process_send_workflow_reminder(
                                str(user.id), workflows["workflow_count"]
                            )
                elif key == core_consts.MEETING_REMINDER_REP:
                    meetings = check_for_uncompleted_meetings(user.id)
                    logger.info(f"UNCOMPLETED MEETINGS FOR {user.email}: {meetings}")
                    if meetings["status"]:
                        emit_process_send_meeting_reminder(str(user.id), meetings["not_completed"])
                elif key == core_consts.MEETING_REMINDER_MANAGER and user.user_level == "Manager":
                    meetings = check_for_uncompleted_meetings(user.id, True)
                    if meetings["status"]:
                        emit_process_send_manager_reminder(str(user.id), meetings["not_completed"])

    return
