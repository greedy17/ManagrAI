from unittest.case import TestCase
from server.managr.slack.helpers.block_builders import text_block
from server.managr.slack.helpers.block_builders import divider_block


class TestDividerBlock(TestCase):
    """ unit test for divider block """

    def test_returns_divider_object(self):
        result = divider_block()
        self.assertEquals(result, {"type": "divider"})
