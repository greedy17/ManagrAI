from rest_framework import permissions, exceptions
from rest_framework.permissions import SAFE_METHODS
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError, PermissionDenied
from managr.lead.models import Lead, List
from managr.zoom.zoom_helper import constants as zoom_helper_consts
from managr.organization.models import Organization, Stage
from managr.core import constants as core_consts
from .models import ACCOUNT_TYPE_MANAGER, STATE_ACTIVE


class IsZoomEvent(permissions.BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get("Authorization", None)
        return token == zoom_helper_consts.ZOOM_WEBHOOK_TOKEN


class IsOrganizationManager(permissions.BasePermission):
    """ Organization has salespeople who are managers or limited """

    """ Managers can invite new users and update account info """

    def has_permission(self, request, view):
        user = request.user
        if not user or request.user.is_anonymous:
            raise exceptions.ValidationError("Authentication Required.")
        if (
            user.type == core_consts.ACCOUNT_TYPE_MANAGER
            and user.organization
            and user.is_active
        ):
            return True
        else:
            return False


class IsExternalIntegrationAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or request.user.is_anonymous:
            raise exceptions.ValidationError("Authentication Required.")
        if request.method in permissions.SAFE_METHODS and user.is_serviceaccount:
            return True
        return False


class IsSalesPerson(permissions.BasePermission):
    def has_permission(self, request, view):

        user = request.user
        if not user or request.user.is_anonymous:
            raise exceptions.ValidationError("Authentication Required.")

        return user.organization and user.is_active


def lead_permissions(self, request, view, obj):
    # currently checking organization.accounts.all() but have changed this to use a quersyset on a seperate branch
    if not request.user.organization.accounts.filter(pk=obj.account_id).exists():
        # check to make sure user is part of org and account is in org
        raise PermissionDenied()
    if view.action == "un_claim":
        if obj.is_claimed and obj.claimed_by == request.user:
            return True
        elif obj.is_claimed and obj.claimed_by != request.user:
            raise PermissionDenied(
                {"detail": "Cannot un claim a Lead that is not claimed By You"}
            )
        else:
            raise PermissionDenied({"detail": "lead is not claimed"})

    elif view.action == "claim":
        if not obj.is_claimed:
            return True
        raise PermissionDenied(
            {"detail": "Leads can only be claimed if they were previously unclaimed"}
        )
    else:
        return request.user == obj.claimed_by


def list_permissions(self, request, view, obj):
    # permissions for LeadsLists
    if obj.created_by.organization_id != request.user.organization_id:
        return False
    else:
        if obj.created_by != request.user:
            return False
        else:
            return True


def org_permissions(self, request, view, obj):
    return IsOrganizationManager()


class CanEditResourceOrReadOnly(permissions.BasePermission):
    """
        Most resources allow read access to all but write access to only an owner
        Leads can be edited by their current claimed_by user we will also create custom methods
        within the endpoints to allow overriding of this base permission however in general this rule
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            """ All users are allowed to perform safe methods GET, OPTIONS"""
            return True
        elif (
            request.user.is_superuser
            or request.user.type == "MANAGER"
            or request.user.type == "INTEGRATION"
        ):
            return True
        elif isinstance(obj, Lead):
            """ if obj is Lead check claimed_by unless it is being claimed or unclaimed"""
            return lead_permissions(self, request, view, obj)
        elif isinstance(obj, List):
            return list_permissions(self, request, view, obj)
        elif isinstance(obj, Organization):
            return org_permissions(self, request, view, obj)
        elif isinstance(obj, Stage):
            return org_permissions(self, request, view, obj)
        else:
            return False


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_superuser


class SuperUserCreateOnly(permissions.BasePermission):
    """ only super_user can create organization
        OrgMangers can edit org
        all else can view own org
    """

    def has_permission(self, request, view):
        if view.action == "create":
            return request.user.is_superuser
        else:
            return True
