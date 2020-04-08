from rest_framework import permissions, exceptions
from rest_framework.permissions import SAFE_METHODS
from django.core.exceptions import ObjectDoesNotExist

from .models import (ACCOUNT_TYPE_MANAGER, STATE_ACTIVE)


class IsOrganizationManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or request.user.is_anonymous:
            raise exceptions.ValidationError('Authentication Required.')
        return user.type == ACCOUNT_TYPE_MANAGER and user.organization and user.state == STATE_ACTIVE


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_superuser
