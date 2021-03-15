import functools
import logging
from managr.salesforce.adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
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


def sf_api_exceptions(error_key):
    """Decorator for sf async functions will error_key: kebab case key"""

    def error_fn(func):
        @functools.wraps(func)
        def wrapper_sf_api_exceptions(*args, **kwargs):
            # only retries for token expired errors
            operation_key = f"Failed on operation {snake_to_space(error_key)}"
            try:
                return func(*args, **kwargs)
            except RequiredFieldError as e:
                from managr.salesforce.models import MeetingWorkflow

                workflow_id = args[0]
                w = MeetingWorkflow.objects.filter(id=workflow_id).first()
                if not w:
                    LOGGER.exception(f"Function wrapped in sfw logger but cannot find workflow {e}")
                w.failed_task_description.append(f"{operation_key} {str(e)}")
                w.save()
            except FieldValidationError as e:
                from managr.salesforce.models import MeetingWorkflow

                workflow_id = args[0]
                w = MeetingWorkflow.objects.filter(id=workflow_id).first()
                if not w:
                    LOGGER.exception(f"Function wrapped in sfw logger but cannot find workflow {e}")
                w.failed_task_description.append(f"{operation_key} {str(e)}")
                w.save()

            except Exception as e:
                LOGGER.exception(e)

        return wrapper_sf_api_exceptions

    return error_fn

