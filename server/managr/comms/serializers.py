from rest_framework import serializers
from .models import Search, Pitch, NewsSource, Article, WritingStyle, EmailAlert
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


class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAlert
        fields = ("title", "text", "user")
