"""Booking views."""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import success_response
from core.pagination import StandardResultsPagination
from core.permissions import IsContractor

from . import services
from .models import AvailabilitySlot, Booking
from .serializers import (
    AvailabilitySlotSerializer,
    BookingSerializer,
    BookingStatusUpdateSerializer,
    CreateBookingSerializer,
)


class BookingListCreateView(APIView):
    """
    GET  /api/v1/bookings/  — list bookings for the current user
    POST /api/v1/bookings/  — create a booking (homeowner only)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = request.user
        if user.is_homeowner:
            qs = Booking.objects.filter(homeowner=user).select_related("homeowner", "contractor")
        else:
            qs = Booking.objects.filter(contractor=user).select_related("homeowner", "contractor")

        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(BookingSerializer(page, many=True).data)

    def post(self, request: Request) -> Response:
        if not request.user.is_homeowner:
            return Response(
                {"success": False, "error": {"code": "permission_denied", "message": "Only homeowners can create bookings."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = CreateBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        booking = services.create_booking(
            homeowner=request.user,
            contractor_id=str(d["contractor_id"]),
            scheduled_start=d["scheduled_start"],
            scheduled_end=d["scheduled_end"],
            description=d["description"],
            location=d["location"],
            estimated_budget=d.get("estimated_budget"),
            slot_id=str(d["slot_id"]) if d.get("slot_id") else None,
        )
        # Trigger notification (import here to avoid circular deps)
        from apps.notifications.tasks import send_booking_notification
        send_booking_notification.delay(str(booking.id), "new_booking")

        return Response(
            {"success": True, "data": BookingSerializer(booking).data},
            status=status.HTTP_201_CREATED,
        )


class BookingDetailView(APIView):
    """
    GET   /api/v1/bookings/{id}/           — retrieve a booking
    PATCH /api/v1/bookings/{id}/status/    — accept/reject (contractor)
    POST  /api/v1/bookings/{id}/complete/  — mark completed
    POST  /api/v1/bookings/{id}/cancel/    — cancel
    """

    permission_classes = [IsAuthenticated]

    def _get_booking(self, pk: str, user) -> Booking:
        try:
            return Booking.objects.select_related("homeowner", "contractor").get(
                id=pk
            )
        except Booking.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Booking not found.")

    def get(self, request: Request, pk: str) -> Response:
        booking = self._get_booking(pk, request.user)
        if booking.homeowner != request.user and booking.contractor != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return success_response(BookingSerializer(booking).data)


class BookingStatusView(APIView):
    """PATCH /api/v1/bookings/{id}/status/"""

    permission_classes = [IsAuthenticated, IsContractor]

    def patch(self, request: Request, pk: str) -> Response:
        try:
            booking = Booking.objects.get(id=pk)
        except Booking.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Booking not found.")

        serializer = BookingStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = services.respond_to_booking(
            booking=booking,
            contractor=request.user,
            action=serializer.validated_data["action"],
            rejection_reason=serializer.validated_data.get("rejection_reason", ""),
        )

        from apps.notifications.tasks import send_booking_notification
        send_booking_notification.delay(str(booking.id), f"booking_{booking.status}")

        return success_response(BookingSerializer(booking).data)


class BookingCompleteView(APIView):
    """POST /api/v1/bookings/{id}/complete/"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk: str) -> Response:
        try:
            booking = Booking.objects.get(id=pk)
        except Booking.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Booking not found.")
        booking = services.complete_booking(booking, request.user)
        return success_response(BookingSerializer(booking).data, message="Booking marked as completed.")


class BookingCancelView(APIView):
    """POST /api/v1/bookings/{id}/cancel/"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk: str) -> Response:
        try:
            booking = Booking.objects.get(id=pk)
        except Booking.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Booking not found.")
        booking = services.cancel_booking(booking, request.user)
        return success_response(BookingSerializer(booking).data, message="Booking cancelled.")


# ---------------------------------------------------------------------------
# Availability slots
# ---------------------------------------------------------------------------

class AvailabilitySlotView(APIView):
    """
    GET  /api/v1/bookings/availability/         — contractor's own slots
    POST /api/v1/bookings/availability/         — add a slot (contractor)
    GET  /api/v1/bookings/availability/{cid}/   — public: contractor's open slots
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        slots = services.get_contractor_availability(request.user)
        return success_response(AvailabilitySlotSerializer(slots, many=True).data)

    def post(self, request: Request) -> Response:
        if not request.user.is_contractor:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = AvailabilitySlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot = services.add_availability_slot(
            contractor=request.user,
            start_time=serializer.validated_data["start_time"],
            end_time=serializer.validated_data["end_time"],
        )
        return Response(
            {"success": True, "data": AvailabilitySlotSerializer(slot).data},
            status=status.HTTP_201_CREATED,
        )
