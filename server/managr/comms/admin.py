from datetime import datetime
from django.contrib import admin
from django.db.models import Q
from .models import (
    Search,
    Pitch,
    NewsSource,
    Article,
    AssistAlert,
    WritingStyle,
    TwitterAccount,
    InstagramAccount,
    Discovery,
    Journalist,
    EmailTracker,
    JournalistContact,
    CompanyDetails,
)

# Register your models here.


def update_date_verified(modeladmin, request, queryset):
    now = datetime.now()
    queryset.update(date_verified=now)
    modeladmin.message_user(request, f"{queryset.count()} contacts were successfully updated.")


update_date_verified.short_description = "Update date verified"


def update_crawling(modeladmin, request, queryset):
    for instance in queryset:
        instance.crawling
    modeladmin.message_user(request, f"{queryset.count()} sources were updated")


update_crawling.short_description = "Update crawling"


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
        "is_crawling",
        "last_scraped",
        "article_link_attribute",
        "article_link_selector",
    )
    ordering = ("-last_scraped", "is_active")
    readonly_fields = ("access_count", "newest_article_date")
    search_fields = ["domain"]
    list_filter = ("is_active", "is_crawling")
    actions = [update_crawling]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            search_terms = search_term.split(",")
            query = Q()
            for term in search_terms:
                query |= Q(domain__icontains=term.strip())
            queryset = self.model.objects.filter(query)
        return queryset, use_distinct


class CustomArticle(admin.ModelAdmin):
    list_display = ("title", "publish_date", "source")
    list_filter = ("source",)
    ordering = ("-publish_date",)
    search_fields = ("title",)


class CustomAssistAlertAdmin(admin.ModelAdmin):
    list_display = ("user", "search", "run_at", "times_sent")
    ordering = ("run_at",)

    def times_sent(self, obj):
        ts = obj.meta_data["sent_count"] if "sent_count" in obj.meta_data.keys() else 0
        return ts

    times_sent.short_description = "Times Sent"


class CustomJournalAdmin(admin.ModelAdmin):
    list_display = ("datetime_created", "email", "outlet", "verified", "date_verified")
    ordering = ("datetime_created",)
    list_filter = ("outlet",)
    ordering = ("-datetime_created",)
    search_fields = ("email",)
    actions = [update_date_verified]


class CustomEmailTrackerAdmin(admin.ModelAdmin):
    list_display = ("datetime_created", "recipient", "user", "received")
    ordering = ("-datetime_created",)


class CustomJournalistContactAdmin(admin.ModelAdmin):
    list_display = ("datetime_created", "user", "journalist")
    ordering = ("-datetime_created",)
    list_filter = ("user",)
    search_fields = ["journalist__email", "journalist__first_name"]


class CustomCompanyDetail(admin.ModelAdmin):
    list_display = ("user", "title")
    list_filter = ("user__organization",)


admin.site.register(Search, CustomSearch)
admin.site.register(Pitch, CustomPitch)
admin.site.register(NewsSource, CustomNewsSource)
admin.site.register(Article, CustomArticle)
admin.site.register(AssistAlert, CustomAssistAlertAdmin)
admin.site.register(WritingStyle)
admin.site.register(TwitterAccount)
admin.site.register(InstagramAccount)
admin.site.register(Discovery)
admin.site.register(Journalist, CustomJournalAdmin)
admin.site.register(EmailTracker, CustomEmailTrackerAdmin)
admin.site.register(JournalistContact, CustomJournalistContactAdmin)
admin.site.register(CompanyDetails, CustomCompanyDetail)
