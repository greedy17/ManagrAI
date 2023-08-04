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


def article_list_seperator(articles_list):
    new_list = []
    if len(" ".join(articles_list)) > 3000:
        half_index = math.floor(len(articles_list) / 2)
        first_half = articles_list[:half_index]
        second_half = articles_list[half_index:]
        if len(" ".join(first_half)) > 3000:
            new_list.extend(article_list_seperator(first_half))
        else:
            new_list.append(" ".join(first_half))
        if len(" ".join(second_half)) > 3000:
            new_list.extend(article_list_seperator(second_half))
        else:
            new_list.append(" ".join(second_half))
    else:
        return [" ".join(articles_list)]
    return new_list
