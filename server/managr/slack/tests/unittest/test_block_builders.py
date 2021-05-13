from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import text_block, simple_section_multiple


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


class TestSimpleSectionMultiple(TestCase):
    """Unit tests for simple_section_multiple"""

    def test_returns_basic_object_correctly(self):
        result = simple_section_multiple([text_block("Test"), text_block("Test2")], block_id="1")
        self.assertEqual(
            result,
            {
                "type": "section",
                "fields": [
                    {"type": "plain_text", "text": "Test"},
                    {"type": "plain_text", "text": "Test2"},
                ],
                "block_id": "1",
            },
        )

    def test_returns_error_with_no_params(self):
        self.assertRaises(TypeError, text_block)

    def test_returns_random_block_id(self):
        result = simple_section_multiple([text_block("Test"), text_block("Test2")])
        self.assertIsInstance(result["block_id"], str)

    def test_returns_one_mrkdwn_type(self):
        result = simple_section_multiple([text_block("Test", "mrkdwn"), text_block("Test2")])
        self.assertEqual(result["fields"][0]["type"], "mrkdwn")
