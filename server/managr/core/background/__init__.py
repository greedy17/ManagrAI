
import logging

from background_task import background
from managr.core.models import EmailAuthAccount, User
from managr.lead.models import Notification, LeadEmail
from ..nylas.emails import retrieve_message
from django.db.models import F, Q, Count
from django.utils import timezone


@background(schedule=0)
def _get_email_info(account_id, object_id, date):
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
            f"The user account_id is not in saved on the system they might need to re-auth a token,{account_id}"
        )
        pass

    # get the message form nylas and make it into a json object
    # from managr.core.background import _get_email_info
    # t = _get_email_info.now
    # t('2yyyiu5lq221zmm4dvhmng5gc','5s0f2hsvh4htrm4fskqn8xnty','')

    # if user.claimed_leads.count() > 0:
    message_contacts = []
    message = retrieve_message(user, object_id)
    # can use this to check if it is incoming or outgoing
    # message_contacts.extend(
    #    message['bcc']+message['cc']+message['to'] + message['from'])
    message_contacts = message_contacts.extend(message['from'])
    query = Q()
    message_contacts = [c['email'] for c in message_contacts if c['email']]
    for c in message_contacts:
        query |= c
    # retrieve user leads and contacts
    # create a new leademailaction
    # create a new notification
    leads = user.leads.filter(query).values_list(
        'id', 'email', flat=True
    )

    if leads.count() > 0:
        #    for lead in leads:
        #        email_log = LeadEmail.objects.create(
        #            created_by = user, lead = lead, thread_id = object_id)

        n = Notification.objects.create(notify_at=timezone.now(
        ), title=message['subject'], notification_type="EMAIL", resource_id=object_id, user=user, meta={'leads': [{'id': l.id, 'title': l.title} for l in leads]})

        print(n)
