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


class InvalidBlocksException(Exception):
    def __init(self, message="Invalid Blocks Sent"):
        self.message = message
        super().__init__(self.message)


class InvalidBlocksFormatException(Exception):
    def __init(self, message="Invalid Blocks Sent"):
        self.message = message
        super().__init__(self.message)


class Api500Error(APIException):
    status_code = 500
    default_detail = """An error occurred with your request, this is an error with our system, please try again in 10 minutes"""
    default_code = "salesforce_api_error"


class CustomAPIException:
    def __init__(self, e, fn_name=None, retries=0, blocks=[]):
        self.error = e
        self.error_class_name = e.__class__.__name__
        self.code = e.args[0]["error_code"]
        self.param = e.args[0]["error_param"]
        self.message = e.args[0]["error_message"]
        self.blocks = blocks
        self.fn_name = fn_name
        self.retry_attempts = 0
        self.raise_error()

    def raise_error(self):
        # if an invalid Basic auth is sent the response is still a 200 success
        # instead we check data.json() which will return a JSONDecodeError
        if self.error_class_name == "JSONDecodeError":
            logger.error(f"An error occured with a salesforce integration, {self.fn_name}")
            raise Api500Error()
        elif self.code == 401:
            raise TokenExpired()
        elif self.code == 403:
            raise ApiRateLimitExceeded()
        elif self.code == 200 and self.param == "invalid_blocks":
            # find the block_indexes
            blocks = [self._extract_block(error) for error in self.message]
            message = f"Invalid Blocks {'------'.join(blocks)}"
            logger.error(f"An error occured building blocks {message}")
            raise InvalidBlocksException(message)
            # this error is a malformced query error we should log this (most likely from relationship feilds)
        elif self.code == 200 and self.param == "invalid_blocks_format":
            # find the block_indexes
            logger.error(f"An error occured building blocks {self.message}")
            raise InvalidBlocksFormatException(message)
            # this error is a malformced query error we should log this (most likely from relationship feilds)

        else:
            raise ValidationError(
                {"detail": {"key": self.code, "message": self.message, "field": self.param,}}
            )

    def _extract_block(self, error):
        # regex to get [json-pointer:/blocks/0/text]
        matches = re.search(r"json-pointer:", error)
        if matches:
            block_index = int(error[matches.end() + 8])
            return f"{error[:matches.start()]} on block {self.blocks[block_index]}"
        return None

        return
