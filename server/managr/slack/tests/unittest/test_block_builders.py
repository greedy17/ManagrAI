from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import text_block, static_select, option


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


class TestStaticSelect(TestCase):
    """Unit tests for static select"""

    def test_returns_basic_object(self):
        result = static_select(
            "Test", [option("Test", "TEST"), option("Test2", "TEST2")], block_id="1"
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Test"},
                "block_id": "1",
                "accessory": {
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Select"},
                    "options": [
                        {"text": {"type": "plain_text", "text": "Test"}, "value": "TEST"},
                        {"text": {"type": "plain_text", "text": "Test2"}, "value": "TEST2"},
                    ],
                },
            },
        )

    def test_returns_error_with_missing_params(self):
        self.assertRaises(TypeError, static_select)

    def test_returns_initial_option(self):
        result = static_select(
            "Test",
            [option("Test", "TEST"), option("Test2", "TEST2")],
            initial_option=option("Test", "TEST"),
            block_id="1",
        )
        print(result.keys())
        self.assertTrue("initial_option" in result["accessory"].keys())
        self.assertTrue(result["accessory"]["initial_option"]["value"] == "TEST")

    def test_returns_action_id(self):
        result = static_select(
            "Test", [option("Test", "TEST"), option("Test2", "TEST2")], action_id="1"
        )
        self.assertIs(result["accessory"]["action_id"], "1")
