from rest_framework.exceptions import ValidationError

from django.test import TestCase

from .serializers import EmailSerializer


class EmailSerializerTestCase(TestCase):
    def setUp(self):
        # This is the minimum valid data
        self.valid_data = {
            "subject": "Hello World",
            "body": "Hello World - Body of Email",
            "to": [{"name": "Foo Bar", "email": "foo@test.com",}],
        }

    def test_validation(self):
        """Valid data should pass validation."""
        serializer = EmailSerializer(data=self.valid_data)
        self.assertEqual(serializer.is_valid(raise_exception=True), True)

    def test_validate_to_contact_dict(self):
        self.valid_data["to"] = ["foo@test.com"]
        serializer = EmailSerializer(data=self.valid_data)
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(
            str(error.exception),
            "{'to': {0: [ErrorDetail(string='Expected a dictionary of items but got type \"str\".', code='not_a_dict')]}}",
        )

