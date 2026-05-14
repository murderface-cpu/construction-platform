"""Admin configuration for marketplace app."""

from django.contrib import admin
from .models import ContractorProfile, PortfolioProject, PortfolioImage


class PortfolioImageInline(admin.TabularInline):
    """Inline for PortfolioImage."""

    model = PortfolioImage
    extra = 1
    fields = ["image", "s3_key", "caption", "order"]


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    """Admin for PortfolioProject."""

    list_display = ["title", "contractor", "category", "is_featured", "completion_date", "created_at"]
    list_filter = ["category", "is_featured", "created_at"]
    search_fields = ["title", "description", "contractor__user__name"]
    raw_id_fields = ["contractor"]
    inlines = [PortfolioImageInline]


@admin.register(ContractorProfile)
class ContractorProfileAdmin(admin.ModelAdmin):
    """Admin for ContractorProfile."""

    list_display = ["user", "company_name", "category", "availability_status", "is_verified", "completed_projects"]
    list_filter = ["category", "availability_status", "is_verified", "years_experience"]
    search_fields = ["user__email", "user__name", "company_name", "license_number"]
    raw_id_fields = ["user"]
    readonly_fields = ["completed_projects", "created_at", "updated_at"]


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    """Admin for PortfolioImage."""

    list_display = ["id", "portfolio_project", "caption", "order", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["caption", "s3_key"]
    raw_id_fields = ["portfolio_project"]