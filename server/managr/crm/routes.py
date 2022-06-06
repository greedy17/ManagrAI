from managr.crm import constants as crm_consts
from managr.core import models as core_models
from managr.core import serializers as core_ser
from managr.hubspot import constants as hs_consts
from managr.hubspot.adapter import models as hubspot_adapters
from managr.salesforce import constants as sf_consts
from managr.salesforce.adapter import models as salesforce_adapters

USER_RESOURCE = "User"

routes = {
    crm_consts.CRM_CHOICE_HUBSPOT: {
        hs_consts.RESOURCE_SYNC_COMPANY: hubspot_adapters.CompanyAdapter,
        hs_consts.RESOURCE_SYNC_DEAL: hubspot_adapters.DealAdapter,
        hs_consts.RESOURCE_SYNC_HUBSPOTCONTACT: hubspot_adapters.HubspotContactAdapter,
    },
    crm_consts.CRM_CHOICE_SALESFORCE: {
        sf_consts.RESOURCE_SYNC_ACCOUNT: salesforce_adapters.AccountAdapter,
        sf_consts.RESOURCE_SYNC_OPPORTUNITY: salesforce_adapters.OpportunityAdapter,
        sf_consts.RESOURCE_SYNC_CONTACT: salesforce_adapters.ContactAdapter,
        sf_consts.RESOURCE_SYNC_LEAD: salesforce_adapters.LeadAdapter,
        sf_consts.RESOURCE_SYNC_PRODUCT2: salesforce_adapters.Product2Adapter,
        sf_consts.RESOURCE_SYNC_PRICEBOOK2: salesforce_adapters.Pricebook2Adapter,
        sf_consts.RESOURCE_SYNC_PRICEBOOKENTRY: salesforce_adapters.PricebookEntryAdapter,
        sf_consts.RESOURCE_SYNC_OPPORTUNITYLINEITEM: salesforce_adapters.OpportunityLineItemAdapter,
        sf_consts.SALESFORCE_RESOURCE_TASK: salesforce_adapters.TaskAdapter,
    },
    USER_RESOURCE: {"model": core_models.User, "serializer": core_ser.UserSerializer,},
}
