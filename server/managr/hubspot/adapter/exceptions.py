import logging
import re

from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError
from managr.crm.exceptions import (
    TokenExpired,
    InvalidFieldError,
    MalformedQuery,
    ApiRateLimitExceeded,
    Api500Error,
    APIException,
    InvalidRefreshToken,
    FieldValidationError,
    RequiredFieldError,
    SFNotFoundError,
    SFQueryOffsetError,
    UnableToUnlockRow,
    UnhandledCRMError,
    ConvertTargetNotAllowedError,
    CannotRetreiveObjectType,
)

logger = logging.getLogger("managr")


# class CRM(Exception):
#     def __init(self, message="Token Expired"):
#         self.message = message
#         super().__init__(self.message)


# class InvalidRefreshToken(Exception):
#     def __init(self, message="Cannot Refresh Token User Must Revoke Token"):
#         self.message = message
#         super().__init__(self.message)


# class MalformedQuery(Exception):
#     def __init(self, message="Cannot Refresh Token User Must Revoke Token"):
#         self.message = message
#         super().__init__(self.message)


# class ApiRateLimitExceeded(Exception):
#     def __init(self, message="Token Expired"):
#         self.message = message
#         super().__init__(self.message)


# class FieldValidationError(Exception):
#     def __init(self, message="Validation Error on Fields"):
#         self.message = message
#         super().__init__(self.message)


# class RequiredFieldError(Exception):
#     def __init(self, message="Invalid/Missing Required Field"):
#         self.message = message
#         super().__init__(self.message)


# class SFNotFoundError(Exception):
#     def __init(self, message="Error Generating Slack Modal"):
#         self.message = message
#         super().__init__(self.message)


# class SFQueryOffsetError(Exception):
#     def __init(self, message="OFFSET MAX IS 2000"):
#         self.message = message
#         super().__init__(self.message)


# class InvalidFieldError(Exception):
#     def __init(self, message="Invalid/Duplicate Field in query"):
#         self.message = message
#         super().__init__(self.message)


# class UnableToUnlockRow(Exception):
#     def __init(self, message="Unable to unlock row"):
#         self.message = message
#         super().__init__(self.message)


# class CannotRetreiveObjectType(Exception):
#     def __init(self, message="A new error occured Invalid Type/Insufficient Access"):
#         self.message = message
#         super().__init__(self.message)


# class UnhandledHubspotError(Exception):
#     def __init(self, message="A new error occured"):
#         self.message = message
#         super().__init__(self.message)


# class Api500Error(APIException):
#     status_code = 500
#     default_detail = """An error occurred with your request, this is an error with our system, please try again in 10 minutes"""
#     default_code = "hubspot_api_error"


# class ConvertTargetNotAllowedError(Exception):
#     def __init(self, message="A new error occured"):
#         self.message = message
#         super().__init__(self.message)


class CustomAPIException:
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
            logger.error(f"An error occured with a hubspot integration, {self.fn_name}")
            raise Api500Error()
        elif self.status_code == 401:
            raise TokenExpired()
        elif self.status_code == 404 and self.param == "EXPIRED_AUTHENTICATION":
            raise TokenExpired()
        elif self.status_code == 403:
            raise ApiRateLimitExceeded()
        elif self.status_code == 400 and self.param == "FIELD_CUSTOM_VALIDATION_EXCEPTION":
            raise FieldValidationError(self.message)
        elif self.status_code == 400 and self.param == "REQUIRED_FIELD_MISSING":
            raise RequiredFieldError(self.message)
        elif self.status_code == 400 and self.param == "MALFORMED_QUERY":
            raise MalformedQuery(self.message)
        elif self.status_code == 400 and self.param == "NUMBER_OUTSIDE_VALID_RANGE":
            raise SFQueryOffsetError(self.message)
        elif self.status_code == 400 and self.param == "invalid_grant":
            raise InvalidRefreshToken(self.message)
        elif self.status_code == 400 and "Property values were not valid" in self.message:
            # invalid field could apply to a number of different errors
            # we are trying to parse out duplicate field errors and non queryable errors
            try:
                removed_string = self.message[self.message.index("[") : self.message.index("]") + 1]
                removed_string = removed_string.replace("false", "False")
                eval_list = eval(removed_string)
                error_message = eval_list[0].get("localizedErrorMessage", None)
                error_message_field = eval_list[0].get("name", None)
                raise InvalidFieldError(
                    f"There was an error with on of your field values: {error_message_field} - {error_message}"
                )
            except Exception as e:
                logger.exception(e)
                raise InvalidFieldError(
                    f"There was an error with on of your field values: {self.message}"
                )

        elif self.status_code == 400 and self.param == "NOT_FOUND":
            raise UnhandledCRMError(f"The selected object does not exist in hubspot {self.message}")
        elif self.status_code == 400 and self.param == "INVALID_TYPE":
            raise CannotRetreiveObjectType(
                f"User does not have access to this object type {self.message}"
            )
        elif self.status_code == 400 and self.param == "INSUFFICIENT_ACCESS":
            raise CannotRetreiveObjectType(
                f"User does not have access to this object type {self.message}"
            )
        elif self.status_code == 400 and self.param == "UNABLE_TO_LOCK_ROW":
            raise UnableToUnlockRow(
                f"Unable to save data because row is locked by hubspot {self.message}"
            )
        elif self.status_code == 429 and self.param == "RATE_LIMITS":
            raise ApiRateLimitExceeded("Secondly Limit")
        else:
            raise UnhandledCRMError(f"HubSpot error: {self.message}")
