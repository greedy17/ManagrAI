from rest_framework import serializers
from .models import Search


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = ("id", "user", "name", "input_text", "search_boolean", "instructions", "type", "meta_data")