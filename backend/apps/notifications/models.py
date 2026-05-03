"""In-app notification model."""

from django.db import models
from apps.users.models import User
from core.mixins import BaseModel


class Notification(BaseModel):
    """Persisted in-app notification."""

    class Type(models.TextChoices):
        BOOKING_NEW = "booking_new", "New Booking Request"
        BOOKING_ACCEPTED = "booking_accepted", "Booking Accepted"
        BOOKING_REJECTED = "booking_rejected", "Booking Rejected"
        BOOKING_COMPLETED = "booking_completed", "Booking Completed"
        MILESTONE_UPDATED = "milestone_updated", "Milestone Updated"
        PROJECT_UPDATE = "project_update", "Project Update"
        NEW_REVIEW = "new_review", "New Review"
        SYSTEM = "system", "System Message"

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)  # e.g. {"booking_id": "..."}

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
        ]

    def __str__(self) -> str:
        return f"Notification({self.recipient.name}: {self.notification_type})"
