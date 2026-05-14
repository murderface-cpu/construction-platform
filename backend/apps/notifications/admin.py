"""Admin configuration for notifications app."""

from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification."""

    list_display = ["recipient", "notification_type", "title", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read", "created_at"]
    search_fields = ["recipient__email", "recipient__name", "title", "message"]
    raw_id_fields = ["recipient"]
    readonly_fields = ["created_at", "updated_at"]