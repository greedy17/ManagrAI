from django.contrib import admin
from .models import Search

# Register your models here.


class CustomSearch(admin.ModelAdmin):
    list_display = ("user", "type", "input_text", "search_boolean")
    list_filter = ("user__organization",)
    ordering = ("-datetime_created",)


admin.site.register(Search, CustomSearch)
