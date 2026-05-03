"""
Marketplace service layer.
"""

from __future__ import annotations

from django.core.cache import cache
from django.db.models import QuerySet
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.users.models import User

from .models import ContractorProfile, PortfolioImage, PortfolioProject

CONTRACTOR_LIST_CACHE_KEY = "contractors:list"
CONTRACTOR_LIST_CACHE_TTL = 60 * 5  # 5 minutes


def get_or_create_contractor_profile(user: User) -> ContractorProfile:
    """
    Return the contractor's profile, creating one if it doesn't exist.

    Raises:
        ValidationError: if the user is not a contractor.
    """
    if not user.is_contractor:
        raise ValidationError("Only contractors can have a contractor profile.")
    profile, _ = ContractorProfile.objects.get_or_create(user=user)
    return profile


def update_contractor_profile(user: User, **fields) -> ContractorProfile:
    """Update profile fields and invalidate cached listings."""
    profile = get_or_create_contractor_profile(user)
    for key, value in fields.items():
        setattr(profile, key, value)
    profile.save()
    cache.delete(CONTRACTOR_LIST_CACHE_KEY)
    return profile


def list_contractors(
    *,
    location: str = "",
    category: str = "",
    min_rating: float | None = None,
    search: str = "",
    availability: str = "",
) -> QuerySet[ContractorProfile]:
    """
    Return filtered queryset of contractor profiles.
    Optimised with select_related to avoid N+1 queries.
    """
    qs = (
        ContractorProfile.objects.select_related("user")
        .prefetch_related("portfolio_projects")
        .filter(user__is_active=True)
        .order_by("-user__rating")
    )

    if location:
        qs = qs.filter(user__location__icontains=location)
    if category:
        qs = qs.filter(category=category)
    if min_rating is not None:
        qs = qs.filter(user__rating__gte=min_rating)
    if availability:
        qs = qs.filter(availability_status=availability)
    if search:
        qs = qs.filter(user__name__icontains=search) | qs.filter(
            company_name__icontains=search
        )

    return qs


def get_contractor_profile(profile_id: str) -> ContractorProfile:
    """Retrieve a single contractor profile by UUID."""
    try:
        return (
            ContractorProfile.objects.select_related("user")
            .prefetch_related("portfolio_projects__images")
            .get(id=profile_id, user__is_active=True)
        )
    except ContractorProfile.DoesNotExist:
        raise NotFound("Contractor profile not found.")


# ---------------------------------------------------------------------------
# Portfolio operations
# ---------------------------------------------------------------------------

def add_portfolio_project(
    contractor: ContractorProfile, **fields
) -> PortfolioProject:
    return PortfolioProject.objects.create(contractor=contractor, **fields)


def update_portfolio_project(
    project_id: str, contractor: ContractorProfile, **fields
) -> PortfolioProject:
    try:
        project = PortfolioProject.objects.get(id=project_id, contractor=contractor)
    except PortfolioProject.DoesNotExist:
        raise NotFound("Portfolio project not found.")
    for key, value in fields.items():
        setattr(project, key, value)
    project.save()
    return project


def delete_portfolio_project(project_id: str, contractor: ContractorProfile) -> None:
    try:
        project = PortfolioProject.objects.get(id=project_id, contractor=contractor)
        project.delete()
    except PortfolioProject.DoesNotExist:
        raise NotFound("Portfolio project not found.")


def add_portfolio_image(
    project: PortfolioProject,
    s3_key: str,
    caption: str = "",
    order: int = 0,
) -> PortfolioImage:
    return PortfolioImage.objects.create(
        portfolio_project=project, s3_key=s3_key, caption=caption, order=order
    )
