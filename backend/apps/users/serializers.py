"""
Serializers for user registration, login, and profile management.
"""

from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Validate and create a new user account."""

    password = serializers.CharField(
        write_only=True, min_length=8, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "password",
            "password_confirm",
            "role",
            "location",
            "phone",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data: dict) -> User:
        return User.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extend the default JWT payload to include role and name so the
    frontend can skip an extra /me call after login.
    """

    @classmethod
    def get_token(cls, user: User):  # type: ignore[override]
        token = super().get_token(user)
        token["role"] = user.role
        token["name"] = user.name
        token["email"] = user.email
        return token

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        data["user"] = UserProfileSerializer(self.user).data
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Read serializer for the authenticated user's profile."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "role",
            "location",
            "profile_image",
            "bio",
            "phone",
            "rating",
            "reviews_count",
            "email_verified",
            "created_at",
        ]
        read_only_fields = ["id", "email", "rating", "reviews_count", "created_at"]


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Allows a user to update their own profile (excludes sensitive fields)."""

    class Meta:
        model = User
        fields = ["name", "location", "bio", "phone", "profile_image"]


class ChangePasswordSerializer(serializers.Serializer):
    """Validates a password change request."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs: dict) -> dict:
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        return attrs


class PublicUserSerializer(serializers.ModelSerializer):
    """Minimal read-only view of a user for embedding in other resources."""

    class Meta:
        model = User
        fields = ["id", "name", "profile_image", "rating", "role", "location"]
        read_only_fields = fields

class PasswordResetRequestSerializer(serializers.Serializer):
    """Validates the forgot-password request (step 1)."""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Validates the token + new password (step 2)."""
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs: dict) -> dict:
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )
        return attrs
