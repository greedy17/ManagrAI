from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import external_select, text_block


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


class TestExternalSelect(TestCase):
    """unit test for external select"""

    def test_returned_block(self):
        result = external_select(
            "test_label",
            "test_action_id",
            initial_option=None,
            block_id=None,
            min_query_length=0,
            placeholder="Select_test",
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "test_label"},
                "accessory": {
                    "type": "external_select",
                    "action_id": "test_action_id",
                    "placeholder": {"type": "plain_text", "text": "Select_test"},
                    "min_query_length": 0,
                },
            },
        )

    def test_initial_option(self):
        result = external_select(
            label="test_label",
            action_id="test_actiion_id",
            initial_option={
                "type": "external_select",
                "action_id": "test_action_id",
                "placeholder": {"type": "plain_text", "text": "Select_test"},
                "min_query_length": 0,
            },
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "test_label"},
                "accessory": {
                    "type": "external_select",
                    "action_id": "test_action_id",
                    "placeholder": {"type": "plain_text", "text": "Select_test"},
                    "min_query_length": 0,
                },
            },
        )
