from unittest.case import TestCase


from managr.slack.helpers.block_builders import (
    actions_block,
    simple_button_block,
    text_block,
    section_with_button_block,
    section_with_accessory_block,
    simple_image_block,
    external_select,
    datepicker,
    simple_section_multiple,
    simple_section,
    input_block,
    text_block,
    option,
    divider_block,
    header_block,
    checkbox_block,
    static_select,
    multi_static_select,
    multi_external_select,
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


class TestDividerBlock(TestCase):
    """ unit test for divider block """

    def test_returns_divider_object(self):
        result = divider_block()
        self.assertEquals(result, {"type": "divider"})


class TestOption(TestCase):
    """Unit test for option"""

    def test_returns_object_correctly(self):
        result = option("test", "TEST")
        self.assertEqual(result, {"text": {"type": "plain_text", "text": "test"}, "value": "TEST"})

    def test_returns_error_with_no_params(self):
        self.assertRaises(TypeError, option)

    def test_returns_error_with_one_param(self):
        self.assertRaises(TypeError, option, "test")


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


class TestDatePicker(TestCase):
    """Unit tests for date_picker"""

    def test_returns_basic_object(self):
        result = datepicker(block_id="1")
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Select Date"},
                "block_id": "1",
                "accessory": {
                    "type": "datepicker",
                    "placeholder": {"type": "plain_text", "text": "Select a date"},
                },
            },
        )

    def test_returns_random_block_id(self):
        result = datepicker()
        self.assertIsInstance(result["block_id"], str)

    def test_returns_correct_initial_date(self):
        result = datepicker(initial_date="2021-04-01")
        self.assertEqual(result["accessory"]["initial_date"], "2021-04-01")

    def test_returns_different_label(self):
        result = datepicker(label="Test")
        self.assertEqual(result["text"]["text"], "Test")


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


class TestMultiExternalSelect(TestCase):
    """Unit test for multi external select"""

    def test_returned_block(self):
        result = multi_external_select(
            label="label_test",
            action_id="test123",
            initial_options=None,
            placeholder="Select",
            block_id="test_id",
            min_query_length=0,
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "label_test"},
                "block_id": "test_id",
                "accessory": {
                    "type": "multi_external_select",
                    "placeholder": {"type": "plain_text", "text": "Select"},
                    "action_id": "test123",
                    "min_query_length": 0,
                },
            },
        )

    def test_initial_options(self):
        result = multi_external_select(
            label="label_test",
            action_id="test123",
            initial_options=[{"text": {"type": "plain_text", "text": "test"}, "value": "test",}],
            placeholder="Select",
            block_id="test_id",
            min_query_length=0,
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "label_test"},
                "block_id": "test_id",
                "accessory": {
                    "type": "multi_external_select",
                    "placeholder": {"type": "plain_text", "text": "Select"},
                    "action_id": "test123",
                    "min_query_length": 0,
                    "initial_options": [
                        {"text": {"type": "plain_text", "text": "test"}, "value": "test",}
                    ],
                },
            },
        )


class TestCheckBoxBlock(TestCase):
    """unit test for checkbox block"""

    def test_returned_block(self):
        result = checkbox_block(
            "test",
            [{"text": {"type": "plain_text", "text": "test"}, "value": "test",}],
            action_id="action_test",
            initial_options=None,
            block_id="block_test",
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "block_id": "block_test",
                "text": {"type": "mrkdwn", "text": "test"},
                "accessory": {
                    "type": "checkboxes",
                    "action_id": "action_test",
                    "options": [{"text": {"type": "plain_text", "text": "test"}, "value": "test",}],
                },
            },
        )

    def test_initial_options(self):
        result = checkbox_block(
            "test",
            [{"text": {"type": "plain_text", "text": "test"}, "value": "test",}],
            initial_options=[{"text": {"type": "plain_text", "text": "test"}, "value": "test",}],
            block_id="block_test",
            action_id="block_test",
        )
        self.assertEqual(
            result,
            {
                "type": "section",
                "block_id": "block_test",
                "text": {"type": "mrkdwn", "text": "test"},
                "accessory": {
                    "type": "checkboxes",
                    "action_id": "block_test",
                    "options": [{"text": {"type": "plain_text", "text": "test"}, "value": "test",}],
                    "initial_options": [
                        {"text": {"type": "plain_text", "text": "test"}, "value": "test",}
                    ],
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
