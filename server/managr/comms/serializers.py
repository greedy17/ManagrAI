from rest_framework import serializers
from .models import Search

class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = ("user", "name", "input_text", "search_boolean", "instructions")