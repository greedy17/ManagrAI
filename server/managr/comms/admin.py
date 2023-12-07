from django.contrib import admin
from .models import Search, Pitch, NewsSource, Article, EmailAlert, WritingStyle

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
    list_display = (
        "domain",
        "site_name",
        "is_active",
        "crawling_display",
        "last_scraped",
        "article_link_attribute",
        "article_link_selector",
    )
    ordering = ("-last_scraped", "is_active")
    readonly_fields = ("access_count",)
    search_fields = ("domain", "site_name")

    def crawling_display(self, obj):
        return obj.crawling

    crawling_display.boolean = True
    crawling_display.short_description = "Crawling"


class CustomArticle(admin.ModelAdmin):
    list_display = ("title", "publish_date", "source")
    list_filter = ("source",)
    ordering = ("-publish_date",)
    search_fields = ("title",)


class CustomEmailAlertAdmin(admin.ModelAdmin):
    list_display = ("user", "search", "run_at")
    ordering = ("run_at",)


admin.site.register(Search, CustomSearch)
admin.site.register(Pitch, CustomPitch)
admin.site.register(NewsSource, CustomNewsSource)
admin.site.register(Article, CustomArticle)
admin.site.register(EmailAlert, CustomEmailAlertAdmin)
admin.site.register(WritingStyle)
