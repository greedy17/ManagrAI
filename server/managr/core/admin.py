from django.contrib import admin
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    model = User

    fieldsets = (
        (None, {'fields': (
            'password',
            'last_login',
            'first_name',
            'last_name',
            'email',
        )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'organization',),
        }),
    )

    list_display = (
        'email',
        'first_name',
        'last_name'
    )

    list_display_links = (
        'email',
        'first_name',
        'last_name',
    )

    search_fields = (
        'email',
        'first_name',
        'last_name',
    )

    ordering = []


admin.site.register(User, CustomUserAdmin)
