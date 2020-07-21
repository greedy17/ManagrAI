import kronos
import requests
from django.utils import timezone
from django.db.models import Q

from managr.core.nylas.auth import revoke_all_access_tokens
from managr.core.models import EmailAuthAccount
from managr.lead.models import Reminder, Notification


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
def create_notifications():
    """ Poll the reminders endpoint and create a notification if the reminder is 5 mins away """
    now = timezone.now()
    remind_time = now+timezone.timedelta(minutes=5)
    ns = Notification.objects.filter(
        notification_type="REMINDER").values_list('resource_id', flat=True)
    query = Q()
    for n in ns:
        query |= Q(id=n)

    for row in Reminder.objects.filter(datetime_for__lte=remind_time).exclude(query):
        n = Notification.objects.create(
            notify_at=row.datetime_for,
            title=row.title,
            notification_type="REMINDER",
            resource_id=row.id,
            user=row.created_by,
            meta={
                'id': str(row.id),
                'title': row.title,
                'content': row.content,
                'linked_contacts': [
                    {"id": str(c.id), "full_name": c.full_name, }
                    for c in row.linked_contacts.all()
                ],
                'leads': [{'id': str(row.created_for.id), 'title': row.created_for.title}]
            }


        )
        n.save()
