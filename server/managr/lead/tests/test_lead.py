import json

from rest_framework.exceptions import ValidationError

from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.db.models import F, Q, Count
from managr.lead.factories import LeadFactory
from managr.organization.models import Organization, Contact
from managr.organization.factories import AccountFactory, ContactFactory
from managr.core.models import User, MessageAuthAccount
from managr.lead.models import LeadMessage, Notification
from managr.lead.serializers import LeadMessageSerializer

from managr.core import views as core_views
from managr.lead import constants as lead_consts


class MockRequest:
    def __init__(self, user):
        self.user = user


class LeadMessageTestCase(TestCase):
    # The fixture provides a test user and org
    fixtures = ["dev.json"]

    def setUp(self):
        with open("mock-message.json", "r+") as message_json:
            data = message_json.read()
            message_data = json.loads(data)
        self.factory = RequestFactory()

        self.org = Organization.objects.first()
        self.user = self.org.users.first()

        # create an extra org
        self.org_1 = Organization.objects.create(name="test org", state="ACTIVE")
        self.user_1 = User.objects.create_user(
            organization=self.org_1, email="test2@thinknimble.com"
        )
        message_auth_account = MessageAuthAccount.objects.first()
        message_auth_account.pk = None
        message_auth_account.id = None
        message_auth_account.user = self.user_1
        message_auth_account.save()

        # create an extra user for org

        # create 2 accounts 1 in each org
        self.account = AccountFactory(organization=self.org)
        self.account_1 = AccountFactory(organization=self.org_1)
        # create 2 leads 1 in each account/org
        self.lead = LeadFactory(account=self.account, claimed_by=self.user)
        self.lead_1 = LeadFactory(account=self.account, claimed_by=self.user_1)

        # create 2 contacts and set them to each lead 1 to 1
        self.contact = ContactFactory(
            account=self.account, phone_number_1="+18888888888"
        )
        self.contact_1 = ContactFactory(
            account=self.account_1, phone_number_1="+18888888888"
        )
        self.lead.linked_contacts.add(self.contact)
        self.lead_1.linked_contacts.add(self.contact_1)

        # send mock lead message to lead message end point from user 1
        self.message = message_data

        # send mock lead message to lead message end point from user 2
        # get Lead Messages each one should only have one linked_contact

    def test_create_lead_message(self):
        # it should 'send' a message to the webhook for receiving messages from twilio
        # it should create a LeadMessage
        # the lead message should only have one contact
        # TODO replace with the view PB 08/13/2020
        # request = self.factory.post("/api/twilio/callback/messages", self.message)

        # request.user = self.user
        # response = core_views.TwilioMessageWebhook.as_view()(request)
        self.request = MockRequest(self.user)
        self.request.data = self.message

        sender = self.request.data.get("From", None)
        body = self.request.data.get("Body", None)
        message_id = self.request.data.get("MessageSid", None)

        contacts_object = Contact.objects.for_user(self.user).filter(
            Q(phone_number_1=sender) | Q(phone_number_2=sender)
        )
        leads = self.user.claimed_leads.filter(
            linked_contacts__in=contacts_object
        ).distinct()

        if leads.count() > 0:
            for lead in leads:
                lead_message = LeadMessage.objects.create(
                    created_by=self.user,
                    lead=lead,
                    message_id=message_id,
                    direction=lead_consts.RECEIVED,
                    body=body,
                    status=lead_consts.MESSAGE_DELIVERED,
                )

                lead_message.linked_contacts.set(contacts_object)
                lead_message.save()

                #
                # emit and event with LeadMessage.RECEIVED to create activity log
            # create the notification with resource id being the leadmessage
            # no need to emit an event for this as the notification has no async actions

        self.assertEqual(self.lead.messages.first().linked_contacts.all().count(), 1)
