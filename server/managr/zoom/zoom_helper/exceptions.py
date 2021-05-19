import logging
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError

logger = logging.getLogger("managr")


class TokenExpired(Exception):
    def __init(self, message="Token Expired"):
        self.message = message
        super().__init__(self.message)


class AccountSubscriptionLevel(Exception):
    def __init(self, message="Account Level Basic Not Allowed"):
        self.message = message
        super().__init__(self.message)


class InvalidRequest(Exception):
    def __init(self, message="Invalid Request Sent"):
        self.message = message
        super().__init__(self.message)


class Zoom500Error(APIException):
    status_code = 500
    default_detail = """An error occurred with your request, this is an error with our system, please try again in 10 minutes"""
    default_code = "zoom_api_error"


class ZoomAPIException:
    def __init__(self, e, fn_name=None, retries=0):
        self.error = e
        self.error_class_name = e.__class__.__name__
        self.status_code = e.args[0]["status_code"]
        self.code = e.args[0]["error_code"]
        self.param = e.args[0]["error_param"]
        self.message = e.args[0]["error_message"]
        self.fn_name = fn_name
        self.retry_attempts = 0
        self.raise_error()

    def raise_error(self):
        # if an invalid Basic auth is sent the response is still a 200 success
        # instead we check data.json() which will return a JSONDecodeError
        if self.status_code == 429 or self.error_class_name == "JSONDecodeError":
            logger.error(f"An error occured with a zoom integration, {self.message}")
            raise Zoom500Error()
        elif self.status_code == 401 and self.code == 124:
            raise TokenExpired()
        elif self.status_code == 400 and self.code == 200:
            raise AccountSubscriptionLevel(self.message)
        elif self.status_code == 400 and not self.code:
            raise InvalidRequest(f"The request was invalid {self.param}")
        else:
            raise ValidationError(
                {"detail": {"key": self.code, "message": self.message, "field": self.param,}}
            )
