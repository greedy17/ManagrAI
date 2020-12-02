from managr.slack.models import UserSlackIntegration


def generate_slack_option(text=None, value=None):
    """
    Returns a dict formatted to be an option for a
    Slack select_field
    """
    if text is None or value is None:
        raise TypeError("Required args: text=, value=")
    return {
        "text": {"type": "plain_text", "text": text},
        "value": value,
    }


def action_with_params(action, params=[]):
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


def get_access_token_from_user_slack_id(user_slack_id):
    return (
        UserSlackIntegration.objects.select_related(
            "user__organization__slack_integration"
        )
        .get(slack_id=user_slack_id)
        .user.organization.slack_integration.access_token
    )


def get_organization_from_user_slack_id(user_slack_id):
    return (
        UserSlackIntegration.objects.select_related("user__organization")
        .get(slack_id=user_slack_id)
        .user.organization
    )
