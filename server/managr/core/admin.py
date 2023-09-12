import pytz
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm, UserChangeForm
from managr.slack.models import UserSlackIntegration
from managr.zoom.models import ZoomAuthAccount
from managr.salesloft.models import SalesloftAccount
from .models import User, NylasAuthAccount, UserActivity, NoteTemplate, Report

TRUE_FALSE_CHOICES = (
    (
        "True",
        "ON",
    ),
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
                    "last_login",
                    "first_name",
                    "last_name",
                    "email",
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
                    "team",
                    "make_team_lead",
                    "meta_data",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    list_display = ("email", "first_name", "last_name", "datetime_created")

    list_display_links = (
        "email",
        "first_name",
        "last_name",
    )
    readonly_fields = ["meta_data"]

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )
    list_filter = ("organization",)

    ordering = ("-datetime_created",)


class CustomNylasAuthAccount(admin.ModelAdmin):
    form = EmailAuthAccForm


class CustomUserActivity(admin.ModelAdmin):
    model = UserActivity
    list_display = ("user",)


class CustomNoteTemplate(admin.ModelAdmin):
    model = NoteTemplate
    list_display = ("subject", "user")
    ordering = ("-datetime_created",)
    list_filter = ("user",)


class CustomReportAdmin(admin.ModelAdmin):
    model = Report
    list_display = ("title", "user")
    ordering = ("-datetime_created",)
    list_filter = ("user__organization",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(NylasAuthAccount, CustomNylasAuthAccount)
admin.site.register(NoteTemplate, CustomNoteTemplate)
admin.site.register(Report, CustomReportAdmin)
