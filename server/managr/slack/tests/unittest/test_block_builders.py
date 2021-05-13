from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import text_block, header_block


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


class TestHeaderBlock(TestCase):
    """Unit tests for header_block"""

    def test_returns_object_correctly(self):
        result = header_block("Test", "1")
        self.assertEqual(
            result,
            {"type": "header", "text": {"type": "plain_text", "text": "Test"}, "block_id": "1"},
        )

    def test_returns_error_with_no_params(self):
        self.assertRaises(TypeError, header_block)

    def test_returns_random_block_id(self):
        result = header_block("Test")
        self.assertIsInstance(result["block_id"], str)
