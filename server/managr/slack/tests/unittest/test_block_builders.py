from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import text_block, option, multi_static_select


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


class TestMultiStaticSelect(TestCase):
    """Unit tests for multi static select"""

    def test_returns_basic_object(self):
        result = multi_static_select(
            "Test", [option("Test", "TEST"), option("Test2", "TEST2")], block_id="1"
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Test"},
                "block_id": "1",
                "accessory": {
                    "type": "multi_static_select",
                    "placeholder": {"type": "plain_text", "text": "Select"},
                    "options": [
                        {"text": {"type": "plain_text", "text": "Test"}, "value": "TEST"},
                        {"text": {"type": "plain_text", "text": "Test2"}, "value": "TEST2"},
                    ],
                },
            },
        )

    def test_returns_error_with_missing_params(self):
        self.assertRaises(TypeError, multi_static_select)

    def test_returns_random_block_id(self):
        result = multi_static_select("Test", [option("Test", "TEST"), option("Test2", "TEST2")])
        self.assertIsInstance(result["block_id"], str)

    def test_returns_object_with_initial_options(self):
        result = multi_static_select(
            "Test",
            [option("Test", "TEST"), option("Test2", "TEST2")],
            initial_options=[option("Test", "TEST"), option("Test2", "TEST2")],
        )
        self.assertEqual(len(result["accessory"]["initial_options"]), 2)
        self.assertEqual(
            result["accessory"]["initial_options"][0],
            {"text": {"type": "plain_text", "text": "Test"}, "value": "TEST"},
        )
        self.assertEqual(
            result["accessory"]["initial_options"][1],
            {"text": {"type": "plain_text", "text": "Test2"}, "value": "TEST2"},
        )

    def returns_different_placeholder(self):
        result = multi_static_select(
            "Test", [option("Test", "TEST"), option("Test2", "TEST2")], placeholder="Test"
        )
        self.assertEqual(result["accessory"]["placeholder"], "Test")
