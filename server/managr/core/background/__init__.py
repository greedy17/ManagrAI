import logging
import time
import pytz
import uuid
import requests
import json
import httpx
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
from managr.core.models import User, StripeAdapter
from managr.core.utils import (
    get_summary_completion,
    swap_submitted_data_labels,
    clean_prompt_string,
    ask_managr_data_collector,
    convert_date_string,
)
from managr.salesforce.models import MeetingWorkflow
from managr.crm.models import BaseAccount, BaseOpportunity, ObjectField
from managr.meetings.models import Meeting
from managr.meetings.serializers import MeetingSerializer
from managr.slack.helpers import requests as slack_requests
from managr.slack.models import OrgCustomSlackFormInstance
from managr.slack import constants as slack_consts
from managr.slack.helpers import block_builders
from managr.zoom.background import emit_kick_off_slack_interaction
from managr.slack.helpers.block_sets import get_block_set
from managr.utils.client import Variable_Client
from managr.salesforce.routes import routes as sf_routes
from managr.hubspot.routes import routes as hs_routes
from managr.salesforce.background import emit_add_update_to_sf, emit_add_call_to_sf
from managr.hubspot.tasks import emit_add_update_to_hs, emit_add_call_to_hs
from managr.core.exceptions import _handle_response, ServerError, StopReasonLength
from managr.zoom.zoom_helper import exceptions as zoom_exceptions
from managr.crm.utils import set_owner_field

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
    return _process_calendar_meetings(
        user_id,
        slack_interaction,
        date,
        verbose_name=verbose_name,
    )


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


def emit_process_submit_chat_prompt(user_id, prompt, context):
    return _process_submit_chat_prompt(user_id, prompt, context)


def emit_process_submit_chat_note(user_id, prompt, resource_type, context):
    return _process_submit_chat_note(user_id, prompt, resource_type, context)


def emit_process_send_email_draft(payload, context):
    return _process_send_email_draft(payload, context)


def emit_process_send_regenerate_email_message(payload, context):
    return _process_send_regenerate_email_message(payload, context)


def emit_process_send_regenerated_email_draft(payload, context):
    return _process_send_regenerated_email_draft(payload, context)


def emit_process_send_regenerated_ask_managr(payload, context):
    return _process_send_regenerated_ask_managr(payload, context)


def emit_process_send_next_steps(payload, context):
    return _process_send_next_steps(payload, context)


def emit_process_send_summary_to_dm(payload, context):
    return _process_send_summary_to_dm(payload, context)


def emit_process_add_call_analysis(workflow_id, summaries):
    return _process_add_call_analysis(workflow_id, summaries)


def emit_process_send_call_analysis_to_dm(payload, context):
    return _process_send_call_analysis_to_dm(payload, context)


def emit_process_send_call_summary_to_dm(payload, context):
    return _process_send_call_summary_to_dm(payload, context)


def emit_process_send_ask_managr_to_dm(payload, context):
    return _process_send_ask_managr_to_dm(payload, context)


def emit_send_activation_email(user_id):
    return _send_activation_email(user_id)


def emit_process_check_subscription_status(session_id, user_id):
    return _process_check_subscription_status(session_id, user_id)


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
        hour=hour, minute=0, second=0, microsecond=0
    ) and current > current.replace(hour=hr, minute=0, second=0, microsecond=0)


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
        return [
            {
                "propertyName": "email",
                "operator": "IN",
                "values": emails,
            }
        ]
    else:
        email_string = "','".join(emails)
        return [f"AND Email IN ('{email_string}')"]


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
    print("starting calendar check")
    user = User.objects.get(id=user_id)
    if user.has_nylas_integration:
        try:
            processed_data = _process_calendar_details(user_id, date)
            print(processed_data)
        except Exception:
            logger.exception(f"Pulling calendar data error for {user.email} <ERROR: {e}>")
            processed_data = None
        if user.has_zoom_integration:
            while True:
                try:
                    if date is None:
                        user_timezone = pytz.timezone(user.timezone)
                        todays_date = pytz.utc.localize(datetime.today()).astimezone(user_timezone)
                        date = str(todays_date.date())
                    meetings = user.zoom_account.helper_class.get_meetings_by_date(
                        user.zoom_account.access_token, user.zoom_account.zoom_id, date
                    )["meetings"]
                    print("MEETINGS:", meetings)
                    break
                except zoom_exceptions.TokenExpired:
                    user.zoom_account.regenerate_token()
                except Exception as e:
                    logger.exception(f"Pulling calendar data error for {user.email} <ERROR: {e}>")
                    meetings = []
                    break
        if processed_data is not None:
            workflows = MeetingWorkflow.objects.for_user(user, date)
            print(workflows)
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
                original_id = id
                meeting_data = {**event, "user": user, "original_id": id}
                if user.has_zoom_integration:
                    meetings_by_topic = [
                        meeting for meeting in meetings if event["title"] == meeting["topic"]
                    ]
                    if len(meetings_by_topic):
                        meeting = meetings_by_topic[0]
                        meeting_data["id"] = meeting["id"]
                        id = meeting["id"]
                workflow_check = workflows.filter(
                    Q(meeting__meeting_id=id) | Q(meeting__meeting_id=original_id)
                ).first()
                register_check = should_register_this_meetings(user_id, event)
                if workflow_check is None and register_check:
                    meeting_serializer = MeetingSerializer(data=meeting_data)
                    meeting_serializer.is_valid(raise_exception=True)
                    meeting_serializer.save()
                    meeting = Meeting.objects.filter(user=user).first()
                    meeting.save()
                    # Conditional Check for Zoom meeting or Non-Zoom Meeting
                    meeting_workflow = MeetingWorkflow.objects.create(
                        operation_type="MEETING_REVIEW",
                        meeting=meeting,
                        user=user,
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
            user_timezone = pytz.timezone(user.timezone)
            todays_date = (
                pytz.utc.localize(datetime.today()).astimezone(user_timezone)
                if date is None
                else datetime.strptime(date, "%Y-%m-%d")
            )
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
        if user.has_slack_integration:
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
                {
                    "u": str(user.id),
                    "not_completed": meetings["uncompleted"],
                    "name": name,
                },
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
    core_consts.MEETING_REMINDER: emit_process_send_meeting_reminder,
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
            f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.CALENDAR_URI}",
            headers=headers,
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
            if cleaned_data[key] is None or cleaned_data[key] in [
                "",
                "TBD",
                "Unknown",
                "None",
                "N/A",
            ]:
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
        except KeyError:
            continue
    cleaned_data["meeting_comments"] = notes
    cleaned_data["meeting_type"] = subject
    # logger.info(f"CLEAN PROMPT DEBUGGER: {cleaned_data}")
    return cleaned_data


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
def _process_submit_chat_prompt(user_id, prompt, context):
    from managr.crm import exceptions as crm_exceptions

    user = User.objects.get(id=user_id)
    workflow_id = context.get("w", None)
    if workflow_id:
        workflow = MeetingWorkflow.objects.get(id=workflow_id)
        workflow.save()
    resource_type = context.get("resource_type")
    form_type = (
        "CREATE" if ("create" in prompt.lower() and "update" not in prompt.lower()) else "UPDATE"
    )
    form_template = user.team.team_forms.filter(form_type=form_type, resource=resource_type).first()
    form = OrgCustomSlackFormInstance.objects.create(
        template=form_template, user=user, update_source="chat", chat_submission=prompt
    )
    fields = form_template.custom_fields.all()
    field_list = list(fields.values_list("label", flat=True))
    full_prompt = core_consts.OPEN_AI_UPDATE_PROMPT(field_list, prompt, datetime.now())
    url = core_consts.OPEN_AI_COMPLETIONS_URI
    resource = (
        CRM_SWITCHER[user.crm][context.get("resource_type")]["model"]
        .objects.filter(id=context.get("resource_id"))
        .first()
    )
    attempts = 1
    has_error = False
    blocks = []
    token_amount = 500
    timeout = 60.0
    while True:
        message = None
        try:
            body = core_consts.OPEN_AI_COMPLETIONS_BODY(
                user.email, full_prompt, token_amount=token_amount, top_p=0.1
            )
            # logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: body <{body}>")
            with Variable_Client(timeout) as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
                r = _handle_response(r)
                # logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: response <{r}>")
                choice = r["choices"][0]

                text = choice["text"]
                data = clean_prompt_string(text)
                data = correct_data_keys(data)
                if resource:
                    form.resource_id = str(resource.id)
                    form.save()
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
        except StopReasonLength:
            logger.exception(
                f"Retrying again due to token amount, amount currently at: {token_amount}"
            )
            if token_amount <= 2000:
                if workflow_id is None:
                    slack_res = slack_requests.update_channel_message(
                        user.slack_integration.channel,
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
        except httpx.ReadTimeout as e:
            timeout += 30.0
            if timeout >= 120.0:
                has_error = True
                message = "There was an error communicating with Open AI"
                logger.exception(f"Read timeout from Open AI {e}")
                break
            else:
                attempts += 1
                continue
        except Exception as e:
            logger.exception(f"Exception from Open AI response {e}")
            has_error = True
            message = ":no_entry_sign: Looks like we ran into an issue with your prompt, try removing things like quotes and ampersands"
            slack_res = slack_requests.update_channel_message(
                user.slack_integration.channel,
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
            break
    if has_error:
        if workflow_id:
            logger.exception(
                f"There was an error processing chat submission for workflow {workflow} {message}"
            )
            workflow.failed_task_description.append(
                f"There was an error processing chat submission {message}"
            )
            workflow.save()
        blocks = [
            block_builders.section_with_button_block(
                "Reopen Chat",
                "OPEN_CHAT",
                f":no_entry_sign: {message}",
                action_id=action_with_params(
                    slack_consts.REOPEN_CHAT_MODAL, [f"form_id={str(form.id)}"]
                ),
            )
        ]
    if not has_error:
        params = [
            f"u={str(user.id)}",
            f"f={str(form.id)}",
            f"resource_type={resource_type}",
            f"resource_id={str(resource.id)}",
            "type=chat",
        ]
        if workflow_id:
            params.append(f"w={workflow_id}")
            params.append(f"ts={context.get('ts')}")
        blocks = [
            block_builders.section_with_button_block(
                f"Review & Update {'Salesforce' if user.crm == 'SALESFORCE' else 'HubSpot'}",
                "REVIEW_CHAT_UPDATE",
                section_text=f":robot_face: {resource.display_value} {'fields' if user.crm == 'SALESFORCE' else 'properties'} have been filled, please review",
                action_id=action_with_params(
                    slack_consts.OPEN_REVIEW_CHAT_UPDATE_MODAL,
                    params=params,
                ),
                style="primary",
            )
        ]
    if workflow_id:
        if not has_error:
            form.workflow = workflow
            form.update_source = "meeting (chat)"
            form.save()
            workflow.resource_type = resource_type
            workflow.resource_id = str(resource.id)
            workflow.save()

    try:
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return


def _process_submit_chat_note(user_id, prompt, resource_type, context):
    user = User.objects.get(id=user_id)
    field_list = [resource_type, "Note", "Note Subject"]
    form_id = context.get("form_id")
    form = OrgCustomSlackFormInstance.objects.get(id=form_id)
    full_prompt = core_consts.OPEN_AI_UPDATE_PROMPT(field_list, prompt, datetime.now())
    body = core_consts.OPEN_AI_COMPLETIONS_BODY(user.email, full_prompt, 500, top_p=0.1)
    url = core_consts.OPEN_AI_COMPLETIONS_URI
    has_error = False
    attempts = 1
    while True:
        try:
            with Variable_Client() as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
                # logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: response <{r}>")
                r = _handle_response(r)
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
        try:
            data_collector = {**form.saved_data, **data_collector}
        except Exception:
            continue

    prompt = core_consts.OPEN_AI_MEETING_EMAIL_DRAFT(data_collector)
    body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
        user.email, prompt, token_amount=500, temperature=0.2
    )
    attempts = 1
    while True:
        try:
            with Variable_Client() as client:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
                r = _handle_response(r)
                text = r.get("choices")[0].get("message").get("content")
                user.add_meta_data("emails")
            break
        except Exception as e:
            logger.exception(e)
            text = "There was an error generating your draft"
            break

    blocks = [
        block_builders.header_block("AI Generated Email", "HEADER_BLOCK"),
        block_builders.context_block(f"{forms.first().resource_object.display_value}"),
        block_builders.divider_block(),
        block_builders.simple_section(text, "mrkdwn", block_id="PROMPT_BLOCK"),
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
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return


@background()
def _process_send_regenerated_email_draft(payload, context):
    from managr.slack.helpers.utils import block_finder

    instructions_check = payload["state"]["values"]["REGENERATE_INSTRUCTIONS"]["plain_input"][
        "value"
    ]
    user = User.objects.get(id=context.get("u"))
    form_ids = context.get("form_ids").split(",")
    forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids)
    data_collector = {}
    for form in forms:
        data_collector = {**data_collector, **form.saved_data}
    try:
        previous_blocks = payload["message"]["blocks"]
        index, block = block_finder("PROMPT_BLOCK", previous_blocks)
    except ValueError:
        # did not find the block
        block = None
        pass
    prompt = core_consts.OPEN_AI_EMAIL_DRAFT_WITH_INSTRUCTIONS(
        block["text"]["text"], instructions_check
    )
    body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(user.email, prompt, token_amount=1000)
    attempts = 1
    while True:
        try:
            with Variable_Client() as client:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
                r = _handle_response(r)
                text = r.get("choices")[0].get("message").get("content")
            break
        except Exception as e:
            logger.exception(e)
            text = "There was an error generating your draft"
            break

    blocks = [
        block_builders.header_block("AI Generated Email"),
        block_builders.context_block(f"{forms.first().resource_object.display_value}"),
        block_builders.divider_block(),
        block_builders.simple_section(text, "mrkdwn", block_id="PROMPT_BLOCK"),
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
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return


@background()
def _process_send_regenerated_ask_managr(payload, context):
    from managr.slack.helpers.utils import block_finder

    instructions_check = payload["state"]["values"]["REGENERATE_INSTRUCTIONS"]["plain_input"][
        "value"
    ]
    user = User.objects.get(id=context.get("u"))
    data = ask_managr_data_collector(
        str(user.id),
        context.get("resource_type"),
        context.get("resource_id"),
    )
    resource = CRM_SWITCHER[user.crm][context.get("resource_type")]["model"].objects.get(
        id=context.get("resource_id")
    )
    try:
        previous_blocks = payload["message"]["blocks"]
        index, block = block_finder("PROMPT_TEXT", previous_blocks)
    except ValueError:
        # did not find the block
        block = None
        pass
    prompt = core_consts.OPEN_AI_ASK_MANAGR_WITH_INSTRUCTIONS(
        block["text"]["text"], instructions_check, data
    )
    body = core_consts.OPEN_AI_COMPLETIONS_BODY(user.email, prompt, 1000)
    tokens = 500
    has_error = False
    attempts = 1
    timeout = 60.0
    while True:
        try:
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email, prompt, "You are an experienced sales leader", token_amount=tokens
            )
            with Variable_Client(timeout) as client:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            r = _handle_response(r)
            text = r.get("choices")[0].get("message").get("content")
            break
        except StopReasonLength:
            if tokens >= 2000:
                break
            else:
                tokens += 500
                continue
        except ServerError:
            if attempts >= 5:
                has_error = True
                text = ":no_entry_sign: There was a server error with Open AI"
                break
            else:
                attempts += 1
                time.sleep(10.0)
        except ValueError as e:
            print(e)
            if str(e) == "substring not found":
                continue
            else:
                has_error = True
                text = ":no_entry_sign: Looks like we ran into an internal issue"
                break
        except SyntaxError as e:
            print(e)
            continue
        except httpx.ReadTimeout:
            logger.exception(
                f"Read timeout to Open AI from ask managr, trying again. TIMEOUT AT: {timeout}"
            )
            if timeout >= 120.0:
                has_error = True
                break
            else:
                timeout += 30.0
        except Exception as e:
            logger.exception(f"Unknown error on ask managr <{e}>")
            break

    blocks = [
        block_builders.header_block("Ask Managr"),
        block_builders.context_block(f"{resource.display_value}"),
        block_builders.divider_block(),
        block_builders.simple_section(text, "mrkdwn", block_id="PROMPT_TEXT"),
        block_builders.divider_block(),
        block_builders.actions_block(
            [
                block_builders.simple_button_block(
                    "Regenerate",
                    "ASK_MANAGR",
                    action_id=action_with_params(
                        slack_consts.PROCESS_REGENERATE_ACTION,
                        params=[
                            f"u={str(user.id)}",
                            f"resource_id={context.get('resource_id')}",
                            f"resource_type={context.get('resource_type')}",
                        ],
                    ),
                )
            ]
        ),
        block_builders.context_block("This version will not be saved."),
    ]
    try:
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return


@background()
def _process_send_regenerate_email_message(payload, context):
    from managr.slack.helpers.utils import block_finder

    instructions_check = (
        payload["state"]["values"]["REGENERATE_INSTRUCTIONS"]["plain_input"]["value"]
        if "REGENERATE_INSTRUCTIONS" in payload["state"]["values"].keys()
        else None
    )
    if instructions_check:
        if len(instructions_check):
            return _process_send_regenerated_email_draft(payload, context)
        else:
            return _process_send_email_draft(payload, context)
    user = User.objects.get(id=context.get("u"))
    form_ids = context.get("form_ids").split(",")
    forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids)
    previous_blocks = payload["message"]["blocks"]

    try:
        index, block = block_finder("PROMPT_BLOCK", previous_blocks)
    except ValueError:
        # did not find the block
        block = None
        pass
    blocks = [
        block_builders.header_block("AI Generated Email", "HEADER_BLOCK"),
        block_builders.context_block(f"{forms.first().resource_object.display_value}"),
        block_builders.divider_block(),
        block_builders.simple_section(block["text"]["text"], "mrkdwn", block_id="PROMPT_BLOCK"),
        block_builders.divider_block(),
        block_builders.input_block(
            "Provide additional instructions below:",
            block_id="REGENERATE_INSTRUCTIONS",
            multiline=True,
        ),
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
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
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
    body = core_consts.OPEN_AI_COMPLETIONS_BODY(user.email, prompt, 500, temperature=0.2)
    attempts = 1
    while True:
        try:
            with Variable_Client() as client:
                url = core_consts.OPEN_AI_COMPLETIONS_URI
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
                r = _handle_response(r)
                text = r.get("choices")[0].get("text")
                break
        except Exception as e:
            logger.exception(e)
            text = "There was an error generating your draft"
            break

    blocks = [
        block_builders.header_block("AI Generated Next Steps"),
        block_builders.context_block(f"{forms.first().resource_object.display_value}"),
        block_builders.divider_block(),
        block_builders.simple_section(text, "mrkdwn", block_id="EMAIL_TEXT"),
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
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
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


@background()
def _process_send_summary_to_dm(payload, context):
    form_ids = context.get("form_ids", [])
    if form_ids and len(form_ids):
        form_ids = form_ids.split(",")
        submitted_forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids).exclude(
            template__resource="OpportunityLineItem"
        )
    else:
        user = User.objects.get(id=context.get("u"))
        submitted_forms = OrgCustomSlackFormInstance.objects.for_user(user).exclude(
            template__resource="OpportunityLineItem"
        )
    main_form = submitted_forms.filter(template__form_type__in=["CREATE", "UPDATE"]).first()
    user = main_form.user
    new_data = dict()
    for form in submitted_forms:
        new_data = {**new_data, **form.saved_data}
    blocks = [
        block_builders.header_block("AI Generated Summary", "HEADER_BLOCK"),
        block_builders.context_block(f"{main_form.resource_object.display_value}"),
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
    blocks.append(block_builders.simple_section(message_string_for_recap, "mrkdwn", "PROMPT_BLOCK"))
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


@background()
def _process_add_call_analysis(workflow_id, summaries):
    import httpx

    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    timeout = 60.0
    prompt = core_consts.OPEN_AI_CALL_ANALYSIS_PROMPT(summaries, workflow.datetime_created.date())
    has_error = False
    attempts = 1
    text = None
    tokens = 500
    while True:
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            workflow.user.email, prompt, "You are an experience VP of Sales", token_amount=tokens
        )
        try:
            with Variable_Client(timeout) as client:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            r = _handle_response(r)
            text = r.get("choices")[0].get("message").get("content")
            break
        except StopReasonLength:
            if tokens >= 2000:
                break
            else:
                tokens += 500
                continue
        except ServerError:
            if attempts >= 5:
                has_error = True
                error_message = ":no_entry_sign: There was a server error with Open AI"
                break
            else:
                attempts += 1
                time.sleep(5.0)
        except ValueError as e:
            print(e)
            if str(e) == "substring not found":
                continue
            else:
                has_error = True
                error_message = ":no_entry_sign: Looks like we ran into an internal issue"
                break
        except SyntaxError as e:
            has_error = True
            error_message = ":no_entry_sign: Looks like we ran into an internal issue"
            print(e)
            continue
        except httpx.ReadTimeout:
            logger.exception(f"Read timeout to Open AI, trying again. TIMEOUT AT: {timeout}")
            error_message = (
                ":no_entry_sign: Looks like we ran into an issue communicating with Open AI"
            )
            if timeout >= 120.0:
                has_error = True
                break
            else:
                timeout += 30.0
        except Exception as e:
            has_error = True
            logger.exception(f"Unknown error on call analysis for {str(workflow.id)} <{e}>")
            error_message = f"Unknown error on call analysis: {e}"
    if has_error:
        workflow.transcript_analysis = error_message
        workflow.save()
        return
    else:
        workflow.transcript_analysis = text
        workflow.save()
    return


@background()
def _process_send_call_analysis_to_dm(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    text = (
        workflow.transcript_analysis
        if workflow.transcript_analysis
        else "There was an issue creating your analysis"
    )
    blocks = [
        block_builders.header_block("AI Generated Call Analysis"),
        block_builders.context_block(f"{workflow.meeting.topic}"),
        block_builders.divider_block(),
        block_builders.simple_section(text, "mrkdwn"),
    ]
    try:
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return


@background()
def _process_send_call_summary_to_dm(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    text = (
        workflow.transcript_summary
        if workflow.transcript_summary
        else "There was an issue creating your analysis"
    )
    blocks = [
        block_builders.header_block("AI Generated Call Summary"),
        block_builders.context_block(f"{workflow.meeting.topic}"),
        block_builders.divider_block(),
        block_builders.simple_section(text, "mrkdwn"),
    ]
    try:
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return


@background
def _process_send_ask_managr_to_dm(payload, context):
    user = User.objects.get(id=context.get("u"))
    data = ask_managr_data_collector(
        str(user.id),
        context.get("resource_type"),
        context.get("resource_id"),
    )
    prompt = core_consts.OPEN_AI_ASK_MANAGR_PROMPT(
        user, datetime.today(), context.get("prompt"), data
    )
    tokens = 500
    has_error = False
    attempts = 1
    timeout = 60.0
    while True:
        try:
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email, prompt, "You are an experienced sales leader", token_amount=tokens
            )
            with Variable_Client(timeout) as client:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            r = _handle_response(r)
            text = r.get("choices")[0].get("message").get("content")
            break
        except StopReasonLength:
            if tokens >= 2000:
                break
            else:
                tokens += 500
                continue
        except ServerError:
            if attempts >= 5:
                has_error = True
                error_message = ":no_entry_sign: There was a server error with Open AI"
                break
            else:
                attempts += 1
                time.sleep(10.0)
        except ValueError as e:
            print(e)
            if str(e) == "substring not found":
                continue
            else:
                has_error = True
                error_message = ":no_entry_sign: Looks like we ran into an internal issue"
                break
        except SyntaxError as e:
            print(e)
            continue
        except httpx.ReadTimeout:
            logger.exception(
                f"Read timeout to Open AI from ask managr, trying again. TIMEOUT AT: {timeout}"
            )
            if timeout >= 120.0:
                has_error = True
                break
            else:
                timeout += 30.0
        except Exception as e:
            logger.exception(f"Unknown error on ask managr <{e}>")
            break
    if has_error:
        return
    blocks = [
        block_builders.header_block("Ask Managr"),
        block_builders.divider_block(),
        block_builders.simple_section(text, "mrkdwn", "PROMPT_TEXT"),
        block_builders.divider_block(),
        block_builders.actions_block(
            [
                block_builders.simple_button_block(
                    "Regenerate",
                    "ASK_MANAGR",
                    action_id=action_with_params(
                        slack_consts.PROCESS_REGENERATE_ACTION,
                        params=[
                            f"u={str(user.id)}",
                            f"resource_id={context.get('resource_id')}",
                            f"resource_type={context.get('resource_type')}",
                        ],
                    ),
                )
            ]
        ),
    ]
    try:
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return


@background()
def _send_activation_email(user_id):
    user = User.objects.get(id=user_id)
    content = {
        "first_name": user.first_name,
        "activation_link": user.activation_link,
    }
    send_html_email(
        "Managr Activation",
        "core/email-templates/admin-activation.html",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        context=content,
    )
    return


@background(schedule=300)
def _process_check_subscription_status(session_id, user_id):
    user = User.objects.get(id=user_id)
    url = core_consts.STRIPE_API_BASE_URL + core_consts.STRIPE_CHECKOUT_SESSION + f"/{session_id}"
    adapter = StripeAdapter(**{"user": user})
    while True:
        try:
            with Variable_Client() as client:
                res = client.get(
                    url, headers={"Authorization": f"Bearer {settings.STRIPE_API_KEY}"}
                )
                res = adapter._handle_response(response=res)
            if res["payment_status"] == "paid":
                sub_id = res["subscription"]
                user.private_meta_data["stripe_sub_id"] = sub_id
                user.save()
                break
            else:
                time.sleep(30)
        except Exception as e:
            logger.exception(str(e))
    return
