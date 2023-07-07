import logging
import json
import httpx
import datetime
from background_task import background
from managr.utils.client import Variable_Client
from ..utils import get_news_for_company
from .. import constants as comms_consts
from managr.core import constants as core_consts
from managr.core.models import User
from managr.core import exceptions as open_ai_exceptions

logger = logging.getLogger("managr")


def emit_process_news_summary(payload, context, schedule=datetime.datetime.now()):
    return _process_news_summary(payload, context, schedule=schedule)


@background()
def _process_news_summary(payload, context):
    print(payload)
    user = User.objects.get(id=context.get("u"))
    news_res = get_news_for_company(company)
    descriptions = [article["description"] for article in news_res]
    attempts = 1
    has_error = False
    token_amount = 500
    timeout = 60.0
    while True:
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        prompt = comms_consts.OPEN_AI_NEWS_CLIPS_SUMMARY(
            datetime.datetime.now().date(), descriptions, company
        )
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email, prompt, token_amount=token_amount, top_p=0.1
        )
        print(body)
        with Variable_Client(timeout) as client:
            r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
        try:
            r = open_ai_exceptions._handle_response(r)
            print(message)
            break
        except open_ai_exceptions.StopReasonLength:
            logger.exception(
                f"Retrying again due to token amount, amount currently at: {token_amount}"
            )
            if token_amount <= 2000:
                return
            else:
                token_amount += 500
                continue
        except httpx.ReadTimeout as e:
            timeout += 30.0
            if timeout >= 120.0:
                has_error = True
                logger.exception(f"Read timeout from Open AI {e}")
                break
            else:
                attempts += 1
                continue
        except Exception as e:
            has_error = True
            logger.exception(e)
            break
    return
