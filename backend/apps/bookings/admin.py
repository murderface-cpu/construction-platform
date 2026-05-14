"""Admin configuration for bookings app."""

from django.contrib import admin
from .models import Booking, AvailabilitySlot


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin for Booking."""

    list_display = ["id", "homeowner", "contractor", "status", "scheduled_start", "scheduled_end", "created_at"]
    list_filter = ["status", "created_at", "scheduled_start"]
    search_fields = ["homeowner__email", "homeowner__name", "contractor__email", "contractor__name", "description"]
    raw_id_fields = ["homeowner", "contractor", "availability_slot", "cancelled_by"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    """Admin for AvailabilitySlot."""

    list_display = ["contractor", "start_time", "end_time", "is_booked", "created_at"]
    list_filter = ["is_booked", "created_at"]
    search_fields = ["contractor__email", "contractor__name"]
    raw_id_fields = ["contractor"]