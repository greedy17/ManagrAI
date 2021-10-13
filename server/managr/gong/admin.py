from django.contrib import admin
from . import models as models

admin.site.register(models.GongAuthAccount)
admin.site.register(models.GongAccount)
admin.site.register(models.GongCall)
