import logging
import kronos
import requests
import datetime
import random

from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from managr.core.nylas.auth import revoke_all_access_tokens
from managr.core.models import EmailAuthAccount, User
from managr.lead.models import Reminder, Notification, Lead, LeadActivityLog
from managr.core import constants as core_consts
from managr.lead import constants as lead_consts

from managr.core.nylas.auth import revoke_all_access_tokens, revoke_access_token
from managr.lead.lead_score_generation import generate_lead_scores
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets import get_block_set

from managr.zoom.models import ZoomMeeting
from managr.zoom.utils import score_meeting

from .nylas.emails import send_system_email

NOTIFICATION_TITLE_STALLED_IN_STAGE = "Opportunity Stalled in Stage"
NOTIFICATION_TITLE_INACTIVE = "Opportunity Inactive"


NOTIFICATION_TITLE_LAPSED_1 = "Opportunity expected close date lapsed by at least 1 day"
NOTIFICATION_TITLE_LAPSED_14 = (
    "Opportunity expected close date lapsed by at least 14 days"
)
NOTIFICATION_TITLE_LAPSED_30 = (
    "Opportunity expected close date lapsed by at least 30 days"
)


logger = logging.getLogger("managr")


def _check_days_lead_expected_close_lapsed(lead_expected_close_date):
    now = timezone.now()
    if (now - lead_expected_close_date).days > 0:
        return (now - lead_expected_close_date).days
    else:
        return 0


def _convert_to_user_friendly_date(date):
    return date.strftime("%m/%d/%Y")


def _has_alert(user, notification_class, notification_type, resource_id):
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
    send_system_email(recipient, message)


def _create_notification(
    title, content, notification_type, lead, user, notification_class="ALERT"
):
    Notification.objects.create(
        notify_at=timezone.now(),
        title=title,
        notification_type=notification_type,
        resource_id=str(lead.id),
        notification_class=notification_class,
        user=user,
        meta={
            "id": str(lead.id),
            "title": title,
            "content": content,
            "leads": [{"id": str(lead.id), "title": lead.title}],
        },
    )


def _generate_notification_key_lapsed(num):
    if num == 1:
        return (
            core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_1_DAY
        )
    if num == 14:
        return (
            core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_14_DAYS
        )
    if num == 30:
        return (
            core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_30_DAYS
        )

    # its not ideal that we are checking against a string, but since these are loaded from the fixture
    # we can assume they will be the same


# Daily, at hour 0, minute 0 (12am)
@kronos.register("0 0 * * *")
def revoke_extra_access_tokens():
    """ this will remove excess access tokens managr will be charged for excess tokens as accounts
    it will only keep access tokens we have stored in the EmailAuthAccount regardless of sync status
    """
    for row in EmailAuthAccount.objects.all():
        try:
            revoke_all_access_tokens(row.account_id, keep_token=row.access_token)
            row.delete()

        except requests.exceptions.HTTPError as error:
            if 404 in error.args:
                # delete the record so we can create a new link
                row.email_auth_account.delete()
                # we have out of sync data, pass
                # we have a cron job running every 24 hours to remove all old tokens which are not
                # in sync
            else:
                """
                Most likely an error with our account or their server will
                just log this when the logger is set up
                """
                continue


@kronos.register("* * * * *")
def create_notifications():
    """ Poll the reminders endpoint and create a notification if the reminder is 5 mins away """
    now = timezone.now()
    remind_time = now + timezone.timedelta(minutes=5)
    ns = Notification.objects.filter(notification_type="REMINDER").values_list(
        "resource_id", flat=True
    )
    query = Q()
    for n in ns:
        query |= Q(id=n)

    for row in (
        Reminder.objects.filter(datetime_for__lte=remind_time)
        .exclude(query)
        .order_by("-datetime_for")
    ):
        if row.created_for:
            user = row.created_by
            # check notification settings
            if user.check_notification_enabled_setting(
                core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_REMINDER,
                core_consts.NOTIFICATION_TYPE_ALERT,
            ):

                n = Notification.objects.create(
                    notify_at=row.datetime_for,
                    title=row.title,
                    notification_type="REMINDER",
                    resource_id=row.id,
                    user=user,
                    notification_class="ALERT",
                    meta={
                        "id": str(row.id),
                        "title": row.title,
                        "content": row.content,
                        "linked_contacts": [
                            {"id": str(c.id), "full_name": c.full_name,}
                            for c in row.linked_contacts.all()
                        ],
                        "leads": [
                            {
                                "id": str(row.created_for.id),
                                "title": row.created_for.title,
                            }
                        ],
                    },
                )
            if user.check_notification_enabled_setting(
                core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_REMINDER,
                core_consts.NOTIFICATION_TYPE_SLACK,
            ):
                # when checking slack notification settings, if the user has opted to
                # receive slack notifs but has not integrated slack send them an email (assuming their org has set it up)
                # reminding them to set up slack

                if user.send_email_to_integrate_slack:
                    _send_slack_int_email(user)
                if hasattr(user, "slack_integration"):
                    user_slack_channel = user.slack_integration.channel
                    slack_org_access_token = (
                        user.organization.slack_integration.access_token
                    )
                    block_set = get_block_set("reminder_block_set", {"r": str(row.id)})
                    slack_requests.send_channel_message(
                        user_slack_channel, slack_org_access_token, block_set=block_set
                    )
                    n = Notification.objects.create(
                        notify_at=row.datetime_for,
                        title=row.title,
                        notification_type="REMINDER",
                        resource_id=row.id,
                        user=user,
                        notification_class="SLACK",
                        meta={
                            "id": str(row.id),
                            "title": row.title,
                            "content": row.content,
                            "linked_contacts": [
                                {"id": str(c.id), "full_name": c.full_name,}
                                for c in row.linked_contacts.all()
                            ],
                            "leads": [
                                {
                                    "id": str(row.created_for.id),
                                    "title": row.created_for.title,
                                }
                            ],
                        },
                    )

        else:

            logger.exception(f"The Reminder with id {row.id} does not reference a lead")


@kronos.register("0 0 * * *")
def create_lead_notifications():
    # alerts for
    #   activity no activity in last 90 days
    #   no response from email after 3 days ## LEAVING THIS OUT FOR NOW
    #   days since expected close date 1 day 14 days 30 days
    #   stalled in stage 60days
    #   admins receive only alerts reps recieve alerts and emails admins
    # can choose to remove receive or not receive

    # 1 get all users who are active will also include super user so mike can also get notifs
    users = User.objects.filter(is_active=True)
    for user in users:
        # 2 get leads for specific user
        leads = list()
        # rep level users only get notifs for leads they are claiming except closed leads
        if user.type == core_consts.ACCOUNT_TYPE_REP:
            leads = user.claimed_leads.all().exclude(
                status__title="CLOSED", status__type="PUBLIC"
            )
        else:
            leads = Lead.objects.filter(
                account__organization=user.organization_id
            ).exclude(status__title="CLOSED", status__type="PUBLIC")

        # 3 check if lead meets requirements for each type of alert/email
        for lead in leads:
            now = timezone.now()
            target_date = now - timezone.timedelta(days=90)
            latest_activity = None
            if lead.activity_logs.filter(
                activity__in=lead_consts.LEAD_ACTIONS_TRIGGER_ALERT
            ).exists():
                latest_activity = (
                    lead.activity_logs.filter(
                        activity__in=lead_consts.LEAD_ACTIONS_TRIGGER_ALERT
                    )
                    .latest("action_timestamp")
                    .action_timestamp
                ).date()
            else:
                latest_activity = (lead.datetime_created).date()

            if latest_activity < target_date.date():
                # 4 check if an alert/email already exists (reps only get alerts not emails)
                if user.check_notification_enabled_setting(
                    core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_INACTIVE_90_DAYS,
                    core_consts.NOTIFICATION_TYPE_ALERT,
                ):
                    # check notifications for one first
                    latest_activity_str = _convert_to_user_friendly_date(
                        latest_activity
                    )
                    title = "Inactive 90+ Days"
                    content = f"Your claimed opportunity {lead.title} has had no activity since {latest_activity_str}"
                    if not _has_alert(
                        user,
                        core_consts.NOTIFICATION_TYPE_ALERT,
                        lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
                        str(lead.id),
                    ):
                        # create alert
                        _create_notification(
                            title,
                            content,
                            lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
                            lead,
                            user,
                        )
                        # managers do not get emails for this version
                if user.type == core_consts.ACCOUNT_TYPE_REP:
                    # check if email alert already sent

                    if not _has_alert(
                        user,
                        core_consts.NOTIFICATION_TYPE_EMAIL,
                        lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
                        str(lead.id),
                    ):
                        recipient = [{"name": user.full_name, "email": user.email}]
                        title = f"No New Activity on opportunity {lead.title} since {latest_activity_str}"
                        message = {
                            "subject": title,
                            "body": content,
                        }
                        send_system_email(recipient, message)
                        # create notification of that class in notifications

                        _create_notification(
                            title,
                            content,
                            lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
                            lead,
                            user,
                            core_consts.NOTIFICATION_TYPE_EMAIL,
                        )

                if user.check_notification_enabled_setting(
                    core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_INACTIVE_90_DAYS,
                    core_consts.NOTIFICATION_TYPE_SLACK,
                ):
                    if not _has_alert(
                        user,
                        core_consts.NOTIFICATION_TYPE_SLACK,
                        lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
                        str(lead.id),
                    ):
                        latest_activity_str = _convert_to_user_friendly_date(
                            latest_activity
                        )
                        # create notification of that class in notifications

                        # when checking slack notification settings, if the user has opted to
                        # receive slack notifs but has not integrated slack send them an email (assuming their org has set it up)
                        # reminding them to set up slack

                        if user.send_email_to_integrate_slack:
                            _send_slack_int_email(user)
                        if hasattr(user, "slack_integration"):
                            ## check if alert already exists
                            title = f"No New Activity on opportunity {lead.title} since {latest_activity_str}"
                            slack_message = f"No New Activity on opportunity {lead.title} since {latest_activity_str}"

                            user_slack_channel = user.slack_integration.channel
                            slack_org_access_token = (
                                user.organization.slack_integration.access_token
                            )
                            block_set = get_block_set(
                                "opp_inactive_block_set",
                                {
                                    "l": str(lead.id),
                                    "m": slack_message,
                                    "u": str(user.id),
                                },
                            )
                            slack_requests.send_channel_message(
                                user_slack_channel,
                                slack_org_access_token,
                                block_set=block_set,
                            )

                            _create_notification(
                                title,
                                slack_message,
                                lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
                                lead,
                                user,
                                core_consts.NOTIFICATION_TYPE_SLACK,
                            )

            expected_close_date = None
            if lead.expected_close_date:
                expected_close_date = lead.expected_close_date
                is_lapsed = _check_days_lead_expected_close_lapsed(expected_close_date)
                if is_lapsed >= 1 and is_lapsed < 14:
                    notification_late_for_days = 1
                elif is_lapsed >= 14 and is_lapsed < 30:
                    notification_late_for_days = 14
                elif is_lapsed >= 30:
                    notification_late_for_days = 30
                if is_lapsed > 0:
                    notification_type_str = "OPPORTUNITY.LAPSED_EXPECTED_CLOSE_DATE_{}".format(
                        notification_late_for_days
                    )

                    expected_close_date_str = _convert_to_user_friendly_date(
                        expected_close_date
                    )
                    if user.check_notification_enabled_setting(
                        _generate_notification_key_lapsed(notification_late_for_days),
                        core_consts.NOTIFICATION_TYPE_ALERT,
                    ):
                        # check notifications for one first

                        if not _has_alert(
                            user,
                            core_consts.NOTIFICATION_TYPE_ALERT,
                            notification_type_str,
                            str(lead.id),
                        ):

                            # create alert

                            title = (
                                f"Lapsed Close Date {notification_late_for_days} day(s)"
                            )
                            content = f"This opportunity was expected to close on {expected_close_date_str}, you are now {is_lapsed} day(s) over"
                            _create_notification(
                                title, content, notification_type_str, lead, user
                            )
                    if user.type == core_consts.ACCOUNT_TYPE_REP:
                        # check if email alert already sent

                        if not _has_alert(
                            user,
                            core_consts.NOTIFICATION_TYPE_EMAIL,
                            notification_type_str,
                            str(lead.id),
                        ):
                            recipient = [{"name": user.full_name, "email": user.email}]
                            title = f"Opportunity {lead.title} expected close date lapsed over {notification_late_for_days} day(s)"
                            content = f"This opportunity was expected to close on {expected_close_date_str}, you are now {is_lapsed} day(s) over"
                            message = {
                                "subject": title,
                                "body": content,
                            }
                            send_system_email(recipient, message)
                            _create_notification(
                                title,
                                content,
                                notification_type_str,
                                lead,
                                user,
                                core_consts.NOTIFICATION_TYPE_EMAIL,
                            )

                    if user.check_notification_enabled_setting(
                        _generate_notification_key_lapsed(notification_late_for_days),
                        core_consts.NOTIFICATION_TYPE_SLACK,
                    ):

                        if not _has_alert(
                            user,
                            core_consts.NOTIFICATION_TYPE_SLACK,
                            notification_type_str,
                            str(lead.id),
                        ):
                            # create notification of that class in notifications
                            if user.send_email_to_integrate_slack:
                                _send_slack_int_email(user)
                            if hasattr(user, "slack_integration"):
                                ## check if alert already exists
                                title = f"Opportunity {lead.title} expected close date lapsed over {notification_late_for_days} day(s)"
                                content = f"This {lead.title}  opportunity was expected to close on {expected_close_date_str}, you are now {is_lapsed} day(s) over"

                                user_slack_channel = user.slack_integration.channel
                                slack_org_access_token = (
                                    user.organization.slack_integration.access_token
                                )
                                block_set = get_block_set(
                                    "opp_inactive_block_set",
                                    {
                                        "l": str(lead.id),
                                        "m": content,
                                        "u": str(user.id),
                                    },
                                )
                                slack_requests.send_channel_message(
                                    user_slack_channel,
                                    slack_org_access_token,
                                    block_set=block_set,
                                )

                                _create_notification(
                                    title,
                                    content,
                                    notification_type_str,
                                    lead,
                                    user,
                                    core_consts.NOTIFICATION_TYPE_SLACK,
                                )

            target_date = (now - timezone.timedelta(days=60)).date()
            if lead.status_last_update.date() < target_date:
                if user.check_notification_enabled_setting(
                    core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_STALLED_IN_STAGE,
                    core_consts.NOTIFICATION_TYPE_ALERT,
                ):
                    # check notifications for one first
                    status_last_updated_str = _convert_to_user_friendly_date(
                        lead.status_last_update.date()
                    )
                    if not _has_alert(
                        user,
                        core_consts.NOTIFICATION_TYPE_ALERT,
                        lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE,
                        str(lead.id),
                    ):
                        # create alert

                        title = "60+ days in stage"

                        content = f"{lead.title} has been in the same stage since {status_last_updated_str}"

                        _create_notification(
                            title,
                            content,
                            lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE,
                            lead,
                            user,
                        )
                    if user.type == core_consts.ACCOUNT_TYPE_REP:
                        if not _has_alert(
                            user,
                            core_consts.NOTIFICATION_TYPE_EMAIL,
                            lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE,
                            str(lead.id),
                        ):
                            recipient = [{"name": user.full_name, "email": user.email}]
                            title = "Opportunity stalled in stage for over 60 days"
                            content = f"{lead.title} has been in the same stage since {status_last_updated_str}"
                            message = {
                                "subject": title,
                                "body": content,
                            }
                            send_system_email(recipient, message)
                            _create_notification(
                                title,
                                content,
                                lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE,
                                lead,
                                user,
                                core_consts.NOTIFICATION_TYPE_EMAIL,
                            )
                    if user.check_notification_enabled_setting(
                        core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_STALLED_IN_STAGE,
                        core_consts.NOTIFICATION_TYPE_SLACK,
                    ):

                        if not _has_alert(
                            user,
                            core_consts.NOTIFICATION_TYPE_SLACK,
                            lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE,
                            str(lead.id),
                        ):
                            title = "Opportunity stalled in stage for over 60 days"
                            content = f"{lead.title} has been in the same stage since {status_last_updated_str}"
                            # create notification of that class in notifications

                            # when checking slack notification settings, if the user has opted to
                            # receive slack notifs but has not integrated slack send them an email (assuming their org has set it up)
                            # reminding them to set up slack
                            if user.send_email_to_integrate_slack:
                                _send_slack_int_email(user)
                            if hasattr(user, "slack_integration"):
                                ## check if alert already exists
                                user_slack_channel = user.slack_integration.channel
                                slack_org_access_token = (
                                    user.organization.slack_integration.access_token
                                )
                                block_set = get_block_set(
                                    "opp_inactive_block_set",
                                    {
                                        "l": str(lead.id),
                                        "m": content,
                                        "u": str(user.id),
                                    },
                                )
                                slack_requests.send_channel_message(
                                    user_slack_channel,
                                    slack_org_access_token,
                                    block_set=block_set,
                                )

                                _create_notification(
                                    title,
                                    content,
                                    lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE,
                                    lead,
                                    user,
                                    core_consts.NOTIFICATION_TYPE_SLACK,
                                )

    return


@kronos.register("0 0 * * *")
def revoke_tokens():
    expire = timezone.now() + datetime.timedelta(days=5)
    """ revokes tokens for email auth accounts in state of sync_error, stopped, invalid """
    email_auth_accounts = EmailAuthAccount.objects.filter(
        sync_status__in=core_consts.NYLAS_SYNC_STATUSES_FAILING, last_edited__gte=expire
    ).values_list("access_token", flat=True)
    for token in email_auth_accounts:
        revoke_access_token(token)


# Daily, at 11:59 PM
@kronos.register("59 23 * * *")
def _generate_lead_scores():
    generate_lead_scores()


def generate_meeting_scores():

    meetings = ZoomMeeting.objects.all()
    for meeting in meetings:
        # set scoring in progress in case we run this job multiple times
        meeting.scoring_in_progress = True
        meeting.save()
        meeting.meeting_score = score_meeting(meeting)
        meeting.scoring_in_progress = False
        meeting.save()

        user = meeting.zoom_account.user
        if user.send_email_to_integrate_slack:
            _send_slack_int_email(user)
        if hasattr(user, "slack_integration"):
            user_slack_channel = user.slack_integration.channel
            slack_org_access_token = user.organization.slack_integration.access_token
            managers = user.organization.users.filter(type="MANAGER")
            for manager in managers:
                if hasattr(manager, "slack_integration"):
                    slack_requests.send_channel_message(
                        user_slack_channel,
                        slack_org_access_token,
                        block_set=get_block_set(
                            "meeting_review_score", {"m": str(meeting.id)}
                        ),
                    )

