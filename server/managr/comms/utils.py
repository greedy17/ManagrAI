import logging
from . import constants as comms_consts
from managr.utils.client import Client, Variable_Client
from .exceptions import _handle_response as _handle_news_response

logger = logging.getLogger("managr")


def get_news_for_company(company):
    news_url = comms_consts.NEW_API_URI + "/" + comms_consts.NEW_API_EVERYTHING_URI(company)
    with Variable_Client() as client:
        new_res = client.get(news_url, headers=comms_consts.NEWS_API_HEADERS)
        return _handle_news_response(new_res)

