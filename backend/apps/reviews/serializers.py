"""Reviews serializers."""

from rest_framework import serializers
from apps.users.serializers import PublicUserSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = PublicUserSerializer(read_only=True)
    contractor = PublicUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "reviewer", "contractor", "rating", "comment", "booking", "created_at"]
        read_only_fields = ["id", "reviewer", "contractor", "created_at"]


class CreateReviewSerializer(serializers.Serializer):
    contractor_id = serializers.UUIDField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True)
    booking_id = serializers.UUIDField(required=False)
