"""
Tests for the users app.

Run with: pytest apps/users/tests/
"""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

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
        email="homeowner@test.com",
        name="Test Homeowner",
        password="Passw0rd!",
        role=User.Role.HOMEOWNER,
    )


@pytest.fixture
def contractor(db) -> User:
    return User.objects.create_user(
        email="contractor@test.com",
        name="Test Contractor",
        password="Passw0rd!",
        role=User.Role.CONTRACTOR,
    )


@pytest.fixture
def auth_client(api_client, homeowner) -> APIClient:
    """Authenticated API client for homeowner."""
    api_client.force_authenticate(user=homeowner)
    return api_client


# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email="new@test.com", name="New User", password="Passw0rd!"
        )
        assert user.email == "new@test.com"
        assert user.is_homeowner
        assert not user.is_contractor
        assert user.check_password("Passw0rd!")

    def test_create_contractor(self, contractor):
        assert contractor.is_contractor
        assert not contractor.is_homeowner

    def test_email_is_unique(self, homeowner):
        with pytest.raises(Exception):
            User.objects.create_user(
                email="homeowner@test.com", name="Dup", password="Passw0rd!"
            )

    def test_str_representation(self, homeowner):
        assert "homeowner@test.com" in str(homeowner)

    def test_superuser_creation(self):
        su = User.objects.create_superuser(
            email="admin@test.com", password="Admin1234!"
        )
        assert su.is_staff
        assert su.is_superuser


# ---------------------------------------------------------------------------
# Registration Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRegistration:
    url = "/api/v1/auth/register/"

    def test_register_homeowner(self, api_client):
        payload = {
            "email": "new@test.com",
            "name": "New User",
            "password": "Passw0rd!",
            "password_confirm": "Passw0rd!",
            "role": "homeowner",
        }
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "access" in data["data"]
        assert User.objects.filter(email="new@test.com").exists()

    def test_register_password_mismatch(self, api_client):
        payload = {
            "email": "bad@test.com",
            "name": "Bad User",
            "password": "Passw0rd!",
            "password_confirm": "Different!",
            "role": "homeowner",
        }
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client, homeowner):
        payload = {
            "email": "homeowner@test.com",
            "name": "Dup",
            "password": "Passw0rd!",
            "password_confirm": "Passw0rd!",
            "role": "homeowner",
        }
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Authentication Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestLogin:
    url = "/api/v1/auth/login/"

    def test_login_success(self, api_client, homeowner):
        response = api_client.post(
            self.url, {"email": "homeowner@test.com", "password": "Passw0rd!"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        assert "refresh" in data

    def test_login_wrong_password(self, api_client, homeowner):
        response = api_client.post(
            self.url, {"email": "homeowner@test.com", "password": "WrongPass!"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        response = api_client.post(
            self.url, {"email": "ghost@test.com", "password": "Whatever!"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Profile Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProfile:
    me_url = "/api/v1/auth/me/"

    def test_get_profile(self, auth_client, homeowner):
        response = auth_client.get(self.me_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["email"] == homeowner.email

    def test_update_profile(self, auth_client):
        response = auth_client.patch(self.me_url, {"name": "Updated Name", "location": "Nairobi"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["name"] == "Updated Name"

    def test_unauthenticated_profile(self, api_client):
        response = api_client.get(self.me_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
