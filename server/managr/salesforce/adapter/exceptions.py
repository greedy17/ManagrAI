import logging
import re

from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError


logger = logging.getLogger("managr")


class TokenExpired(Exception):
    def __init(self, message="Token Expired"):
        self.message = message
        super().__init__(self.message)


class ApiRateLimitExceeded(Exception):
    def __init(self, message="Token Expired"):
        self.message = message
        super().__init__(self.message)


class FieldValidationError(Exception):
    def __init(self, message="Validation Error on Fields"):
        self.message = message
        super().__init__(self.message)


class RequiredFieldError(Exception):
    def __init(self, message="Invalid/Missing Required Field"):
        self.message = message
        super().__init__(self.message)


class SFNotFoundError(Exception):
    def __init(self, message="Error Generating Slack Modal"):
        self.message = message
        super().__init__(self.message)


class SFQueryOffsetError(Exception):
    def __init(self, message="OFFSET MAX IS 2000"):
        self.message = message
        super().__init__(self.message)


class InvalidFieldError(Exception):
    def __init(self, message="Invalid/Duplicate Field in query"):
        self.message = message
        super().__init__(self.message)


class UnhandledSalesforceError(Exception):
    def __init(self, message="Invalid/Duplicate Field in query"):
        self.message = message
        super().__init__(self.message)


class Api500Error(APIException):
    status_code = 500
    default_detail = """An error occurred with your request, this is an error with our system, please try again in 10 minutes"""
    default_code = "salesforce_api_error"


class CustomAPIException:
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
        if self.error_class_name == "JSONDecodeError":
            logger.error(f"An error occured with a salesforce integration, {self.fn_name}")
            raise Api500Error()
        elif self.status_code == 401:
            raise TokenExpired()
        elif self.status_code == 404:
            raise SFNotFoundError()
        elif self.status_code == 403:
            raise ApiRateLimitExceeded()
        elif self.status_code == 400 and self.param == "FIELD_CUSTOM_VALIDATION_EXCEPTION":
            raise FieldValidationError(self.message)
        elif self.status_code == 400 and self.param == "REQUIRED_FIELD_MISSING":
            raise RequiredFieldError(self.message)
        elif self.status_code == 400 and self.param == "NUMBER_OUTSIDE_VALID_RANGE":
            raise SFQueryOffsetError(self.message)
        elif self.status_code == 400 and self.param == "INVALID_FIELD":
            # invalid field could apply to a number of different errors
            # we are trying to parse out duplicate field errors and non queryable errors
            message_split = self.message.splitlines()
            if len(message_split) == 5:
                error_line = message_split[4]
                # check if error is on column
                no_column_match = re.match(r"(No such column)", error_line)
                if no_column_match:
                    field = re.match(r"\s+\'\w+\' ", error_line[no_column_match.end() :])
                    field_str = (
                        error_line[
                            no_column_match.end()
                            + field.start() : no_column_match.end()
                            + field.end()
                        ]
                        .lstrip(" ")
                        .rstrip(" ")
                    )
                    logger.info(f"Invalid Field {field_str}")
                    raise InvalidFieldError(f"There was an invalid field in the query {field_str}")

            raise InvalidFieldError(
                f"There was an error in the data sent to salesforce but we could not determine what field caused this {e}"
            )

        elif self.status_code == 400 and self.param == "NOT_FOUND":
            raise UnhandledSalesforceError(
                f"The selected object does not exist in salesforce {self.message}"
            )

        else:

            raise UnhandledSalesforceError(f"salesforce returned {self.param} {self.message}")
