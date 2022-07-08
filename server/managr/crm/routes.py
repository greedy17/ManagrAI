from managr.crm import constants as crm_consts
from managr.core import models as core_models
from managr.core import serializers as core_ser
from managr.hubspot import constants as hs_consts
from managr.hubspot.adapter import models as hubspot_adapters
from managr.salesforce import constants as sf_consts
from managr.salesforce.adapter import models as salesforce_adapters

USER_RESOURCE = "User"
OPPORTUNITY = "Opportunity"
ACCOUNT = "Account"
CONTACT = "Contact"
LEAD = "Lead"
PRODUCT = "Product"
PRICEBOOK = "Pricebook"
PRICEBOOKENTRY = "PriceBookEntry"
OPPORTUNITYLINEITEM = "OpportunityLineItem"


routes = {
    crm_consts.CRM_CHOICE_HUBSPOT: {
        OPPORTUNITY: hubspot_adapters.CompanyAdapter,
        ACCOUNT: hubspot_adapters.DealAdapter,
        CONTACT: hubspot_adapters.HubspotContactAdapter,
    },
    crm_consts.CRM_CHOICE_SALESFORCE: {
        ACCOUNT: salesforce_adapters.AccountAdapter,
        OPPORTUNITY: salesforce_adapters.OpportunityAdapter,
        CONTACT: salesforce_adapters.ContactAdapter,
        LEAD: salesforce_adapters.LeadAdapter,
        PRODUCT: salesforce_adapters.Product2Adapter,
        PRICEBOOK: salesforce_adapters.Pricebook2Adapter,
        PRICEBOOKENTRY: salesforce_adapters.PricebookEntryAdapter,
        OPPORTUNITYLINEITEM: salesforce_adapters.OpportunityLineItemAdapter,
        sf_consts.SALESFORCE_RESOURCE_TASK: salesforce_adapters.TaskAdapter,
    },
}
