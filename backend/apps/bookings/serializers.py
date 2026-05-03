"""Serializers for the bookings app."""

from __future__ import annotations

from rest_framework import serializers

from apps.users.serializers import PublicUserSerializer

from .models import AvailabilitySlot, Booking


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilitySlot
        fields = ["id", "start_time", "end_time", "is_booked", "created_at"]
        read_only_fields = ["id", "is_booked", "created_at"]


class BookingSerializer(serializers.ModelSerializer):
    homeowner = PublicUserSerializer(read_only=True)
    contractor = PublicUserSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "homeowner",
            "contractor",
            "scheduled_start",
            "scheduled_end",
            "status",
            "description",
            "location",
            "estimated_budget",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "rejection_reason", "created_at", "updated_at"]


class CreateBookingSerializer(serializers.Serializer):
    contractor_id = serializers.UUIDField()
    scheduled_start = serializers.DateTimeField()
    scheduled_end = serializers.DateTimeField()
    description = serializers.CharField(min_length=10)
    location = serializers.CharField(max_length=255)
    estimated_budget = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    slot_id = serializers.UUIDField(required=False)


class BookingStatusUpdateSerializer(serializers.Serializer):
    """Used when a contractor accepts/rejects a booking."""

    action = serializers.ChoiceField(choices=["accepted", "rejected"])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
