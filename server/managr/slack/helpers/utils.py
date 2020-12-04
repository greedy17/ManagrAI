import os
import time
import hmac
import hashlib
import binascii

import pdb

from managr.slack.models import UserSlackIntegration


def create_sha256_signature(key, message):
    # byte_key = binascii.unhexlify(key)
    byte_key = key.encode()
    message = message.encode()
    # message = binascii.unhexlify(message)
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest()


# NOTE: this method does not work yet
def validate_slack_request(request):
    slack_app_secret = os.environ.get("SLACK_SECRET")
    timestamp = request.headers["X-Slack-Request-Timestamp"]
    slack_signature = request.headers["X-Slack-Signature"]

    if abs(time.time() - int(timestamp)) > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        return

    base_str = "v0:" + timestamp + ":" + request.body.decode("utf-8")
    managr_signature = "v0=" + create_sha256_signature(slack_app_secret, base_str)

    return managr_signature == slack_signature


def NO_OP(*args):
    """
    No operation.
    """
    pass


def action_with_params(action, params=[]):
    """
    Max length of return is 255 characters.
    Slack will return a 200 but not display UI
    whose action_id is greater than this limit.
    """
    if not isinstance(action, str):
        raise TypeError("action must be str")
    if not isinstance(params, list):
        raise TypeError("params must be list")
    return action + "?" + "&".join(params)


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


class block_set:
    """
    Decorator. Checks for required context for a block_set.
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

    def __init__(self, required_context=[]):
        self.required_context = required_context

    def __call__(self, f):
        def wrapped_f(payload, context):
            for prop in self.required_context:
                if context.get(prop) is None:
                    raise ValueError(f"context missing: {prop}, in {f.__name__}")
            return f(payload, context)

        return wrapped_f
