from django import forms
from django.contrib import admin
from . import models as models


# Register your models here.

admin.site.register(models.AlertConfig)
admin.site.register(models.AlertGroup)
admin.site.register(models.AlertMessageTemplate)
admin.site.register(models.AlertInstance)
admin.site.register(models.AlertOperand)
admin.site.register(models.AlertTemplate)
