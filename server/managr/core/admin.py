from django.contrib import admin
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.forms import ModelForm, Textarea
from .models import User, EmailAuthAccount, EmailTemplate


class EmailAuthAccForm(forms.ModelForm):
    linked_at = forms.IntegerField()

    class Meta:
        model = EmailAuthAccount
        fields = ("access_token", "account_id", "email_address",
                  "provider", "sync_state", "name", "user", "linked_at",)


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
                    "is_active",
                    "is_invited",
                    "quota",
                    "commit",
                    "upside",
                    "magic_token_expiration",
                    "is_serviceaccount",
                    "is_superuser",
                    "is_staff",
                    "organization",
                )
            },
        ),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": (
            "email", "password1", "password2",), }),
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


class CustomEmailAuthAccount(admin.ModelAdmin):
    form = EmailAuthAccForm


admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailAuthAccount, CustomEmailAuthAccount)
admin.site.register(EmailTemplate)
