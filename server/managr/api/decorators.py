import functools
import logging
from managr.salesforce.adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
)

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


def sf_api_exceptions(func):
    """Decorator for alert functions that will catch and log any exceptions."""

    @functools.wraps(func)
    def wrapper_sf_api_exceptions(*args, **kwargs):
        # only retries for token expired errors

        try:
            return func(*args, **kwargs)
        except RequiredFieldError as e:
            from managr.salesforce.models import MeetingWorkflow

            workflow_id = args[0]
            w = MeetingWorkflow.objects.filter(id=workflow_id).first()
            if not w:
                LOGGER.exception(f"Function wrapped in sfw logger but cannot find workflow {e}")
            w.failed_task_description.append(str(e))
            w.save()
        except FieldValidationError as e:
            from managr.salesforce.models import MeetingWorkflow

            workflow_id = args[0]
            w = MeetingWorkflow.objects.filter(id=workflow_id).first()
            if not w:
                LOGGER.exception(f"Function wrapped in sfw logger but cannot find workflow {e}")
            w.failed_task_description.append(str(e))
            w.save()

        except Exception as e:
            LOGGER.exception(e)

    return wrapper_sf_api_exceptions

