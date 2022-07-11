from django.contrib import admin
from managr.crm import models as crm_models

# Register your models here.
admin.site.register(crm_models.BaseAccount)
admin.site.register(crm_models.BaseOpportunity)
admin.site.register(crm_models.BaseContact)
