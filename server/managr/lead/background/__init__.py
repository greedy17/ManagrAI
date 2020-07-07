import logging

from background_task import background
from .routing import routes
from .exceptions import ConsumerConfigError
from managr.core.models import EmailAuthAccount, User

logger = logging.getLogger("managr")


def emit_event(action, user, obj):
    """Background tasks need JSON-serializable params, so this function is for convenience.

    TODO: Make 'emit_event' and its consumers more general. At the moment, the
          handlers only log the event by creating a LeadActivityLog.
    """
    _log_lead_action(action, str(user.id), str(obj.id))


@background(schedule=0)
def _log_lead_action(action, user_id, obj_id):
    """Activity log event dispatcher."""
    # Retrieve and instantiate a consumer class
    route_name, action = action.split(".")

    try:
        consumer = routes[route_name](action, user_id, obj_id)
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


@background(schedule=0)
def _get_email_info(account_id, object_id, date):
    """ 
        check if the email is for a lead that the user is claiming 
        account_id email account of the user 
        object_id the id of the object for querying 
        date epoch datetime when the change occured
    """
    user = None
    try:
        user = User.objects.get(email_auth_account__account_id=account_id)
    except User.DoesNotExist as e:
        print(e)
        pass
    print(user)
