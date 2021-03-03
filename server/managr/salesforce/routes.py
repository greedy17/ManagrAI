from managr.organization import models as org_models
from managr.opportunity import models as opp_models
from managr.organization import serializers as org_ser
from managr.opportunity import serializers as opp_ser
from managr.salesforce import constants as sf_consts

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
}
