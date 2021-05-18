from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import (
    simple_image_block,
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


class TestSimpleImageBlock(TestCase):
    """Unit test for simple image block"""

    def test_returns_url_and_alt(self):
        result = simple_image_block("testurl123", "alt_test")
        self.assertEqual(
            result, {"type": "image", "image_url": "testurl123", "alt_text": "alt_test"}
        )
