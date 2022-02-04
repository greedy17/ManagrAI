import logging
import re
from typing import Any
import uuid
from django.conf import settings
import kronos
import datetime

from managr.utils.misc import custom_paginator
from managr.slack.helpers.block_sets.command_views_blocksets import (
    custom_meeting_paginator_block,
    custom_task_paginator_block,
)
from django.utils import timezone
from django.db.models import Q

from managr.slack.helpers import block_builders, block_sets
from managr.alerts.models import AlertConfig
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
from managr.core.background import emit_non_zoom_meetings
from managr.core.background import non_zoom_meeting_message


NOTIFICATION_TITLE_STALLED_IN_STAGE = "Opportunity Stalled in Stage"
NOTIFICATION_TITLE_INACTIVE = "Opportunity Inactive"


NOTIFICATION_TITLE_LAPSED_1 = "Opportunity expected close date lapsed by at least 1 day"
NOTIFICATION_TITLE_LAPSED_14 = "Opportunity expected close date lapsed by at least 14 days"
NOTIFICATION_TITLE_LAPSED_30 = "Opportunity expected close date lapsed by at least 30 days"


logger = logging.getLogger("managr")


def to_date_string(date):
    if not date:
        return "n/a"
    d = datetime.datetime.strptime(date, "%Y-%m-%d")
    return d.strftime("%a, %B %d, %Y")


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
    if events:
        processed_data = []
        for event in events:
            data = {}
            data["title"] = event.get("title", None)
            data['owner'] = event.get('owner', None)
            data["participants"] = event.get("participants", None)
            conferencing = event.get('conferencing', None)
            if conferencing:
                data['provider'] = conferencing['provider']
            data["times"] = event.get("when", None)
            processed_data.append(data)
        return processed_data
    else:
        return None



def meeting_prep(processed_data, user_id, invocation=1, send_slack=True):
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
    event_data = processed_data
    processed_data.pop("participants")
    data = {
        "user": user.id,
        "participants": meeting_contacts,
        "event_data": event_data,
        "invocation": invocation,
    }
    resource_check = meeting_resource_data.get("resource_id", None)
    provider = processed_data.get('provider')
     
    if resource_check:
        data["resource_id"] = meeting_resource_data["resource_id"]
        data["resource_type"] = meeting_resource_data["resource_type"]

    # Creates Meeting Prep Instance 
    serializer = MeetingPrepInstanceSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    meeting_prep_instance = (
        MeetingPrepInstance.objects.filter(user=user).order_by('-datetime_created').first()
    )


    # Conditional Check for Zoom meeting or Non-Zoom Meeting
    if provider != [None,'zoom']:
        # Google Meet (Non-Zoom)
        meeting_workflow = MeetingWorkflow.objects.create(
        non_zoom_meeting=meeting_prep_instance, user=user,
        )

        # Sending end_times, workflow_id, and user values to emit function 
        non_zoom_end_times = processed_data.get('times').get('end_time')
        workflow_id = str(meeting_workflow.id)
        user_id = str(user.id)
        user_tz = str(user.timezone)
        return emit_non_zoom_meetings(workflow_id, user_id, user_tz, non_zoom_end_times)



def _send_calendar_details(
    user_id, page, invocation=None,
):
    user = User.objects.get(id=user_id)
    try:
        processed_data = _process_calendar_details(user_id)
    except Exception as e:
        logger.exception("MORNING DIGEST ERROR IN SEND CALENDAR DETAILS: {e}")
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
            meetings = MeetingPrepInstance.objects.filter(user=user).filter(invocation=invocation)
        else:
            last_instance = (
                MeetingPrepInstance.objects.filter(user=user).order_by("-datetime_created").first()
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
                    *get_block_set(
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
    return blocks


def process_get_task_list(user_id, page=1):
    user = User.objects.get(id=user_id)
    task_blocks = []
    try:
        tasks = user.salesforce_account.adapter_class.list_tasks()
    except Exception as e:
        logger.exception(f"Morning digest tasks error: {e}")
        task_blocks.extend(
            [
                block_builders.simple_section(
                    ":white_check_mark: *Upcoming Tasks*", "mrkdwn", block_id="task_header",
                ),
                block_builders.simple_section("There was an issue retreiving your tasks", "mrkdwn"),
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
            resource_type = None
            if t.what_id:
                # first check for opp
                obj = user.imported_opportunity.filter(integration_id=t.what_id).first()
                resource_type = "Opportunity"
                if not obj:
                    obj = user.imported_account.filter(integration_id=t.what_id).first()
                    resource_type = "Account"
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
        task_blocks.extend(custom_task_paginator_block(paged_tasks, user.slack_integration.channel))
    else:
        task_blocks = [
            block_builders.simple_section("You have no upcoming tasks :clap:", "mrkdwn"),
        ]
    return task_blocks


def process_current_alert_list(user_id):
    user = User.objects.get(id=user_id)
    configs = AlertConfig.objects.filter(Q(template__user=user.id, template__is_active=True))
    alert_blocks = [
        block_builders.simple_section(f":eyes: *Pipeline Monitor*", "mrkdwn"),
    ]
    if configs:
        for config in configs:
            channel_info = slack_requests.get_channel_info(
                user.organization.slack_integration.access_token, config.recipients[0]
            )
            name = channel_info.get("channel").get("name")
            alert_blocks = [
                *alert_blocks,
                block_builders.simple_section(f"{config.template.title}: #{name}", "mrkdwn"),
            ]
    else:
        alert_blocks.append(
            block_builders.simple_section("Your pipeline look good today :thumbsup: ", "mrkdwn")
        )
    return alert_blocks


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
        except Exception as e:
            logger.exception(f"Failed to send morning digest message to {user.email} due to {e}")
    else:
        return blocks


def process_uncompleted_meeting(user_id, meetings):
    user = User.objects.get(id=user_id)
    meetings = check_for_uncompleted_meetings(user.id, True)
    print(meetings, "this is meetings")
    total_meetings = meetings['not_completed']
    print(total_meetings, "this is total meetings")
    paged_tasks = custom_paginator((total_meetings), count=1)
    results = paged_tasks.get("results", [])
    if results:
        uncompleted_meetings = ''
        for t in results:
            uncompleted_meetings = t
            uncompleted_meetings = str(t).split(',')
            uncompleted_meeting_name = uncompleted_meetings[1]
            # text += ", "
        
            task_blocks = [
                block_builders.simple_section(":calendar: *Non-Zoom Meetings*", "mrkdwn"),
            ]
            task_blocks = [
                *task_blocks, block_builders.simple_section(f"{uncompleted_meeting_name}")
            ]
            task_blocks.extend(
                custom_task_paginator_block(paged_tasks, user.slack_integration.channel)
            )
    else:
        task_blocks = [
            block_builders.simple_section("You have no tasks due today :clap:", "mrkdwn"),
        ]
                    
    # if meetings["status"]:
    #        message = [block_builders.simple_section("This is {meetings}", "mrkdwn")]
    return task_blocks


def generate_afternoon_digest(user_id):
    user = User.objects.get(id=user_id)
    #   check user_level for manager
    if user.user_level == "MANAGER":
        meetings = check_for_uncompleted_meetings(user.id, True)
        name = user.first_name if hasattr(user, "first_name") else user.full_name
        if meetings["status"]:
            # slack_id = meetings['slack_id']
            total_meetings = meetings['not_completed']
            paged_meetings = custom_paginator((total_meetings), count=1)
            print(paged_meetings, "This is paged meetings")
            paginate_results = paged_meetings.get("results", [])
            if (paginate_results):
                meeting = [block_sets.get_block_set(
                    "manager_meeting_reminder",
                    {"u": str(user.id), "not_completed": meetings["not_completed"]},
                ),
                ]
                meeting.extend(custom_task_paginator_block(paged_meetings, user.slack_integration.channel))

        

            meeting = block_sets.get_block_set(
                "manager_meeting_reminder",
                {"u": str(user.id), "not_completed": meetings},
            )

        else:
            meeting = [
                block_builders.simple_section(
                    "Your team has logged all of their meetings today! :clap:", "mrkdwn"
                )
            ]
    else:
        meetings = check_for_uncompleted_meetings(user.id)
        logger.info(f"UNCOMPLETED MEETINGS FOR {user.email}: {meetings}")
        if meetings["status"]:
            meeting = block_sets.get_block_set(
                "meeting_reminder", {"u": str(user.id), "not_completed": meetings['not_completed']}
            )
        else:
            meeting = [
                block_builders.simple_section(
                    "You've completed all your meetings today! :clap:", "mrkdwn"
                )
            ]
    actions = block_sets.get_block_set("actions_block_set", {"u": str(user.id)})
    message = process_uncompleted_meeting(user_id, meetings)
    try:
        slack_requests.send_channel_message(
            user.slack_integration.channel,
            user.organization.slack_integration.access_token,
            block_set=[
                block_builders.simple_section("*Afternoon Digest* :beer:", "mrkdwn"),
                {"type": "divider"},
                *meeting,
                {"type": "divider"},
                *message,
                {"type": "divider"},
                *actions,
            ],
        )
    except Exception as e:
        logger.exception(f"Failed to send reminder message to {user.email} due to {e}")


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
                if key == core_consts.MORNING_DIGEST:
                    if hasattr(user, "nylas"):
                        generate_morning_digest(user_id)
                elif key == core_consts.WORKFLOW_REMINDER:
                    if datetime.datetime.today().weekday() == 4:
                        workflows = check_workflows_count(user.id)
                        if workflows["status"] and workflows["workflow_count"] <= 2:
                            emit_process_send_workflow_reminder(
                                str(user.id), workflows["workflow_count"]
                            )
                elif key == core_consts.AFTERNOON_DIGEST_REP and user.user_level != "MANAGER":
                    generate_afternoon_digest(user_id)
                elif key == core_consts.AFTERNOON_DIGEST_MANAGER and user.user_level == "MANAGER":
                    generate_afternoon_digest(user_id)
    return
