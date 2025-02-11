from datetime import datetime
from django.utils.timesince import timesince
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
    Thread,
    ArchivedArticle,
)

# Register your models here.


class CustomActiveNotCrawlingFilter(admin.SimpleListFilter):
    title = "New Sources"
    parameter_name = "active_not_crawling"

    def lookups(self, request, model_admin):
        return (("yes", "New Sources"),)

    def queryset(self, request, queryset):
        if self.value() == "yes":
            # Filter by is_active=True, is_crawling=False and order by datetime_created desc
            return queryset.filter(is_active=True, is_crawling=False).order_by("-datetime_created")
        return queryset


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


def update_active_status(modeladmin, request, queryset):
    for instance in queryset:
        instance.is_active = not instance.is_active
        instance.save()
    modeladmin.message_user(request, f"{queryset.count()} sources were updated")


update_active_status.short_description = "Update active status"


def update_stopped(modeladmin, request, queryset):
    for instance in queryset:
        instance.check_if_stopped()
    modeladmin.message_user(request, f"{queryset.count()} sources were updated")


update_stopped.short_description = "Update stopped status"


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
        "is_active",
        "is_crawling",
        "is_stopped",
        "get_last_scraped",
        "art_link_attrs",
    )
    ordering = ("-last_scraped",)
    readonly_fields = ("access_count", "newest_article_date")
    search_fields = ["domain"]
    list_filter = (
        "is_active",
        "is_crawling",
        "is_stopped",
        "use_scrape_api",
        CustomActiveNotCrawlingFilter,
    )
    actions = [update_crawling, update_active_status, update_stopped]

    def get_last_scraped(self, obj):
        return timesince(obj.last_scraped)

    get_last_scraped.short_description = "Last Scrape"

    def art_link_attrs(self, obj):
        if obj.article_link_attribute:
            return "({}) {}".format(obj.article_link_attribute, obj.article_link_selector)
        return "-"

    art_link_attrs.short_description = "Link Attr/Sel"

    def get_ordering(self, request):
        """
        Handles dynamic ordering from the `o` parameter in the request,
        which supports multiple fields for ordering.
        """
        if request.GET.get("new_sources"):
            return ["is_active", "-datetime_created"]
        ordering_param = request.GET.get("o")
        if ordering_param:
            order_fields = ordering_param.split(".")
            ordering = []
            for order_field in order_fields:
                try:
                    ordering_index = int(order_field.lstrip("-")) - 1
                    ordering_field = self.list_display[ordering_index]
                    if order_field.startswith("-"):
                        ordering.append(f"-{ordering_field}")
                    else:
                        ordering.append(ordering_field)
                except (IndexError, ValueError):
                    pass
            if ordering:
                return ordering
        else:
            return self.ordering
        return super().get_ordering(request)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["search_help_text"] = "Search by domain"
        extra_context["new_sources"] = bool(request.GET.get("new_sources"))
        return super().changelist_view(request, extra_context=extra_context)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term and not request.GET.get("new_sources"):
            search_terms = search_term.split(",")
            query = Q()
            for term in search_terms:
                query |= Q(domain__icontains=term.strip())
            queryset = self.model.objects.filter(query)
            for param, value in request.GET.items():
                if param.endswith("__exact") and value in ["0", "1"]:
                    boolean_value = value == "1"
                    queryset = queryset.filter(**{param: boolean_value})
        ordering = self.get_ordering(request)
        if ordering:
            queryset = queryset.order_by(*ordering)
        return queryset, use_distinct


class CustomArticle(admin.ModelAdmin):
    list_display = ("title", "publish_date", "source")
    list_filter = ("source",)
    ordering = ("-publish_date",)
    search_fields = ("title", "link")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["search_help_text"] = "Search by title or url"
        return super().changelist_view(request, extra_context=extra_context)


class CustomArchivedArticle(admin.ModelAdmin):
    list_display = ("title", "publish_date", "source", "archived_on")
    list_filter = ("source",)
    ordering = ("-publish_date",)
    search_fields = ("title", "link")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["search_help_text"] = "Search by title or url"
        return super().changelist_view(request, extra_context=extra_context)


class CustomAssistAlertAdmin(admin.ModelAdmin):
    list_display = ("user", "search", "run_at", "times_sent", "last_sent")
    ordering = ("run_at",)
    list_filter = ("type", "search__type")
    search_fields = ["user__email"]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["search_help_text"] = "Search by user email"
        return super().changelist_view(request, extra_context=extra_context)

    def times_sent(self, obj):
        ts = obj.meta_data["sent_count"] if "sent_count" in obj.meta_data.keys() else 0
        return ts

    def last_sent(self, obj):
        ls = obj.meta_data["last_sent"] if "last_sent" in obj.meta_data.keys() else "N/A"
        return ls

    times_sent.short_description = "Times Sent"
    last_sent.short_description = "Last Sent"


class CustomJournalAdmin(admin.ModelAdmin):
    list_display = ("datetime_created", "email", "outlet", "verified", "date_verified")
    ordering = ("datetime_created",)
    list_filter = ("needs_review", "outlet")
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


class CustomThread(admin.ModelAdmin):
    list_display = ("user", "title", "thread_type", "follow_ups")
    list_filter = (
        "search__type",
        "user__organization",
    )
    search_fields = ["user__email", "title"]

    def thread_type(self, obj):
        return obj.search.type.title()

    def follow_ups(self, obj):
        meta_data = obj.meta_data
        followups = meta_data.get("followUps")
        return len(followups)

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context["search_help_text"] = "Search by title or user email"
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Search, CustomSearch)
admin.site.register(Pitch, CustomPitch)
admin.site.register(NewsSource, CustomNewsSource)
admin.site.register(Article, CustomArticle)
admin.site.register(ArchivedArticle, CustomArchivedArticle)
admin.site.register(AssistAlert, CustomAssistAlertAdmin)
admin.site.register(WritingStyle)
admin.site.register(TwitterAccount)
admin.site.register(InstagramAccount)
admin.site.register(Discovery)
admin.site.register(Journalist, CustomJournalAdmin)
admin.site.register(EmailTracker, CustomEmailTrackerAdmin)
admin.site.register(JournalistContact, CustomJournalistContactAdmin)
admin.site.register(CompanyDetails, CustomCompanyDetail)
admin.site.register(Thread, CustomThread)
