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

from . import constants as hs_consts
from managr.utils.misc import snake_to_space

LOGGER = logging.getLogger("managr")
WORKFLOW_KEY_MAP = {
    "update_object_from_review": hs_consts.MEETING_REVIEW__UPDATE_RESOURCE,
    "add_call_log": hs_consts.MEETING_REVIEW__SAVE_CALL_LOG,
}


def hs_api_exceptions_wf(error_key):
    """Decorator for sf async (for workflows only) functions will error_key: kebab case key"""

    def error_fn(func):
        @functools.wraps(func)
        def wrapper_hs_api_exceptions_wf(*args, **kwargs):
            # only retries for token expired errors
            try:
                return func(*args, **kwargs)
            except RequiredFieldError as e:
                from managr.salesforce.models import MeetingWorkflow

                operation_key = f"Failed to {snake_to_space(error_key)}"
                workflow_id = args[0]
                failed_task_string = f"{str(e)}.{WORKFLOW_KEY_MAP[error_key]}"
                w = MeetingWorkflow.objects.filter(id=workflow_id).first()
                if not w:
                    return LOGGER.exception(
                        f"Function wrapped in sfw logger but cannot find workflow {e}"
                    )
                w.failed_task_description.append(failed_task_string)
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
                failed_task_string = f"{str(e)}.{WORKFLOW_KEY_MAP[error_key]}"
                w.failed_task_description.append(failed_task_string)
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
                w.failed_task_description.append(f"{WORKFLOW_KEY_MAP[error_key]}.{str(e)}")
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

        return wrapper_hs_api_exceptions_wf

    return error_fn
