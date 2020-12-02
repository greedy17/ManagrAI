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
