import logging
import kronos
import requests
import datetime
from django.utils import timezone

from django.db.models import Q

from managr.core.nylas.auth import revoke_all_access_tokens
from managr.core.models import EmailAuthAccount, User
from managr.lead.models import Reminder, Notification, Lead, LeadActivityLogs
from managr.core import constants as core_consts
from managr.lead import constants as lead_consts
from .nylas.emails import send_system_email
from managr.core.nylas.auth import revoke_all_access_tokens, revoke_access_token


logger = logging.getLogger("managr")

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


@kronos.register("* * * * *")
def create_lead_notifications():
    # alerts for
    #   activity no activity in last 90 days
    #   no response from email after 3 days ## LEAVING THIS OUT FOR NOW
    #   days since expected close date 1 day 14 days 30 days
    #   stalled in stage
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
            leads = Lead.objects.filter(account__organization=user.organization_id)

        # 3 check if lead meets requirements for each type of alert/email
        for lead in leads:
            now = timezone.now()
            target_date = now + timezone.timedelta(days=90)
            # last activity
            latest_activity = (
                lead.activity_logs.latest("datetime_created").datetime_created
            ).date()
            if latest_activity > target_date.date():
                # 4 check if an alert/email already exists (reps only get alerts not emails)
                if user.type == core_consts.ACCOUNT_TYPE_REP:
                    # check notifications for one first
                    # has_alert = Notification.objects.filter(
                    #    user=user,
                    #    notification_type=lead_consts.NOTIFICATION_TYPE_OPPORTUNITY,
                    #    resource_id=str(lead.id),
                    # ).first()
                    # TODO: Skipping email check because it is impossible currently to know if it was already sent user will recieve email every day pb 10/13/2020
                    # if has_alert:
                    #    continue
                    # else:
                    # create alert
                    title = f"No New Activity on opportunity {lead.title} since {latest_activity}"
                    Notification.objects.create(
                        notify_at=timezone.now(),
                        title=title,
                        notification_type="LEAD",
                        resource_id=lead.id,
                        user=user,
                        meta={
                            "id": str(lead.id),
                            "title": "This opportunity has had no activity for at least 90 days",
                        },
                    )
                    recipient = user.email
                    message = {
                        "subject": f"No New Activity on opportunity {lead.title} since {latest_activity}",
                        "body": f"Your claimed opportunity {lead.title} has had no activity since {latest_activity}",
                    }
                    send_system_email(recipient, message)

            target_date_1 = now + timezone.timedelta(days=1)
            target_date_14 = now + timezone.timedelta(days=14)
            target_date_30 = now + timezone.timedelta(days=30)
            expected_close_date = lead.expected_close_date.date()
            if (
                lead.expected_close_date.date() > target_date_1
                or lead.expected_close_date.date() > target_date_14
                or lead.expected_close_date.date() > target_date_30
            ):
                if user.type == core_consts.ACCOUNT_TYPE_REP:
                    # check notifications for one first
                    # has_alert = Notification.objects.filter(
                    #    user=user,
                    #    notification_type=lead_consts.NOTIFICATION_TYPE_OPPORTUNITY,
                    #    resource_id=str(lead.id),
                    # ).first()
                    # TODO: Skipping email check because it is impossible currently to know if it was already sent user will recieve email every day pb 10/13/2020
                    # if has_alert:
                    #    continue
                    # else:
                    # create alert

                    title = f"Opportunity {lead.title} expected close date lapsed"
                    Notification.objects.create(
                        notify_at=timezone.now(),
                        title=title,
                        notification_type="LEAD",
                        resource_id=lead.id,
                        user=user,
                        meta={
                            "id": str(lead.id),
                            "title": f"This opportunity was expected to close on {expected_close_date}",
                        },
                    )
                    recipient = user.email
                    message = {
                        "subject": f"Opportunity {lead.title} expected close date lapsed",
                        "body": f"Your claimed opportunity was expected to close on {expected_close_date}",
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

