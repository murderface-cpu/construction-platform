"""Designs serializers."""

from rest_framework import serializers
from core.storage import generate_presigned_read_url
from .models import DesignImage, DesignTemplate, SavedDesign


class DesignImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = DesignImage
        fields = ["id", "url", "caption", "order", "s3_key"]
        read_only_fields = ["id", "url"]

    def get_url(self, obj: DesignImage) -> str | None:
        return generate_presigned_read_url(obj.s3_key)


class DesignListSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()
    saved_count = serializers.IntegerField(source="saves.count", read_only=True)

    class Meta:
        model = DesignTemplate
        fields = [
            "id", "title", "category", "style_tags",
            "cover_url", "view_count", "saved_count", "created_at",
        ]

    def get_cover_url(self, obj: DesignTemplate) -> str | None:
        return generate_presigned_read_url(obj.cover_image_key)


class DesignDetailSerializer(serializers.ModelSerializer):
    images = DesignImageSerializer(many=True, read_only=True)
    cover_url = serializers.SerializerMethodField()
    saved_count = serializers.IntegerField(source="saves.count", read_only=True)

    class Meta:
        model = DesignTemplate
        fields = [
            "id", "title", "description", "category", "style_tags",
            "cover_url", "images", "view_count", "saved_count", "created_at",
        ]

    def get_cover_url(self, obj: DesignTemplate) -> str | None:
        return generate_presigned_read_url(obj.cover_image_key)
