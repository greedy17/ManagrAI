from . import models as model_adapters
from managr.salesforce import constants as sf_consts

routes = {
    sf_consts.RESOURCE_SYNC_ACCOUNT: model_adapters.AccountAdapter,
    sf_consts.RESOURCE_SYNC_OPPORTUNITY: model_adapters.OpportunityAdapter,
    sf_consts.RESOURCE_SYNC_CONTACT: model_adapters.ContactAdapter,
    sf_consts.RESOURCE_SYNC_LEAD: model_adapters.LeadAdapter,
    sf_consts.RESOURCE_SYNC_PRODUCT2: model_adapters.Product2Adapter,
    sf_consts.RESOURCE_SYNC_PRICEBOOK2: model_adapters.Pricebook2Adapter,
    sf_consts.RESOURCE_SYNC_PRICEBOOKENTRY: model_adapters.PricebookEntryAdapter,
    sf_consts.RESOURCE_SYNC_OPPORTUNITYLINEITEM: model_adapters.OpportunityLineItemAdapter,
    sf_consts.SALESFORCE_RESOURCE_TASK: model_adapters.TaskAdapter,
}
