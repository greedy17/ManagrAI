import logging

from background_task import background
from .routing import routes
from .exceptions import ConsumerConfigError


logger = logging.getLogger("managr")


def emit_event(action, user, obj, extra_meta=None):
    """Background tasks need JSON-serializable params, so this function is for convenience.

    TODO: Make 'emit_event' and its consumers more general. At the moment, the
          handlers only log the event by creating a LeadActivityLog.
    """
    _log_lead_action(action, str(user.id), str(obj.id), extra_meta=extra_meta)


@background(schedule=0)
def _log_lead_action(action, user_id, obj_id, extra_meta=None):
    """Activity log event dispatcher."""
    # Retrieve and instantiate a consumer class
    route_name, action = action.split(".")

    try:
        consumer = routes[route_name](action, user_id, obj_id, extra_meta=extra_meta)
    except KeyError:
        logger.exception(
            f"Background consumer route '{route_name}' "
            f"not found in the routing table."
        )

    try:
        consumer.create_log()
    except ConsumerConfigError as e:
        logger.exception(
            f"The consumer class class '{consumer.__class__.__name__}' is misconfigured: {e}"
        )
