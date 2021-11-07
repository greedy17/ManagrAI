import logging
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError

logger = logging.getLogger("managr")


class TokenExpired(Exception):
    def __init(self, error="Invalid Bearer token"):
        self.message = error
        super().__init__(self.message)


class InvalidRequest(Exception):
    def __init(self, message="Invalid Request Sent"):
        self.message = message
        super().__init__(self.message)


class OutreachAPIException:
    def __init__(self, e, fn_name=None, retries=0):
        self.error = e
        self.error_class_name = e.__class__.__name__
        self.status_code = e.args[0]["status_code"]
        self.error = e.args[0]["error_param"]
        self.fn_name = fn_name
        self.retry_attempts = 0
        self.raise_error()

    def raise_error(self):
        # if an invalid Basic auth is sent the response is still a 200 success
        # instead we check data.json() which will return a JSONDecodeError
        if self.status_code == 422:
            logger.error(f"Outreach API error: {self.error}")
            raise InvalidRequest()
        elif self.status_code == 403 or self.status_code == 401:
            raise TokenExpired()
        else:
            raise ValidationError({"detail": {"message": self.error,}})
