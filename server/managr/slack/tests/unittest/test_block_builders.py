from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import (
    multi_external_select,
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


class TestMultiExternalSelect(TestCase):
    """Unit test for multi external select"""

    def test_returned_block(self):
        result = multi_external_select(
            label="label_test",
            action_id="test123",
            initial_options=None,
            placeholder="Select",
            block_id="test_id",
            min_query_length=0,
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "label_test"},
                "block_id": "test_id",
                "accessory": {
                    "type": "multi_external_select",
                    "placeholder": {"type": "plain_text", "text": "Select"},
                    "action_id": "test123",
                    "min_query_length": 0,
                },
            },
        )

    def test_initial_options(self):
        result = multi_external_select(
            label="test label",
            block_id="test block",
            initial_options={
                "type": "multi_external_select",
                "placeholder": {"type": "plain_text", "text": "initial options test"},
                "action_id": "initial id test",
                "min_query_length": 0,
            },
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "test label"},
                "block_id": "test block",
                "accessory": {
                    "type": "multi_external_select",
                    "placeholder": {"type": "plain_text", "text": "initial options test"},
                    "action_id": "initial id test",
                    "min_query_length": 0,
                },
            },
        )
