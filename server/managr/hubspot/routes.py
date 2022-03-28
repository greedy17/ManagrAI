from managr.core import models as core_models
from managr.core import serializers as core_ser
from managr.hubspot import constants as hs_consts
from managr.hubspot import models as hs_models
from managr.hubspot import serializers as hs_ser

ACTION_CHOICE_RESOURCE = "ActionChoice"
USER_RESOURCE = "User"
routes = {
    hs_consts.RESOURCE_SYNC_COMPANY: {
        "model": hs_models.Company,
        "serializer": hs_ser.CompanySerializer,
    },
    hs_consts.RESOURCE_SYNC_DEAL: {"model": hs_models.Deal, "serializer": hs_ser.DealSerializer,},
    hs_consts.RESOURCE_SYNC_CONTACT: {
        "model": hs_models.HubspotContact,
        "serializer": hs_ser.HubspotContactSerializer,
    },
    USER_RESOURCE: {"model": core_models.User, "serializer": core_ser.UserSerializer,},
}
