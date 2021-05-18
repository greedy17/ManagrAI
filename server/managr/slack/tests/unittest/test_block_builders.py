from unittest.case import TestCase


from managr.slack.helpers.block_builders import (
    actions_block,
    simple_button_block,
    text_block,
    section_with_button_block,
    section_with_accessory_block,
    simple_image_block,
    external_select,
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


class TestExternalSelect(TestCase):
    """unit test for external select"""

    def test_returned_block(self):
        result = external_select(
            "test_label",
            "test_action_id",
            initial_option=None,
            block_id=None,
            min_query_length=0,
            placeholder="Select_test",
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "test_label"},
                "accessory": {
                    "type": "external_select",
                    "action_id": "test_action_id",
                    "placeholder": {"type": "plain_text", "text": "Select_test"},
                    "min_query_length": 0,
                },
            },
        )

    def test_initial_option(self):
        result = external_select(
            "test_label",
            "test_action_id",
            initial_option={"text": {"type": "plain_text", "text": "test"}, "value": "test",},
            block_id=None,
            min_query_length=0,
            placeholder="Select_test",
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "test_label"},
                "accessory": {
                    "type": "external_select",
                    "action_id": "test_action_id",
                    "placeholder": {"type": "plain_text", "text": "Select_test"},
                    "min_query_length": 0,
                    "initial_option": {
                        "text": {"type": "plain_text", "text": "test"},
                        "value": "test",
                    },
                },
            },
        )


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


class TestActionsBlock(TestCase):
    """Unit test for actions block"""

    def test_returned_block(self):
        result = actions_block(blocks=["test_button", "test_menu"], block_id="test")
        self.assertEqual(
            result,
            {"type": "actions", "block_id": "test", "elements": ["test_button", "test_menu"]},
        )

    def test_no_blocks_entered(self):
        result = actions_block(blocks=[], block_id=None)
        self.assertEqual(result, None)

    def test_too_many_blocks_entered(self):
        result = actions_block(
            blocks=["test", "test", "test", "test", "test", "test"], block_id=None
        )
        self.assertEqual(result, None)


class TestSimpleButtonBlock(TestCase):
    """unit tests for simple_button_block"""

    def test_returns_basic_object(self):
        result = simple_button_block("Test", "TEST", action_id="1")
        self.assertEqual(
            result,
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Test"},
                "value": "TEST",
                "action_id": "1",
            },
        )

    def test_returns_proper_url(self):
        result = simple_button_block("Test", "TEST", url="https://www.test.com")
        self.assertEqual(result["url"], "https://www.test.com")

    def test_returns_proper_style(self):
        result = simple_button_block("Test", "TEST", style="danger")
        self.assertEqual(result["style"], "danger")


class TestSectionWithAccessoryBlock(TestCase):
    """Unit tests for section_with_accessory_block"""

    def test_returns_basic_object(self):
        result = section_with_accessory_block("Test", accessory={}, block_id="1")
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Test"},
                "block_id": "1",
                "accessory": {},
            },
        )

    def test_returns_image_block(self):
        result = section_with_accessory_block(
            "Test", simple_image_block("https://www.test.com/image.png", "test image")
        )
        self.assertEqual(
            result["accessory"],
            {
                "type": "image",
                "image_url": "https://www.test.com/image.png",
                "alt_text": "test image",
            },
        )


class TestSimpleImageBlock(TestCase):
    """Unit test for simple image block"""

    def test_returns_url_and_alt(self):
        result = simple_image_block("testurl123", "alt_test")
        self.assertEqual(
            result, {"type": "image", "image_url": "testurl123", "alt_text": "alt_test"}
        )
