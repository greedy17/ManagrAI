from django.test import TestCase
from django.utils import timezone

from managr.core.models import User
from managr.organization.models import Organization
from managr.organization.factories import AccountFactory, ContactFactory

from ..factories import LeadFactory, CallNoteFactory
from ..background.consumers import BaseActionConsumer, CallNoteActionConsumer
from ..background.exceptions import ConsumerConfigError
from managr.lead.background import emit_event as emit_log_event
from managr.lead.background import _log_lead_action
from ..models import Lead, CallNote, LeadActivityLog, LeadEmail
from ..insights import LeadInsights
from .. import constants as lead_constants
from managr.core.nylas.emails import send_new_email, send_new_email_legacy


class SendEmailTestCase(TestCase):
    # The fixture provides a test user and org
    fixtures = ["dev.json"]

    def setUp(self):
        self.org = Organization.objects.first()
        self.user = self.org.users.get(email="testing@thinknimble.com")
        self.account = AccountFactory(organization=self.org)
        # Random lead for basic insight testing
        self.lead = LeadFactory(
            amount=25000, claimed_by=self.user, account=self.account
        )
        contact = ContactFactory()
        self.lead.linked_contacts.set([contact])

    # NOTE (Bruno 10-21-2020):  commenting these out as Nylas keeps giving us 401 Unauth
    #                           As per Pari's comment, may be an expired test-token.

    # def test_send_email(self):
    #     email = dict(
    #         auth=self.user.email_auth_account.access_token,
    #         receipient=self.lead.linked_contacts.first(),
    #         subject="Django Test Sent Email",
    #         body="This Email was sent with a Django Test",
    #         sender=self.user,
    #     )
    #     response = send_new_email_legacy(
    #         auth=email["auth"],
    #         sender={"name": email["sender"].first_name, "email": email["sender"].email},
    #         receipient=[
    #             {"name": email["receipient"].title, "email": email["receipient"].email}
    #         ],
    #         message={"subject": email["subject"], "body": email["body"]},
    #     )
    #     LeadEmail.objects.create(
    #         created_by=self.user, lead=self.lead, thread_id=response["thread_id"]
    #     )
    #     self.assertEqual(LeadEmail.objects.all().count(), 1)

    # def test_send_email_and_emit_event(self):
    #     email = dict(
    #         auth=self.user.email_auth_account.access_token,
    #         receipient=self.lead.linked_contacts.first(),
    #         subject="Django Test Sent Email",
    #         body="This Email was sent with a Django Test",
    #         sender=self.user,
    #     )
    #     response = send_new_email_legacy(
    #         auth=email["auth"],
    #         sender={"name": email["sender"].first_name, "email": email["sender"].email},
    #         receipient=[
    #             {"name": email["receipient"].title, "email": email["receipient"].email}
    #         ],
    #         message={"subject": email["subject"], "body": email["body"]},
    #     )
    #     lead_email = LeadEmail.objects.create(
    #         created_by=self.user, lead=self.lead, thread_id=response["thread_id"]
    #     )

    #     # run background task now
    #     register_log = _log_lead_action.now
    #     register_log("LeadEmail.SENT", self.user.id, lead_email.id)
    #     # if task was successful there should be an item in the log
    #     self.assertEqual(LeadActivityLog.objects.all().count(), 1)
