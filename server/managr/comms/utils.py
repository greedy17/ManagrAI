import logging
import math
from . import constants as comms_consts
from managr.utils.client import Client, Variable_Client
from .exceptions import _handle_response as _handle_news_response
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests

logger = logging.getLogger("managr")


def get_news_for_company(search):
    news_url = comms_consts.NEW_API_URI + "/" + comms_consts.NEW_API_EVERYTHING_URI(search)
    with Variable_Client() as client:
        new_res = client.get(news_url, headers=comms_consts.NEWS_API_HEADERS)
        return _handle_news_response(new_res)
