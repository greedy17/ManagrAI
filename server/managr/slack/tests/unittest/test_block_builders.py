from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import text_block, datepicker


class TestTextBlock(TestCase):
    """Unit tests text_block"""

    def test_returns_object_correctly(self):
        result = text_block("test")
        self.assertEqual(result, {"type": "plain_text", "text": "test"})

    def test_returns_error_with_no_parameters(self):
        self.assertRaises(TypeError, text_block)

    def test_returns_object_with_mrkdwn_type(self):
        result = text_block("test", "mrkdwn")
        self.assertEqual(result, {"type": "mrkdwn", "text": "test"})


class TestDatePicker(TestCase):
    """Unit tests for date_picker"""

    def test_returns_basic_object(self):
        result = datepicker(block_id="1")
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Select Date"},
                "block_id": "1",
                "accessory": {
                    "type": "datepicker",
                    "placeholder": {"type": "plain_text", "text": "Select a date"},
                },
            },
        )

    def test_returns_random_block_id(self):
        result = datepicker()
        self.assertIsInstance(result["block_id"], str)

    def test_returns_correct_initial_date(self):
        result = datepicker(initial_date="2021-04-01")
        self.assertEqual(result["accessory"]["initial_date"], "2021-04-01")

    def test_returns_different_label(self):
        result = datepicker(label="Test")
        self.assertEqual(result["text"]["text"], "Test")
