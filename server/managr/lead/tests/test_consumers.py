from django.test import TestCase
from django.utils import timezone

from managr.organization.models import Organization
from managr.organization.factories import AccountFactory, ContactFactory

from ..factories import LeadFactory, CallNoteFactory
from ..background.consumers import BaseActionConsumer, CallNoteActionConsumer
from ..background.exceptions import ConsumerConfigError
from ..models import CallNote, LeadActivityLog
from .. import constants as lead_constants


class MissingModelClassActionConsumer(BaseActionConsumer):
    """This misconfigured consumer does not define a model_class."""

    pass


class MissingGetLeadActionConsumer(BaseActionConsumer):
    """This misconfigured consumer defines a model_class but not a get_lead method."""

    model_class = CallNote


class MisconfiguredConsumerTestCase(TestCase):
    def test_missing_model_class(self):
        with self.assertRaises(ConsumerConfigError):
            consumer = MissingModelClassActionConsumer(None, None, None)
            consumer.create_log()

    def test_missing_model_class(self):
        with self.assertRaises(NotImplementedError):
            consumer = MissingGetLeadActionConsumer(None, None, None)
            consumer.create_log()


class CallNoteActionConsumerTestCase(TestCase):
    # The fixture provides a test user and org
    fixtures = ["dev.json"]

    def setUp(self):
        self.org = Organization.objects.first()
        self.user = self.org.users.first()

        # Create some lead-related data
        self.account = AccountFactory()
        self.contact_1 = ContactFactory(account=self.account)
        self.contact_2 = ContactFactory(account=self.account)
        self.contact_3 = ContactFactory(account=self.account)
        self.lead = LeadFactory(account=self.account)

        # Create a call note
        self.call_note = CallNoteFactory(
            created_by=self.user,
            updated_by=self.user,
            created_for=self.lead,
            call_date="2020-05-01T14:00",
        )
        self.call_note.linked_contacts.set([self.contact_1, self.contact_2])

        # Refresh from DB to ensure that that call_date field will
        # be a proper datetime obj
        self.call_note.refresh_from_db()

        # Create a consumer to test
        self.consumer = CallNoteActionConsumer(
            lead_constants.CREATED, self.user.id, self.call_note.id
        )

    def test_call_note_consumer_model_class_name(self):
        self.assertEqual(self.consumer.model_class_name, "CallNote")

    def test_call_note_consumer_created_creates_log(self):
        self.consumer.create_log()

        # There should now be one activity log entry
        self.assertEqual(
            LeadActivityLog.objects.all().count(), 1,
        )

    def test_call_note_consumer_created_activity_name(self):
        log = self.consumer.create_log()

        # The activity log should have the correct activity name
        self.assertEqual(log.activity, "CallNote.CREATED")

    def test_call_note_consumer_updated_creates_log(self):
        self.consumer.action = lead_constants.UPDATED
        self.consumer.create_log()

        # There should now be one activity log entry
        self.assertEqual(
            LeadActivityLog.objects.all().count(), 1,
        )

    def test_call_note_consumer_updated_activity_name(self):
        self.consumer.action = lead_constants.UPDATED
        log = self.consumer.create_log()

        # The activity log should have the correct activity name
        self.assertEqual(log.activity, "CallNote.UPDATED")

    def test_call_note_consumer_activity_meta(self):
        log = self.consumer.create_log()

        # The activity log should have the correct activity name
        self.assertEqual(log.meta, self.call_note.activity_log_meta)

    def test_call_note_consumer_created_timestamp(self):
        log = self.consumer.create_log()

        #
        self.assertEqual(log.action_timestamp, self.call_note.call_date)

    def test_call_note_consumer_updated_timestamp(self):
        self.consumer.action = lead_constants.UPDATED
        log = self.consumer.create_log()

        # When logging an UPDATE action, the log's timestamp should be
        # "now" (the time of the update), so NOT the time of the call,
        # which is in the past.
        self.assertNotEqual(log.action_timestamp, self.call_note.call_date)
