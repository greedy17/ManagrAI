import logging
import kronos
import requests
import datetime
from django.utils import timezone

from django.db.models import Q

from managr.core.nylas.auth import revoke_all_access_tokens
from managr.core.models import EmailAuthAccount, User
from managr.lead.models import Reminder, Notification, Lead, LeadActivityLog
from managr.core import constants as core_consts
from managr.lead import constants as lead_consts
from .nylas.emails import send_system_email
from managr.core.nylas.auth import revoke_all_access_tokens, revoke_access_token

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


def _create_notification(title, content, notification_type, lead, user):
    Notification.objects.create(
        notify_at=timezone.now(),
        title=title,
        notification_type=notification_type,
        resource_id=lead.id,
        user=user,
        meta={
            "id": str(lead.id),
            "title": title,
            "content": content,
            "leads": [{"id": str(lead.id), "title": lead.title}],
        },
    )


def _check_if_user_has_enabled_lead_alerts(user, notification_title):
    """ Manager type users can choose to disable alerts, they do not receive the emails"""
    if user.type == core_consts.ACCOUNT_TYPE_REP:
        return True
    else:
        notification_settings = user.notification_settings.filter(
            option__key=core_consts.NOTIFICATION_KEY_OPPORTUNITY,
            option__title=notification_title,
        ).first()

        if notification_settings:
            return notification_settings.value
        else:
            return True


def _generate_notification_title_lapsed(num):
    if num == 1:
        return "Opportunity expected close date lapsed by at least 1 day"
    else:
        return f"Opportunity expected close date lapsed by at least {num} days"

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
            # check notification settings
            notification_settings = row.created_by.notification_settings.filter(
                option__key="REMINDER", option__notification_type="ALERT"
            ).first()
            if notification_settings and notification_settings.value != True:
                return
            n = Notification.objects.create(
                notify_at=row.datetime_for,
                title=row.title,
                notification_type="REMINDER",
                resource_id=row.id,
                user=row.created_by,
                meta={
                    "id": str(row.id),
                    "title": row.title,
                    "content": row.content,
                    "linked_contacts": [
                        {"id": str(c.id), "full_name": c.full_name,}
                        for c in row.linked_contacts.all()
                    ],
                    "leads": [
                        {"id": str(row.created_for.id), "title": row.created_for.title}
                    ],
                },
            )
            n.save()
        else:

            logger.exception(f"The Reminder with id {row.id} does not reference a lead")


@kronos.register("0 0 * * *")
def create_lead_notifications():
    # alerts for
    #   activity no activity in last 90 days
    #   no response from email after 3 days ## LEAVING THIS OUT FOR NOW
    #   days since expected close date 1 day 14 days 30 days
    #   stalled in stage 60days
    #   admins receive only alerts reps recieve alerts and emails admins can choose to remove
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
            if lead.activity_logs.exists():
                latest_activity = (
                    lead.activity_logs.latest("action_timestamp").action_timestamp
                ).date()
            else:
                latest_activity = (lead.datetime_created).date()

            if latest_activity < target_date.date():
                # 4 check if an alert/email already exists (reps only get alerts not emails)
                if (
                    user.type == core_consts.ACCOUNT_TYPE_REP
                    or _check_if_user_has_enabled_lead_alerts(
                        user, NOTIFICATION_TITLE_INACTIVE
                    )
                ):
                    # check notifications for one first
                    has_alert = Notification.objects.filter(
                        user=user,
                        notification_type=lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
                        resource_id=str(lead.id),
                    ).first()
                    # TODO: Skipping email check because it is impossible currently to know if it was already sent user will recieve email every day pb 10/13/2020
                    if not has_alert:
                        # create alert
                        latest_activity_str = _convert_to_user_friendly_date(
                            latest_activity
                        )
                        title = f"Inactive 90+ Days"
                        content = f"Your claimed opportunity {lead.title} has had no activity since {latest_activity_str}"

                        _create_notification(
                            title,
                            content,
                            lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
                            lead,
                            user,
                        )
                        if user.type == core_consts.ACCOUNT_TYPE_REP:
                            recipient = [{"name": user.full_name, "email": user.email}]
                            title = f"No New Activity on opportunity {lead.title} since {latest_activity_str}"
                            message = {
                                "subject": title,
                                "body": content,
                            }
                            send_system_email(recipient, message)

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
                    if (
                        user.type == core_consts.ACCOUNT_TYPE_REP
                        or _check_if_user_has_enabled_lead_alerts(
                            user,
                            _generate_notification_title_lapsed(
                                notification_late_for_days
                            ),
                        )
                    ):
                        # check notifications for one first
                        has_alert = Notification.objects.filter(
                            user=user,
                            notification_type=notification_type_str,
                            resource_id=str(lead.id),
                        ).first()
                        # TODO: Skipping email check because it is impossible currently to know if it was already sent user will recieve email every day pb 10/13/2020
                        if not has_alert:

                            # create alert
                            expected_close_date_str = _convert_to_user_friendly_date(
                                expected_close_date
                            )

                            title = (
                                f"Lapsed Close Date {notification_late_for_days} day(s)"
                            )
                            content = f"This opportunity was expected to close on {expected_close_date_str}, you are now {is_lapsed} day(s) over"
                            _create_notification(
                                title, content, notification_type_str, lead, user
                            )
                            if user.type == core_consts.ACCOUNT_TYPE_REP:
                                recipient = [
                                    {"name": user.full_name, "email": user.email}
                                ]
                                title = f"Opportunity {lead.title} expected close date lapsed over {notification_late_for_days} day(s)"
                                message = {
                                    "subject": title,
                                    "body": content,
                                }
                                send_system_email(recipient, message)

            target_date = (now - timezone.timedelta(days=60)).date()
            if lead.status_last_update.date() < target_date:
                if (
                    user.type == core_consts.ACCOUNT_TYPE_REP
                    or _check_if_user_has_enabled_lead_alerts(
                        user, NOTIFICATION_TITLE_STALLED_IN_STAGE
                    )
                ):
                    # check notifications for one first
                    has_alert = Notification.objects.filter(
                        user=user,
                        notification_type=lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE,
                        resource_id=str(lead.id),
                    ).first()
                    # TODO: Skipping email check because it is impossible currently to know if it was already sent user will recieve email every day pb 10/13/2020
                    if not has_alert:
                        # create alert
                        status_last_updated_str = _convert_to_user_friendly_date(
                            lead.status_last_update.date()
                        )
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
                            recipient = [{"name": user.full_name, "email": user.email}]
                            title = "Opportunity stalled in stage for over 60 days"
                            message = {
                                "subject": title,
                                "body": content,
                            }
                            send_system_email(recipient, message)


@kronos.register("0 0 * * *")
def revoke_tokens():
    expire = timezone.now() + datetime.timedelta(days=5)
    """ revokes tokens for email auth accounts in state of sync_error, stopped, invalid """
    email_auth_accounts = EmailAuthAccount.objects.filter(
        sync_status__in=core_consts.NYLAS_SYNC_STATUSES_FAILING, last_edited__gte=expire
    ).values_list("access_token", flat=True)
    for token in email_auth_accounts:
        revoke_access_token(token)

