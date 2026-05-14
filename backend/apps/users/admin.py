"""Admin configuration for users app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model."""

    list_display = ["email", "name", "role", "is_active", "is_staff", "email_verified", "created_at"]
    list_filter = ["role", "is_active", "is_staff", "email_verified", "created_at"]
    search_fields = ["email", "name"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name", "profile_image", "bio", "phone", "location")}),
        ("Role & Rating", {"fields": ("role", "rating", "reviews_count")}),
        ("Status", {"fields": ("is_active", "is_staff", "is_superuser", "email_verified")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "role", "password1", "password2"),
        }),
    )
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin for PasswordResetToken."""

    list_display = ["user", "token", "created_at", "used"]
    list_filter = ["used", "created_at"]
    search_fields = ["user__email", "user__name"]
    readonly_fields = ["token", "created_at"]
    raw_id_fields = ["user"]