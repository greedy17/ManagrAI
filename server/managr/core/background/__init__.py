import logging
import time
import random
import textwrap
import jwt
import pytz
import uuid
import requests
from datetime import datetime, timezone
from copy import copy
import re
from background_task import background
from django.conf import settings

from django.db.models import Q
from django.utils import timezone
from managr.salesforce.adapter.exceptions import TokenExpired
from managr.alerts.models import AlertConfig, AlertInstance, AlertTemplate
from managr.core.models import User, MeetingPrepInstance
from managr.core.serializers import MeetingPrepInstanceSerializer
from managr.core import constants as core_consts
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce.adapter.models import ContactAdapter
from managr.slack.helpers.block_sets.command_views_blocksets import (
    custom_meeting_paginator_block,
    custom_task_paginator_block,
)
from managr.meetings.models import Meeting
from managr.meetings.serializers import MeetingSerializer
from managr.slack.helpers import requests as slack_requests
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.slack import constants as slack_consts
from managr.slack.helpers import block_builders
from managr.organization.models import Contact
from managr.organization.models import Account
from managr.opportunity.models import Lead, Opportunity
from managr.zoom.background import _split_first_name, _split_last_name
from managr.utils.misc import custom_paginator
from managr.zoom.background import emit_kick_off_slack_interaction

logger = logging.getLogger("managr")

if settings.IN_DEV:
    MANAGR_URL = "http://localhost:8080"
elif settings.IN_STAGING:
    MANAGR_URL = "https://staging.managr.ai"
else:
    MANAGR_URL = "https://app.managr.ai"


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


def emit_process_send_meeting_reminder(user_id, not_completed):
    return _process_send_meeting_reminder(user_id, not_completed)


def emit_process_send_manager_reminder(user_id, not_completed):
    return _process_send_manager_reminder(user_id, not_completed)


def emit_generate_morning_digest(user_id, verbose_name):
    return generate_morning_digest(user_id, verbose_name=verbose_name)


def emit_generate_reminder_message(user_id, verbose_name):
    return generate_reminder_message(user_id, verbose_name=verbose_name)


def emit_check_reminders(user_id, verbose_name):
    return check_reminders(user_id, verbose_name=verbose_name)


def emit_process_non_zoom_meetings(user_id, verbose_name):
    return _process_non_zoom_meetings(user_id, verbose_name=verbose_name)


# Functions for Scheduling Meeting
def emit_non_zoom_meetings(workflow_id, user_id, user_tz, non_zoom_end_times):
    return non_zoom_meeting_message(workflow_id, user_id, user_tz, non_zoom_end_times)


def emit_timezone_tasks(user_id, verbose_name):
    return timezone_tasks(user_id, verbose_name=verbose_name)


def emit_process_workflow_config_check(user_id, verbose_name):
    return _process_workflow_config_check(user_id, verbose_name=verbose_name)


def emit_morning_refresh_message(user_id, verbose_name):
    return _morning_refresh_message(user_id, verbose_name=verbose_name)


#########################################################
# Helper functions
#########################################################


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


def reminder_message_scheduler(self):
    if self.access_token:
        decoded = jwt.decode(
            self.access_token, algorithms="HS512", options={"verify_signature": False}
        )
    exp = decoded["exp"]
    expiration = datetime.fromtimestamp(exp) - timezone.timedelta(minutes=10)

    t = emit_generate_reminder_message(str(self.id), expiration.strftime("%Y-%m-%dT%H:%M"))
    self.refresh_token_task = str(t.id)


def morning_digest_scheduler(self):
    if self.access_token:
        decoded = jwt.decode(
            self.access_token, algorithms="HS512", options={"verify_signature": False}
        )
    exp = decoded["exp"]
    expiration = datetime.fromtimestamp(exp) - timezone.timedelta(minutes=10)

    t = emit_generate_morning_digest(str(self.id), expiration.strftime("%Y-%m-%dT%H:%M"))
    self.refresh_token_task = str(t.id)


def check_for_time(tz, hour, minute):
    user_timezone = pytz.timezone(tz)
    currenttime = datetime.today().time()
    current = pytz.utc.localize(datetime.combine(datetime.today(), currenttime)).astimezone(
        user_timezone
    )
    min = 00 if minute >= 30 else 30
    hr = hour - 1 if minute < 30 else hour
    return current <= current.replace(hour=hour, minute=minute) and current >= current.replace(
        hour=hr, minute=min
    )


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


def _process_calendar_details(user_id):
    user = User.objects.get(id=user_id)
    events = user.nylas._get_calendar_data()
    if events:
        processed_data = []
        for event in events:
            description = event.get("description", None)
            if description is None:
                description = "No Description"
            data = {}
            data["title"] = event.get("title", None)
            data["owner"] = event.get("owner", None)
            data["participants"] = event.get("participants", None)
            data["description"] = description
            conferencing = event.get("conferencing", None)
            if conferencing:
                if "Zoom" in description:
                    data["provider"] = "Zoom Meeting"
                else:
                    data["provider"] = conferencing["provider"]
            data["times"] = event.get("when", None)
            processed_data.append(data)
        return processed_data
    else:
        return None


def meeting_prep(processed_data, user_id):
    def get_domain(email):
        """Parse domain out of an email"""
        return email[email.index("@") + 1 :]

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
    provider = processed_data.get("provider")
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
    if user.has_zoom_integration:
        if (provider == "Zoom Meeting" and user.email not in processed_data["owner"]) or (
            provider not in [None, "Zoom Meeting",]
            and "Zoom meeting" not in processed_data["description"]
        ):
            # Google Meet (Non-Zoom)
            # Sending end_times, workflow_id, and user values to emit function
            non_zoom_end_times = processed_data.get("times").get("end_time")
            workflow_id = str(meeting_workflow.id)
            user_id = str(user.id)
            user_tz = str(user.timezone)
            emit_non_zoom_meetings(workflow_id, user_id, user_tz, non_zoom_end_times)
            logger.info(
                f"-------------------------\nMEETING PREP INFO FOR {user.email}\nMEETING PREP INSTANCE: {meeting_prep_instance.id}\nMEETING WORKFLOW: {meeting_workflow.id}\n-------------------------"
            )
        return


def _send_calendar_details(
    user_id, page, invocation=None,
):
    user = User.objects.get(id=user_id)
    if hasattr(user, "nylas"):
        try:
            processed_data = _process_calendar_details(user_id)
        except Exception as e:
            logger.exception(f"MORNING DIGEST ERROR IN SEND CALENDAR DETAILS: {e}")
            blocks = [
                block_builders.simple_section(":calendar: *Meetings Today* ", "mrkdwn"),
                block_builders.simple_section(
                    "There was an error retreiving your calendar events :exclamation:", "mrkdwn"
                ),
            ]
            return blocks
        current_invocation = invocation
        if processed_data is not None and "status" in processed_data:
            blocks = [
                block_builders.simple_section(":calendar: *Meetings Today* ", "mrkdwn"),
                block_builders.simple_section(
                    "There was an error retreiving your calendar events :exclamation:", "mrkdwn"
                ),
            ]
            return blocks
        if processed_data is not None:
            # processed_data checks to see how many events exists
            if invocation:
                meetings = MeetingPrepInstance.objects.filter(user=user).filter(
                    invocation=invocation
                )
            else:
                last_instance = (
                    MeetingPrepInstance.objects.filter(user=user)
                    .order_by("-datetime_created")
                    .first()
                )
                current_invocation = last_instance.invocation + 1 if last_instance else 1
                for event in processed_data:
                    meeting_prep(event, user_id, current_invocation)
                meetings = MeetingPrepInstance.objects.filter(user=user).filter(
                    invocation=current_invocation
                )
            if meetings:
                paged_meetings = custom_paginator(meetings, count=1, page=page)
                paginate_results = paged_meetings.get("results", [])
                if len(paginate_results):
                    current_instance = paginate_results[0]
                    blocks = [
                        block_builders.simple_section(
                            f":calendar: *Meetings Today*: {len(meetings)}", "mrkdwn"
                        ),
                        *block_sets.get_block_set(
                            "calendar_reminders_blockset",
                            {"prep_id": str(current_instance.id), "u": str(user.id)},
                        ),
                        *custom_meeting_paginator_block(
                            paged_meetings, current_invocation, user.slack_integration.channel
                        ),
                    ]
        else:
            blocks = [
                block_builders.simple_section(":calendar: *Meetings Today*: 0", "mrkdwn"),
                block_builders.simple_section("No meetings scheduled!"),
            ]
    else:
        blocks = [
            block_builders.simple_section(":calendar: *Meetings Today* ", "mrkdwn"),
            block_builders.simple_section(
                "You don't have your calendar connected :exclamation:", "mrkdwn"
            ),
        ]
    return blocks


def process_get_task_list(user_id, page=1):
    user = User.objects.get(id=user_id)
    task_blocks = []
    if hasattr(user, "salesforce_account"):
        attempts = 1
        while True:
            try:
                tasks = user.salesforce_account.adapter_class.list_tasks()
                break
            except TokenExpired:
                if attempts >= 5:
                    task_blocks.extend(
                        [
                            block_builders.simple_section(
                                ":white_check_mark: *Upcoming Tasks*",
                                "mrkdwn",
                                block_id="task_header",
                            ),
                            block_builders.simple_section(
                                "There was an issue retreiving your tasks", "mrkdwn"
                            ),
                        ]
                    )
                    return task_blocks
                else:
                    sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                    time.sleep(sleep)
                    user.salesforce_account.regenerate_token()
                    attempts += 1
            except Exception as e:
                logger.exception(f"Morning digest tasks error: {e}")
                task_blocks.extend(
                    [
                        block_builders.simple_section(
                            ":white_check_mark: *Upcoming Tasks*", "mrkdwn", block_id="task_header",
                        ),
                        block_builders.simple_section(
                            "There was an issue retreiving your tasks", "mrkdwn"
                        ),
                    ]
                )
                return task_blocks
        paged_tasks = custom_paginator(tasks, count=3, page=page)
        results = paged_tasks.get("results", [])
        if results:
            task_blocks.append(
                block_builders.simple_section(
                    f":white_check_mark: *Upcoming Tasks: {len(tasks)}*",
                    "mrkdwn",
                    block_id="task_header",
                ),
            )
            for t in results:
                resource = "_salesforce object n/a_"
                # get the resource if it is what_id is for account/opp
                # get the resource if it is who_id is for lead
                if t.what_id:
                    # first check for opp
                    obj = user.imported_opportunity.filter(integration_id=t.what_id).first()
                    if not obj:
                        obj = user.imported_account.filter(integration_id=t.what_id).first()
                    if obj:
                        resource = f"*{obj.name}*"

                elif t.who_id:
                    obj = user.imported_lead.filter(integration_id=t.who_id).first()
                    if obj:
                        resource = f"*{obj.name}*"
                task_blocks.extend(
                    [
                        block_builders.section_with_button_block(
                            "View Task",
                            "view_task",
                            f"{resource}, due _*{to_date_string(t.activity_date)}*_, {t.subject} `{t.status}`",
                            url=f"{user.salesforce_account.instance_url}/lightning/r/Task/{t.id}/view",
                        ),
                    ]
                )
            task_blocks.extend(
                custom_task_paginator_block(paged_tasks, user.slack_integration.channel)
            )
    return task_blocks


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
def _process_non_zoom_meetings(user_id):
    user = User.objects.get(id=user_id)
    if user.has_nylas_integration:
        try:
            processed_data = _process_calendar_details(user_id)
        except Exception as e:
            logger.exception(f"Pulling calendar data error for {user.email} <ERROR: {e}>")
            processed_data = None
        if processed_data is not None:
            for event in processed_data:
                meeting_prep(event, user_id)
    return


@background()
def non_zoom_meeting_message(workflow_id, user_id, user_tz, non_zoom_end_times):
    # Convert Non-Zoom Meeting from UNIX time to UTC
    unix_time = datetime.utcfromtimestamp(int(non_zoom_end_times))
    tz = pytz.timezone("UTC")
    local_end = unix_time.astimezone(tz)
    current_time = datetime.now()
    local_current = current_time.astimezone(pytz.timezone("UTC"))
    if local_end < local_current:
        seconds = local_current
        time_difference = "Meeting passed current time"
    else:
        time_difference = local_end - local_current
        seconds = time_difference.total_seconds()
        seconds = int(seconds)
    logger.info(
        f"NON ZOOM MEETING SCHEDULER: \n END TIME: {non_zoom_end_times}\n LOCAL END: {local_end}\n CURRENT TIME: {current_time} \n TIME DIFFERENCE: {time_difference}"
    )
    return emit_kick_off_slack_interaction(user_id, workflow_id, schedule=seconds)


@background()
def _process_send_workflow_reminder(user_id, workflow_count):
    user = User.objects.get(id=user_id)
    if hasattr(user, "slack_integration"):
        access_token = user.organization.slack_integration.access_token
        blocks = block_sets.get_block_set("workflow_reminder", {"workflow_count": workflow_count})

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
def _process_send_meeting_reminder(user_id, not_completed):
    user = User.objects.get(id=user_id)
    if hasattr(user, "slack_integration"):
        access_token = user.organization.slack_integration.access_token
        blocks = block_sets.get_block_set("meeting_reminder", {"not_completed": not_completed})
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


@background()
def _process_send_manager_reminder(user_id, not_completed):
    user = User.objects.get(id=user_id)
    if hasattr(user, "slack_integration"):
        access_token = user.organization.slack_integration.access_token
        name = user.first_name if hasattr(user, "first_name") else user.full_name
        blocks = block_sets.get_block_set(
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
def generate_morning_digest(user_id, invocation=None, page=1):
    user = User.objects.get(id=user_id)
    blocks = [
        block_builders.simple_section("*Morning Digest* :coffee:", "mrkdwn"),
        {"type": "divider"},
    ]
    alerts = process_current_alert_list(user_id)
    meeting = _send_calendar_details(user_id, page, invocation)
    tasks = process_get_task_list(user_id)
    blocks = [
        *blocks,
        *meeting,
        {"type": "divider"},
        *tasks,
        {"type": "divider", "block_id": "task_divider"},
        *alerts,
    ]
    if invocation is None:
        try:
            slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
            return {"response_action": "clear"}
        except Exception as e:
            logger.exception(f"Failed to send morning digest message to {user.email} due to {e}")
    else:
        return blocks


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
            meeting = block_sets.get_block_set(
                "manager_meeting_reminder",
                {"u": str(user.id), "not_completed": meetings["uncompleted"], "name": name,},
            )
    else:
        meetings = check_for_uncompleted_meetings(user.id)
        if meetings["status"]:
            meeting = block_sets.get_block_set(
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
                if key == core_consts.WORKFLOW_REMINDER:
                    if datetime.today().weekday() == 4:
                        workflows = check_workflows_count(user.id)
                        if workflows["status"] and workflows["workflow_count"] <= 2:
                            emit_process_send_workflow_reminder(
                                str(user.id), workflows["workflow_count"]
                            )
                elif key == core_consts.REMINDER_MESSAGE_REP and user.user_level != "MANAGER":
                    emit_generate_reminder_message(
                        user_id, f"reminder-message-{user.email}-{str(uuid.uuid4())}"
                    )
                elif key == core_consts.REMINDER_MESSAGE_MANAGER and user.user_level == "MANAGER":
                    emit_generate_reminder_message(
                        user_id, f"reminder-message-{user.email}-{str(uuid.uuid4())}"
                    )
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


####################################################
# TIMEZONE TASK FUNCTIONS
####################################################

TIMEZONE_TASK_FUNCTION = {
    core_consts.NON_ZOOM_MEETINGS: emit_process_non_zoom_meetings,
    core_consts.CALENDAR_CHECK: emit_process_add_calendar_id,
    core_consts.WORKFLOW_CONFIG_CHECK: emit_process_workflow_config_check,
    core_consts.MORNING_REFRESH: emit_morning_refresh_message,
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
    for key in tasks.keys():
        check = check_for_time(user.timezone, tasks[key]["HOUR"], tasks[key]["MINUTE"])
        if check:
            verbose_name = f"{key}-{user.email}-{str(uuid.uuid4())}"
            TIMEZONE_TASK_FUNCTION[key](user_id, verbose_name)
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
        logger.info(
            textwrap.dedent(
                f"""
            ------------------------------------
            NYLAS CALENAR ACCOUNT CREATION INFO: \n
            CALENDAR INFO:{calendar}\n
            EMAIL CHECK: {email_check} \n 
            CALENDAR CHECK: {calendar} \n
            FOUND CALENDAR ID: {calendar_id}\n
            ------------------------------------"""
            )
        )
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
