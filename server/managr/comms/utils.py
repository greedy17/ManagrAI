import json
import logging
import datetime
from . import constants as comms_consts
from managr.utils.client import Client, Variable_Client
from .exceptions import _handle_response as _handle_news_response
from managr.core.exceptions import _handle_response as _handle_open_ai_response
from managr.core import constants as core_consts
from managr.core.models import User

logger = logging.getLogger("managr")


def get_news_for_company(user_id, company):
    user = User.objects.get(id=user_id)
    news_url = comms_consts.NEW_API_URI + "/" + comms_consts.NEW_API_EVERYTHING_URI(company)
    while True:
        try:
            with Variable_Client() as client:
                new_res = client.get(news_url, headers=comms_consts.NEWS_API_HEADERS)
            new_res = _handle_news_response(new_res)
            new_res = new_res["articles"]
            break
        except Exception as e:
            logger.exception(e)
            break

    descriptions = [article["description"] for article in new_res]
    attempts = 1
    has_error = False
    token_amount = 500
    timeout = 60.0
    while True:
        url = core_consts.OPEN_AI_COMPLETIONS_URI
        prompt = comms_consts.OPEN_AI_NEWS_CLIPS_SUMMARY(
            datetime.datetime.now().date(), descriptions, company
        )
        body = core_consts.OPEN_AI_COMPLETIONS_BODY(
            user.email, prompt, token_amount=token_amount, top_p=0.1
        )
        # logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: body <{body}>")
        Client = Variable_Client(timeout)
        with Client as client:
            r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
            r = _handle_open_ai_response(r)
