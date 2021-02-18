import os
import time
import hmac
import hashlib
import binascii

import pdb

from django.conf import settings

from managr.slack.models import UserSlackIntegration
from managr.slack.helpers import block_builders


def create_sha256_signature(key, message):
    # byte_key = binascii.unhexlify(key)
    byte_key = key.encode()
    message = message.encode()
    # message = binascii.unhexlify(message)
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest()


def NO_OP(*args):
    """
    No operation.
    """
    pass


def action_with_params(action, params=[]):
    """
    Max length of return is 255 characters.
    Slack will return a 200 but not display UI
    if action_id is greater than this limit.
    """
    if not isinstance(action, str):
        raise TypeError("action must be str")
    if not isinstance(params, list):
        raise TypeError("params must be list")
    output = action + "?" + "&".join(params)
    if len(output) > 255:
        raise ValueError("action_id would be longer than 255 characters")
    return output


def process_action_id(action_string):
    output = {}
    x = action_string.split("?")
    output["true_id"] = x[0]
    output["params"] = {}
    if len(x) > 1:
        ps_list = x[1].split("&")
        for param_str in ps_list:
            b = param_str.split("=")
            output["params"][b[0]] = b[1]
    return output


def get_lead_rating_emoji(rating):
    placeholder_count = 5 - rating
    output = ""
    for i in range(rating):
        output += ":star: "
    for i in range(placeholder_count):
        output += ":black_small_square: "
    return output


def block_finder(block_id, blocks=[]):
    """ Takes in a list of blocks and return block and index (used for updating and removing from modal) """
    item = list(filter(lambda x: x[1]["block_id"] == block_id, enumerate(blocks),))
    if len(item):
        return item[0]
    return item


def map_fields_to_type(fields):
    data = list()
    for field in fields:
        if field["type"] == "Picklist":
            data.append(
                block_builders.static_select(
                    f'*{field["label"]}*',
                    list(
                        map(
                            lambda opt: block_builders.option(opt["label"], opt["value"]),
                            field["options"],
                        )
                    ),
                    initial_option=dict(
                        *map(
                            lambda value: block_builders.option(value["label"], value["value"]),
                            filter(
                                lambda opt: opt.get("value", None) == field.get("value", None),
                                field.get("options", []),
                            ),
                        ),
                    ),
                    block_id=field.get("key", None),
                )
            )
        elif field["type"] == "Date":
            data.append(
                block_builders.datepicker(
                    label=f"*{field['label']}*",
                    initial_date=field.get("value", None),
                    block_id=field.get("key", None),
                )
            )
        elif field["type"] == "Boolean":
            data.append(
                block_builders.checkbox_block(
                    " ",
                    [block_builders.option(field["label"], "true")],
                    action_id=field["key"],
                    block_id=field["key"],
                )
            )
        else:
            if field["type"] == "String" and field["length"] >= 250:
                # set these fields to be multiline
                data.append(
                    block_builders.input_block(
                        field["label"],
                        multiline=True,
                        initial_value=field.get("value", None),
                        block_id=field.get("key", None),
                    )
                )
            else:
                data.append(
                    block_builders.input_block(
                        field["label"],
                        # optional=not field["required"],
                        initial_value=str(field.get("value")) if field.get("value", None) else None,
                        block_id=field.get("key", None),
                    ),
                )
    return data


class block_set:
    """A decorator that validates that required context keys are present.

    Use this decorator to wrap a function that renders a block set for Slack.
    This will check that the context provided to the renderer contains all the
    required context variables.

    Args:
        required_context (list): List of keys to look up in context.
    """

    def __init__(self, required_context=[]):
        self.required_context = required_context

    def __call__(self, f):
        def wrapped_f(context):
            for prop in self.required_context:
                if context.get(prop) is None:
                    raise ValueError(f"context missing: {prop}, in {f.__name__}")
            return f(context)

        return wrapped_f


class processor:
    """
    Decorator. Checks for required context for a processor.
    """

    def __init__(self, required_context=[], *args, **kwargs):
        self.required_context = required_context

    def __call__(self, f):
        def wrapped_f(payload, context, *args, **kwargs):
            for prop in self.required_context:
                if context.get(prop) is None:
                    raise ValueError(f"context missing: {prop}, in {f.__name__}")
            return f(payload, context, *args, **kwargs)

        return wrapped_f
