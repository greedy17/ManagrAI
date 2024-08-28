import logging
import re

from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError
from managr.api import constants as api_consts

logger = logging.getLogger("managr")


class TokenExpired(Exception):
    def __init__(self, message="Token Expired"):
        self.message = message
        super().__init__(self.message)


class TokenRevoked(Exception):
    def __init__(self, message="Your token is revoked, please reconnect Slack"):
        self.message = message
        super().__init__(self.message)


class ApiRateLimitExceeded(Exception):
    def __init__(self, message="Token Expired"):
        self.message = message
        super().__init__(self.message)


class InvalidBlocksException(Exception):
    def __init__(self, message="Invalid Blocks Sent"):
        self.message = message
        super().__init__(self.message)


class InvalidBlocksFormatException(Exception):
    def __init__(self, message="Invalid Blocks Sent"):
        self.message = message
        super().__init__(self.message)


class UnHandeledBlocksException(Exception):
    def __init__(self, message="Error Generating Slack Modal"):
        self.message = message
        super().__init__(self.message)


class InvalidArgumentsException(Exception):
    def __init__(self, message="Error Generating Slack Modal"):
        self.message = message
        super().__init__(self.message)


class InvalidAccessToken(Exception):
    def __init__(self, message="Slack Token Invalid"):
        self.message = message
        super().__init__(self.message)


class CannotUpdateMessage(Exception):
    def __init__(self, message="You do not have permission to update this message"):
        self.message = message
        super().__init__(self.message)


class TextTooLong(Exception):
    def __init__(self, message="Message text if over Slack character limit"):
        self.message = message
        super().__init__(self.message)


class CannotSendToChannel(Exception):
    def __init__(
        self, message="Unable to post in channel most likely because bot/user not in channel"
    ):
        self.message = message
        super().__init__(self.message)


class ChannelArchived(Exception):
    def __init__(self, message="Unable to post to channel because it is archived"):
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

            logger.error(
                f"{api_consts.SLACK_ERROR} ---An error occured with a slack integration, {self.fn_name}"
            )
            raise Api500Error()
        elif self.code == 401:
            raise TokenExpired()
        elif self.code == 403:
            raise ApiRateLimitExceeded()
        elif self.code == 200:
            if "less than 3001 characters" in self.message:
                raise TextTooLong()
            elif self.param == "token_revoked":
                raise TokenRevoked()
            elif self.param == "invalid_blocks":
                # find the block_indexes
                blocks = [self._extract_invalid_block(error) for error in self.message]
                message = f"Invalid Blocks {'------'.join(blocks)}"
                logger.error(
                    f"{api_consts.SLACK_ERROR} ---An error occured building blocks {message}"
                )
                raise InvalidBlocksException(message)
            elif self.param == "cant_update_message":
                raise CannotUpdateMessage()
            elif self.param == "invalid_auth":
                logger.error(
                    f"{api_consts.SLACK_ERROR} ---An error occured with the access token this access token is org level {self.message}"
                )
                raise InvalidAccessToken(self.message)
            elif self.param == "invalid_blocks_format":
                logger.error(
                    f"{api_consts.SLACK_ERROR} An error occured building blocks because of an invalid format"
                )
                raise InvalidBlocksFormatException(self.message)
            elif self.param == "invalid_arguments":
                blocks = [self._extract_invalid_args_block(error) for error in self.message]
                message = f"Invalid Args {'------'.join(blocks)}"
                logger.error(
                    f"{api_consts.SLACK_ERROR} ---{self.param}-{self.message} blocks {blocks}"
                )
                raise InvalidArgumentsException(
                    f"{api_consts.SLACK_ERROR} ---{self.param}-{self.message} blocks {blocks}"
                )
            elif self.param == "not_in_channel" or self.param == "channel_not_found":
                raise CannotSendToChannel("ManagrAI is not in this channel")
        if "is_archived" in self.message:
            raise ChannelArchived
        else:
            # we may not have come accross this error yet
            logger.error(f"{api_consts.SLACK_ERROR} ---{self.param}-{self.message}")
            raise UnHandeledBlocksException(
                f"{api_consts.SLACK_ERROR} ---{self.param}-{self.message}"
            )

    def _extract_invalid_block(self, error):
        # regex to get [json-pointer:/blocks/0/text]
        matches = re.search(r"json-pointer:", error)
        if matches:
            if len(error) >= matches.end() + 8:
                block_index = int(error[matches.end() + 8])
                return f"{error[:matches.start()]} on block {self.blocks[block_index]}"
        return error

    def _extract_invalid_args_block(self, error):
        # regex to get [json-pointer:/blocks/0/text]
        matches = re.search(r"json-pointer:", error)
        print(f"INVALID ARGS ERROR: {error}")
        if matches:
            if len(error) >= matches.end() + 13 and self.blocks:
                block_index = int(error[matches.end() + 13])
                return f"{error[:matches.start()]} on block {self.blocks[block_index]}"
        return error
