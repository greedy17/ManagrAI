from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import text_block, simple_section


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


class TestSimpleSection(TestCase):
    """Unit tests for simple section"""

    def test_returns_basic_object_correctly(self):
        result = simple_section("Test", block_id="1")
        self.assertEqual(
            result,
            {"type": "section", "text": {"type": "plain_text", "text": "Test"}, "block_id": "1"},
        )

    def test_returns_random_block_id(self):
        results = simple_section("Test")
        self.assertIsInstance(results["block_id"], str)

    def test_returns_error_with_no_params(self):
        self.assertRaises(TypeError, simple_section)

    def test_returns_with_text_type_mrkdwn(self):
        results = simple_section("Test", "mrkdwn")
        self.assertEqual(results["text"]["type"], "mrkdwn")
