import logging
import kronos
import datetime

from django.utils import timezone
from django.db.models import Q

from managr.core import constants as core_consts
from managr.core.models import NylasAuthAccount
from managr.core.nylas.auth import revoke_access_token

from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets import get_block_set

from managr.zoom.models import ZoomMeeting
from managr.zoom.utils import score_meeting
from server.managr.core.models import Notification


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
    # disabling since email is currently not working
    # send_system_email(recipient, message)


def _create_notification(
    title, content, notification_type, opportunity, user, notification_class="ALERT"
):
    Notification.objects.create(
        notify_at=timezone.now(),
        title=title,
        notification_type=notification_type,
        resource_id=str(opportunity.id),
        notification_class=notification_class,
        user=user,
        meta={
            "id": str(opportunity.id),
            "title": title,
            "content": content,
            "opportunities": [{"id": str(opportunity.id), "title": opportunity.title}],
        },
    )

def _convert_nylas_calendar_details(
    title, events_data, notification_type, opportunity, user, notification_class="ALERT"
):
    Notification.objects.create(
        notify_at=timezone.now(),
        title=title,
        notification_type=notification_type,
        resource_id=str(opportunity.id),
        notification_class=notification_class,
        user=user,
        mata={
            "id": str(opportunity.id),
            "title": title,
            "content": events_data,
            "opportunities": [{"id": str(opportunity.id), "title": opportunity.title}],        
        }
    )   


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
