from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import text_block
from server.managr.slack.helpers.block_builders import divider_block


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


class TestDividerBlock(TestCase):
    """ unit test for divider block """

    def test_returns_divider_object(self):
        result = divider_block()
        self.assertEquals(result, {"type": "divider"})
