"""
Tests for the bookings app — models, services, and API endpoints.
"""

from __future__ import annotations

import datetime

import pytest
import pytz
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.bookings.models import AvailabilitySlot, Booking
from apps.bookings import services
from apps.users.models import User


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def homeowner(db) -> User:
    return User.objects.create_user(
        email="homeowner@booking.test",
        name="Home Owner",
        password="Passw0rd!",
        role=User.Role.HOMEOWNER,
    )


@pytest.fixture
def contractor(db) -> User:
    return User.objects.create_user(
        email="contractor@booking.test",
        name="Pro Contractor",
        password="Passw0rd!",
        role=User.Role.CONTRACTOR,
    )


@pytest.fixture
def homeowner_client(api_client, homeowner) -> APIClient:
    api_client.force_authenticate(user=homeowner)
    return api_client


@pytest.fixture
def contractor_client(api_client, contractor) -> APIClient:
    api_client.force_authenticate(user=contractor)
    return api_client


def _future_dt(hours_from_now: int = 24):
    return datetime.datetime.now(tz=pytz.UTC) + datetime.timedelta(hours=hours_from_now)


# ---------------------------------------------------------------------------
# Service layer tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAvailabilitySlotService:

    def test_add_slot_success(self, contractor):
        start = _future_dt(24)
        end = _future_dt(28)
        slot = services.add_availability_slot(contractor, start, end)
        assert slot.contractor == contractor
        assert not slot.is_booked

    def test_add_slot_end_before_start_raises(self, contractor):
        from rest_framework.exceptions import ValidationError
        with pytest.raises(ValidationError):
            services.add_availability_slot(contractor, _future_dt(10), _future_dt(5))

    def test_add_overlapping_slot_raises(self, contractor):
        from rest_framework.exceptions import ValidationError
        services.add_availability_slot(contractor, _future_dt(24), _future_dt(28))
        with pytest.raises(ValidationError, match="overlaps"):
            services.add_availability_slot(contractor, _future_dt(26), _future_dt(30))

    def test_non_overlapping_slots_allowed(self, contractor):
        services.add_availability_slot(contractor, _future_dt(24), _future_dt(28))
        slot2 = services.add_availability_slot(contractor, _future_dt(30), _future_dt(34))
        assert slot2.id is not None


@pytest.mark.django_db
class TestBookingService:

    def test_create_booking_success(self, homeowner, contractor):
        booking = services.create_booking(
            homeowner=homeowner,
            contractor_id=str(contractor.id),
            scheduled_start=_future_dt(24),
            scheduled_end=_future_dt(27),
            description="Need bathroom tiles replaced.",
            location="123 Main St",
        )
        assert booking.status == Booking.Status.PENDING
        assert booking.homeowner == homeowner
        assert booking.contractor == contractor

    def test_cannot_book_self(self, contractor):
        from rest_framework.exceptions import ValidationError
        with pytest.raises(ValidationError, match="yourself"):
            services.create_booking(
                homeowner=contractor,  # same user
                contractor_id=str(contractor.id),
                scheduled_start=_future_dt(24),
                scheduled_end=_future_dt(27),
                description="...",
                location="Somewhere",
            )

    def test_double_booking_prevented(self, homeowner, contractor):
        from rest_framework.exceptions import ValidationError
        services.create_booking(
            homeowner=homeowner,
            contractor_id=str(contractor.id),
            scheduled_start=_future_dt(24),
            scheduled_end=_future_dt(28),
            description="First booking",
            location="Addr 1",
        )
        # Mark the first booking as accepted to trigger conflict detection
        Booking.objects.filter(contractor=contractor).update(status=Booking.Status.ACCEPTED)

        with pytest.raises(ValidationError, match="already has a booking"):
            services.create_booking(
                homeowner=homeowner,
                contractor_id=str(contractor.id),
                scheduled_start=_future_dt(25),
                scheduled_end=_future_dt(27),
                description="Overlapping",
                location="Addr 2",
            )

    def test_accept_booking(self, homeowner, contractor):
        booking = services.create_booking(
            homeowner=homeowner,
            contractor_id=str(contractor.id),
            scheduled_start=_future_dt(48),
            scheduled_end=_future_dt(51),
            description="Paint the living room.",
            location="456 Oak Ave",
        )
        accepted = services.respond_to_booking(booking, contractor, "accepted")
        assert accepted.status == Booking.Status.ACCEPTED

    def test_reject_booking_with_reason(self, homeowner, contractor):
        booking = services.create_booking(
            homeowner=homeowner,
            contractor_id=str(contractor.id),
            scheduled_start=_future_dt(72),
            scheduled_end=_future_dt(75),
            description="New driveway.",
            location="789 Pine Rd",
        )
        rejected = services.respond_to_booking(
            booking, contractor, "rejected", rejection_reason="Not available that week."
        )
        assert rejected.status == Booking.Status.REJECTED
        assert "Not available" in rejected.rejection_reason

    def test_wrong_contractor_cannot_respond(self, homeowner, contractor, db):
        other_contractor = User.objects.create_user(
            email="other@test.com", name="Other", password="Passw0rd!", role="contractor"
        )
        booking = services.create_booking(
            homeowner=homeowner,
            contractor_id=str(contractor.id),
            scheduled_start=_future_dt(96),
            scheduled_end=_future_dt(99),
            description="Roof repair.",
            location="Somewhere",
        )
        from rest_framework.exceptions import PermissionDenied
        with pytest.raises(PermissionDenied):
            services.respond_to_booking(booking, other_contractor, "accepted")

    def test_complete_booking(self, homeowner, contractor):
        booking = services.create_booking(
            homeowner=homeowner,
            contractor_id=str(contractor.id),
            scheduled_start=_future_dt(48),
            scheduled_end=_future_dt(51),
            description="Window installation.",
            location="100 Test St",
        )
        services.respond_to_booking(booking, contractor, "accepted")
        completed = services.complete_booking(booking, homeowner)
        assert completed.status == Booking.Status.COMPLETED

    def test_cancel_pending_booking(self, homeowner, contractor):
        booking = services.create_booking(
            homeowner=homeowner,
            contractor_id=str(contractor.id),
            scheduled_start=_future_dt(48),
            scheduled_end=_future_dt(51),
            description="Plumbing fix.",
            location="200 River Ln",
        )
        cancelled = services.cancel_booking(booking, homeowner)
        assert cancelled.status == Booking.Status.CANCELLED
        assert cancelled.cancelled_by == homeowner


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestBookingAPI:
    list_url = "/api/v1/bookings/"

    def test_create_booking_as_homeowner(self, homeowner_client, contractor):
        payload = {
            "contractor_id": str(contractor.id),
            "scheduled_start": (_future_dt(48)).isoformat(),
            "scheduled_end": (_future_dt(51)).isoformat(),
            "description": "I need my bathroom renovated completely.",
            "location": "15 Maple Drive, Nairobi",
        }
        response = homeowner_client.post(self.list_url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["status"] == "pending"

    def test_contractor_cannot_create_booking(self, contractor_client, homeowner):
        payload = {
            "contractor_id": str(homeowner.id),
            "scheduled_start": (_future_dt(48)).isoformat(),
            "scheduled_end": (_future_dt(51)).isoformat(),
            "description": "Test.",
            "location": "Somewhere",
        }
        response = contractor_client.post(self.list_url, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_bookings_as_homeowner(self, homeowner_client, homeowner, contractor):
        Booking.objects.create(
            homeowner=homeowner,
            contractor=contractor,
            scheduled_start=_future_dt(24),
            scheduled_end=_future_dt(27),
            description="Test booking",
            location="Test Location",
        )
        response = homeowner_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] >= 1

    def test_accept_booking_as_contractor(self, homeowner_client, contractor_client, homeowner, contractor):
        # Create booking as homeowner
        payload = {
            "contractor_id": str(contractor.id),
            "scheduled_start": (_future_dt(72)).isoformat(),
            "scheduled_end": (_future_dt(75)).isoformat(),
            "description": "Kitchen cabinet installation project.",
            "location": "42 Elm Street",
        }
        create_resp = homeowner_client.post(self.list_url, payload, format="json")
        booking_id = create_resp.json()["data"]["id"]

        # Accept as contractor
        status_url = f"/api/v1/bookings/{booking_id}/status/"
        accept_resp = contractor_client.patch(
            status_url, {"action": "accepted"}, format="json"
        )
        assert accept_resp.status_code == status.HTTP_200_OK
        assert accept_resp.json()["data"]["status"] == "accepted"

    def test_unauthenticated_cannot_access_bookings(self, api_client):
        response = api_client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
