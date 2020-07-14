import kronos
import requests
from managr.core.nylas.auth import revoke_all_access_tokens
from managr.core.models import EmailAuthAccount
from managr.lead.models import Reminder, Notification
from django.utils import timezone

# Daily, at hour 0, minute 0 (12am)
@kronos.register("0 0 * * *")
def revoke_extra_access_tokens():
    """ this will remove excess access tokens managr will be charged for excess tokens as accounts
    it will only keep access tokens we have stored in the EmailAuthAccount regardless of sync status
    """
    for row in EmailAuthAccount.objects.all():
        try:
            revoke_all_access_tokens(
                row.account_id, keep_token=row.access_token)
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
def create_notification():
    """ Poll the reminders endpoint and create a notification if the reminder is 5 mins away """
    now = timezone.now()
    remind_time = now+timezone.timedelta(minutes=5)
    for row in Reminder.objects.filter(datetime_for__gte=now, datetime_for__lte=remind_time):
        if row.has_notification:
            return
        else:
            n = Notification.objects.create(
                notify_at=row.datetime_for,
                title=row.title,
                notification_type="REMINDER",
                resource_id=row.id,


            )
            n.save()

        return row
