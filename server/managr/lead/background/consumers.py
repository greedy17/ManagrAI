import logging

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser


from django.utils import timezone
from dateutil.parser import parse
from managr.core.models import User

from .. import models as lead_models
from .. import constants as lead_constants
from ..serializers import ActionSerializer

from .exceptions import ConsumerConfigError

logger = logging.getLogger("managr")


class BaseActionConsumer:
    """Consumes lead actions and creates the proper LeadActivityLog entry."""

    model_class = None

    def __init__(self, action, user_id, obj_id):
        self.action = action
        self.user_id = user_id
        self.obj_id = obj_id
        self._user = None
        self._obj = None

    def assert_model_class(self):
        if self.model_class is None:
            raise ConsumerConfigError(
                f"Consumer class '{self.__class__.__name__}' does not specify "
                f"a model_class. BaseActionConsumer sub-classes must specify a model_class"
            )

    @property
    def model_class_name(self):
        self.assert_model_class()
        return self.model_class.__name__

    @property
    def activity_name(self):
        return f"{self.model_class_name}.{self.action}"

    def get_user(self):
        if not self._user:
            try:
                self._user = User.objects.get(id=self.user_id)
            except User.DoesNotExist:
                logger.exception(
                    f"Consumer '{self.__class__.__name__}' attempted to "
                    f"retrieve a User with id '{self.user_id}', but it does not exist."
                )
        return self._user

    def get_object(self):
        self.assert_model_class()

        if not self._obj:
            try:
                self._obj = self.model_class.objects.get(id=self.obj_id)
            except self.model_class.DoesNotExist:
                logger.exception(
                    f"Consumer '{self.__class__.__name__}' attempted to "
                    f"to retrieve a '{self.model_class_name}' instance with id "
                    f"{obj_id}, but it does not exist."
                )
        return self._obj

    def get_meta(self):
        obj = self.get_object()

        try:
            return obj.activity_log_meta
        except AttributeError:
            logger.warning(
                f"{self.model_class_name} does not implement a 'activity_log_meta' property. "
                f"This means LeadActivityLog entries will have no metadata about this model."
            )
        return {}

    def get_lead(self):
        """This MUST be overriden on sub-classes."""
        raise NotImplementedError(
            f"The 'get_lead' method is not implemented on consumer '{self.__class__.__name__}'."
        )

    def get_timestamp(self):
        """Default timestamp to now for most items, but can be overriden in sub-class."""
        return timezone.now()

    def create_log(self):
        self.assert_model_class()

        return lead_models.LeadActivityLog.objects.create(
            lead=self.get_lead(),
            activity=self.activity_name,
            action_taken_by=self.get_user(),
            action_timestamp=self.get_timestamp(),
            meta=self.get_meta(),
        )


class LeadActionConsumer(BaseActionConsumer):
    model_class = lead_models.Lead

    def get_lead(self):
        obj = self.get_object()
        return obj


class NoteActionConsumer(BaseActionConsumer):
    model_class = lead_models.Note

    def get_lead(self):
        obj = self.get_object()
        return obj.created_for


class CallNoteActionConsumer(BaseActionConsumer):
    model_class = lead_models.CallNote

    def get_timestamp(self):
        obj = self.get_object()
        return (
            obj.call_date if self.action == lead_constants.CREATED else timezone.now()
        )

    def get_lead(self):
        obj = self.get_object()
        return obj.created_for


class FileActionConsumer(BaseActionConsumer):
    model_class = lead_models.File

    def get_lead(self):
        obj = self.get_object()
        return obj.created_for


class ReminderActionConsumer(BaseActionConsumer):
    model_class = lead_models.Reminder

    def get_meta(self):
        obj = self.get_object()

        try:
            rem_meta = obj.activity_log_meta
            rem_meta['datetime_for'] = obj.datetime_for.strftime(
                '%Y-%m-%dT%H:%M:%S.%fZ')
            return rem_meta
        except AttributeError:
            logger.warning(
                f"{self.model_class_name} does not implement a 'activity_log_meta' property. "
                f"This means LeadActivityLog entries will have no metadata about this model."
            )
        return {}

    def get_lead(self):
        obj = self.get_object()
        return obj.created_for


class ActionActionConsumer(BaseActionConsumer):
    model_class = lead_models.Action

    def get_lead(self):
        obj = self.get_object()
        return obj.lead


class LeadEmailActionConsumer(BaseActionConsumer):
    model_class = lead_models.LeadEmail

    def get_lead(self):
        obj = self.get_object()
        return obj.lead
