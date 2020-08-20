import logging

from background_task import background

from django.db.models import F, Q, Count
from django.utils import timezone

from managr.core.models import EmailAuthAccount, User
from managr.lead.background import emit_event as log_event
from managr.lead import constants as lead_constants
from managr.core import constants as core_consts
from managr.lead.models import Notification, LeadEmail, LeadActivityLog
from managr.report.story_report_generation import generate_story_report_data

from ..nylas.emails import retrieve_message, retrieve_thread

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
<<<<<<< HEAD
=======


def emit_report_event(report_id, generated_by_id):
    _generate_story_report_data(report_id, generated_by_id)


@background(schedule=0)
def _generate_story_report_data(report_id, generated_by_id):
    return generate_story_report_data(report_id, generated_by_id)
>>>>>>> develop


@background(schedule=0)
def _get_email_notification(account_id, object_id, date):
    """
        check if the email is for a lead that the user is claiming
        account_id email account of the user
        object_id the id of the object for querying
        date epoch datetime when the change occured
        we can also use this to emit to the activity log
        currently only looking for incoming emails
    """

    user = None
    try:
        user = User.objects.get(email_auth_account__account_id=account_id)
    except User.DoesNotExist as e:
        logger.exception(
            f"The user account_id is not in saved on the system they might need"
            "to re-auth a token,{account_id}"
        )
        return

    # get the message form nylas and make it into a json object
    # from managr.core.background import _get_email_info
    # t = _get_email_info.now
    # t('2yyyiu5lq221zmm4dvhmng5gc','5s0f2hsvh4htrm4fskqn8xnty','')

    # if user.claimed_leads.count() > 0:
    try:
        if user:

            # the webhook returns a thread_object with a thread_id which does not have enough information
            # to know if it was sent/received and by whom so we need to get the message_id
            # the thread object contains a field called message_ids which is a list of messages
            # relating to each thread, the last message_id is the message of the most recent
            # iteration of the thread so we take that one
            thread = retrieve_thread(user, object_id)

            message_id = thread["message_ids"].pop()

            message = retrieve_message(user, message_id)

            # can use this to check if it is incoming or outgoing
            # message_contacts.extend(
            #    message['bcc']+message['cc']+message['to'] + message['from'])

            message_contacts = message["from"]
            message_to = message["to"]

            message_contacts = [c["email"] for c in message_contacts if c["email"]]
            message_to = [c["email"] for c in message_to if c["email"]]
            # retrieve user leads and contacts
            # create a new leademailaction
            # create a new notification

            leads = user.claimed_leads.filter(
                linked_contacts__email__in=message_contacts
            )

            if leads.count() > 0:

                meta_contacts = "".join(message_contacts)
                meta_body = thread["snippet"]
                n = Notification.objects.create(
                    notify_at=timezone.now(),
                    title=message["subject"],
                    notification_type="EMAIL",
                    resource_id=object_id,
                    user=user,
                    meta={
                        "content": meta_body,
                        "linked_contacts": meta_contacts,
                        "leads": [{"id": str(l.id), "title": l.title} for l in leads],
                    },
                )

                # PLACEHOLDER = IN FUTURE EMAILS SENT/RECIEVED WILL ALL LOG ON THE WEBHOOK
                # if user.email in message_to:
                for lead in leads:
                    obj = LeadEmail.objects.create(
                        created_by=user, lead=lead, thread_id=object_id
                    )
                    linked_contacts = lead.linked_contacts.filter(
                        email__in=message_contacts
                    )
                    obj.linked_contacts.set(linked_contacts)

                    # Emit an EMAIL_SENT event and pass in Lead/Thread record.
                    log_event(lead_constants.EMAIL_RECEIVED, user, obj)

    except Exception as e:
        logger.exception(f"Failed {e}")


@background(schedule=0)
def _get_email_metadata_info(account_id, object_id, date, **kwargs):

    user = None
    try:
        user = User.objects.get(email_auth_account__account_id=account_id)
    except User.DoesNotExist as e:
        logger.exception(
            f"The user account_id is not in saved on the system they might need to re-auth a token,{account_id}"
        )
        return
    try:
        # get account details if they dont exist to send a system email and revoke the old token
        if user:
            message = retrieve_message(user, object_id)
            # for consistency add thread_id to resource id
            thread_id = message["thread_id"]
            already_notified = False

            # find the email object created in the db
            le = LeadEmail.objects.filter(thread_id=thread_id).first()
            le.opened_count = kwargs["count"]
            le.save()
            # find its corresponding log and regenerate it (update)
            la = LeadActivityLog.objects.filter(meta__id=str(le.id))
            la.update(meta=le.activity_log_meta)
            le.save()

            already_notified = _check_notification(thread_id)
            if already_notified:
                return

            message_contacts = message["to"]
            message_contacts = [c["email"] for c in message_contacts if c["email"]]

            # retrieve user leads and contacts
            # create a new leademailaction
            # create a new notification
            # _get_email_metadata_info('2yyyiu5lq221zmm4dvhmng5gc','5ahzrbuw7jdl0rysvs1s5oiz4','1595304936', **{'count':5})
            # a=LeadEmail.objects.filter(thread_id="asxshviynv3vlwegqg5om2zaq")
            leads = user.claimed_leads.filter(
                linked_contacts__email__in=message_contacts
            )

            if leads.count() > 0:
                meta_contacts = "".join(message_contacts)
                meta_body = message["snippet"]
                n = Notification.objects.create(
                    notify_at=timezone.now(),
                    title=message["subject"],
                    notification_type="EMAIL_OPENED",
                    resource_id=thread_id,
                    user=user,
                    meta={
                        "content": meta_body,
                        "linked_contacts": meta_contacts,
                        "leads": [{"id": str(l.id), "title": l.title} for l in leads],
                    },
                )

    except Exception as e:
        logger.exception(f"Error {e}")
