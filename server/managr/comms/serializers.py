from rest_framework import serializers
from .models import (
    Search,
    Pitch,
    NewsSource,
    Article,
    WritingStyle,
    AssistAlert,
    Process,
    TwitterAccount,
    InstagramAccount,
    Discovery,
    Journalist,
    EmailTracker,
    JournalistContact,
    CompanyDetails,
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


class AssistAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistAlert
        fields = ("id", "user", "type", "title", "search", "run_at", "meta_data", "recipients")


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


class InstagramAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramAccount
        fields = ("id", "user", "access_token", "hashtag_list")


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
            "results",
        )


class JournalistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journalist
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "outlet",
            "verified",
            "date_verified",
            "accuracy_score",
            "number_of_sources",
        )


class EmailTrackerSerializer(serializers.ModelSerializer):
    journalist_ref = serializers.SerializerMethodField("get_journalist_ref")

    class Meta:
        model = EmailTracker
        fields = (
            "id",
            "user",
            "recipient",
            "name",
            "subject",
            "body",
            "cc_recipients",
            "bcc_recipients",
            "message_id",
            "opens",
            "replies",
            "clicks",
            "activity_log",
            "received",
            "failed",
            "is_approved",
            "is_rejected",
            "is_draft",
            "journalist_ref",
        )

    def get_journalist_ref(self, instance):
        journalist_check = Journalist.objects.filter(email=instance.recipient).first()
        if journalist_check:
            return journalist_check.as_object()
        return None


class JournalistContactSerializer(serializers.ModelSerializer):
    journalist_ref = JournalistSerializer(source="journalist", read_only=True)

    def update(self, instance, validated_data):
        if "notes" in validated_data.keys():
            current_notes = instance.notes
            new_notes = current_notes + validated_data["notes"]
            validated_data["notes"] = new_notes
        return super().update(instance, validated_data)

    class Meta:
        model = JournalistContact
        fields = (
            "id",
            "user",
            "journalist",
            "journalist_ref",
            "tags",
            "bio",
            "images",
            "notes",
            "email",
            "outlet",
        )


class CompanyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetails
        fields = ("id", "details", "user", "title")
