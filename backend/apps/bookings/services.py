"""
Booking service layer.

Enforces the booking state machine and prevents double-booking.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.users.models import User

from .models import AvailabilitySlot, Booking


# ---------------------------------------------------------------------------
# Availability
# ---------------------------------------------------------------------------

def add_availability_slot(
    contractor: User,
    start_time,
    end_time,
) -> AvailabilitySlot:
    """
    Add a new open slot for a contractor.

    Raises:
        ValidationError: if the slot overlaps an existing one.
    """
    if end_time <= start_time:
        raise ValidationError("End time must be after start time.")

    overlapping = AvailabilitySlot.objects.filter(
        contractor=contractor,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).exists()

    if overlapping:
        raise ValidationError("This time slot overlaps with an existing availability slot.")

    return AvailabilitySlot.objects.create(
        contractor=contractor, start_time=start_time, end_time=end_time
    )


def get_contractor_availability(contractor: User) -> list[AvailabilitySlot]:
    return list(
        AvailabilitySlot.objects.filter(
            contractor=contractor,
            is_booked=False,
            start_time__gte=timezone.now(),
        ).order_by("start_time")
    )


# ---------------------------------------------------------------------------
# Booking lifecycle
# ---------------------------------------------------------------------------

@transaction.atomic
def create_booking(
    homeowner: User,
    contractor_id: str,
    scheduled_start,
    scheduled_end,
    description: str,
    location: str,
    estimated_budget=None,
    slot_id: str | None = None,
) -> Booking:
    """
    Create a booking and optionally lock an availability slot.

    Uses select_for_update() to prevent concurrent double-bookings.
    """
    try:
        contractor = User.objects.get(id=contractor_id, role=User.Role.CONTRACTOR)
    except User.DoesNotExist:
        raise ValidationError("Contractor not found.")

    if homeowner == contractor:
        raise ValidationError("You cannot book yourself.")

    if scheduled_end <= scheduled_start:
        raise ValidationError("Booking end time must be after start time.")

    # Treat pending bookings as reserved time until the contractor accepts or rejects.
    conflict = Booking.objects.filter(
        contractor=contractor,
        status__in=[Booking.Status.PENDING, Booking.Status.ACCEPTED],
        scheduled_start__lt=scheduled_end,
        scheduled_end__gt=scheduled_start,
    ).exists()

    if conflict:
        raise ValidationError(
            "The contractor already has a booking during this time window."
        )

    slot = None
    if slot_id:
        try:
            slot = AvailabilitySlot.objects.select_for_update().get(
                id=slot_id,
                contractor=contractor,
                is_booked=False,
            )
        except AvailabilitySlot.DoesNotExist:
            raise ValidationError("The selected availability slot is no longer available.")
        slot.is_booked = True
        slot.save(update_fields=["is_booked"])

    booking = Booking.objects.create(
        homeowner=homeowner,
        contractor=contractor,
        availability_slot=slot,
        scheduled_start=scheduled_start,
        scheduled_end=scheduled_end,
        description=description,
        location=location,
        estimated_budget=estimated_budget,
    )
    return booking


@transaction.atomic
def respond_to_booking(
    booking: Booking,
    contractor: User,
    action: str,
    rejection_reason: str = "",
) -> Booking:
    """
    Accept or reject a pending booking.

    Args:
        action: 'accepted' or 'rejected'
    """
    if booking.contractor != contractor:
        raise PermissionDenied("You can only respond to your own bookings.")

    if booking.status != Booking.Status.PENDING:
        raise ValidationError(f"Cannot respond to a booking with status '{booking.status}'.")

    if action == Booking.Status.ACCEPTED:
        booking.status = Booking.Status.ACCEPTED
    elif action == Booking.Status.REJECTED:
        booking.status = Booking.Status.REJECTED
        booking.rejection_reason = rejection_reason
        # Rejected requests reopen the slot for other homeowners.
        if booking.availability_slot:
            booking.availability_slot.is_booked = False
            booking.availability_slot.save(update_fields=["is_booked"])
    else:
        raise ValidationError("Action must be 'accepted' or 'rejected'.")

    booking.save(update_fields=["status", "rejection_reason"])
    return booking


@transaction.atomic
def complete_booking(booking: Booking, requestor: User) -> Booking:
    """Mark a booking as completed (homeowner or contractor can do this)."""
    if booking.homeowner != requestor and booking.contractor != requestor:
        raise PermissionDenied("Only participants can complete a booking.")

    if booking.status != Booking.Status.ACCEPTED:
        raise ValidationError("Only accepted bookings can be marked as completed.")

    booking.status = Booking.Status.COMPLETED
    booking.save(update_fields=["status"])
    return booking


@transaction.atomic
def cancel_booking(booking: Booking, requestor: User) -> Booking:
    """Cancel a booking (only allowed in pending state by participants)."""
    if booking.homeowner != requestor and booking.contractor != requestor:
        raise PermissionDenied("Only participants can cancel a booking.")

    if booking.status not in [Booking.Status.PENDING, Booking.Status.ACCEPTED]:
        raise ValidationError(f"Cannot cancel a booking with status '{booking.status}'.")

    booking.status = Booking.Status.CANCELLED
    booking.cancelled_by = requestor
    if booking.availability_slot:
        booking.availability_slot.is_booked = False
        booking.availability_slot.save(update_fields=["is_booked"])
    booking.save(update_fields=["status", "cancelled_by"])
    return booking
