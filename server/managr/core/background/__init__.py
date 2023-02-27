import logging
import time
import random
import pytz
import uuid
import requests
from datetime import datetime
from copy import copy
import re
from django.template.loader import render_to_string
from managr.api.emails import send_html_email
from background_task import background
from django.conf import settings

from django.db.models import Q
from managr.alerts.models import AlertConfig, AlertInstance, AlertTemplate
from managr.core import constants as core_consts
from managr.core.models import User
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce.adapter.models import ContactAdapter
from managr.hubspot.adapter.models import HubspotContactAdapter
from managr.crm.models import BaseAccount, BaseOpportunity, BaseContact
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


logger = logging.getLogger("managr")

if settings.IN_DEV:
    MANAGR_URL = "http://localhost:8080"
elif settings.IN_STAGING:
    MANAGR_URL = "https://staging.managr.ai"
else:
    MANAGR_URL = "https://app.managr.ai"


def get_domain(email):
    """Parse domain out of an email"""
    return email[email.index("@") + 1 :]


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

