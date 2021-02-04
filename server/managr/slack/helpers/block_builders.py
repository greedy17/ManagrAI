import uuid


def text_block(value, text_type="plain_text"):
    return {"type": text_type, "text": value}


def input_block(
    label,
    initial_value=False,
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
    """ sections can have multiple fields they are a collection of simple_selections """
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
    label, options, action_id=None, initial_option=None, placeholder="Select",
):
    block = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"{label}"},
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


def datepicker(
    date=None, action_id=None, block_id=None, label="Select Date", placeholder="Select a date",
):
    block = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"{label}"},
        "accessory": {
            "type": "datepicker",
            "placeholder": {"type": "plain_text", "text": f"{placeholder}"},
        },
    }
    if date:
        block["accessory"]["initial_date"] = date
    if action_id:
        block["accessory"]["action_id"] = action_id
    if block_id:
        block["block_id"] = block_id
    return block
