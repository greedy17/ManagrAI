from rest_framework.exceptions import ValidationError

from django.test import TestCase

from managr.lead.factories import LeadFactory
from managr.organization.models import Organization
from managr.organization.factories import AccountFactory, ContactFactory

from .serializers import EmailSerializer


class MockRequest:
    def __init__(self, user):
        self.user = user


class EmailSerializerTestCase(TestCase):
    # The fixture provides a test user and org
    fixtures = ["dev.json"]

    def setUp(self):
        self.org = Organization.objects.first()
        self.user = self.org.users.first()

        # Create some lead-related data
        self.account = AccountFactory(organization=self.org)
        self.contact_1 = ContactFactory(account=self.account)
        self.contact_2 = ContactFactory(account=self.account)
        self.contact_3 = ContactFactory(account=self.account)
        self.lead = LeadFactory(account=self.account)

        # This is the minimum valid data
        self.valid_data = {
            "subject": "Hello World",
            "body": "Hello World - Body of Email",
            "to": [{"name": "Foo Bar", "email": "foo@test.com",}],
            "lead": str(self.lead.id),
        }

        # We also need a mock Request object
        self.request = MockRequest(self.user)

    def test_validation(self):
        """Valid data should pass validation."""
        serializer = EmailSerializer(
            data=self.valid_data, context={"request": self.request}
        )
        self.assertEqual(serializer.is_valid(raise_exception=True), True)

    def test_validate_to_contact_dict(self):
        self.valid_data["to"] = ["foo@test.com"]
        serializer = EmailSerializer(
            data=self.valid_data, context={"request": self.request}
        )
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(
            str(error.exception),
            "{'to': {0: [ErrorDetail(string='Expected a dictionary of items but got type \"str\".', code='not_a_dict')]}}",
        )
