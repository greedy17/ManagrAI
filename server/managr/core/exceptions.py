import json
import logging
from requests.exceptions import HTTPError

logger = logging.getLogger("managr")


class MaximumTokenLength(Exception):
    def __init__(self, error="The transcript was to large to process"):
        self.message = error
        super().__init__(self.message)


class StopReasonLength(Exception):
    def __init__(self, error="There were not enough tokens assigned"):
        self.message = error
        super().__init__(self.message)


class ServerError(Exception):
    def __init__(self, error="There was an issue communicating with Open AI"):
        self.message = error
        super().__init__(self.message)


class OpenAIException:
    def __init__(self, e, fn_name=None, retries=0):
        self.error = e
        self.error_class_name = e.__class__.__name__
        self.status_code = e.args[0]["status_code"]
        self.param = e.args[0]["error_param"]
        self.message = e.args[0]["error_message"]
        self.fn_name = fn_name
        self.retry_attempts = 0
        self.raise_error()

    def raise_error(self):
        # if an invalid Basic auth is sent the response is still a 200 success
        # instead we check data.json() which will return a JSONDecodeError
        if self.error_class_name == "JSONDecodeError":
            logger.error(f"An error occured decoding the json, {self.fn_name}")
            return
        elif self.status_code == 400 and "maximum context length is" in self.message:
            raise MaximumTokenLength()
        elif self.status_code == 401:
            return
        elif self.status_code == 404 and self.param == "EXPIRED_AUTHENTICATION":
            return
        elif self.status_code == 500:
            raise ServerError()
        else:
            raise Exception(f"OpenAI error: {self.message}")


def _handle_response(response, fn_name=None):
    if not hasattr(response, "status_code"):
        raise ValueError
    elif response.status_code == 200:
        try:
            data = response.json()
            choice = data["choices"][0]
            if "finish_reason" in choice.keys():
                stop_reason = choice["finish_reason"]
                if stop_reason == "length":
                    raise StopReasonLength()
        except StopReasonLength:
            raise StopReasonLength()
        except json.decoder.JSONDecodeError as e:
            return logger.error(f"An error occured with a zoom integration, {e}")
        except Exception as e:
            OpenAIException(e, fn_name)
    else:
        status_code = response.status_code
        error_data = response.json()
        error_check = error_data.get("error", None)
        error_param = error_check if error_check else error_data.get("errors")
        kwargs = {
            "status_code": status_code,
            "error_param": error_param,
            "error_message": error_param["message"],
        }
        OpenAIException(HTTPError(kwargs), fn_name)
    return data


class StripeException:
    def __init__(self, e, fn_name=None, retries=0):
        self.error = e
        self.error_class_name = e.__class__.__name__
        self.status_code = e.args[0]["status_code"]
        self.param = e.args[0]["error_param"]
        self.message = e.args[0]["error_message"]
        self.fn_name = fn_name
        self.retry_attempts = 0
        self.raise_error()

    def raise_error(self):
        # if an invalid Basic auth is sent the response is still a 200 success
        # instead we check data.json() which will return a JSONDecodeError
        if self.error_class_name == "JSONDecodeError":
            logger.error(f"An error occured decoding the json, {self.fn_name}")
            return
        elif self.status_code == 400 and "maximum context length is" in self.message:
            raise MaximumTokenLength()
        elif self.status_code == 401:
            return
        elif self.status_code == 404 and self.param == "EXPIRED_AUTHENTICATION":
            return
        elif self.status_code == 500:
            raise ServerError()
        else:
            raise Exception(f"OpenAI error: {self.message}")
