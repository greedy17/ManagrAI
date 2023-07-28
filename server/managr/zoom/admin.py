from django.contrib import admin
from . import models

# Register your models here.
class CustomZoomAuthAccount(admin.ModelAdmin):
    model = models.ZoomAuthAccount

    list_display = (
        "user",
        "zoom_id",
    )


admin.site.register(models.ZoomAuthAccount, CustomZoomAuthAccount)
