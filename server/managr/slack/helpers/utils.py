import pytz
import hmac
import hashlib
import logging
import random
import datetime
from django.conf import settings
from dateutil import parser

from managr.alerts.models import AlertConfig
from managr.core.models import User
from managr.slack.helpers import block_builders, requests
from managr.slack import constants as slack_consts
from managr.salesforce.models import MeetingWorkflow

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
            context = call["context"]
            context_objects = [
                object["objects"] for object in context if object["system"] == "Salesforce"
            ]
            object_ids = [
                object["objectId"]
                for inner_list in context_objects
                for object in inner_list
                if object["objectId"] in resource_id
            ]
            if len(object_ids):
                call_data = call
                break
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
        return None
    return blocks


def check_contact_last_name(meeting_id):
    workflow = MeetingWorkflow.objects.get(id=meeting_id)
    meeting = workflow.meeting
    contacts = meeting.participants
    for contact in contacts:
        contactData = contact.get("secondary_data")
        if not contactData["LastName"]:
            return False
    return True


def get_random_update_message(topic):
    RANDOM_UPDATED_RESPONSES = [
        f"Great work! {topic} has been logged! :raised_hands:",
        f"Woohoo! {topic} successfully logged! :raised_hands:",
        f"Crushing it! {topic} logged. Keep it going! :raised_hands:",
        f"Great job! {topic} has been logged :raised_hands:",
    ]
    idx = random.randint(0, len(RANDOM_UPDATED_RESPONSES) - 1)
    return RANDOM_UPDATED_RESPONSES[idx]


def get_random_no_update_message(topic):
    RANDOM_NO_CHANGE_RESPONSES = [
        f"Gotcha, {topic} has no updates",
        f"10-4 {topic} needs no updating",
        f"Cool, no updated needed for {topic}",
        f"Ok dokie, {topic} needs no updates",
    ]
    idx = random.randint(0, len(RANDOM_NO_CHANGE_RESPONSES) - 1)
    return RANDOM_NO_CHANGE_RESPONSES[idx]


def check_for_time(tz, hour, minute):
    user_timezone = pytz.timezone(tz)
    currenttime = datetime.today().time()
    current = pytz.utc.localize(datetime.combine(datetime.today(), currenttime)).astimezone(
        user_timezone
    )
    min = 00 if minute >= 30 else 30
    hr = hour - 1 if minute < 30 else hour
    return current <= current.replace(hour=hour, minute=minute) and current >= current.replace(
        hour=hr, minute=min
    )


def check_for_uncompleted_meetings(user_id, org_level=False):
    user = User.objects.get(id=user_id)
    if hasattr(user, "slack_integration"):
        if org_level:
            users = User.objects.filter(
                slack_integration__recap_receivers__contains=[user.slack_integration.slack_id]
            )
            not_completed = []
            for user in users:
                total_meetings = MeetingWorkflow.objects.filter(user=user.id).filter(
                    datetime_created__contains=datetime.today().date()
                )
                user_not_completed = [
                    meeting for meeting in total_meetings if meeting.progress == 0
                ]
                if len(user_not_completed):
                    not_completed = [*not_completed, *user_not_completed]
        else:
            total_meetings = MeetingWorkflow.objects.filter(user=user.id).filter(
                datetime_created__contains=datetime.today().date()
            )
            not_completed = [meeting for meeting in total_meetings if meeting.progress == 0]
        if len(not_completed):
            return {"status": True, "not_completed": len(not_completed)}
    return {"status": False}


def check_workflows_count(user_id):
    workflows = AlertConfig.objects.filter(template__user=user_id)
    if len(workflows):
        return {"status": True, "workflow_count": len(workflows)}
    return {"status": False}


def send_loading_screen(access_token, message, view_type, user_id, trigger_id=None, view_id=None):
    loading_view_data = {
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": [
                block_builders.section_with_accessory_block(
                    f"*{message}*",
                    block_builders.simple_image_block(
                        "https://managr-images.s3.amazonaws.com/slack/logo_loading.gif",
                        "Loading...",
                    ),
                ),
                block_builders.context_block(
                    "* _After a few seconds click Close and try again_", "mrkdwn"
                ),
            ],
        },
    }
    if view_type == "open":
        view = slack_consts.VIEWS_OPEN
        loading_view_data["trigger_id"] = trigger_id
        if view_id is not None:
            loading_view_data["view_id"] = view_id
    elif view_type == "update":
        view = slack_consts.VIEWS_UPDATE
        loading_view_data["view_id"] = view_id
        if trigger_id is not None:
            loading_view_data["trigger_id"] = trigger_id
    else:
        view = slack_consts.VIEWS_PUSH
        loading_view_data["view_id"] = view_id
        if trigger_id is not None:
            loading_view_data["trigger_id"] = trigger_id
    try:
        loading_res = requests.generic_request(
            slack_consts.SLACK_API_ROOT + view, loading_view_data, access_token=access_token,
        )
        return loading_res
    except Exception as e:
        logger.exception(f"Failed To Show Loading Screen for user {user_id} {e}")
        return e

