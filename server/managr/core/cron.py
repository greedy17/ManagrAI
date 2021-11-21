import logging
import kronos
import datetime

from django.utils import timezone
from django.db.models import Q

from managr.slack.helpers import block_builders, block_sets

from managr.core import constants as core_consts
from managr.core.models import NylasAuthAccount, User
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
    for event in events:
        data = {}
        data["title"] = event.get("title", None)
        data["participants"] = event.get("participants", None)
        data["times"] = event.get("when", None)
        processed_data.append(data)
    return processed_data


def _send_calendar_details(user_id):
    user = User.objects.get(id=user_id)
    processed_data = _process_calendar_details(user_id)

    # processed_data checks to see how many events exists
    blocks = [
        block_builders.header_block(
            f"Upcoming Meetings For Today! :calendar:"
            # f"Good Morning! You have " + str(len(processed_data)) + " meetings today"
        )
    ]

    for event in processed_data:
        blocks = [
            *blocks,
            *block_sets.get_block_set("calendar_reminders_blockset", {"event_data": event}),
        ]
    # Loop thru processed_data and create block for each one
    # print(blocks)
    try:
        slack_requests.send_channel_message(
            user.slack_integration.channel,
            user.organization.slack_integration.access_token,
            text="Calendar: Meetings for Today",
            block_set=blocks,
        )
    except Exception as e:
        logger.exception(f"Failed to send reminder message to {user.email} due to {e}")
    # print(processed_data)
    return processed_data


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
                if key == core_consts.WORKFLOW_REMINDER:
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
                elif key == core_consts.MEETING_REMINDER_MANAGER:
                    meetings = check_for_uncompleted_meetings(user.id, True)
                    if meetings["status"]:
                        emit_process_send_manager_reminder(str(user.id), meetings["not_completed"])

    return
