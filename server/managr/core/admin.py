from django.contrib import admin
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.forms import ModelForm, Textarea

from managr.slack.models import UserSlackIntegration
from managr.zoom.models import ZoomAuthAccount
from .models import (
    User,
    NylasAuthAccount,
    #    NotificationOption,
    #    NotificationSelection,
)

from . import constants as core_consts

TRUE_FALSE_CHOICES = (
    ("True", "ON",),
    ("False", "OFF"),
)


class UserSlackIntegrationInline(admin.StackedInline):
    model = UserSlackIntegration


class ZoomAuthAccountInline(admin.StackedInline):
    model = ZoomAuthAccount


class EmailAuthAccForm(forms.ModelForm):
    linked_at = forms.IntegerField()

    class Meta:
        model = NylasAuthAccount
        fields = (
            "access_token",
            "account_id",
            "email_address",
            "provider",
            "sync_state",
            "name",
            "user",
        )


class CustomUserAdmin(UserAdmin):
    model = User

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "password",
                    "last_login",
                    "first_name",
                    "last_name",
                    "email",
                    "profile_photo",
                    "is_active",
                    "is_invited",
                    "is_admin",
                    "is_superuser",
                    "is_staff",
                    "organization",
                    "user_level",
                )
            },
        ),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2",),},),
    )
    inlines = (
        UserSlackIntegrationInline,
        ZoomAuthAccountInline,
    )
    list_display = ("email", "first_name", "last_name")

    list_display_links = (
        "email",
        "first_name",
        "last_name",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    ordering = []


class CustomNylasAuthAccount(admin.ModelAdmin):
    form = EmailAuthAccForm


""" 
class CustomNotificationOptionForm(forms.ModelForm):
    default_value = forms.ChoiceField(
        widget=forms.RadioSelect, choices=TRUE_FALSE_CHOICES
    )
    user_groups = forms.MultipleChoiceField(
        choices=core_consts.ACCOUNT_TYPES, widget=forms.SelectMultiple
    )

    class Meta:
        model = NotificationOption
        fields = (
            "title",
            "description",
            "default_value",
            "user_groups",
            "notification_type",
        )


class CustomNotificationSelectionForm(forms.ModelForm):
    value = forms.ChoiceField(widget=forms.RadioSelect, choices=TRUE_FALSE_CHOICES)

    class Meta:
        model = NotificationSelection
        fields = (
            "option",
            "user",
            "value",
        )


class CustomNotificationSelection(admin.ModelAdmin):
    form = CustomNotificationSelectionForm


class CustomNotificationOption(admin.ModelAdmin):
    form = CustomNotificationOptionForm
 """

admin.site.register(User, CustomUserAdmin)
admin.site.register(NylasAuthAccount, CustomNylasAuthAccount)
# admin.site.register(NotificationOption, CustomNotificationOption)
# admin.site.register(NotificationSelection, CustomNotificationSelection)
