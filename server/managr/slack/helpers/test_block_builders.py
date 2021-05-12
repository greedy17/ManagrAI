from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import text_block


class TestTextBlock(TestCase):
    """Unit tests text_block"""

    def test_text_block_returns_object_correctly(self):
        result = text_block("test")
        self.assertEqual(result, {"type": "plain_text", "text": "test"})
