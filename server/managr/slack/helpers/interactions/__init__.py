from managr.slack.helpers.utils import NO_OP
from managr.slack import constants as slack_const

from .block_actions import handle_block_actions
from .block_suggestion import handle_block_suggestion
from .view_submission import handle_view_submission
from .view_closed import handle_view_closed

# NOTE:
# - The method handle_interaction is the entry point into this architecture.

# - HANDLERS (methods starting with handle_) leverage a switcher to route
#   payload towards proper processing method.
#   They may do some data preparation that gets passed on to the next method.
#   There may be some preparation of data to pass into a Processor.

# - PROCESSORS (methods starting with process_) do the actual processing of
#   the interaction.
# - The architecture is designed so that ultimately the return value of a
#   PROCESSOR is outputted to the view handling the request from the Slack API.


def handle_interaction(payload):
    """Route Slack interactions received via the Managr REST API."""
    switcher = {
        slack_const.BLOCK_ACTIONS: handle_block_actions,
        slack_const.BLOCK_SUGGESTION: handle_block_suggestion,
        slack_const.VIEW_SUBMISSION: handle_view_submission,
        slack_const.VIEW_CLOSED: handle_view_closed,
    }
    typ = payload["type"]
    print(f"TYPE: {typ}")
    return switcher.get(payload["type"], NO_OP)(payload)
