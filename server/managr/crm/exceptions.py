import logging

from rest_framework.exceptions import APIException

logger = logging.getLogger("managr")


class TokenExpired(Exception):
    def __init(self, message="Token Expired"):
        self.message = message
        super().__init__(self.message)


class InvalidRefreshToken(Exception):
    def __init(
        self, message="There was a problem with your SFDC connection, please reconnect to SFDC"
    ):
        self.message = message
        super().__init__(self.message)


class MalformedQuery(Exception):
    def __init(self, message="Cannot Refresh Token User Must Revoke Token"):
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


class UnableToUnlockRow(Exception):
    def __init(self, message="Unable to unlock row"):
        self.message = message
        super().__init__(self.message)


class CannotRetreiveObjectType(Exception):
    def __init(self, message="A new error occured Invalid Type/Insufficient Access"):
        self.message = message
        super().__init__(self.message)


class UnhandledCRMError(Exception):
    def __init(self, message="A new error occured"):
        self.message = message
        super().__init__(self.message)


class Api500Error(APIException):
    status_code = 500
    default_detail = """An error occurred with your request, this is an error with our system, please try again in 10 minutes"""
    default_code = "salesforce_api_error"


class ConvertTargetNotAllowedError(Exception):
    def __init(self, message="A new error occured"):
        self.message = message
        super().__init__(self.message)
