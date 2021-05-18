from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import (
    checkbox_block,
    text_block,
    section_with_button_block,
)


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


class TestSectionWithButtonBlock(TestCase):
    """Unit tests for setion_with_button_block"""

    def test_returns_basic_object(self):
        result = section_with_button_block("Test", "TEST", "Test", block_id="1", action_id="1")
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Test"},
                "block_id": "1",
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Test"},
                    "value": "TEST",
                    "action_id": "1",
                },
            },
        )


class TestCheckBoxBlock(TestCase):
    """unit test for checkbox block"""

    def test_returned_block(self):
        result = checkbox_block(
            label="test",
            options=["test", "test"],
            action_id="action_test",
            initial_options=None,
            block_id="block_test",
        )
        self.assertEqual(
            result,
            {
                {
                    "type": "section",
                    "block_id": "block_test",
                    "text": {"type": "mrkdwn", "text": "test"},
                    "accessory": {
                        "type": "checkboxes",
                        "action_id": "action_test",
                        "options": ["test", "test"],
                    },
                }
            },
        )

    def test_initial_options(self):
        result = checkbox_block(
            label="test",
            block_id="block_test",
            initial_options={
                "type": "checkboxes",
                "action_id": "action_test",
                "options": ["test", "test"],
            },
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "block_id": "block_test",
                "text": {"type": "mrkdwn", "text": "test"},
                "accessory": {
                    "type": "checkboxes",
                    "action_id": "action_test",
                    "options": ["test", "test"],
                },
            },
        )
