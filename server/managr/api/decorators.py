import functools
import logging

LOGGER = logging.getLogger("lighten")


def log_all_exceptions(func):
    """Decorator for alert functions that will catch and log any exceptions."""

    @functools.wraps(func)
    def wrapper_log_all_exceptions(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            LOGGER.exception(e)

    return wrapper_log_all_exceptions

