"""Admin configuration for reviews app."""

from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for Review."""

    list_display = ["id", "reviewer", "contractor", "rating", "booking", "created_at"]
    list_filter = ["rating", "created_at"]
    search_fields = ["reviewer__email", "reviewer__name", "contractor__email", "contractor__name", "comment"]
    raw_id_fields = ["reviewer", "contractor", "booking"]
    readonly_fields = ["created_at", "updated_at"]