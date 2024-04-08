from rest_framework import serializers
from .models import (
    Search,
    Pitch,
    NewsSource,
    Article,
    WritingStyle,
    EmailAlert,
    Process,
    TwitterAccount,
    Discovery,
)
from django.contrib.postgres.search import SearchVector


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = (
            "id",
            "user",
            "name",
            "input_text",
            "search_boolean",
            "instructions",
            "type",
            "meta_data",
        )


class PitchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pitch
        fields = (
            "id",
            "user",
            "name",
            "instructions",
            "type",
            "audience",
            "content",
            "generated_pitch",
        )


class NewsSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsSource
        fields = ("domain", "last_scraped", "is_active", "access_count")


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "description",
            "author",
            "publish_date",
            "content",
            "source",
            "link",
            "image_url",
            "content_search_vector",
        )

    def create(self, validated_data):
        article = Article.objects.create(**validated_data)
        article.content_search_vector = SearchVector("content")
        article.save()
        return article


class WritingStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingStyle
        fields = ("id", "style", "user", "title")


class EmailAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAlert
        fields = ("id", "user", "title", "search", "run_at", "meta_data")


class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = (
            "id",
            "user",
            "name",
            "search_id",
            "type",
            "details",
            "style",
            "generated_content",
        )


class TwitterAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitterAccount
        fields = ("id", "user", "access_token", "access_token_secret")


class DiscoverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Discovery
        fields = (
            "id",
            "user",
            "name",
            "content",
            "type",
            "beat",
            "location",
            "list",
        )        
