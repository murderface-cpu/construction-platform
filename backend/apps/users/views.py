"""
User authentication and profile views.
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.mixins import success_response
from core.storage import generate_presigned_upload_url

from . import services
from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetConfirmSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    UserProfileSerializer,
    PasswordResetRequestSerializer,  
    PasswordResetConfirmSerializer, 
)


class RegisterView(APIView):
    """POST /api/v1/auth/register — create a new user account."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Issue tokens immediately so the client is logged in after registration
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "success": True,
                "message": "Account created successfully.",
                "data": {
                    "user": UserProfileSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /api/v1/auth/login — obtain JWT access + refresh tokens."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """POST /api/v1/auth/logout — blacklist the refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"success": False, "error": {"code": "missing_token", "message": "Refresh token required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"success": False, "error": {"code": "invalid_token", "message": "Token is invalid or already expired."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return success_response(message="Logged out successfully.")


class ProfileView(APIView):
    """GET/PATCH /api/v1/auth/me — view or update the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer = UserProfileSerializer(request.user)
        return success_response(serializer.data)

    def patch(self, request: Request) -> Response:
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = services.update_profile(request.user, **serializer.validated_data)
        return success_response(
            UserProfileSerializer(user).data,
            message="Profile updated successfully.",
        )


class ChangePasswordView(APIView):
    """POST /api/v1/auth/change-password"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.change_password(
            request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
        )
        return success_response(message="Password changed successfully.")


class ProfileImageUploadURLView(APIView):
    """
    POST /api/v1/auth/profile-image-upload-url
    Returns a presigned S3 URL so the client can upload directly.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        filename = request.data.get("filename", "profile.jpg")
        content_type = request.data.get("content_type", "image/jpeg")
        result = generate_presigned_upload_url(
            folder=f"profile_images/{request.user.id}",
            filename=filename,
            content_type=content_type,
        )
        return success_response(result)
    
class PasswordResetRequestView(APIView):
    """POST /api/v1/auth/password/reset/ — request a reset email."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.request_password_reset(serializer.validated_data["email"])
        # Always return 200 regardless of whether email exists
        return success_response(message="If this email is registered, a reset link has been sent.")


class PasswordResetConfirmView(APIView):
    """POST /api/v1/auth/password/reset/confirm/ — set a new password using the token."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.confirm_password_reset(
            token=str(serializer.validated_data["token"]),
            new_password=serializer.validated_data["new_password"],
        )
        return success_response(message="Password reset successfully. You can now sign in.")
