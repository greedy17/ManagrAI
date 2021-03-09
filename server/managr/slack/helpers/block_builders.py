import uuid


def text_block(value, text_type="plain_text"):
    return {"type": text_type, "text": value}


def input_block(
    label,
    initial_value=None,
    placeholder=False,
    multiline=False,
    placeholder_type="plain_text",
    action_id="plain_input",
    block_id=None,
    label_type="plain_text",
    min_length=False,
    max_length=False,
    optional=True,
):
    """ 
    If a placeholder, min_length, max_length is 
    passed in it will be used otherwise False 
    will not add a placeholder 
    """

    if not block_id:
        block_id = str(uuid.uuid4())
    obj = {
        "type": "input",
        "block_id": block_id,
        "label": {"type": label_type, "text": label},
        "optional": optional,
        "element": {"type": "plain_text_input", "action_id": action_id, "multiline": multiline,},
    }
    if placeholder:
        # placeholder is a text_block
        obj["element"]["placeholder"] = text_block(placeholder, placeholder_type)

    if max_length:
        obj["element"]["max_length"] = max_length

    if min_length:
        obj["element"]["min_length"] = min_length

    if initial_value:
        obj["element"]["initial_value"] = initial_value

    return obj


def simple_section(value, text_type="plain_text", block_id=None):
    if not block_id:
        block_id = str(uuid.uuid4())
    return {
        "type": "section",
        "text": {"type": text_type, "text": value},
        "block_id": block_id,
    }


def simple_section_multiple(text_blocks, block_id=None):
    """ sections can have multiple fields they are a collection of text_block """
    if not block_id:
        block_id = str(uuid.uuid4())
    return {"type": "section", "fields": text_blocks, "block_id": block_id}


def option(text, value):
    return {
        "text": {"type": "plain_text", "text": text},
        "value": value,
    }


def external_select(
    label, action_id, initial_option=None, block_id=None, min_query_length=0, placeholder="Select",
):
    block = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"{label}"},
        "accessory": {
            "type": "external_select",
            "action_id": action_id,
            "placeholder": {"type": "plain_text", "text": placeholder},
            "min_query_length": min_query_length,
        },
    }
    if initial_option:
        block["accessory"]["initial_option"] = initial_option
    if block_id:
        block["block_id"] = block_id
    return block


def static_select(
    label, options, action_id=None, initial_option=None, placeholder="Select", block_id=None,
):
    # options are an array of block_optiosn (see above)
    if not block_id:
        block_id = str(uuid.uuid4())
    block = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"{label}"},
        "block_id": block_id,
        "accessory": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": placeholder},
            "options": options,
        },
    }
    if initial_option:
        block["accessory"]["initial_option"] = initial_option
    if action_id:
        block["accessory"]["action_id"] = action_id
    return block


def multi_static_select(
    label, options, action_id=None, initial_options=None, placeholder="Select", block_id=None,
):
    # options are an array of block_optiosn (see above)
    if not block_id:
        block_id = str(uuid.uuid4())
    block = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"{label}"},
        "block_id": block_id,
        "accessory": {
            "type": "multi_static_select",
            "placeholder": {"type": "plain_text", "text": placeholder},
            "options": options,
        },
    }
    if initial_options:
        block["accessory"]["initial_option"] = initial_options
    if action_id:
        block["accessory"]["action_id"] = action_id
    return block


def datepicker(
    initial_date=None,
    action_id=None,
    block_id=None,
    label="Select Date",
    placeholder="Select a date",
):
    if not block_id:
        block_id = str(uuid.uuid4())
    block = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"{label}"},
        "block_id": block_id,
        "accessory": {
            "type": "datepicker",
            "placeholder": {"type": "plain_text", "text": f"{placeholder}"},
        },
    }
    if initial_date:
        block["accessory"]["initial_date"] = initial_date
    if action_id:
        block["accessory"]["action_id"] = action_id
    return block


def section_with_button_block(
    button_label,
    button_value,
    section_text,
    text_type="mrkdwn",
    block_id=None,
    url=None,
    style=None,
    confirm=False,
    action_id=None,
):
    if not block_id:
        block_id = str(uuid.uuid4())
    block = {
        "type": "section",
        "text": {"type": text_type, "text": section_text},
        "block_id": block_id,
        "accessory": {
            "type": "button",
            "text": {"type": "plain_text", "text": button_label},
            "value": button_value,
            # "confirm": confirm,
            "action_id": action_id if action_id else str(uuid.uuid4()),
        },
    }
    if style:
        block["accessory"]["style"] = style
    if url:
        block["accessory"]["url"] = url
    return block


def simple_button_block(label, value, url=None, style=None, confirm=False, action_id=None):
    # action ID must be unique
    block = {
        "type": "button",
        "text": {"type": "plain_text", "text": label},
        "value": value,
        # "confirm": confirm,
        "action_id": action_id if action_id else str(uuid.uuid4()),
    }
    if style:
        block["style"] = style
    if url:
        block["url"] = url
    return block


def actions_block(blocks=[], block_id=None):
    """ 
    Array of interactive element objects - buttons, select menus, overflow menus, or date pickers. 
    max of 5
    """
    if not len(blocks):
        return
    if len(blocks) > 4:
        return
    if not block_id:
        block_id = str(uuid.uuid4())
    return {"type": "actions", "block_id": block_id, "elements": [*blocks]}


def checkbox_block(label, options, action_id=None, initial_options=None, block_id=None):
    if not action_id:
        action_id = str(uuid.uuid4())
    if not block_id:
        block_id = str(uuid.uuid4())
    block = {
        "type": "section",
        "block_id": block_id,
        "text": {"type": "mrkdwn", "text": f"{label}"},
        "accessory": {"type": "checkboxes", "action_id": action_id, "options": options},
    }

    if initial_options:
        block["accessory"]["initial_options"] = initial_options

    return block


def section_with_accessory_block(
    section_text, accessory, text_type="mrkdwn", block_id=None,
):
    """ Builds a section with an accessory (image/button) """
    if not block_id:
        block_id = str(uuid.uuid4())
    block = {
        "type": "section",
        "text": {"type": text_type, "text": section_text},
        "block_id": block_id,
        "accessory": accessory,
    }

    return block


def simple_image_block(url, alt_text):
    return {
        "type": "image",
        "image_url": url,
        "alt_text": alt_text,
    }

