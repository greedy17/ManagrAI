from django.contrib import admin
from .models import Search, Pitch, NewsSource

# Register your models here.


class CustomSearch(admin.ModelAdmin):
    list_display = ("user", "type", "input_text", "search_boolean")
    list_filter = ("user__organization",)
    ordering = ("-datetime_created",)


class CustomPitch(admin.ModelAdmin):
    list_display = ("user", "name")
    list_filter = ("user__organization",)
    ordering = ("-datetime_created",)


class CustomNewsSource(admin.ModelAdmin):
    list_display = ("domain", "is_active", "last_scraped")
    ordering = ("-datetime_created",)
    readonly_fields = ("access_count",)


admin.site.register(Search, CustomSearch)
admin.site.register(Pitch, CustomPitch)
admin.site.register(NewsSource, CustomNewsSource)
