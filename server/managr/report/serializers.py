from rest_framework import serializers
from .models import StoryReport


class StoryReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = StoryReport
        fields = (
            '__all__'
        )
