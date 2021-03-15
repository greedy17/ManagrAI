from . import models as model_adapters
from managr.salesforce import constants as sf_consts

routes = {
    sf_consts.RESOURCE_SYNC_ACCOUNT: model_adapters.AccountAdapter,
    sf_consts.RESOURCE_SYNC_OPPORTUNITY: model_adapters.OpportunityAdapter,
    sf_consts.RESOURCE_SYNC_CONTACT: model_adapters.ContactAdapter,
    sf_consts.RESOURCE_SYNC_LEAD: model_adapters.LeadAdapter,
}

