import json
import logging
from requests.exceptions import HTTPError

logger = logging.getLogger("managr")


class ServerError(Exception):
    def __init__(self, error="There was an issue communicating with the news source"):
        self.message = error
        super().__init__(self.message)


class NewsApiException:
    def __init__(self, e, fn_name=None, retries=0):
        self.error = e
        self.error_class_name = e.__class__.__name__
        self.status_code = e.args[0]["status_code"]
        self.param = e.args[0]["error_param"]
        self.fn_name = fn_name
        self.retry_attempts = 0
        self.raise_error()

    def raise_error(self):
        # if an invalid Basic auth is sent the response is still a 200 success
        # instead we check data.json() which will return a JSONDecodeError
        if self.error_class_name == "JSONDecodeError":
            logger.error(f"An error occured decoding the json, {self.fn_name}")
            return
        elif self.status_code == 401:
            return
        elif self.status_code == 404 and self.param == "EXPIRED_AUTHENTICATION":
            return
        elif self.status_code == 500:
            raise ServerError()
        else:
            raise Exception(f"News error: {self.message}")


def _handle_response(response, fn_name=None):
    data = None
    if not hasattr(response, "status_code"):
        raise ValueError
    elif response.status_code == 200:
        try:
            data = response.json()
        except json.decoder.JSONDecodeError as e:
            return logger.error(f"An error occured with a news source, {e}")
        except Exception as e:
            NewsApiException(e, fn_name)
    else:
        status_code = response.status_code
        error_data = response.json()
        error_check = error_data.get("error", None)
        error_param = error_check if error_check else error_data.get("errors")
        kwargs = {
            "status_code": status_code,
            "error_param": error_param,
        }
        NewsApiException(HTTPError(kwargs), fn_name)
    return data
