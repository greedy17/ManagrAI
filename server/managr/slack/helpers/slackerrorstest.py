from managr.slack.helpers import requests
from managr.slack.helpers import block_builders
from managr.core.models import User

u = User.objects.get(email="pari@thinknimble.com")
org = u.organization


blocks = block_builders.simple_section("")


def send_failed_slack():
    return requests.send_channel_message(
        u.slack_integration.channel, org.slack_integration.access_token, block_set=blocks
    )
