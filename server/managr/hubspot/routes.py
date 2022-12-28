from managr.core import models as core_models
from managr.core import serializers as core_ser
from managr.hubspot import constants as hs_consts
from managr.hubspot import models as hs_models
from managr.crm import models as crm_models
from managr.hubspot import serializers as hs_ser
from managr.crm import serializers as crm_ser

ACTION_CHOICE_RESOURCE = "ActionChoice"
USER_RESOURCE = "User"
routes = {
    hs_consts.RESOURCE_SYNC_COMPANY: {
        "model": crm_models.BaseAccount,
        "serializer": crm_ser.BaseAccountSerializer,
    },
    hs_consts.RESOURCE_SYNC_DEAL: {
        "model": crm_models.BaseOpportunity,
        "serializer": crm_ser.BaseOpportunitySerializer,
    },
    hs_consts.RESOURCE_SYNC_CONTACT: {
        "model": crm_models.BaseContact,
        "serializer": crm_ser.BaseContactSerializer,
    },
    USER_RESOURCE: {"model": core_models.User, "serializer": core_ser.UserSerializer,},
}
