"""
Tests for the reviews and notifications apps.
"""

from __future__ import annotations

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.reviews.models import Review
from apps.reviews import services as review_services
from apps.notifications.models import Notification
from apps.notifications import services as notif_services
from apps.users.models import User


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def homeowner(db) -> User:
    return User.objects.create_user(
        email="reviewer@test.com",
        name="Home Owner",
        password="Passw0rd!",
        role=User.Role.HOMEOWNER,
    )


@pytest.fixture
def contractor(db) -> User:
    return User.objects.create_user(
        email="reviewed@test.com",
        name="Pro Builder",
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


# ===========================================================================
# REVIEWS
# ===========================================================================

@pytest.mark.django_db
class TestReviewService:

    def test_create_review_success(self, homeowner, contractor):
        review = review_services.create_review(
            reviewer=homeowner,
            contractor_id=str(contractor.id),
            rating=5,
            comment="Excellent work! Very professional.",
        )
        assert review.rating == 5
        assert review.reviewer == homeowner
        assert review.contractor == contractor

    def test_create_review_updates_contractor_rating(self, homeowner, contractor):
        review_services.create_review(
            reviewer=homeowner,
            contractor_id=str(contractor.id),
            rating=4,
            comment="Good job.",
        )
        contractor.refresh_from_db()
        assert float(contractor.rating) == 4.0
        assert contractor.reviews_count == 1

    def test_duplicate_review_raises(self, homeowner, contractor):
        from rest_framework.exceptions import ValidationError
        review_services.create_review(
            reviewer=homeowner,
            contractor_id=str(contractor.id),
            rating=5,
            comment="First review.",
        )
        with pytest.raises(ValidationError, match="already reviewed"):
            review_services.create_review(
                reviewer=homeowner,
                contractor_id=str(contractor.id),
                rating=3,
                comment="Second attempt.",
            )

    def test_contractor_cannot_review(self, contractor, homeowner):
        from rest_framework.exceptions import ValidationError
        with pytest.raises(ValidationError, match="homeowners"):
            review_services.create_review(
                reviewer=contractor,  # Wrong role
                contractor_id=str(homeowner.id),
                rating=5,
                comment="Should fail.",
            )

    def test_average_rating_with_multiple_reviews(self, contractor, db):
        reviewers = []
        for i in range(4):
            u = User.objects.create_user(
                email=f"r{i}@test.com", name=f"Reviewer {i}",
                password="Passw0rd!", role="homeowner",
            )
            reviewers.append(u)

        ratings = [5, 4, 3, 4]
        for reviewer, rating in zip(reviewers, ratings):
            review_services.create_review(
                reviewer=reviewer,
                contractor_id=str(contractor.id),
                rating=rating,
                comment="Review.",
            )

        contractor.refresh_from_db()
        assert contractor.reviews_count == 4
        assert float(contractor.rating) == pytest.approx(4.0, 0.01)

    def test_review_linked_to_completed_booking(self, homeowner, contractor, db):
        from apps.bookings.models import Booking
        import datetime, pytz

        now = datetime.datetime.now(tz=pytz.UTC)
        booking = Booking.objects.create(
            homeowner=homeowner,
            contractor=contractor,
            scheduled_start=now - datetime.timedelta(days=2),
            scheduled_end=now - datetime.timedelta(days=1),
            description="Completed job.",
            location="Test Address",
            status=Booking.Status.COMPLETED,
        )
        review = review_services.create_review(
            reviewer=homeowner,
            contractor_id=str(contractor.id),
            rating=5,
            comment="Job done well.",
            booking_id=str(booking.id),
        )
        assert review.booking == booking


@pytest.mark.django_db
class TestReviewAPI:
    url = "/api/v1/reviews/"

    def test_create_review(self, homeowner_client, contractor):
        payload = {
            "contractor_id": str(contractor.id),
            "rating": 4,
            "comment": "Solid work, on time and within budget.",
        }
        response = homeowner_client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["rating"] == 4

    def test_list_reviews_for_contractor(self, api_client, homeowner, contractor):
        Review.objects.create(
            reviewer=homeowner, contractor=contractor, rating=5, comment="Great!"
        )
        response = api_client.get(self.url + f"?contractor_id={contractor.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] >= 1

    def test_unauthenticated_can_list_reviews(self, api_client, homeowner, contractor):
        Review.objects.create(
            reviewer=homeowner, contractor=contractor, rating=3, comment="Average."
        )
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_cannot_create_review(self, api_client, contractor):
        payload = {"contractor_id": str(contractor.id), "rating": 5}
        response = api_client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ===========================================================================
# NOTIFICATIONS
# ===========================================================================

@pytest.mark.django_db
class TestNotificationService:

    def test_create_notification(self, homeowner):
        notif = notif_services.create_notification(
            recipient=homeowner,
            notification_type=Notification.Type.SYSTEM,
            title="Welcome!",
            message="Welcome to the Construction Platform.",
        )
        assert notif.recipient == homeowner
        assert not notif.is_read

    def test_mark_notification_read(self, homeowner):
        notif = Notification.objects.create(
            recipient=homeowner,
            notification_type="system",
            title="Test",
            message="Test message",
        )
        updated = notif_services.mark_read(homeowner, str(notif.id))
        assert updated.is_read is True

    def test_mark_all_read(self, homeowner):
        for i in range(5):
            Notification.objects.create(
                recipient=homeowner,
                notification_type="system",
                title=f"Notif {i}",
                message="msg",
                is_read=False,
            )
        count = notif_services.mark_all_read(homeowner)
        assert count == 5
        assert notif_services.get_unread_count(homeowner) == 0

    def test_unread_count(self, homeowner):
        for i in range(3):
            Notification.objects.create(
                recipient=homeowner,
                notification_type="system",
                title=f"N{i}",
                message="m",
                is_read=False,
            )
        Notification.objects.create(
            recipient=homeowner,
            notification_type="system",
            title="Read",
            message="r",
            is_read=True,
        )
        assert notif_services.get_unread_count(homeowner) == 3

    def test_cannot_mark_other_users_notification_read(self, homeowner, contractor):
        notif = Notification.objects.create(
            recipient=contractor,
            notification_type="system",
            title="For Contractor",
            message="msg",
        )
        from rest_framework.exceptions import NotFound
        with pytest.raises(NotFound):
            notif_services.mark_read(homeowner, str(notif.id))


@pytest.mark.django_db
class TestNotificationAPI:
    url = "/api/v1/notifications/"

    def _create_notifications(self, user, count: int = 3):
        for i in range(count):
            Notification.objects.create(
                recipient=user,
                notification_type="system",
                title=f"Notification {i}",
                message=f"Message {i}",
                is_read=False,
            )

    def test_list_notifications(self, homeowner_client, homeowner):
        self._create_notifications(homeowner, 3)
        response = homeowner_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] >= 3

    def test_filter_unread_notifications(self, homeowner_client, homeowner):
        self._create_notifications(homeowner, 4)
        Notification.objects.filter(recipient=homeowner).first().update_fields = ["is_read"]
        # Mark one as read
        Notification.objects.filter(recipient=homeowner).first().is_read = True
        Notification.objects.filter(recipient=homeowner).first().save()

        response = homeowner_client.get(self.url + "?unread=true")
        assert response.status_code == status.HTTP_200_OK

    def test_unread_count_endpoint(self, homeowner_client, homeowner):
        self._create_notifications(homeowner, 7)
        response = homeowner_client.get(self.url + "unread-count/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["unread_count"] == 7

    def test_mark_notification_read_api(self, homeowner_client, homeowner):
        notif = Notification.objects.create(
            recipient=homeowner,
            notification_type="system",
            title="Mark me",
            message="msg",
            is_read=False,
        )
        response = homeowner_client.patch(f"{self.url}{notif.id}/read/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["is_read"] is True

    def test_mark_all_read_api(self, homeowner_client, homeowner):
        self._create_notifications(homeowner, 5)
        response = homeowner_client.post(self.url + "mark-all-read/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["updated_count"] == 5

    def test_unauthenticated_cannot_access_notifications(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
