from django.contrib import admin
from . import models
from django.forms import ModelForm, Textarea

# Register your models here.
class CustomZoomAuthAccount(admin.ModelAdmin):
    model = models.ZoomAuthAccount

    list_display = (
        "user",
        "zoom_id",
    )


admin.site.register(models.ZoomAuthAccount, CustomZoomAuthAccount)
