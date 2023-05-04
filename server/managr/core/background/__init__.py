import logging
import time
import random
import pytz
import uuid
import requests
import json
import httpx
from django.utils import timezone
from dateutil.parser import parse
import calendar
from datetime import datetime
from copy import copy
import re
from managr.api.emails import send_html_email
from background_task import background
from django.conf import settings
from managr.slack.helpers.utils import action_with_params

from django.db.models import Q
from managr.alerts.models import AlertConfig, AlertInstance, AlertTemplate
from managr.core import constants as core_consts
from managr.core.models import User
from managr.core.utils import get_summary_completion
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce.adapter.models import ContactAdapter
from managr.hubspot.adapter.models import HubspotContactAdapter
from managr.crm.models import BaseAccount, BaseOpportunity, BaseContact, ObjectField
from managr.meetings.models import Meeting
from managr.meetings.serializers import MeetingSerializer
from managr.slack.helpers import requests as slack_requests
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.slack import constants as slack_consts
from managr.slack.helpers import block_builders
from managr.opportunity.models import Lead
from managr.zoom.background import _split_first_name, _split_last_name
from managr.zoom.background import emit_kick_off_slack_interaction
from managr.crm.exceptions import TokenExpired as CRMTokenExpired
from managr.slack.helpers.block_sets import get_block_set
from managr.utils.client import Client
from managr.salesforce.routes import routes as sf_routes
from managr.hubspot.routes import routes as hs_routes
from managr.salesforce.background import emit_add_update_to_sf, emit_add_call_to_sf
from managr.hubspot.tasks import emit_add_update_to_hs, emit_add_call_to_hs

logger = logging.getLogger("managr")

if settings.IN_DEV:
    MANAGR_URL = "http://localhost:8080"
elif settings.IN_STAGING:
    MANAGR_URL = "https://staging.managr.ai"
else:
    MANAGR_URL = "https://app.managr.ai"

CRM_SWITCHER = {"SALESFORCE": sf_routes, "HUBSPOT": hs_routes}


def get_domain(email):
    """Parse domain out of an email"""
    return email[email.index("@") + 1 :]


def ADD_UPDATE_TO_CRM_FUNCTION(crm):
    if crm == "SALESFORCE":
        return emit_add_update_to_sf
    else:
        return emit_add_update_to_hs


def ADD_CALL_TO_CRM_FUNCTION(crm):
    if crm == "SALESFORCE":
        return emit_add_call_to_sf
    else:
        return emit_add_call_to_hs


#########################################################
# Emit functions
#########################################################


def emit_process_send_workflow_reminder(user_id, workflow_count):
    return _process_send_workflow_reminder(user_id, workflow_count)


def emit_process_add_calendar_id(user_id, verbose_name):
    return _process_add_calendar_id(user_id, verbose_name=verbose_name)


def emit_create_calendar_event(user, title, start_time, participants, meeting_link, description):
    return _process_create_calendar_event(
        user, title, start_time, participants, meeting_link, description
    )


def emit_process_send_meeting_reminder(user_id, verbose_name):
    return _process_send_meeting_reminder(user_id, verbose_name=verbose_name)


def emit_process_send_manager_reminder(user_id, not_completed):
    return _process_send_manager_reminder(user_id, not_completed)


def emit_generate_reminder_message(user_id, verbose_name):
    return generate_reminder_message(user_id, verbose_name=verbose_name)


def emit_process_calendar_meetings(user_id, verbose_name, slack_interaction=None, date=None):
    return _process_calendar_meetings(user_id, slack_interaction, date, verbose_name=verbose_name,)


# Functions for Scheduling Meeting
def emit_process_calendar_meeting_message(workflow_id, user_id, user_tz, meeting_end_times):
    return _process_calendar_meeting_message(workflow_id, user_id, user_tz, meeting_end_times)


def emit_timezone_tasks(user_id, verbose_name):
    return timezone_tasks(user_id, verbose_name=verbose_name)


def emit_process_workflow_config_check(user_id, verbose_name):
    return _process_workflow_config_check(user_id, verbose_name=verbose_name)


def emit_morning_refresh_message(user_id, verbose_name):
    return _morning_refresh_message(user_id, verbose_name=verbose_name)


def emit_process_check_trial_status(user_id, verbose_name):
    return _process_check_trial_status(user_id, verbose_name=verbose_name)


def emit_process_submit_chat_prompt(user_id, prompt, resource_type, context):
    return _process_submit_chat_prompt(user_id, prompt, resource_type, context)


def emit_process_submit_chat_note(user_id, prompt, resource_type, context):
    return _process_submit_chat_note(user_id, prompt, resource_type, context)


def emit_process_send_email_draft(payload, context):
    return _process_send_email_draft(payload, context)


def emit_process_send_next_steps(payload, context):
    return _process_send_next_steps(payload, context)


def emit_process_send_summary_to_dm(payload, context):
    return _process_send_summary_to_dm(payload, context)


#########################################################
# Helper functions
#########################################################


def should_register_this_meetings(user_id, processed_data):
    user = User.objects.get(id=user_id)
    ignore_emails = user.organization.ignore_emails
    # Getting all participants from meetings and all their emails
    all_participants = processed_data.get("participants")
    all_emails = []
    for participant in all_participants:
        participants_email = participant.get("email")
        all_emails.append(participants_email)
    # all emails are now in participant_emails
    # Gather Meeting Participants from Zoom and Calendar
    # Gather unique emails from the Zoom Meeting participants
    user = User.objects.get(id=user_id)
    org_email_domain = get_domain(user.email)
    remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
        org_email_domain
    )
    for email in ignore_emails:
        if len(email):
            remove_users_with_these_domains_regex = (
                remove_users_with_these_domains_regex + r"|({})".format(email)
            )
    # re.search(remove_users_with_these_domains_regex, p.get("email", ""))
    # first check if we care about this meeting before going forward
    should_register_this_meeting = [
        p
        for p in all_participants
        if not re.search(remove_users_with_these_domains_regex, p.get("email", ""))
    ]
    if not len(should_register_this_meeting):
        return False
    return True


def _process_create_calendar_event(
    user, title, start_time, participants, meeting_link, description
):
    """
    Created a calendar event for and attaches meeting link.
    Used in Schedule Zoom Meeting action.
    """

    converted_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S%z")
    unix_start_time = int(converted_time.timestamp())
    unix_end_time = unix_start_time + 1800
    try:
        res = user.nylas.schedule_meeting(
            title, unix_start_time, unix_end_time, participants, meeting_link, description
        )
        return res
    except Exception as e:
        logger.info(f"Nylas warning {e}")


def check_for_time(tz, hour, minute):
    user_timezone = pytz.timezone(tz)
    currenttime = datetime.today().time()
    current = pytz.utc.localize(datetime.combine(datetime.today(), currenttime)).astimezone(
        user_timezone
    )
    min = 00 if minute >= 30 else 30
    hr = hour - 1 if minute < 30 else hour
    return current < current.replace(
        hour=hour, minute=minute, second=0, microsecond=0
    ) and current > current.replace(hour=hr, minute=min, second=0, microsecond=0)


def check_for_uncompleted_meetings(user_id, org_level=False):
    user = User.objects.get(id=user_id)
    if hasattr(user, "slack_integration"):
        if org_level:
            users = User.objects.filter(
                slack_integration__recap_receivers__contains=[user.slack_integration.slack_id]
            )
            not_completed = []
            for user in users:
                total_meetings = MeetingWorkflow.objects.filter(user=user.id).filter(
                    datetime_created__contains=datetime.today().date(),
                )
                user_not_completed = [
                    meeting for meeting in total_meetings if meeting.progress == 0
                ]

                if len(user_not_completed):

                    not_completed.extend(user_not_completed)
        else:
            # This will be for the reps
            total_meetings = MeetingWorkflow.objects.filter(user=user.id).filter(
                datetime_created__contains=datetime.today().date()
            )
            not_completed = [meeting for meeting in total_meetings if meeting.progress == 0]
        if len(not_completed):
            return {"status": True, "uncompleted": len(not_completed)}
    return {"status": False}


def to_date_string(date):
    if not date:
        return "n/a"
    d = datetime.strptime(date, "%Y-%m-%d")
    return d.strftime("%a, %B %d, %Y")


def check_workflows_count(user_id):
    workflows = AlertConfig.objects.filter(template__user=user_id)
    if len(workflows):
        return {"status": True, "workflow_count": len(workflows)}
    return {"status": False}


def _process_calendar_details(user_id, date):
    user = User.objects.get(id=user_id)
    events = user.nylas._get_calendar_data(date)
    if events:
        return events
    else:
        return None


def sync_contacts(contacts, user_id):
    from managr.crm.routes import model_routes

    user = User.objects.get(id=user_id)
    model_class = model_routes(user.crm)["Contact"]["model"]
    serializer_class = model_routes(user.crm)["Contact"]["serializer"]
    for item in contacts:
        existing = model_class.objects.filter(integration_id=item.integration_id).first()
        if existing:
            serializer = serializer_class(data=item.as_dict, instance=existing)
        else:
            serializer = serializer_class(data=item.as_dict)
        # check if already exists and update
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.exception(f"Error saving contact in zoom flow: {e}")
            continue
        serializer.save()
        # if contact.secondary_data["associatedcompanyid"]
        if user.crm == "HUBSPOT":
            if (
                isinstance(item.secondary_data["num_associated_deals"], str)
                and len(item.secondary_data["num_associated_deals"]) > 0
            ):
                associated_deals = user.crm_account.adapter_class.get_associated_resource(
                    "Contact", "Deal", item.integration_id
                )["results"][0]["to"]
                filtered_ids = [deal["id"] for deal in associated_deals]
                synced_deals = BaseOpportunity.objects.filter(integration_id__in=filtered_ids)
                for deal in synced_deals:
                    deal.contacts.add(serializer.instance)
                    deal.save()
    return


def CONTACT_FILTERS(crm, emails):
    if crm == "HUBSPOT":
        return [{"propertyName": "email", "operator": "IN", "values": emails,}]
    else:
        email_string = "','".join(emails)
        return [f"AND Email IN ('{email_string}')"]


def meeting_prep(processed_data, user_id):
    user = User.objects.get(id=user_id)
    ignore_emails = user.organization.ignore_emails
    # Getting all participants from meetings and all their emails
    all_participants = processed_data.get("participants")
    all_emails = []
    for participant in all_participants:
        participants_email = participant.get("email")
        all_emails.append(participants_email)

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
    # first check if we care about this meeting before going forward
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
        participant_emails = set([p.get("user_email") for p in participants])
        attempts = 1
        while True:
            try:
                crm_contacts = user.crm_account.adapter_class.list_resource_data(
                    "Contact", filter=CONTACT_FILTERS(user.crm, list(participant_emails)),
                )
                break
            except CRMTokenExpired:
                if attempts >= 5:
                    break
                else:
                    sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                    time.sleep(sleep)
                    user.crm_account.regenerate_token()
                    attempts += 1
        sync_contacts(crm_contacts, str(user.id))
    meeting_contacts = []
    # find existing contacts
    existing_contacts = BaseContact.objects.filter(
        email__in=participant_emails, owner__organization__id=user.organization.id
    ).exclude(email=user.email)
    meeting_resource_data = dict(resource_id="", resource_type="")
    opportunity = BaseOpportunity.objects.filter(
        contacts__email__in=participant_emails, owner__id=user.id
    ).first()
    if opportunity:
        meeting_resource_data["resource_id"] = str(opportunity.id)
        meeting_resource_data["resource_type"] = (
            "Opportunity" if user.crm == "SALESFORCE" else "Deal"
        )
        existing_contacts = existing_contacts.filter(opportunities__in=[str(opportunity.id)])
    else:
        account = BaseAccount.objects.filter(
            contacts__email__in=participant_emails, owner__id=user.id,
        ).first()
        if account:
            meeting_resource_data["resource_id"] = str(account.id)
            meeting_resource_data["resource_type"] = (
                "Account" if user.crm == "SALESFORCE" else "Company"
            )
            existing_contacts = existing_contacts.filter(account=account.id)
        else:
            lead = Lead.objects.filter(email__in=participant_emails, owner__id=user.id).first()
            if lead:
                meeting_resource_data["resource_id"] = str(lead.id)
                meeting_resource_data["resource_type"] = "Lead"

    # convert all contacts to model representation and remove from array
    for contact in existing_contacts:
        formatted_contact = contact.adapter_class.as_dict
        # create a form for each contact to save to workflow
        meeting_contacts.append(formatted_contact)
        for index, participant in enumerate(participants):
            if participant["email"] == contact.email or participant["email"] == User.email:
                del participants[index]
    contact_adapter = ContactAdapter if user.crm == "SALESFORCE" else HubspotContactAdapter
    new_contacts = list(
        filter(
            lambda x: len(x.get("secondary_data", dict())) or x.get("email"),
            list(
                map(
                    lambda participant: {
                        **contact_adapter(
                            **dict(
                                email=participant["email"],
                                # these will only get stored if lastname and firstname are accessible from sf
                                external_owner=user.crm_account.crm_id,
                                secondary_data={
                                    f"{'FirstName' if user.crm == 'SALESFORCE' else 'FirstName'}": _split_first_name(
                                        participant["name"]
                                    ),
                                    f"{'LastName' if user.crm == 'SALESFORCE' else 'firstname'}": _split_last_name(
                                        participant["name"]
                                    ),
                                    f"{'Email' if user.crm == 'SALESFORCE' else 'email'}": participant[
                                        "email"
                                    ],
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

    for contact in meeting_contacts:
        contact["_tracking_id"] = str(uuid.uuid4())
        form_type = (
            slack_consts.FORM_TYPE_UPDATE
            if contact["id"] not in ["", None]
            else slack_consts.FORM_TYPE_CREATE
        )
        template = OrgCustomSlackForm.objects.filter(
            form_type=form_type, resource=slack_consts.FORM_RESOURCE_CONTACT, team=user.team
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
    processed_data.pop("participants")
    meeting_data = {
        **processed_data,
        "user": user,
    }
    meeting_serializer = MeetingSerializer(data=meeting_data)
    meeting_serializer.is_valid(raise_exception=True)
    meeting_serializer.save()
    resource_check = meeting_resource_data.get("resource_id", None)
    meeting = Meeting.objects.filter(user=user).first()
    meeting.participants = meeting_contacts
    meeting.save()
    # Conditional Check for Zoom meeting or Non-Zoom Meeting
    meeting_workflow = MeetingWorkflow.objects.create(
        operation_type="MEETING_REVIEW",
        meeting=meeting,
        user=user,
        resource_id=meeting_resource_data["resource_id"],
        resource_type=meeting_resource_data["resource_type"],
    )
    meeting_workflow.forms.set(contact_forms)
    if resource_check:
        meeting_workflow.add_form(
            meeting_resource_data["resource_type"], slack_consts.FORM_TYPE_UPDATE,
        )
    if user.has_slack_integration:
        if not user.has_zoom_integration or (
            user.has_zoom_integration and "Zoom" not in meeting.provider
        ):
            meeting_end_time = meeting.end_time.strftime("%m/%d/%Y, %H:%M:%S")
            workflow_id = str(meeting_workflow.id)
            user_id = str(user.id)
            user_tz = str(user.timezone)
            emit_process_calendar_meeting_message(workflow_id, user_id, user_tz, meeting_end_time)
    return


def process_current_alert_list(user_id):
    user = User.objects.get(id=user_id)
    configs = AlertConfig.objects.filter(Q(template__user=user.id, template__is_active=True))
    alert_blocks = []
    if configs:
        for config in configs:
            instance_check = AlertInstance.objects.filter(
                Q(
                    config=config.id,
                    datetime_created__date=datetime.today(),
                    form_instance__isnull=True,
                )
            )
            if len(instance_check):
                text = f"{len(instance_check)} {config.template.title} left to complete"
                if config.recipients[0] not in ["SELF", "OWNER"]:
                    channel_info = slack_requests.get_channel_info(
                        user.organization.slack_integration.access_token, config.recipients[0]
                    )
                    name = channel_info.get("channel").get("name")
                    text += f": #{name}"
                alert_blocks = [
                    *alert_blocks,
                    block_builders.simple_section(text, "mrkdwn"),
                ]
    return alert_blocks


#########################################################
# BACKGROUND TASKS
#########################################################


@background()
def _process_calendar_meetings(user_id, slack_int, date):
    user = User.objects.get(id=user_id)
    if user.has_nylas_integration:
        try:
            processed_data = _process_calendar_details(user_id, date)
        except Exception as e:
            logger.exception(f"Pulling calendar data error for {user.email} <ERROR: {e}>")
            processed_data = None
        if processed_data is not None:
            workflows = MeetingWorkflow.objects.for_user(user, date)
            slack_interaction_check = set(
                [
                    workflow.slack_interaction
                    for workflow in workflows
                    if len(workflow.slack_interaction) > 0
                ]
            )
            if len(list(slack_interaction_check)):
                slack_int = list(slack_interaction_check)[0]
            for event in processed_data:
                id = event.get("id", None)
                workflow_check = workflows.filter(meeting__meeting_id=id).first()
                register_check = should_register_this_meetings(user_id, event)
                meeting_data = {
                    **event,
                    "user": user,
                }
                if workflow_check is None and register_check:
                    meeting_serializer = MeetingSerializer(data=meeting_data)
                    meeting_serializer.is_valid(raise_exception=True)
                    meeting_serializer.save()
                    meeting = Meeting.objects.filter(user=user).first()
                    meeting.save()
                    # Conditional Check for Zoom meeting or Non-Zoom Meeting
                    meeting_workflow = MeetingWorkflow.objects.create(
                        operation_type="MEETING_REVIEW", meeting=meeting, user=user,
                    )
                else:
                    if workflow_check:
                        meeting_serializer = MeetingSerializer(
                            instance=workflow_check.meeting, data=meeting_data
                        )
                        meeting_serializer.is_valid(raise_exception=True)
                        meeting_serializer.save()
            blocks = get_block_set("paginated_meeting_blockset", {"u": str(user.id), "date": date})
        else:
            todays_date = datetime.today() if date is None else datetime.strptime(date, "%Y-%m-%d")
            user_timezone = pytz.timezone(user.timezone)
            todays_date = pytz.utc.localize(todays_date).astimezone(user_timezone)
            date_string = f":calendar: Today's Meetings: *{todays_date.month}/{todays_date.day}/{todays_date.year}*"
            blocks = [
                block_builders.section_with_button_block(
                    "Sync Calendar",
                    "sync_calendar",
                    date_string,
                    action_id=f"{slack_consts.MEETING_REVIEW_SYNC_CALENDAR}?u={str(user.id)}&date={str(todays_date.date())}",
                ),
                {"type": "divider"},
                block_builders.simple_section(
                    "You don't have any meeting for today... If that changes, click 'Sync Calendar'"
                ),
            ]
        try:
            if slack_int:
                timestamp, channel = slack_int.split("|")
                slack_res = slack_requests.update_channel_message(
                    channel,
                    timestamp,
                    user.organization.slack_integration.access_token,
                    block_set=blocks,
                )
                slack_interaction = slack_int
            else:
                slack_res = slack_requests.send_channel_message(
                    user.slack_integration.zoom_channel,
                    user.organization.slack_integration.access_token,
                    block_set=blocks,
                )
                slack_interaction = f"{slack_res['ts']}|{slack_res['channel']}"
            workflows = MeetingWorkflow.objects.for_user(user, date)
            workflows.update(slack_interaction=slack_interaction)
        except Exception as e:
            logger.exception(f"Failed to send reminder message to {user.email} due to {e}")
    return


@background()
def _process_calendar_meeting_message(workflow_id, user_id, user_tz, meeting_end_time):
    end_time_timestamp = datetime.strptime(meeting_end_time, "%m/%d/%Y, %H:%M:%S")
    current_time = datetime.now()
    if current_time > end_time_timestamp:
        seconds = int(current_time.timestamp())
        time_difference = "Meeting passed current time"
    else:
        time_difference = end_time_timestamp - current_time
        seconds = time_difference.total_seconds()
        seconds = int(seconds)
    # logger.info(
    #     f"MEETING SCHEDULER: \n END TIME: {end_time_timestamp}\n CURRENT TIME: {current_time} \n TIME DIFFERENCE: {time_difference}"
    # )
    return emit_kick_off_slack_interaction(user_id, workflow_id, schedule=seconds)


@background()
def _process_send_workflow_reminder(user_id, workflow_count):
    user = User.objects.get(id=user_id)
    if hasattr(user, "slack_integration"):
        access_token = user.organization.slack_integration.access_token
        blocks = get_block_set("workflow_reminder", {"workflow_count": workflow_count})

        try:
            slack_requests.send_channel_message(
                user.slack_integration.channel,
                access_token,
                text="Workflow Reminder",
                block_set=blocks,
            )
        except Exception as e:
            logger.exception(f"Failed to send reminder message to {user.email} due to {e}")
    else:
        logger.exception(f"{user.email} does not have a slack account")


@background()
def _process_send_meeting_reminder(user_id):
    user = User.objects.get(id=user_id)
    if hasattr(user, "slack_integration"):
        access_token = user.organization.slack_integration.access_token
        workflows = MeetingWorkflow.objects.for_user(user)
        uncompleted = [workflow for workflow in workflows if workflow.progress < 100]
        if len(uncompleted):
            blocks = get_block_set(
                "meeting_reminder", {"not_completed": len(uncompleted), "u": str(user.id)}
            )
            try:
                slack_requests.send_channel_message(
                    user.slack_integration.channel,
                    access_token,
                    text="Meeting Reminder",
                    block_set=blocks,
                )
            except Exception as e:
                logger.exception(f"Failed to send reminder message to {user.email} due to {e}")
    else:
        logger.exception(f"{user.email} does not have a slack account")
    return


@background()
def _process_send_manager_reminder(user_id, not_completed):
    user = User.objects.get(id=user_id)
    if hasattr(user, "slack_integration"):
        access_token = user.organization.slack_integration.access_token
        name = user.first_name if hasattr(user, "first_name") else user.full_name
        blocks = get_block_set(
            "manager_meeting_reminder", {"not_completed": not_completed, "name": name}
        )
        try:
            slack_requests.send_channel_message(
                user.slack_integration.channel,
                access_token,
                text="Meeting Reminder",
                block_set=blocks,
            )
        except Exception as e:
            logger.exception(f"Failed to send reminder message to {user.email} due to {e}")
    else:
        logger.exception(f"{user.email} does not have a slack account")


@background(schedule=0)
def generate_reminder_message(user_id):
    user = User.objects.get(id=user_id)
    #   check user_level for manager
    meeting = []
    alert_blocks = process_current_alert_list(user_id)
    if user.user_level == "MANAGER":
        meetings = check_for_uncompleted_meetings(user.id, True)
        if meetings["status"]:
            name = user.first_name if hasattr(user, "first_name") else user.full_name
            meeting = get_block_set(
                "manager_meeting_reminder",
                {"u": str(user.id), "not_completed": meetings["uncompleted"], "name": name,},
            )
    else:
        meetings = check_for_uncompleted_meetings(user.id)
        if meetings["status"]:
            meeting = get_block_set(
                "meeting_reminder", {"u": str(user.id), "not_completed": meetings["uncompleted"]}
            )
    title = (
        "*Reminder:* Your team has uncompleted tasks from today"
        if user.user_level == "MANAGER"
        else "*Reminder:* Uncompleted tasks from today"
    )
    if len(meeting) or len(alert_blocks):
        try:
            slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                block_set=[
                    block_builders.simple_section(title, "mrkdwn"),
                    {"type": "divider"},
                    *meeting,
                    *alert_blocks,
                ],
            )
        except Exception as e:
            logger.exception(f"Failed to send reminder message to {user.email} due to {e}")
    else:
        return


@background()
def _process_workflow_config_check(user_id):
    from managr.alerts.serializers import AlertConfigWriteSerializer

    user = User.objects.get(id=user_id)
    if user.user_level == "MANAGER":
        templates = AlertTemplate.objects.filter(user=user)
        for template in templates:
            configs = template.configs.all()
            if "REPS" in template.target_reference:
                config_targets = []
                [config_targets.extend(config.alert_targets) for config in configs]
                config_reference = configs[0]
                new_config_base = {
                    "recurrence_frequency": config_reference.recurrence_frequency,
                    "recurrence_day": config_reference.recurrence_day,
                    "recurrence_days": config_reference.recurrence_days,
                    "recipient_type": config_reference.recipient_type,
                    "template": config_reference.template.id,
                }
                all_reps = User.objects.filter(
                    organization=user.organization,
                    user_level="REP",
                    slack_integration__isnull=False,
                )
                for rep in all_reps:
                    if str(rep.id) not in config_targets:
                        config_copy = copy(new_config_base)
                        config_copy["alert_targets"] = [str(rep.id)]
                        config_copy["recipients"] = [
                            rep.slack_integration.zoom_channel
                            if rep.slack_integration.zoom_channel
                            else rep.slack_integration.channel
                        ]
                        try:
                            serializer = AlertConfigWriteSerializer(
                                data=config_copy, context=template
                            )
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                        except Exception as e:
                            logger.exception(f"CONFIG CHECK CREATING CONFIG ERROR: {e}")
                            continue
        return
    else:
        return


@background()
def _process_check_trial_status(user_id):
    user = User.objects.get(id=user_id)
    today = datetime.now().astimezone(pytz.UTC)
    days_active = (today - user.organization.datetime_created).days
    if days_active > 60 and not user.organization.is_paid:
        logger.info(f"Organization {user.organization.name} has expired and is being deactivated")
        user.organization.deactivate_org()
        subject = f"Trial {user.organization.name} Expiration"
        recipient = ["support@mymanagr.com"]
        send_html_email(
            subject,
            "core/email-templates/deactivated-trial.html",
            settings.SERVER_EMAIL,
            recipient,
            context={"name": user.organization.name},
        )
    return


####################################################
# TIMEZONE TASK FUNCTIONS
####################################################

TIMEZONE_TASK_FUNCTION = {
    core_consts.NON_ZOOM_MEETINGS: emit_process_calendar_meetings,
    core_consts.CALENDAR_CHECK: emit_process_add_calendar_id,
    core_consts.WORKFLOW_CONFIG_CHECK: emit_process_workflow_config_check,
    core_consts.MORNING_REFRESH: emit_morning_refresh_message,
    core_consts.MEETING_REMINDER: emit_process_send_meeting_reminder,
    # core_consts.TRIAL_STATUS: emit_process_check_trial_status,
}


def TESTING_TIMEZONE_TIMES(user_id):
    user = User.objects.get(id=user_id)
    keys = TIMEZONE_TASK_FUNCTION.keys()
    user_timezone = pytz.timezone(user.timezone)
    currenttime = datetime.today().time()
    current = pytz.utc.localize(datetime.combine(datetime.today(), currenttime)).astimezone(
        user_timezone
    )
    minute = 30 if current.minute <= 30 else 00
    hour = current.hour if minute == 30 else current.hour + 1
    time_obj = {"HOUR": hour, "MINUTE": minute}
    obj = {}
    for name in keys:
        obj[name] = time_obj
    return obj


@background()
def timezone_tasks(user_id):
    if settings.IN_DEV:
        tasks = TESTING_TIMEZONE_TIMES(user_id)
    else:
        tasks = core_consts.TIMEZONE_TASK_TIMES
    user = User.objects.get(id=user_id)
    # logger_str = f"{user.email} - {datetime.now()} - "
    for key in tasks.keys():
        # key_str = f"{key}: False, "
        check = check_for_time(user.timezone, tasks[key]["HOUR"], tasks[key]["MINUTE"])
        if check:
            # key_str = f"{key}: True, "
            verbose_name = f"{key}-{user.email}-{str(uuid.uuid4())}"
            TIMEZONE_TASK_FUNCTION[key](user_id, verbose_name)
        # logger_str += key_str
    # logger.info(logger_str)
    return


@background()
def _process_add_calendar_id(user_id):
    user = User.objects.get(id=user_id)
    if hasattr(user, "nylas") and user.nylas.event_calendar_id is None:
        headers = dict(Authorization=f"Bearer {user.nylas.access_token}")
        calendars = requests.get(
            f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.CALENDAR_URI}", headers=headers,
        ).json()

        email_check = [cal for cal in calendars if cal["name"] == user.email]
        calendar = [cal for cal in calendars if cal["read_only"] is False]
        if len(email_check):
            calendar_id = email_check[0]["id"]
        else:
            if len(calendar):
                calendar_id = calendar[0]["id"]
            else:
                calendar_id = None
        # logger.info(
        #     textwrap.dedent(
        #         f"""
        #     ------------------------------------
        #     NYLAS CALENAR ACCOUNT CREATION INFO: \n
        #     CALENDAR INFO:{calendar}\n
        #     EMAIL CHECK: {email_check} \n
        #     CALENDAR CHECK: {calendar} \n
        #     FOUND CALENDAR ID: {calendar_id}\n
        #     ------------------------------------"""
        #     )
        # )
        if calendar_id:
            user.nylas.event_calendar_id = calendar_id
            user.nylas.save()
        else:
            logger.info(f"COULD NOT FIND A CALENDAR ID FOR {user.email}")
        return


@background()
def _morning_refresh_message(user_id):
    user = User.objects.get(id=user_id)

    if user.has_slack_integration and user.user_level == "REP":
        url = f"{MANAGR_URL}/pipelines"
        blocks = [
            block_builders.section_with_button_block(
                "View in Managr",
                "NONE",
                f"Hey {user.first_name}, your pipeline has been updated, take a look",
                url=url,
                style="primary",
            )
        ]
        try:
            slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
        except Exception as e:
            logger.exception(f"Failed to send reminder message to {user.email} due to {e}")
    return


@background()
def _process_change_team_lead(user_id):
    user = User.objects.get(id=user_id)
    try:
        user.team.change_team_lead(user, True)
        user.make_team_lead = False
        user.save()
    except Exception as e:
        logger.exception(f"Failed to change team lead for {user.team.name} due to <{e}>")
    return


def swap_submitted_data_labels(data, fields):
    api_key_data = {}
    for label in data.keys():
        try:
            field_list = fields.filter(label__icontains=label)
            field = None
            for field_value in field_list:
                if len(field_value.label) == len(label):
                    field = field_value
                    break
            api_key_data[field.api_name] = data[label]
        except Exception as e:
            continue
    return api_key_data


WORD_TO_NUMBER = {
    "a": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

TIME_TO_NUMBER = {"week": 7, "weeks": 7, "month": 30, "months": 30, "year": 365, "tomorrow": 1}
DAYS_TO_NUMBER = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def convert_date_string(date_string, value):
    if value is None:
        value = datetime.now().date()
    else:
        value = value.split("T")[0]
    split_date_string = date_string.lower().split(" ")
    time_key = None
    number_key = 1
    if any("push" in s for s in split_date_string) or any("move" in s for s in split_date_string):
        for key in split_date_string:
            if key in TIME_TO_NUMBER.keys():
                time_key = TIME_TO_NUMBER[key]
            if key in WORD_TO_NUMBER:
                number_key = WORD_TO_NUMBER[key]
    elif any(key in split_date_string for key in DAYS_TO_NUMBER.keys()):
        for key in split_date_string:
            if key in DAYS_TO_NUMBER.keys():
                current = datetime.now()
                start = current - timezone.timedelta(days=current.weekday())
                day_value = start + timezone.timedelta(days=DAYS_TO_NUMBER[key])
                if any("next" in s for s in split_date_string):
                    day_value = day_value + timezone.timedelta(days=7)
                logger.info(f"CONVERT DATE STRING DEBUGGER: DAY SPECIFIC {day_value}")
                return day_value
    elif any("end" in s for s in split_date_string):
        if any("week" in s for s in split_date_string):
            current = datetime.strptime(value, "%Y-%m-%d")
            start = current - timezone.timedelta(days=current.weekday())
            logger.info(
                f"CONVERT DATE STRING DEBUGGER: END WEEK {start + timezone.timedelta(days=4)}"
            )
            return start + timezone.timedelta(days=4)
        elif any("month" in s for s in split_date_string):
            current = datetime.strptime(value, "%Y-%m-%d")
            last_of_month = calendar.monthrange(current.year, current.month)[1]
            logger.info(
                f"CONVERT DATE STRING DEBUGGER: END MONTH {current.replace(day=last_of_month)}"
            )
            return current.replace(day=last_of_month)
    elif any("week" in s for s in split_date_string):
        current = datetime.strptime(value, "%Y-%m-%d")
        logger.info(f"CONVERT DATE STRING DEBUGGER: WEEK {current + timezone.timedelta(days=7)}")
        return current + timezone.timedelta(days=7)
    if "back" in date_string:
        new_value = datetime.strptime(value, "%Y-%m-%d") - timezone.timedelta(
            days=(time_key * number_key)
        )
        logger.info(f"CONVERT DATE STRING DEBUGGER: END IF {new_value}")
    else:
        if time_key:
            new_value = datetime.strptime(value, "%Y-%m-%d") + timezone.timedelta(
                days=(time_key * number_key)
            )
        else:
            try:
                date_parsed = parse(date_string)
                new_value = date_parsed
            except Exception as e:
                print(e)
                new_value = value
        logger.info(f"CONVERT DATE STRING DEBUGGER: BACK ELSE {new_value}")
    return new_value


def background_create_resource(crm):
    from managr.salesforce.background import _process_create_new_resource
    from managr.hubspot.tasks import _process_create_new_hs_resource

    if crm == "SALESFORCE":
        return _process_create_new_resource
    else:
        return _process_create_new_hs_resource


def clean_prompt_return_data(data, fields, crm, resource=None):
    cleaned_data = dict(data)
    notes = cleaned_data.pop("meeting_comments", None)
    subject = cleaned_data.pop("meeting_type", None)
    for key in cleaned_data.keys():
        try:
            field = fields.get(api_name=key)
            if resource and field.api_name in ["Name", "dealname"]:
                cleaned_data[key] = resource.secondary_data[key]
            if cleaned_data[key] is None or cleaned_data[key] == "":
                if resource:
                    cleaned_data[key] = resource.secondary_data[key]
                continue
            elif field.data_type == "TextArea":
                if resource and data[key] is not None:
                    current_value = (
                        resource.secondary_data[key]
                        if resource.secondary_data[key] is not None
                        else " "
                    )
                    cleaned_data[key] = f"{data[key]}\n\n{current_value}"
            elif field.data_type in ["Date", "DateTime"]:
                data_value = data[key]
                current_value = resource.secondary_data[key] if resource else None
                new_value = convert_date_string(data_value, current_value)
                if isinstance(new_value, str):
                    if resource:
                        cleaned_data[key] = resource.secondary_data[key]
                    else:
                        cleaned_data[key] = None
                else:
                    cleaned_data[key] = (
                        str(new_value.date())
                        if crm == "SALESFORCE"
                        else (str(new_value.date()) + "T00:00:00.000Z")
                    )
            elif field.api_name == "dealstage":
                if resource:
                    pipeline = field.options[0][resource.secondary_data["pipeline"]]
                    if pipeline:
                        stage_value = data[key].lower()
                        stage = [
                            stage
                            for stage in pipeline["stages"]
                            if stage["label"].lower() == stage_value
                        ]
                        if len(stage):
                            cleaned_data[key] = stage[0]["id"]
                        else:
                            cleaned_data[key] = resource.secondary_data["dealstage"]
            elif field.api_name in ["Amount", "amount"]:
                if isinstance(cleaned_data[key], int):
                    continue
                amount = cleaned_data[key]
                if "k" in amount:
                    amount = amount.replace("k", "000.0")
                if "$" in amount:
                    amount = amount.replace("$", "")
                cleaned_data[key] = amount
            elif field.data_type == "Picklist":
                if crm == "HUBSPOT":
                    options = field.options
                else:
                    options = field.crm_picklist_options.values
                value_found = False
                for value in options:
                    lowered_value = cleaned_data[key].lower()
                    current_value_label = value["label"].lower()
                    if lowered_value in current_value_label:
                        value_found = True
                        cleaned_data[key] = value["value"]
                if not value_found:
                    if resource:
                        cleaned_data[key] = resource.secondary_data[key]
                    else:
                        cleaned_data[key] = None
        except ValueError:
            continue
    cleaned_data["meeting_comments"] = notes
    cleaned_data["meeting_type"] = subject
    logger.info(f"CLEAN PROMPT DEBUGGER: {cleaned_data}")
    return cleaned_data


def set_owner_field(resource, crm):
    if resource in ["Opportunity", "Account", "Contact"] and crm == "SALESFORCE":
        return "Owner ID"
    elif resource == "Company":
        return "Company owner"
    elif resource == "Contact" and crm == "HUBSPOT":
        return "Contact owner"
    elif resource == "Deal":
        return "Deal owner"
    return None


def set_name_field(resource, crm):
    if resource in ["Opportunity", "Account"]:
        return "Name"
    elif resource == "Company":
        return "Company name"
    elif resource == "Deal":
        return "Deal Name"
    elif resource == "Contact":
        return "Email"
    return None


def clean_prompt_string(prompt_string):
    cleaned_string = (
        prompt_string[prompt_string.index("{") : prompt_string.index("}") + 1]
        .replace("\n\n", "")
        .replace("\n ", "")
        .replace("\n", "")
        .replace("  ", "")
        .replace("', '", '", "')
        .replace("': '", '": "')
    )
    while "{  " in cleaned_string:
        cleaned_string = cleaned_string.replace("{  ", "{ ")
    cleaned_string = cleaned_string.replace("{ '", '{ "').replace("'}", '"}')
    return cleaned_string


def correct_data_keys(data):
    if "Company Name" in data.keys():
        data["Company name"] = data["Company Name"]
        del data["Company Name"]
    return data


def name_list_processor(resource_list, chat_response_name):
    most_count = 0
    most_matching = None
    chat_set = set(chat_response_name)
    for resource in resource_list:
        cleaned_string = (
            resource.display_value.lower()
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
            .split(" ")
        )
        same_set = set(chat_set).intersection(cleaned_string)
        if len(same_set) > most_count:
            most_count = len(same_set)
            most_matching = resource.display_value
    return most_matching


@background()
def _process_submit_chat_prompt(user_id, prompt, resource_type, context):
    from managr.crm import exceptions as crm_exceptions

    user = User.objects.get(id=user_id)
    workflow_id = context.get("w", None)
    if workflow_id:
        workflow = MeetingWorkflow.objects.get(id=workflow_id)
        workflow.operations = [slack_consts.MEETING___SUBMIT_CHAT_PROMPT]
        workflow.save()
    form_type = "CREATE" if "create" in prompt.lower() else "UPDATE"
    form_template = user.team.team_forms.filter(form_type=form_type, resource=resource_type).first()
    form = OrgCustomSlackFormInstance.objects.create(
        template=form_template, user=user, update_source="chat", chat_submission=prompt
    )
    fields = form_template.custom_fields.all()
    field_list = list(fields.values_list("label", flat=True))
    full_prompt = core_consts.OPEN_AI_UPDATE_PROMPT(field_list, prompt, datetime.now())
    url = core_consts.OPEN_AI_COMPLETIONS_URI
    attempts = 1
    has_error = False
    resource_check = None
    blocks = []
    token_amount = 500
    while True:
        try:
            body = core_consts.OPEN_AI_COMPLETIONS_BODY(
                user.email, full_prompt, token_amount=token_amount, top_p=0.1
            )
            logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: body <{body}>")
            with Client as client:
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
            if r.status_code == 200:
                r = r.json()
                logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: response <{r}>")
                choice = r["choices"][0]
                stop_reason = choice["finish_reason"]
                if stop_reason == "length":
                    print(f"Current token amount: {token_amount}")
                    if token_amount <= 2000:
                        if workflow_id is None:
                            slack_res = slack_requests.update_channel_message(
                                context.get("channel"),
                                context.get("ts"),
                                user.organization.slack_integration.access_token,
                                block_set=[
                                    block_builders.section_with_button_block(
                                        "Reopen Chat",
                                        "OPEN_CHAT",
                                        "Look like your prompt message is too long to process. Try removing white spaces!",
                                        action_id=action_with_params(
                                            slack_consts.REOPEN_CHAT_MODAL,
                                            [f"form_id={str(form.id)}"],
                                        ),
                                    )
                                ],
                            )

                        return

                    else:
                        token_amount += 500
                        continue
                text = choice["text"]
                cleaned_choice = clean_prompt_string(text)
                data = eval(cleaned_choice)
                name_field = set_name_field(resource_type, user.crm)
                data = correct_data_keys(data)
                resource_check = data[name_field].lower().split(" ")
                lowered_type = resource_type.lower()
                resource = None
                if lowered_type in resource_check:
                    resource_check.remove(lowered_type)
                if form_type == "CREATE" or len(resource_check):
                    if form_type == "UPDATE":
                        resource = None
                        for word in resource_check:
                            if resource_type not in ["Contact", "Lead"]:
                                query = (
                                    CRM_SWITCHER[user.crm][resource_type]["model"]
                                    .objects.for_user(user)
                                    .filter(name__icontains=word)
                                )
                                if query:
                                    if len(query) > 1:
                                        most_matching = name_list_processor(query, resource_check)
                                        resource = query.filter(name=most_matching).first()
                                    else:
                                        resource = query.first()
                                    break
                            else:
                                query = (
                                    CRM_SWITCHER[user.crm][resource_type]["model"]
                                    .objects.for_user(user)
                                    .filter(email__icontains=word)
                                )
                                if query:
                                    if len(query) > 1:
                                        most_matching = name_list_processor(query, resource_check)
                                        resource = query.filter(email=most_matching).first()
                                    else:
                                        resource = query.first()
                                    break
                        if resource:
                            logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: resource <{resource}>")
                            form.resource_id = str(resource.id)
                            form.save()
                        else:
                            has_error = True
                            break
                    else:
                        if user.crm == "SALESFORCE":
                            if resource_type in ["Opportunity", "Account"]:
                                data["Name"] = resource_check
                        else:
                            if resource_type == "Deal":
                                data["Deal Name"] = resource_check
                        resource = None
                    owner_field = set_owner_field(resource_type, user.crm)
                    data[owner_field] = user.crm_account.crm_id
                    swapped_field_data = swap_submitted_data_labels(data, fields)
                    cleaned_data = clean_prompt_return_data(
                        swapped_field_data, fields, user.crm, resource
                    )
                    form.save_form(cleaned_data, False)
                else:
                    has_error = True
                break
            else:
                attempts += 1
        except httpx.ReadTimeout:
            if attempts >= 5:
                message = "There was an error communicating with Open AI"
            else:
                attempts += 1
        except Exception as e:
            logger.exception(e)
            message = (
                f":no_entry_sign: Looks like we ran into an issue with your prompt, try removing things like quotes and ampersands"
                if resource_check is None
                else f":no_entry_sign: We could not find a {resource_type} named {resource_check} because of {e}"
            )
            slack_res = slack_requests.update_channel_message(
                context.get("channel"),
                context.get("ts"),
                user.organization.slack_integration.access_token,
                block_set=[
                    block_builders.section_with_button_block(
                        "Reopen Chat",
                        "OPEN_CHAT",
                        message,
                        action_id=action_with_params(
                            slack_consts.REOPEN_CHAT_MODAL, [f"form_id={str(form.id)}"]
                        ),
                    )
                ],
            )
            return
    if has_error:
        blocks = [
            block_builders.section_with_button_block(
                "Reopen Chat",
                "OPEN_CHAT",
                f":no_entry_sign: We could not find a {resource_type} named {resource_check}",
                action_id=action_with_params(
                    slack_consts.REOPEN_CHAT_MODAL, [f"form_id={str(form.id)}"]
                ),
            )
        ]
    update_attempts = 1
    crm_res = None
    while True and not has_error:
        try:
            if len(cleaned_data):
                if form_type == "UPDATE":
                    crm_res = resource.update(form.saved_data)
                else:
                    if crm_res is None:
                        create_route = CRM_SWITCHER[user.crm][resource_type]["model"]
                        resource_func = background_create_resource(user.crm)
                        crm_res = resource_func.now([str(form.id)])
                    resource = create_route.objects.get(integration_id=crm_res.integration_id)
                    form.resource_id = str(resource.id)
                    form.save()
                form.is_submitted = True
                form.submission_date = datetime.now()
                form.save()
            if cleaned_data["meeting_comments"] is not None:
                if workflow_id:
                    task_type = context.get("task_type")
                    task = ADD_CALL_TO_CRM_FUNCTION(user.crm)(str(workflow_id), [task_type])
                    workflow.operations.append(task.task_hash)
                else:
                    ADD_UPDATE_TO_CRM_FUNCTION(user.crm)(str(form.id))
            blocks = [
                block_builders.section_with_button_block(
                    "Generate Content",
                    "GENERATIVE ACTION",
                    section_text=f":white_check_mark: Successfully {'updated' if form_type == 'UPDATE' else 'created'} {resource_type} {resource.display_value}",
                    action_id=action_with_params(
                        slack_consts.OPEN_GENERATIVE_ACTION_MODAL,
                        params=[f"u={str(user.id)}", f"form_ids={str(form.id)}", "type=command",],
                    ),
                )
            ]
            break
        except crm_exceptions.TokenExpired:
            if attempts >= 5:
                has_error = True
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries"
                )
                blocks = [
                    block_builders.simple_section(
                        f"Looks like we had an issue communicating with {'Salesforce' if user.crm == 'SALESFORCE' else 'HubSpot'}"
                    )
                ]
                break
            else:
                user.crm_account.regenerate_token()
                update_attempts += 1
        except crm_exceptions.FieldValidationError as e:
            logger.exception(f"There was and validation error submitting chat prompt data: {e}")
            has_error = True
            blocks = [
                block_builders.section_with_button_block(
                    "Reopen Chat",
                    "OPEN_CHAT",
                    f":no_entry_sign: Uh-oh we hit a validation: {e}",
                    action_id=action_with_params(
                        slack_consts.REOPEN_CHAT_MODAL, [f"form_id={str(form.id)}"]
                    ),
                )
            ]
            break
        except Exception as e:
            logger.exception(f"There was and error submitting chat prompt data: {e}")
            has_error = True
            blocks = [
                block_builders.section_with_button_block(
                    "Reopen Chat",
                    "OPEN_CHAT",
                    f":no_entry_sign: Uh-oh we hit a error: {e}",
                    action_id=action_with_params(
                        slack_consts.REOPEN_CHAT_MODAL, [f"form_id={str(form.id)}"]
                    ),
                )
            ]
            break
    if workflow_id and not has_error:
        form.workflow = workflow
        form.update_source = "meeting (chat)"
        form.save()
        workflow.completed_operations.append(slack_consts.MEETING___SUBMIT_CHAT_PROMPT)
        workflow.resource_type = resource_type
        workflow.resource_id = str(resource.id)
        workflow.save()
        return
    else:
        try:
            slack_res = slack_requests.update_channel_message(
                context.get("channel"),
                context.get("ts"),
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
        except Exception as e:
            logger.exception(
                f"ERROR sending update channel message for chat submittion because of <{e}>"
            )
    if not has_error and form_type == "UPDATE":
        value_update = form.resource_object.update_database_values(cleaned_data)
    return


def _process_submit_chat_note(user_id, prompt, resource_type, context):
    user = User.objects.get(id=user_id)
    field_list = [resource_type, "Note", "Note Subject"]
    form_id = context.get("form_id")
    form = OrgCustomSlackFormInstance.objects.get(id=form_id)
    full_prompt = core_consts.OPEN_AI_UPDATE_PROMPT(field_list, prompt, datetime.now())
    body = core_consts.OPEN_AI_COMPLETIONS_BODY(user.email, full_prompt, top_p=0.1)
    url = core_consts.OPEN_AI_COMPLETIONS_URI
    has_error = False
    attempts = 1
    while True:
        try:
            with Client as client:
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
            if r.status_code == 200:
                r = r.json()
                logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: response <{r}>")
                choice = r["choices"][0]["text"]
                data = eval(
                    choice[choice.index("{") : choice.index("}") + 1]
                    .replace("null", "'None'")
                    .replace("'", '"')
                )
                resource_check = data.pop(resource_type, None)
                if resource_check:
                    resource = form.resource_object
                    note = data.pop("Note")
                    data["Notes"] = note
                    fields = ObjectField.objects.filter(
                        id__in=[
                            "6407b7a1-a877-44e2-979d-1effafec5034",
                            "0bb152b5-aac1-4ee0-9c25-51ae98d55af2",
                        ]
                    )

                    swapped_field_data = swap_submitted_data_labels(data, fields)
                    swapped_field_data.update(form.saved_data)
                    form.save_form(swapped_field_data, False)
                    form.is_submitted = True
                    form.submission_date = datetime.now()
                    form.save()
                    ADD_UPDATE_TO_CRM_FUNCTION(user.crm)(str(form.id))
                else:
                    has_error = True
                break
            else:
                attempts += 1
        except Exception as e:
            logger.exception(e)
            return
    return


@background()
def _process_send_email_draft(payload, context):
    user = User.objects.get(id=context.get("u"))
    form_ids = context.get("form_ids").split(",")
    forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids)
    data_collector = {}
    for form in forms:
        data_collector = {**data_collector, **form.saved_data}
    prompt = core_consts.OPEN_AI_MEETING_EMAIL_DRAFT(data_collector)
    body = core_consts.OPEN_AI_COMPLETIONS_BODY(user.email, prompt, temperature=0.2)
    attempts = 1
    while True:
        try:
            with Client as client:
                url = core_consts.OPEN_AI_COMPLETIONS_URI
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
            if r.status_code == 200:
                r = r.json()
                text = r.get("choices")[0].get("text")
                break
        except Exception as e:
            logger.exception(e)
            text = "There was an error generating your draft"
            break

    blocks = [
        block_builders.header_block("AI Generated Email"),
        block_builders.context_block(
            "ManagrGPT was used to draft this email based on your last update."
        ),
        block_builders.divider_block(),
        block_builders.simple_section(text, "mrkdwn"),
        block_builders.divider_block(),
        block_builders.actions_block(
            [
                block_builders.simple_button_block(
                    "Regenerate",
                    "DRAFT_EMAIL",
                    action_id=action_with_params(
                        slack_consts.PROCESS_REGENERATE_ACTION,
                        params=[
                            f"u={str(user.id)}",
                            f"form_ids={context.get('form_ids')}",
                            f"workflow_id={str(context.get('workflow_id'))}",
                        ],
                    ),
                )
            ]
        ),
        block_builders.context_block("This version will not be saved."),
    ]
    try:
        if context.get("channel_id", None):
            slack_res = slack_requests.update_channel_message(
                context.get("channel_id"),
                context.get("ts"),
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
        else:
            slack_res = slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return


@background()
def _process_send_next_steps(payload, context):
    user = User.objects.get(id=context.get("u"))
    form_ids = context.get("form_ids").split(",")
    forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids)
    data_collector = {}
    for form in forms:
        data_collector = {**data_collector, **form.saved_data}
    prompt = core_consts.OPEN_AI_NEXT_STEPS(data_collector)
    body = core_consts.OPEN_AI_COMPLETIONS_BODY(user.email, prompt, temperature=0.2)
    attempts = 1
    while True:
        try:
            with Client as client:
                url = core_consts.OPEN_AI_COMPLETIONS_URI
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
            if r.status_code == 200:
                r = r.json()
                text = r.get("choices")[0].get("text")
                break
        except Exception as e:
            logger.exception(e)
            text = "There was an error generating your draft"
            break

    blocks = [
        block_builders.header_block("AI Generated Next Steps"),
        block_builders.context_block(
            "ManagrGPT was used to suggest a range of next steps based on your last update."
        ),
        block_builders.divider_block(),
        block_builders.simple_section(text, "mrkdwn"),
        block_builders.divider_block(),
        block_builders.actions_block(
            [
                block_builders.simple_button_block(
                    "Regenerate",
                    "NEXT_STEPS",
                    action_id=action_with_params(
                        slack_consts.PROCESS_REGENERATE_ACTION,
                        params=[
                            f"u={str(user.id)}",
                            f"form_ids={context.get('form_ids')}",
                            f"workflow_id={str(context.get('workflow_id'))}",
                        ],
                    ),
                )
            ]
        ),
        block_builders.context_block("This version will not be saved."),
    ]
    try:
        if context.get("channel_id", None):
            slack_res = slack_requests.update_channel_message(
                context.get("channel_id"),
                context.get("ts"),
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
        else:
            slack_res = slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return


def clean_data_for_summary(user_id, data, integration_id, resource_type):
    from managr.hubspot.routes import routes as hs_routes
    from managr.salesforce.routes import routes as sf_routes

    cleaned_data = dict(data)
    CRM_SWITCHER = {"SALESFORCE": sf_routes, "HUBSPOT": hs_routes}
    user = User.objects.get(id=user_id)
    owner_field = "hubspot_owner_id" if user.crm == "HUBSPOT" else "OwnerId"
    try:
        cleaned_data.pop(owner_field)
    except KeyError:
        owner_field = None
    if "meeting_comments" in data.keys() and data["meeting_comments"] is None:
        cleaned_data.pop("meeting_comments")
        cleaned_data.pop("meeting_type")
    fields = user.object_fields.filter(api_name__in=cleaned_data.keys())
    ref_fields = fields.filter(data_type="Reference", crm_object=resource_type)
    if user.crm == "HUBSPOT":
        if "dealstage" in data.keys():
            found_stage = False
            field = fields.filter(api_name="dealstage").first()
            for pipeline in field.options[0].keys():
                if found_stage:
                    break
                current_pipeline = field.options[0][pipeline]["stages"]
                for stage in current_pipeline:
                    if stage["id"] == cleaned_data["dealstage"]:
                        cleaned_data["dealstage"] = stage["label"]
                        found_stage = True
    if len(ref_fields):
        for field in ref_fields:
            relationship = field.reference_to_infos[0]["api_name"]
            try:
                reference_record = (
                    CRM_SWITCHER[user.crm][relationship]["model"]
                    .objects.filter(integration_id=cleaned_data[field.api_name])
                    .first()
                ).display_value

            except Exception as e:
                logger.info(e)
                reference_record = integration_id
                pass
            cleaned_data[field.api_name] = reference_record
    return cleaned_data


def _process_send_summary_to_dm(payload, context):
    form_ids = context.get("form_ids").split(",")
    submitted_forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids).exclude(
        template__resource="OpportunityLineItem"
    )
    main_form = submitted_forms.filter(template__form_type__in=["CREATE", "UPDATE"]).first()
    user = main_form.user
    main_form = submitted_forms.filter(template__form_type__in=["CREATE", "UPDATE"]).first()
    main_form.save()
    user = main_form.user
    old_data = dict()
    if main_form.template.form_type == "UPDATE":
        for additional_stage_form in submitted_forms:
            old_data = {**old_data, **additional_stage_form.previous_data}
    new_data = dict()
    for form in submitted_forms:
        new_data = {**new_data, **form.saved_data}
    blocks = [
        block_builders.header_block("AI Generated Summary"),
        block_builders.context_block(
            "ManagrGPT was used to generate this summary based on your last update."
        ),
        block_builders.divider_block(),
    ]
    cleaned_data = clean_data_for_summary(
        str(user.id),
        new_data,
        main_form.resource_object.integration_id,
        main_form.template.resource,
    )
    completions_prompt = get_summary_completion(user, cleaned_data)
    message_string_for_recap = completions_prompt["choices"][0]["text"]
    blocks.append(block_builders.simple_section(message_string_for_recap, "mrkdwn"))
    blocks.append(block_builders.context_block("Powered by ChatGPT © :robot_face:"))
    try:
        if context.get("ts", None):
            slack_res = slack_requests.update_channel_message(
                user.slack_integration.channel,
                context.get("ts"),
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
        else:
            slack_res = slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return
