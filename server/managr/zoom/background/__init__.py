import logging
import json
import re
import pytz
import uuid
import random
from datetime import datetime

from django.conf import settings
from django.db.models import Q

from background_task import background
from rest_framework.exceptions import ValidationError

from managr.core.calendars import calendar_participants_from_zoom_meeting

from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
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
from ..models import ZoomAuthAccount, ZoomMeeting
from ..zoom_helper.models import ZoomAcct
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


def emit_send_meeting_summary(workflow_id):
    return _send_meeting_summary(workflow_id)


def emit_process_schedule_zoom_meeting(user, zoom_data):
    return _process_schedule_zoom_meeting(user, zoom_data)


def _send_zoom_error_message(user, meeting_uuid):
    if hasattr(user, "slack_integration"):
        user_slack_channel = user.slack_integration.channel
        slack_org_access_token = user.organization.slack_integration.access_token

        try:
            slack_requests.send_channel_message(
                user_slack_channel,
                slack_org_access_token,
                text=f"Unable to log meeting",
                block_set=get_block_set(
                    "error_message",
                    {
                        "message": "Unfortunately we cannot gather meeting details for (basic) free level zoom accounts"
                    },
                ),
            )
        except InvalidBlocksException as e:
            return logger.exception(
                f"Failed to gather meeting for user {user.email} with uuid {meeting_uuid}"
            )
        except InvalidBlocksFormatException as e:
            return logger.exception(
                f"Failed to gather meeting for user {user.email} with uuid {meeting_uuid}"
            )
        except UnHandeledBlocksException as e:
            return logger.exception(
                f"Failed to gather meeting for user {user.email} with uuid {meeting_uuid}"
            )
        except InvalidAccessToken as e:
            return logger.exception(
                f"Failed to gather meeting for user {user.email} with uuid {meeting_uuid}"
            )


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

    def get_domain(email):
        """Parse domain out of an email"""
        return email[email.index("@") + 1 :]

    # SEND SLACK IS USED FOR TESTING ONLY
    zoom_account = ZoomAuthAccount.objects.filter(user__id=user_id).first()
    user = zoom_account.user
    ignore_emails = user.organization.ignore_emails
    meeting = {}
    if zoom_account and not zoom_account.is_revoked:

        # emit the process

        while True:
            attempts = 1
            zoom_account = user.zoom_account
            try:
                meeting = zoom_account.helper_class.get_past_meeting(meeting_uuid)

                meeting.original_duration = original_duration
                logger.info(f"{meeting.original_duration}")
                if meeting.original_duration < 0:
                    # zoom weired bug where instance meetings get a random -1324234234 negative big int
                    meeting.original_duration = 0
                # this will fail if a user has a free account
                meeting = meeting.get_past_meeting_participants(zoom_account.access_token)

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
                _send_zoom_error_message(user, meeting_uuid)
                return

        #
        logger.info(
            f"    Got Meeting: {meeting} with ID: {meeting_uuid} for user {user.email} with user_id {str(user.id)}"
        )
        logger.info(f"    Meeting Start: {meeting.start_time}")
        logger.info(f"    Meeting End: {meeting.end_time}")

        # Gather Meeting Participants from Zoom and Calendar
        logger.info("Gathering meeting participants...")
        zoom_participants = meeting.as_dict.get("participants", [])

        logger.info(f"    Zoom Participants: {zoom_participants}")

        # Gather unique emails from the Zoom Meeting participants
        participants = []
        user = zoom_account.user

        org_email_domain = get_domain(user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )
        for email in ignore_emails:
            remove_users_with_these_domains_regex = (
                remove_users_with_these_domains_regex + r"|({})".format(email)
            )
        # re.search(remove_users_with_these_domains_regex, p.get("user_email", ""))
        #### first check if we care about this meeting before going forward
        should_register_this_meeting = [
            p
            for p in zoom_participants
            if not re.search(remove_users_with_these_domains_regex, p.get("user_email", ""))
        ]

        if not len(should_register_this_meeting):
            return

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)

        # If the user has their calendar connected through Nylas, find a
        # matching meeting and gather unique participant emails.
        calendar_participants = calendar_participants_from_zoom_meeting(meeting, user)

        # Combine the sets of participants. Filter out empty emails, meeting owner, and any
        # emails with domains that match the owner, which are teammates of the owner.
        logger.info(f"    Got list of participants: {participants}")

        for p in calendar_participants:
            if not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ) and p.get("user_email", "") not in ["", None]:
                if p.get("user_email", "") in memo.keys():
                    index = memo[p.get("user_email")]
                    participants[index]["name"] = p.get("name", "")
                else:
                    memo[p.get("user_email")] = len(participants)
                    participants.append(p)

        if settings.IN_DEV or settings.IN_STAGING:
            participants.append(
                {
                    "name": "Definitely NOT Mike",
                    "id": "",
                    "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
                }
            )
            participants.append(
                {
                    "name": "Looks like Mike",
                    "id": "",
                    "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
                }
            )
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
            user_slack_channel = (
                user.slack_integration.zoom_channel
                if user.slack_integration.zoom_channel
                else user.slack_integration.channel
            )
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
                    f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
                )
            except InvalidBlocksFormatException as e:
                return logger.exception(
                    f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
                )
            except UnHandeledBlocksException as e:
                return logger.exception(
                    f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
                )
            except InvalidAccessToken as e:
                return logger.exception(
                    f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
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
def _send_meeting_summary(workflow_id):

    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    organization = user.organization
    # only send meeting reviews for opps if the leadership box is selected or owner is selected
    send_summ_to_leadership = (
        workflow.forms.filter(template__form_type="UPDATE")
        .first()
        .saved_data.get("__send_recap_to_leadership")
    )
    send_summ_to_owner = (
        workflow.forms.filter(template__form_type="UPDATE")
        .first()
        .saved_data.get("__send_recap_to_reps")
    )
    if hasattr(workflow.meeting, "zoom_meeting_review") and workflow.resource_type == "Opportunity":
        slack_access_token = organization.slack_integration.access_token

        query = Q()
        if send_summ_to_leadership is not None:
            manager_list = send_summ_to_leadership.split(";")
            query |= Q(user_level="MANAGER", id__in=manager_list)
        if send_summ_to_owner is not None:
            rep_list = send_summ_to_owner.split(";")
            query |= Q(id__in=rep_list)

        user_list = (
            organization.users.filter(query)
            .filter(is_active=True)
            .distinct()
            .select_related("slack_integration")
        )
        for u in user_list:
            if hasattr(u, "slack_integration"):
                try:
                    slack_requests.send_channel_message(
                        u.slack_integration.channel,
                        slack_access_token,
                        text=f"Meeting Review Summary For {user.email} from meeting",
                        block_set=get_block_set("meeting_summary", {"w": workflow_id}),
                    )
                except InvalidBlocksException as e:
                    logger.exception(
                        f"Failed To Generate  Summary Interaction for user {str(workflow.id)} email {user.email} {e}"
                    )
                    continue
                except InvalidBlocksFormatException as e:
                    logger.exception(
                        f"Failed To Generate  Summary Interaction for user {str(workflow.id)} email {user.email} {e}"
                    )
                    continue
                except UnHandeledBlocksException as e:
                    logger.exception(
                        f"Failed To Generate  SummaryInteraction for user {str(workflow.id)} email {user.email} {e}"
                    )
                    continue
                except InvalidAccessToken as e:
                    logger.exception(
                        f"Failed To Generate  SummaryInteraction for workflow {str(workflow.id)} for user  email {user.email} {e}"
                    )
                    continue

                except Exception as e:
                    logger.exception(
                        f"Failed to Generate Summary Interaction for workflow  workflow {str(workflow.id)} for user  email {workflow.user.email} {e}"
                    )
                    continue
    return


@background(schedule=0)
def _process_confirm_compliance(obj):
    """Sends Compliance verification on app deauth to zoom"""
    ZoomAcct.compliance_api(json.loads(obj))
    return


def _process_schedule_zoom_meeting(user, zoom_data):
    # get details of meeting
    hour = int(zoom_data["meeting_hour"])
    if zoom_data["meeting_time"] == "PM" and hour != 12:
        hour = hour + 12
    formatted_time = f"{str(hour)}:{zoom_data['meeting_minute']}"
    try:
        res = user.zoom_account.helper_class.schedule_meeting(
            zoom_data["meeting_topic"],
            zoom_data["meeting_date"],
            formatted_time,
            int(zoom_data["meeting_duration"]),
        )
        return res
    except Exception as e:
        logger.warning(f"Zoom schedule error: {e}")
