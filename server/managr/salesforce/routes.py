from managr.organization import models as org_models
from managr.opportunity import models as opp_models
from managr.core import models as core_models
from managr.core import serializers as core_ser
from managr.organization import serializers as org_ser
from managr.opportunity import serializers as opp_ser
from managr.salesforce import constants as sf_consts

ACTION_CHOICE_RESOURCE = "ActionChoice"
USER_RESOURCE = "User"
routes = {
    sf_consts.RESOURCE_SYNC_ACCOUNT: {
        "model": org_models.Account,
        "serializer": org_ser.AccountSerializer,
    },
    sf_consts.RESOURCE_SYNC_OPPORTUNITY: {
        "model": opp_models.Opportunity,
        "serializer": opp_ser.OpportunitySerializer,
    },
    sf_consts.RESOURCE_SYNC_CONTACT: {
        "model": org_models.Contact,
        "serializer": org_ser.ContactSerializer,
    },
    sf_consts.RESOURCE_SYNC_LEAD: {"model": opp_models.Lead, "serializer": opp_ser.LeadSerializer,},
    ACTION_CHOICE_RESOURCE: {
        "model": org_models.ActionChoice,
        "serializer": org_ser.ActionChoiceSerializer,
    },
    sf_consts.RESOURCE_SYNC_PRICEBOOK2: {
        "model": org_models.Pricebook2,
        "serializer": org_ser.Pricebook2Serializer,
    },
    sf_consts.RESOURCE_SYNC_PRODUCT2: {
        "model": org_models.Product2,
        "serializer": org_ser.Product2Serializer,
    },
    sf_consts.RESOURCE_SYNC_PRICEBOOKENTRY: {
        "model": org_models.PricebookEntry,
        "serializer": org_ser.PricebookEntrySerializer,
    },
    USER_RESOURCE: {"model": core_models.User, "serializer": core_ser.UserSerializer,},
}
