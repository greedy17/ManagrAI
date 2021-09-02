from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import SalesloftAuthAccount


class SalesloftAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesloftAuthAccount
        fields = (
            "id",
            "organization",
            "access_token",
            "refresh_token",
            "admin",
        )
