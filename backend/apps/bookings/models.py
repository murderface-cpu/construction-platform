"""
Booking system models.

Booking     — a homeowner's booking request to a contractor.
AvailabilitySlot — time slots a contractor marks as open for bookings.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone

from apps.users.models import User
from core.mixins import BaseModel


class AvailabilitySlot(BaseModel):
    """
    A time window that a contractor has marked as available.
    Used to prevent double-booking.
    """

    contractor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="availability_slots",
        limit_choices_to={"role": User.Role.CONTRACTOR},
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        db_table = "availability_slots"
        ordering = ["start_time"]
        # Prevent overlapping slots for the same contractor at DB level
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="slot_end_after_start",
            )
        ]

    def __str__(self) -> str:
        return f"{self.contractor.name}: {self.start_time} – {self.end_time}"


class Booking(BaseModel):
    """
    A booking request from a homeowner to a contractor.

    State machine:
        pending  →  accepted  →  completed
                 →  rejected
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    homeowner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings_as_homeowner",
        limit_choices_to={"role": User.Role.HOMEOWNER},
    )
    contractor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings_as_contractor",
        limit_choices_to={"role": User.Role.CONTRACTOR},
    )
    availability_slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booking",
    )

    # Scheduling
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()

    # Details
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    description = models.TextField(help_text="What work needs to be done?")
    location = models.CharField(max_length=255)
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Rejection/cancellation reason
    rejection_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="cancelled_bookings"
    )

    class Meta:
        db_table = "bookings"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["homeowner", "status"]),
            models.Index(fields=["contractor", "status"]),
        ]

    def __str__(self) -> str:
        return f"Booking({self.homeowner.name} → {self.contractor.name}, {self.status})"

    @property
    def is_upcoming(self) -> bool:
        return self.scheduled_start > timezone.now()
