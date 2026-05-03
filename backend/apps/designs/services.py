"""Designs service layer."""

from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from apps.users.models import User
from .models import DesignTemplate, SavedDesign


def list_designs(category: str = "", search: str = ""):
    qs = DesignTemplate.objects.filter(is_published=True)
    if category:
        qs = qs.filter(category=category)
    if search:
        qs = qs.filter(title__icontains=search)
    return qs


def get_design(design_id: str) -> DesignTemplate:
    try:
        design = DesignTemplate.objects.prefetch_related("images").get(id=design_id, is_published=True)
        DesignTemplate.objects.filter(id=design_id).update(view_count=design.view_count + 1)
        return design
    except DesignTemplate.DoesNotExist:
        raise NotFound("Design not found.")


def save_design(user: User, design_id: str) -> SavedDesign:
    try:
        design = DesignTemplate.objects.get(id=design_id, is_published=True)
    except DesignTemplate.DoesNotExist:
        raise NotFound("Design not found.")
    saved, created = SavedDesign.objects.get_or_create(user=user, design=design)
    if not created:
        raise ValidationError("You have already saved this design.")
    return saved


def unsave_design(user: User, design_id: str) -> None:
    deleted, _ = SavedDesign.objects.filter(user=user, design_id=design_id).delete()
    if not deleted:
        raise NotFound("Saved design not found.")
