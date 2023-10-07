from rest_framework import serializers
from .models import Search, Pitch, NewsSource, Article


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
        fields = ("domain", "last_scraped", "is_active")


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
        )
