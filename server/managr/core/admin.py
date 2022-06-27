import pytz
from django.contrib import admin
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.forms import ModelForm, Textarea
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm, UserChangeForm
from rest_framework.authtoken.models import Token

from managr.slack.models import UserSlackIntegration
from managr.zoom.models import ZoomAuthAccount
from managr.salesloft.models import SalesloftAccount
from managr.outreach.models import OutreachAccount
from .models import (
    User,
    NylasAuthAccount,
    MeetingPrepInstance,
    UserActivity,
    UserForecast,
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


class SalesloftAccountInline(admin.StackedInline):
    model = SalesloftAccount


class EmailAuthAccForm(forms.ModelForm):
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
            "event_calendar_id",
        )


def tz_as_choice_set():
    return list(map(lambda c: [c, c], pytz.all_timezones))


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        timezone = forms.ChoiceField(widget=forms.Select, choices=tz_as_choice_set())
        model = User
        fields = (
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
            "role",
            "timezone",
        )


class CustomUserChangeForm(UserChangeForm):
    timezone = forms.ChoiceField(widget=forms.Select, choices=tz_as_choice_set())

    class Meta:
        model = User
        fields = (
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
            "role",
            "timezone",
        )


class CustomUserForm(UserCreationForm):
    timezone = forms.ChoiceField(widget=forms.Select, choices=tz_as_choice_set())
    password = ReadOnlyPasswordHashField(
        label=("Password"),
        help_text=(
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            'using <a href="../password/">this form</a>.'
        ),
    )

    class Meta:
        model = User
        fields = (
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
            "role",
            "onboarding",
            "timezone",
        )


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

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
                    "role",
                    "timezone",
                    "reminders",
                    "crm",
                    "onboarding",
                    "activated_managr_configs",
                )
            },
        ),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2",),},),
    )

    inlines = (UserSlackIntegrationInline, ZoomAuthAccountInline, SalesloftAccountInline)
    list_display = ("email", "first_name", "last_name", "datetime_created")

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
    list_filter = ("organization",)

    ordering = ("-datetime_created",)


class CustomNylasAuthAccount(admin.ModelAdmin):
    form = EmailAuthAccForm


class CustomMeetingPrepInstance(admin.ModelAdmin):
    model = MeetingPrepInstance
    list_display = ("user", "event_data", "datetime_created")
    ordering = ("-datetime_created",)


class CustomUserActivity(admin.ModelAdmin):
    model = UserActivity
    list_display = ("user",)


class CustomUserForecast(admin.ModelAdmin):
    model = UserForecast
    list_display = ("user",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(NylasAuthAccount, CustomNylasAuthAccount)
admin.site.register(MeetingPrepInstance, CustomMeetingPrepInstance)
admin.site.register(UserActivity, CustomUserActivity)
admin.site.register(UserForecast, CustomUserActivity)


# admin.site.register(NotificationOption, CustomNotificationOption)
# admin.site.register(NotificationSelection, CustomNotificationSelection)
