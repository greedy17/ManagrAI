from managr.slack.helpers.utils import NO_OP


def handle_view_closed(payload):

    switcher = {}
    view = payload["view"]
    callback_id = payload["view"]["callback_id"]
    return switcher.get(callback_id, NO_OP)(payload, view)
