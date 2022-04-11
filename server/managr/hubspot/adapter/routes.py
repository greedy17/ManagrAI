from . import models as model_adapters
from managr.hubspot import constants as hs_consts

routes = {
    hs_consts.RESOURCE_SYNC_COMPANY: model_adapters.CompanyAdapter,
    hs_consts.RESOURCE_SYNC_DEAL: model_adapters.DealAdapter,
    hs_consts.RESOURCE_SYNC_HUBSPOTCONTACT: model_adapters.HubspotContactAdapter,
}
