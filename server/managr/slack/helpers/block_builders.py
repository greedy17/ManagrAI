import uuid


def simple_section(value, section_type="plain_text", block_id=str(uuid.uuid4())):
    return {
        "type": "section",
        "text": {"type": section_type, "text": value},
        "block_id": block_id,
    }


def simple_section_multiple_options(value, sections):
    """ sections can have multiple fields they are a collection of simple_selections """
    return {"type": "section", "fields": sections}


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
