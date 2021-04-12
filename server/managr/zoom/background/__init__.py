import logging
import json
import pytz
import uuid
import random
from datetime import datetime

from django.conf import settings

from background_task import background
from rest_framework.exceptions import ValidationError

from managr.core.calendars import calendar_participants_from_zoom_meeting

from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
)
from managr.slack.helpers.block_sets import get_block_set
from managr.organization.models import Contact, Account
from managr.opportunity.models import Opportunity, Lead
from managr.salesforce.adapter.models import ContactAdapter
from managr.salesforce.models import MeetingWorkflow
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.slack import constants as slack_consts
from managr.api import constants as api_consts

from .. import constants as zoom_consts
from ..zoom_helper.exceptions import TokenExpired, AccountSubscriptionLevel
from ..models import ZoomAuthAccount, ZoomMeeting, MeetingReview, ZoomMeetingReview
from ..serializers import ZoomMeetingSerializer

logger = logging.getLogger("managr")


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


def emit_refresh_zoom_token(zoom_account_id, schedule):
    # scedule can be seconds int or datetime string
    zoom_account_id = str(zoom_account_id)
    schedule = datetime.strptime(schedule, "%Y-%m-%dT%H:%M")
    return _refresh_zoom_token(zoom_account_id, schedule=schedule)


def emit_process_past_zoom_meeting(user_id, meeting_uuid, send_slack=True):
    return _get_past_zoom_meeting_details(user_id, meeting_uuid, send_slack)


def emit_kick_off_slack_interaction(user_id, managr_meeting_id):
    return _kick_off_slack_interaction(user_id, managr_meeting_id)


def emit_save_meeting_review(managr_meeting_id, data):
    return _save_meeting_review(managr_meeting_id, data)


def emit_send_meeting_summary(workflow_id):
    return _send_meeting_summary(workflow_id)


@background()
def _refresh_zoom_token(zoom_account_id):
    zoom_account = ZoomAuthAccount.objects.filter(id=zoom_account_id).first()
    if zoom_account and not zoom_account.is_revoked:
        try:
            zoom_account.regenerate_token()
        except TokenExpired:
            logger.exception(
                f"Failed to refresh zoom token for user {zoom_account.user.id},{zoom_account.user.email}"
            )
    elif zoom_account and zoom_account.is_revoked:
        logger.info(
            f"Did not attempt refresh for user because token was revoked, {zoom_account.user.id}, {zoom_account.user.email}"
        )
    return


@background(schedule=0)
def _get_past_zoom_meeting_details(user_id, meeting_uuid, original_duration, send_slack=True):
    logger.info("Retrieving past Zoom meeting details...")

    # SEND SLACK IS USED FOR TESTING ONLY
    zoom_account = ZoomAuthAccount.objects.filter(user__id=user_id).first()
    user = zoom_account.user
    meeting = {}
    if zoom_account and not zoom_account.is_revoked:

        # emit the process

        while True:
            attempts = 1
            zoom_account = user.zoom_account
            try:
                meeting = zoom_account.helper_class.get_past_meeting(meeting_uuid)
                meeting = meeting.get_past_meeting_participants(zoom_account.access_token)
                meeting.original_duration = original_duration
                logger.info(f"{meeting.original_duration}")
                if meeting.original_duration < 0:
                    # zoom weired bug where instance meetings get a random -1324234234 negative big int
                    meeting.original_duration = 0

                break
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to retrieve meeeting data user zoom token is expired and we were unable to regenerate a new one {str(user.id)} email {user.email}"
                    )
                else:
                    zoom_account.regenerate_token()
                    attempts += 1
            except AccountSubscriptionLevel:
                logger.info(
                    f"failed to list participants from zoom because {zoom_account.user.email} has a free zoom account"
                )

        #
        logger.info(f"    Got Meeting: {meeting} with ID: {meeting_uuid}")
        logger.info(f"    Meeting Start: {meeting.start_time}")
        logger.info(f"    Meeting End: {meeting.end_time}")

        # Gather Meeting Participants from Zoom and Calendar
        logger.info("Gathering meeting participants...")
        zoom_participants = meeting.as_dict.get("participants", [])

        logger.info(f"    Zoom Participants: {zoom_participants}")

        # Gather unique emails from the Zoom Meeting participants
        participants = []
        user = zoom_account.user
        for participant in zoom_participants:
            if participant not in participants and participant.get("user_email") != user.email:
                participants.append(participant)
            ### ADDING RANDOM USER FOR TESTING PURPOSES ONLY ###

        if settings.IN_DEV or settings.IN_STAGING:
            participants.append(
                {
                    "name": "testertesty baker",
                    "id": "",
                    "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
                }
            )
            participants.append(
                {
                    "name": "another1 baker",
                    "id": "",
                    "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
                }
            )
        # If the user has their calendar connected through Nylas, find a
        # matching meeting and gather unique participant emails.
        calendar_participants = calendar_participants_from_zoom_meeting(meeting, user)

        # Combine the sets of participants. Filter out empty emails, meeting owner, and any
        # emails with domains that match the owner, which are teammates of the owner.
        logger.info(f"    Got list of participants: {participants}")

        def get_domain(email):
            """Parse domain out of an email"""
            return email[email.index("@") + 1 :]

        participants = [
            p
            for p in [*participants, *calendar_participants]
            if p.get("user_email", "") not in ["", user.email]
            and get_domain(p.get("user_email", "")) != get_domain(user.email)
        ]

        contact_forms = []
        if len(participants):
            # Reduce to set of unique participant emails
            participant_emails = set([p.get("user_email") for p in participants])

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
                    if (
                        participant["user_email"] == contact.email
                        or participant["user_email"] == user.email
                    ):
                        del participants[index]
            new_contacts = list(
                filter(
                    lambda x: len(x.get("secondary_data", dict())) or x.get("email"),
                    list(
                        map(
                            lambda participant: {
                                **ContactAdapter(
                                    **dict(
                                        email=participant["user_email"],
                                        # these will only get stored if lastname and firstname are accessible from sf
                                        external_owner=user.salesforce_account.salesforce_id,
                                        secondary_data={
                                            "FirstName": _split_first_name(participant["name"]),
                                            "LastName": _split_last_name(participant["name"]),
                                            "Email": participant["user_email"],
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
                    lead = Lead.objects.filter(
                        email__in=participant_emails, owner__id=user.id
                    ).first()
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
                    logger.info(f"contact_id: {contact['id']}")
                    form = OrgCustomSlackFormInstance.objects.create(
                        user=user,
                        template=template,
                        resource_id="" if contact.get("id") in ["", None] else contact.get("id"),
                    )
                    contact_forms.append(form)
                    contact["_form"] = str(form.id)
            meeting.participants = meeting_contacts
            serializer = ZoomMeetingSerializer(data=meeting.as_dict)

            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except ValidationError as e:
                logger.exception(
                    f"Unable to save and initiate slack for meeting with uuid "
                    f"{meeting_uuid} because of error {json.dumps(e.detail)}"
                )
                return e

            # emit the event to start slack interaction
            workflow = MeetingWorkflow.objects.create(
                user=user,
                meeting=serializer.instance,
                operation_type=zoom_consts.MEETING_REVIEW_OPERATION,
                **meeting_resource_data,
            )

            workflow.forms.set(contact_forms)
            if send_slack:
                # sends false only for Mike testing
                workflow.begin_communication()
            return workflow


@background(schedule=0)
def _kick_off_slack_interaction(user_id, managr_meeting_id):
    # get meeting
    workflow = MeetingWorkflow.objects.filter(id=managr_meeting_id).first()
    if workflow:
        # get user
        user = workflow.user

        if hasattr(user, "slack_integration"):
            user_slack_channel = user.slack_integration.channel
            slack_org_access_token = user.organization.slack_integration.access_token
            block_set = get_block_set("initial_meeting_interaction", {"w": managr_meeting_id,},)
            try:
                res = slack_requests.send_channel_message(
                    user_slack_channel,
                    slack_org_access_token,
                    text=f"Your Meeting just ended {workflow.meeting.topic}",
                    block_set=block_set,
                )
            except InvalidBlocksException as e:
                return logger.exception(
                    f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
                )
            except InvalidBlocksFormatException as e:
                return logger.exception(
                    f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
                )
            except UnHandeledBlocksException as e:
                return logger.exception(
                    f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
                )

            # save slack message ts and channel id to remove if the meeting is deleted before being filled
            workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
            workflow.save()


def to_float(amount):
    if amount in ["", None]:
        return None
    try:
        return "{:.2f}".format(float(amount))
    except ValueError:
        return None


@background(schedule=0)
def _save_meeting_review(workflow_id):

    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    # get the create form
    meeting = workflow.meeting

    if not hasattr(meeting, "zoom_meeting_review"):

        # format data appropriately
        review_form = workflow.forms.filter(
            template__form_type=slack_consts.FORM_TYPE_MEETING_REVIEW
        ).first()

        # get data
        form_data = review_form.saved_data
        forecast_category = ""
        if form_data.get("ForecastCategoryName", None) not in ["", None]:
            forecast_category = form_data.get("ForecastCategoryName")
        elif form_data.get("ForecastCategory", None) not in ["", None]:
            forecast_category = form_data.get("ForecastCategory")
        # format data appropriately
        print(form_data.get("meeting_sentiment"))
        data = {
            "meeting": meeting,
            "resource_type": workflow.resource_type,
            "resource_id": workflow.resource_id,
            "forecast_category": forecast_category,
            "stage": form_data.get("StageName", ""),
            "meeting_comments": form_data.get("meeting_comments", ""),
            "meeting_type": form_data.get("meeting_type", ""),
            "meeting_sentiment": form_data.get("meeting_sentiment", ""),
            "amount": to_float(form_data.get("Amount", None)),
            "close_date": pytz.utc.localize(
                datetime.strptime(form_data.get("CloseDate", None), "%Y-%m-%d")
            )
            if form_data.get("CloseDate", None) not in ["", None]
            else None,
            "next_step": form_data.get("NextStep", ""),
        }

        return ZoomMeetingReview.objects.create(**data)


@background(schedule=0)
def _send_meeting_summary(workflow_id):

    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    if (
        hasattr(workflow.meeting, "zoom_meeting_review")
        and workflow.meeting.zoom_meeting_review.meeting_sentiment
        == zoom_consts.MEETING_SENTIMENT_GREAT
    ):

        user = workflow.user
        slack_access_token = user.organization.slack_integration.access_token

        user_list = user.organization.users.filter(user_level="MANAGER").select_related(
            "slack_integration"
        )
        try:
            for u in user_list:
                if hasattr(u, "slack_integration"):
                    slack_requests.send_channel_message(
                        u.slack_integration.channel,
                        slack_access_token,
                        text=f"Meeting Review Summary For {user.email} from meeting",
                        block_set=get_block_set("meeting_summary", {"w": workflow_id}),
                    )
        except InvalidBlocksException as e:
            return logger.exception(
                f"Failed To Generate Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
            )
        except InvalidBlocksFormatException as e:
            return logger.exception(
                f"Failed To Generate  Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
            )
        except UnHandeledBlocksException as e:
            return logger.exception(
                f"Failed To Generate Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
            )

        return
    return
