"""Admin configuration for designs app."""

from django.contrib import admin
from .models import DesignTemplate, DesignImage, SavedDesign


class DesignImageInline(admin.TabularInline):
    """Inline for DesignImage."""

    model = DesignImage
    extra = 1
    fields = ["s3_key", "caption", "order"]


@admin.register(DesignTemplate)
class DesignTemplateAdmin(admin.ModelAdmin):
    """Admin for DesignTemplate."""

    list_display = ["title", "category", "is_published", "view_count", "uploaded_by", "created_at"]
    list_filter = ["category", "is_published", "created_at"]
    search_fields = ["title", "description"]
    raw_id_fields = ["uploaded_by"]
    inlines = [DesignImageInline]
    readonly_fields = ["view_count", "created_at", "updated_at"]


@admin.register(DesignImage)
class DesignImageAdmin(admin.ModelAdmin):
    """Admin for DesignImage."""

    list_display = ["id", "design", "caption", "order", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["caption", "s3_key", "design__title"]
    raw_id_fields = ["design"]


@admin.register(SavedDesign)
class SavedDesignAdmin(admin.ModelAdmin):
    """Admin for SavedDesign."""

    list_display = ["user", "design", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "user__name", "design__title"]
    raw_id_fields = ["user", "design"]