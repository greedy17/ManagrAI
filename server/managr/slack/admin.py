from django.contrib import admin
from django.urls import resolve
from django.forms.models import ModelChoiceField
from . import models as slack_models
from . import constants as slack_consts
from managr.salesforce import models as sf_models
from managr.crm import models as crm_models
from managr.hubspot.models import HObjectField
from django.db.models import Q
from managr.core.models import User


class CustomFormFieldInline(admin.StackedInline):
    def get_parent_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.kwargs:
            return slack_models.OrgCustomSlackForm.objects.get(pk=resolved.kwargs["object_id"])
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent = self.get_parent_object_from_request(request)
        if parent:
            if db_field.name == "field":
                queryset = crm_models.ObjectField.objects.filter(
                    (
                        Q(user__organization=parent.organization)
                        & Q(crm_object=parent.resource)
                        & Q(user__team_lead_of=parent.team)
                    )
                    | Q(is_public=True)
                ).order_by("label")
                return ModelChoiceField(queryset)
        else:
            queryset = crm_models.ObjectField.objects.all()
            return ModelChoiceField(queryset)
        return super(CustomFormField, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = slack_models.CustomFormField
    fields = (
        "field",
        "order",
    )
    extra = 0


class CustomFormFieldAdmin(admin.ModelAdmin):
    model = slack_models.FormField
    list_display = ("form", "order")
    ordering = ("-datetime_created",)


class CustomFormField(admin.ModelAdmin):
    model = slack_models.CustomFormField
    list_display = ("form", "order")
    ordering = ("-datetime_created",)


class CustomOrgSlackForms(admin.ModelAdmin):
    model = slack_models.OrgCustomSlackForm
    inlines = (CustomFormFieldInline,)
    list_display = (
        "form_type",
        "resource",
        "team",
    )
    list_filter = ("organization",)


class CustomOrgSlackFormsInstance(admin.ModelAdmin):
    model = slack_models.OrgCustomSlackFormInstance
    list_filter = ("user", "user__organization", "template__form_type", "update_source")
    list_display = ("template", "user", "submission_date", "update_source")
    ordering = ("-datetime_created",)
    exclude = []
    readonly_fields = [
        "user",
        "template",
        "saved_data",
        "previous_data",
        "alert_instance_id",
        "recap_data",
        "chat_submission",
    ]


# admin.site.register(slack_models.OrgCustomSlackForm, CustomOrgSlackForms)
# admin.site.register(slack_models.OrgCustomSlackFormInstance, CustomOrgSlackFormsInstance)
admin.site.register(slack_models.OrganizationSlackIntegration)
admin.site.register(slack_models.UserSlackIntegration)
# admin.site.register(slack_models.FormField, CustomFormFieldAdmin)
# admin.site.register(slack_models.CustomFormField, CustomFormField)
