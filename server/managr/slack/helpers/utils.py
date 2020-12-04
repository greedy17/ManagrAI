from managr.slack.models import UserSlackIntegration


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
