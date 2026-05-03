"""
Marketplace models.

ContractorProfile — extended profile for contractor users.
PortfolioProject — showcase projects a contractor has completed.
"""

from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.users.models import User
from core.mixins import BaseModel


class ContractorProfile(BaseModel):
    """
    Extended profile for users with role=contractor.
    One-to-one with User.
    """

    class ServiceCategory(models.TextChoices):
        GENERAL = "general", "General Contractor"
        ELECTRICAL = "electrical", "Electrical"
        PLUMBING = "plumbing", "Plumbing"
        CARPENTRY = "carpentry", "Carpentry"
        PAINTING = "painting", "Painting"
        LANDSCAPING = "landscaping", "Landscaping"
        ROOFING = "roofing", "Roofing"
        HVAC = "hvac", "HVAC"
        MASONRY = "masonry", "Masonry"
        INTERIOR_DESIGN = "interior_design", "Interior Design"
        OTHER = "other", "Other"

    class AvailabilityStatus(models.TextChoices):
        AVAILABLE = "available", "Available"
        BUSY = "busy", "Busy"
        UNAVAILABLE = "unavailable", "Unavailable"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="contractor_profile",
        limit_choices_to={"role": User.Role.CONTRACTOR},
    )

    # Professional info
    company_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(
        max_length=50, choices=ServiceCategory.choices, default=ServiceCategory.GENERAL
    )
    skills = models.JSONField(default=list, blank=True)  # ["Tiling", "Demolition", ...]
    years_experience = models.PositiveSmallIntegerField(default=0)
    license_number = models.CharField(max_length=100, blank=True)
    insurance_info = models.TextField(blank=True)

    # Pricing
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Availability
    availability_status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE,
    )

    # Stats (updated by services)
    completed_projects = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)  # admin-verified contractor

    class Meta:
        db_table = "contractor_profiles"
        verbose_name = "Contractor Profile"
        verbose_name_plural = "Contractor Profiles"

    def __str__(self) -> str:
        return f"ContractorProfile({self.user.name})"


class PortfolioProject(BaseModel):
    """
    A completed project a contractor can showcase in their portfolio.
    Supports multiple images via PortfolioImage.
    """

    contractor = models.ForeignKey(
        ContractorProfile,
        on_delete=models.CASCADE,
        related_name="portfolio_projects",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=ContractorProfile.ServiceCategory.choices,
        default=ContractorProfile.ServiceCategory.GENERAL,
    )
    location = models.CharField(max_length=255, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    project_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        db_table = "portfolio_projects"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.contractor.user.name} — {self.title}"


class PortfolioImage(BaseModel):
    """Individual image within a PortfolioProject."""

    portfolio_project = models.ForeignKey(
        PortfolioProject,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="portfolio/", blank=True, null=True)
    s3_key = models.CharField(max_length=500, blank=True)  # for presigned URL generation
    caption = models.CharField(max_length=300, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "portfolio_images"
        ordering = ["order", "created_at"]
