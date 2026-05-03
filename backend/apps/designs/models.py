"""Design discovery models (Houzz-style)."""

from django.db import models
from apps.users.models import User
from core.mixins import BaseModel


class DesignTemplate(BaseModel):
    """A design inspiration template browsable by homeowners."""

    class Category(models.TextChoices):
        INTERIOR = "interior", "Interior"
        EXTERIOR = "exterior", "Exterior"
        LANDSCAPING = "landscaping", "Landscaping"
        KITCHEN = "kitchen", "Kitchen"
        BATHROOM = "bathroom", "Bathroom"
        BEDROOM = "bedroom", "Bedroom"
        LIVING = "living", "Living Room"
        OFFICE = "office", "Home Office"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=Category.choices)
    style_tags = models.JSONField(default=list, blank=True)  # ["modern", "minimalist"]
    cover_image_key = models.CharField(max_length=500, blank=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_designs"
    )
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "design_templates"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Design: {self.title} ({self.category})"


class DesignImage(BaseModel):
    """Multiple images per design template."""

    design = models.ForeignKey(DesignTemplate, on_delete=models.CASCADE, related_name="images")
    s3_key = models.CharField(max_length=500)
    caption = models.CharField(max_length=300, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "design_images"
        ordering = ["order"]


class SavedDesign(BaseModel):
    """A homeowner bookmarks/saves a design template."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_designs")
    design = models.ForeignKey(DesignTemplate, on_delete=models.CASCADE, related_name="saves")

    class Meta:
        db_table = "saved_designs"
        unique_together = [("user", "design")]
