"""Reviews models."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.users.models import User
from core.mixins import BaseModel


class Review(BaseModel):
    """A homeowner's review of a contractor after project completion."""

    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_reviews",
        limit_choices_to={"role": User.Role.HOMEOWNER},
    )
    contractor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_reviews",
        limit_choices_to={"role": User.Role.CONTRACTOR},
    )
    # Optional link to the booking that triggered the review
    booking = models.OneToOneField(
        "bookings.Booking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="review",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)

    class Meta:
        db_table = "reviews"
        ordering = ["-created_at"]
        # One review per homeowner per contractor
        unique_together = [("reviewer", "contractor")]

    def __str__(self) -> str:
        return f"Review({self.reviewer.name} → {self.contractor.name}, {self.rating}★)"
