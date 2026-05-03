"""
Serializers for the marketplace (contractor profiles and portfolios).
"""

from __future__ import annotations

from rest_framework import serializers

from apps.users.serializers import PublicUserSerializer
from core.storage import generate_presigned_read_url

from .models import ContractorProfile, PortfolioImage, PortfolioProject


class PortfolioImageSerializer(serializers.ModelSerializer):
    """Serializes a portfolio image, providing a presigned URL when on S3."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioImage
        fields = ["id", "url", "caption", "order", "s3_key"]
        read_only_fields = ["id", "url"]

    def get_url(self, obj: PortfolioImage) -> str | None:
        if obj.s3_key:
            return generate_presigned_read_url(obj.s3_key)
        if obj.image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class PortfolioProjectSerializer(serializers.ModelSerializer):
    """Full serializer for a portfolio project (with images)."""

    images = PortfolioImageSerializer(many=True, read_only=True)

    class Meta:
        model = PortfolioProject
        fields = [
            "id",
            "title",
            "description",
            "category",
            "location",
            "completion_date",
            "project_cost",
            "is_featured",
            "images",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PortfolioProjectWriteSerializer(serializers.ModelSerializer):
    """Used for creating/updating portfolio projects."""

    class Meta:
        model = PortfolioProject
        fields = [
            "title",
            "description",
            "category",
            "location",
            "completion_date",
            "project_cost",
            "is_featured",
        ]


class ContractorProfileSerializer(serializers.ModelSerializer):
    """Full read serializer — used in contractor detail view."""

    user = PublicUserSerializer(read_only=True)
    portfolio_projects = PortfolioProjectSerializer(many=True, read_only=True)
    rating = serializers.DecimalField(source="user.rating", max_digits=3, decimal_places=2, read_only=True)
    reviews_count = serializers.IntegerField(source="user.reviews_count", read_only=True)

    class Meta:
        model = ContractorProfile
        fields = [
            "id",
            "user",
            "company_name",
            "category",
            "skills",
            "years_experience",
            "license_number",
            "hourly_rate",
            "daily_rate",
            "availability_status",
            "completed_projects",
            "is_verified",
            "rating",
            "reviews_count",
            "portfolio_projects",
            "created_at",
        ]
        read_only_fields = ["id", "is_verified", "completed_projects", "rating", "reviews_count"]


class ContractorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing contractors (avoids N+1 on portfolio)."""

    name = serializers.CharField(source="user.name", read_only=True)
    location = serializers.CharField(source="user.location", read_only=True)
    profile_image = serializers.ImageField(source="user.profile_image", read_only=True)
    rating = serializers.DecimalField(source="user.rating", max_digits=3, decimal_places=2, read_only=True)
    reviews_count = serializers.IntegerField(source="user.reviews_count", read_only=True)

    class Meta:
        model = ContractorProfile
        fields = [
            "id",
            "name",
            "location",
            "profile_image",
            "company_name",
            "category",
            "skills",
            "years_experience",
            "hourly_rate",
            "availability_status",
            "is_verified",
            "completed_projects",
            "rating",
            "reviews_count",
        ]


class ContractorProfileUpdateSerializer(serializers.ModelSerializer):
    """Allows a contractor to update their own profile."""

    class Meta:
        model = ContractorProfile
        fields = [
            "company_name",
            "category",
            "skills",
            "years_experience",
            "license_number",
            "insurance_info",
            "hourly_rate",
            "daily_rate",
            "availability_status",
        ]
