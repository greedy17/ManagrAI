import functools
import logging

from managr.crm.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    UnhandledCRMError,
    SFNotFoundError,
    InvalidRefreshToken,
    InvalidFieldError,
    UnableToUnlockRow,
    CannotRetreiveObjectType,
    MalformedQuery,
)
from managr.slack.helpers.exceptions import (
    TokenExpired,
    ApiRateLimitExceeded,
    InvalidBlocksException,
    InvalidBlocksFormatException,
    UnHandeledBlocksException,
    InvalidArgumentsException,
    InvalidAccessToken,
    CannotSendToChannel,
)
from managr.utils.misc import snake_to_space

LOGGER = logging.getLogger("managr")


def log_all_exceptions(func):
    """Decorator for alert functions that will catch and log any exceptions."""

    @functools.wraps(func)
    def wrapper_log_all_exceptions(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            LOGGER.exception(e)

    return wrapper_log_all_exceptions


def sf_api_exceptions_wf(error_key):
    """Decorator for sf async (for workflows only) functions will error_key: kebab case key"""

    def error_fn(func):
        @functools.wraps(func)
        def wrapper_sf_api_exceptions_wf(*args, **kwargs):
            # only retries for token expired errors
            try:
                return func(*args, **kwargs)
            except RequiredFieldError as e:
                from managr.salesforce.models import MeetingWorkflow

                operation_key = f"Failed to {snake_to_space(error_key)}"

                workflow_id = args[0]
                w = MeetingWorkflow.objects.filter(id=workflow_id).first()
                if not w:
                    return LOGGER.exception(
                        f"Function wrapped in sfw logger but cannot find workflow {e}"
                    )
                w.failed_task_description.append(f"{operation_key} {str(e)}")
                w.save()
            except FieldValidationError as e:
                from managr.salesforce.models import MeetingWorkflow

                operation_key = f"Failed to {snake_to_space(error_key)}"

                workflow_id = args[0]
                w = MeetingWorkflow.objects.filter(id=workflow_id).first()
                if not w:
                    return LOGGER.exception(
                        f"Function wrapped in sfw logger but cannot find workflow {e}"
                    )
                w.failed_task_description.append(f"{operation_key} {str(e)}")
                w.save()
            except InvalidFieldError as e:
                from managr.salesforce.models import MeetingWorkflow

                operation_key = f"Failed to {snake_to_space(error_key)}"

                workflow_id = args[0]
                w = MeetingWorkflow.objects.filter(id=workflow_id).first()
                if not w:
                    return LOGGER.exception(
                        f"Function wrapped in sfw logger but cannot find workflow {e}"
                    )
                w.failed_task_description.append(f"{operation_key} {str(e)}")
                w.save()
            except UnhandledCRMError as e:
                from managr.salesforce.models import MeetingWorkflow

                operation_key = f"Failed to {snake_to_space(error_key)}"
                workflow_id = args[0]
                w = MeetingWorkflow.objects.filter(id=workflow_id).first()
                if not w:
                    return LOGGER.exception(
                        f"Function wrapped in sfw logger but cannot find workflow {e}"
                    )
                w.failed_task_description.append(f"{operation_key} {str(e)}")
                w.save()
            except SFNotFoundError as e:
                from managr.salesforce.models import MeetingWorkflow

                operation_key = f"Failed to {snake_to_space(error_key)}"
                workflow_id = args[0]
                w = MeetingWorkflow.objects.filter(id=workflow_id).first()
                if not w:
                    return LOGGER.exception(
                        f"Function wrapped in sfw logger but cannot find workflow {e}"
                    )
                w.failed_task_description.append(f"{operation_key} {str(e)}")
                w.save()
            except UnableToUnlockRow as e:
                from managr.salesforce.models import MeetingWorkflow

                operation_key = f"Failed to {snake_to_space(error_key)}"
                workflow_id = args[0]
                w = MeetingWorkflow.objects.filter(id=workflow_id).first()
                if not w:
                    return LOGGER.exception(
                        f"Function wrapped in sfw logger but cannot find workflow {e}"
                    )
                w.failed_task_description.append(f"{operation_key} {str(e)}")
                w.save()
            except InvalidRefreshToken as e:
                from managr.salesforce.models import MeetingWorkflow

                operation_key = f"Failed to {snake_to_space(error_key)}"
                workflow_id = args[0]
                w = MeetingWorkflow.objects.filter(id=workflow_id).first()
                if not w:
                    return LOGGER.exception(
                        f"Function wrapped in sfw logger but cannot find workflow {e}"
                    )
                w.failed_task_description.append(
                    f"{operation_key} Refresh Token is invalid/expired please revoke and refresh token"
                )
                w.save()

            except Exception as e:
                LOGGER.exception(f"Function wrapped in sfw logger but cannot find workflow {e}")

        return wrapper_sf_api_exceptions_wf

    return error_fn


def sf_api_exceptions(rethrow=False):
    """Decorator for sf async functions will error_key: kebab case key"""

    def error_fn(func):
        @functools.wraps(func)
        def wrapper_sf_api_exceptions(*args, **kwargs):
            # only retries for token expired errors
            try:
                return func(*args, **kwargs)
            except RequiredFieldError as e:
                LOGGER.exception(f"{e}")
                if rethrow:
                    raise e

            except FieldValidationError as e:
                LOGGER.exception(f"{e}")
                if rethrow:
                    raise e

            except UnhandledCRMError as e:
                LOGGER.exception(f"{e}")
                if rethrow:
                    raise e

            except SFNotFoundError as e:
                LOGGER.exception(f"{e}")
                if rethrow:
                    raise e

            except InvalidRefreshToken as e:
                LOGGER.exception(f"{e}")
                if rethrow:
                    raise e

            except InvalidFieldError as e:
                LOGGER.exception(f"{e}")
                if rethrow:
                    raise e

            except CannotRetreiveObjectType as e:
                LOGGER.exception(f"{e}")
                if rethrow:
                    raise e
            except MalformedQuery as e:
                LOGGER.exception(f"{e}")
                if rethrow:
                    raise e

            except Exception as e:
                if rethrow:
                    raise e

                LOGGER.exception(f"Non SF related error {e}")

        return wrapper_sf_api_exceptions

    return error_fn


def slack_api_exceptions(rethrow=False, return_opt=None):
    """
    Decorator for cathcing common slack errors
    return_object: if provided will return what is passed eg return Response()
    rethrow: False will rethrow any caught errors if provided (return object will override)

    """

    def error_fn(func):
        @functools.wraps(func)
        def wrapper_slack_api_exceptions(*args, **kwargs):

            should_rethrow = rethrow and not return_opt
            try:
                return func(*args, **kwargs)
            except TokenExpired as e:
                if should_rethrow:
                    raise TokenExpired
                if return_opt:
                    return return_opt
            except ApiRateLimitExceeded as e:
                if should_rethrow:
                    raise ApiRateLimitExceeded
                if return_opt:
                    return return_opt
            except InvalidAccessToken as e:
                if should_rethrow:
                    raise InvalidAccessToken
                if return_opt:
                    return return_opt
            except InvalidBlocksException as e:
                if should_rethrow:
                    raise InvalidBlocksException
                if return_opt:
                    return return_opt
            except InvalidBlocksFormatException as e:
                if should_rethrow:
                    raise InvalidBlocksFormatException
                if return_opt:
                    return return_opt
            except InvalidArgumentsException as e:
                if should_rethrow:
                    raise InvalidArgumentsException
                if return_opt:
                    return return_opt
            except CannotSendToChannel as e:
                if should_rethrow:
                    raise CannotSendToChannel
                if return_opt:
                    return return_opt
            except Exception as e:
                LOGGER.exception(f"Unhandled error occured {e}")

        return wrapper_slack_api_exceptions

    return error_fn
