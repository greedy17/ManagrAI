import os
import time
import hmac
import hashlib
import binascii
import logging

import pdb

from django.conf import settings
from dateutil import parser

from managr.slack.models import UserSlackIntegration
from managr.slack.helpers import block_builders, requests
from managr.slack import constants as slack_consts

logger = logging.getLogger("managr")


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
    """Takes in a list of blocks and return block and index (used for updating and removing from modal)"""
    item = list(filter(lambda x: x[1].get("block_id", None) == block_id, enumerate(blocks),))
    if len(item):
        return item[0]
    return item


def map_fields_to_type(fields, **kwargs):
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

        elif field["type"] == "Reference":
            initial_option = (
                block_builders.option(field["value"], field["value"]) if field["value"] else None
            )
            relationship_name = field["relationshipName"]
            relationship_fields = list(
                *map(
                    lambda rel: rel["nameFields"],
                    filter(
                        lambda details: details["apiName"] == relationship_name,
                        field["relationshipDetails"],
                    ),
                )
            )
            data.append(
                block_builders.external_select(
                    f'*{field["label"]}*',
                    f"{slack_consts.GET_EXTERNAL_RELATIONSHIP_OPTIONS}?u={kwargs.get('user_id')}&relationship={relationship_name}&fields={','.join(relationship_fields)}",
                    block_id=field.get("key", None),
                    initial_option=initial_option,
                )
            )
        elif field["type"] == "MultiPicklist":
            data.append(
                block_builders.multi_static_select(
                    f'*{field["label"]}*',
                    list(
                        map(
                            lambda opt: block_builders.option(opt["label"], opt["value"]),
                            field["options"],
                        )
                    ),
                    initial_options=list(
                        dict(
                            *map(
                                lambda value: block_builders.option(value["label"], value["value"]),
                                filter(
                                    lambda opt: opt.get("value", None) == field.get("value", None),
                                    field.get("options", []),
                                ),
                            ),
                        )
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
                        optional=not field["required"],
                        initial_value=field.get("value", None),
                        block_id=field.get("key", None),
                    )
                )
            else:
                data.append(
                    block_builders.input_block(
                        field["label"],
                        optional=not field["required"],
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


def process_done_alert(block_id, blocks):
    found_block = block_finder(block_id, blocks)
    block_index = found_block[0]
    old_text = found_block[1].get("text").get("text").split("\n")
    if old_text[len(old_text) - 1] == "":
        old_text.pop()
    new_text = []
    for idx in old_text:
        new_text.append("~" + idx + "~")
    new_text = "\n".join(new_text)
    updated_blocks = blocks
    updated_blocks[int(block_index)] = block_builders.simple_section(new_text, text_type="mrkdwn")
    return updated_blocks


def generate_call_block(call_res, resource_id=None):
    blocks = []
    if resource_id:
        call_data = None
        for call in call_res["calls"]:
            resource_check = [
                d for d in call["context"][0].get("objects") if d["objectType"] == "Opportunity"
            ][0]
            if resource_check["objectId"] == resource_id:
                call_data = call
    else:
        call_data = call_res["calls"][0]
    if call_data:
        content_data = call_data.get("content", None)
        meta_data = call_data.get("metaData", None)
        trackers = content_data["trackers"]
        topics = content_data["topics"]
        trackers_string = "Trackers:\n"
        topics_string = "Topics:\n"
        modal_url = meta_data["url"]
        for tracker in trackers:
            if tracker["count"] > 0:
                trackers_string += f"{tracker['name']} mentioned {tracker['count']} times\n"
        for topic in topics:
            if topic["duration"] > 0:
                if topic["duration"] > 60:
                    dur = topic["duration"] // 60
                    topics_string += f"{topic['name']} talked about for {dur} minutes\n"
                else:
                    topics_string += (
                        f"{topic['name']} talked about for {topic['duration']} seconds\n"
                    )
        blocks.append(block_builders.simple_section(f"Title:{meta_data['title']}"))
        blocks.append(
            block_builders.simple_section(
                f"Date: {parser.parse(meta_data['scheduled']).strftime('%m/%d/%Y, %H:%M:%S')}"
            )
        )
        blocks.append(
            block_builders.simple_section(f"Duration: {round(meta_data['duration'] / 60)} min")
        )
        blocks.append(block_builders.simple_section(trackers_string))
        blocks.append(block_builders.simple_section(topics_string))
        blocks.append(
            block_builders.simple_section(
                f"Number of participants: {len(call_data.get('parties'))}"
            )
        )
        blocks.append(
            block_builders.section_with_button_block(
                "Recording",
                "get_recording_url",
                "Listen to call recording",
                url=modal_url,
                style="primary",
            )
        )
    else:
        blocks.append(block_builders.simple_section("Call still processing"))
    return blocks


