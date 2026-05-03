"""Reviews service layer."""

from __future__ import annotations

from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.users.models import User
from apps.users.services import update_user_rating

from .models import Review


def create_review(
    reviewer: User,
    contractor_id: str,
    rating: int,
    comment: str = "",
    booking_id: str | None = None,
) -> Review:
    if not reviewer.is_homeowner:
        raise ValidationError("Only homeowners can leave reviews.")

    try:
        contractor = User.objects.get(id=contractor_id, role=User.Role.CONTRACTOR)
    except User.DoesNotExist:
        raise NotFound("Contractor not found.")

    if Review.objects.filter(reviewer=reviewer, contractor=contractor).exists():
        raise ValidationError("You have already reviewed this contractor.")

    booking = None
    if booking_id:
        from apps.bookings.models import Booking
        try:
            booking = Booking.objects.get(
                id=booking_id,
                homeowner=reviewer,
                contractor=contractor,
                status=Booking.Status.COMPLETED,
            )
        except Booking.DoesNotExist:
            raise ValidationError("No completed booking found for this contractor.")

    with transaction.atomic():
        review = Review.objects.create(
            reviewer=reviewer,
            contractor=contractor,
            booking=booking,
            rating=rating,
            comment=comment,
        )
        update_user_rating(contractor)
    return review
