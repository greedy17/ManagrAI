from rest_framework import serializers

from .models import HubspotAuthAccount


class HubspotAuthAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = HubspotAuthAccount
        fields = (
            "id",
            "user",
            "access_token",
            "refresh_token",
            "hubspot_id",
        )
