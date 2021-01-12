import logging

import datetime

from background_task import background

from django.db.models import F, Q, Count
from django.utils import timezone


from managr.core.models import EmailAuthAccount, User
from managr.lead.background import emit_event as log_event
from managr.lead import constants as lead_constants
from managr.core import constants as core_consts
from managr.lead.models import Notification,LeadActivityLog

from managr.report.story_report_generation import generate_story_report_data
from managr.report.performance_report_generation import generate_performance_report_data

from managr.report import constants as report_const

from ..nylas.emails import retrieve_message, retrieve_thread, send_system_email

logger = logging.getLogger("managr")


def _check_notification(thread_id):
    return Notification.objects.filter(
        resource_id=thread_id, notification_type="EMAIL_OPENED"
    ).exists()


def emit_event(account_id, object_id, date, action, **kwargs):
    if action == core_consts.NYLAS_WEBHOOK_TYPE_MSG_CREATED:
        _get_email_notification(account_id, object_id, date)
    elif action == core_consts.NYLAS_WEBHOOK_TYPE_MSG_OPENED:
        _get_email_metadata_info(
            account_id, object_id, date, **{"count": kwargs["count"]}
        )


def emit_generate_story_report_on_close(report, share_to_channel):
    # auto generates report with claimed by user on close

    return _generate_story_report_data(str(report.id), share_to_channel)


def emit_report_event(report_id, report_type):
    if report_type is report_const.STORY_REPORT:
        _generate_story_report_data(report_id)
    else:
        _generate_performance_report_data(report_id)


def emit_email_sync_event(user_id, sync_state):
    _notify_user_of_email_status(user_id, sync_state)


@background(schedule=0)
def _notify_user_of_email_status(user_id, sync_state):
    ## when the branch with alerts is merged we will check
    ## if the user has notifs turned off
    ## In theory running and stopped should not reach here since we are setting those synchroniously
    user = User.objects.filter(pk=user_id).first()
    if user:
        try:
            recipients = [{"name": user.full_name, "email": user.email}]
            message = f"Your Nylas Email Account is currently {sync_state}"
            if sync_state == "stopped":
                message = (
                    message
                    + f" you have either stopped or canceled your integration, \
                    we will remove your account from our platform and from nylas"
                )
            if sync_state == "invalid" or sync_state == "sync_error":
                expire = timezone.now() + datetime.timedelta(days=5)

                message = (
                    message
                    + f" you must login to managr and re authenticate your account \
                        Note, we will remove your integration from our system by {expire}"
                )

            message_obj = {"subject": "Email Integration Alert", "body": message}
            send_system_email(recipients, message_obj)
        except Exception as e:
            logger.warning(
                f"An error occured trying to notify the user with email {user.email} by email, that their account is {sync_state}"
            )
        try:
            Notification.objects.create(
                notify_at=timezone.now(),
                title="Email Integration",
                notification_type="SYSTEM",
                resource_id=str(user.email_auth_account.id),
                user=user,
                meta={"content": message},
            )
        except Exception as e:
            logger.warning(
                f"An error occured trying to notify the user with email {user.email} by notification, that their account is {sync_state}"
            )


@background(schedule=0)
def _generate_story_report_data(report_id, share_to_channel=False):
    return generate_story_report_data(report_id, share_to_channel)


@background(schedule=0)
def _generate_performance_report_data(report_id):
    return generate_performance_report_data(report_id)



