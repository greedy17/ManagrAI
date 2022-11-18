from managr.salesforce.routes import routes as sf_routes
from managr.hubspot.routes import routes as hs_routes


CRM_SWITCHER = {"SALESFORCE": sf_routes, "HUBSPOT": hs_routes}
