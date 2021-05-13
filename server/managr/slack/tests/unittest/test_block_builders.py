from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import text_block
from server.managr.slack.helpers.block_builders import input_block


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


class TestInputBlock(TestCase):
    """ Unit test for input_block """

    def test_returns_object_with_userinput(self):
        result = input_block(
            label="test label",
            initial_value=None,
            placeholder=False,
            multiline=False,
            placeholder_type="plain_text",
            action_id="plain_input",
            block_id="testingBlockId123",
            label_type="plain_text",
            min_length=False,
            max_length=False,
            optional=True,
        )
        self.assertEqual(
            result,
            {
                "type": "input",
                "block_id": "testingBlockId123",
                "label": {"type": "plain_text", "text": "test label"},
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_input",
                    "multiline": False,
                },
            },
        )
