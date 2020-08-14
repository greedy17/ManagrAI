from django.contrib import admin
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.admin import UserAdmin

from .models import User, EmailAuthAccount, EmailTemplate, MessageAuthAccount


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


admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailAuthAccount)
admin.site.register(EmailTemplate)
admin.site.register(MessageAuthAccount)
