import logging
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError

logger = logging.getLogger("managr")


class Zoom500Error(APIException):
    status_code = 500
    default_detail = """An error occurred with your request, this is an error with our system, please try again in 10 minutes"""
    default_code = "zoom_api_error"


class ZoomAPIException:
    def __init__(self, e, fn_name=None, retries=0):
        self.error = e
        self.error_class_name = e.__class__.__name__
        self.code = e.args[0]["error_code"]
        self.param = e.args[0]["error_param"]
        self.message = e.args[0]["error_message"]
        self.fn_name = fn_name
        self.retry_attempts = 0
        self.raise_error()

    def raise_error(self):
        # if an invalid Basic auth is sent the response is still a 200 success
        # instead we check data.json() which will return a JSONDecodeError
        if self.code == 429 or self.error_class_name == "JSONDecodeError":
            logger.error(f"An error occured with a zoom integration, {self.fn_name}")
            raise Zoom500Error()
        else:
            raise ValidationError(
                {
                    "detail": {
                        "key": self.code,
                        "message": self.message,
                        "field": self.param,
                    }
                }
            )

