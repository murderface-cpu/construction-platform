"""
Tests for the marketplace app — contractor profiles and portfolios.
"""

from __future__ import annotations

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.marketplace.models import ContractorProfile, PortfolioProject
from apps.marketplace import services
from apps.users.models import User


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def contractor(db) -> User:
    return User.objects.create_user(
        email="pro@market.test",
        name="Pro Contractor",
        password="Passw0rd!",
        role=User.Role.CONTRACTOR,
        location="Nairobi, Kenya",
    )


@pytest.fixture
def homeowner(db) -> User:
    return User.objects.create_user(
        email="buyer@market.test",
        name="Home Buyer",
        password="Passw0rd!",
        role=User.Role.HOMEOWNER,
    )


@pytest.fixture
def contractor_client(api_client, contractor) -> APIClient:
    api_client.force_authenticate(user=contractor)
    return api_client


@pytest.fixture
def homeowner_client(api_client, homeowner) -> APIClient:
    api_client.force_authenticate(user=homeowner)
    return api_client


@pytest.fixture
def profile(contractor) -> ContractorProfile:
    return services.get_or_create_contractor_profile(contractor)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestContractorProfileModel:

    def test_profile_created_for_contractor(self, contractor):
        profile = services.get_or_create_contractor_profile(contractor)
        assert profile.user == contractor
        assert profile.availability_status == ContractorProfile.AvailabilityStatus.AVAILABLE

    def test_homeowner_cannot_have_profile(self, homeowner):
        from rest_framework.exceptions import ValidationError
        with pytest.raises(ValidationError):
            services.get_or_create_contractor_profile(homeowner)

    def test_profile_str(self, profile):
        assert "Pro Contractor" in str(profile)


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestContractorListService:

    def test_list_all_contractors(self, profile):
        qs = services.list_contractors()
        assert qs.filter(id=profile.id).exists()

    def test_filter_by_location(self, profile):
        qs = services.list_contractors(location="Nairobi")
        assert qs.filter(id=profile.id).exists()

        qs_miss = services.list_contractors(location="Mombasa")
        assert not qs_miss.filter(id=profile.id).exists()

    def test_filter_by_category(self, profile):
        services.update_contractor_profile(profile.user, category="electrical")
        qs = services.list_contractors(category="electrical")
        assert qs.filter(id=profile.id).exists()

    def test_filter_by_min_rating(self, profile):
        # Default rating is 0
        qs = services.list_contractors(min_rating=4.5)
        assert not qs.filter(id=profile.id).exists()

        profile.user.rating = 4.8
        profile.user.save()
        qs = services.list_contractors(min_rating=4.5)
        assert qs.filter(id=profile.id).exists()

    def test_search_by_name(self, profile):
        qs = services.list_contractors(search="Pro Contractor")
        assert qs.filter(id=profile.id).exists()

    def test_search_by_company_name(self, profile):
        services.update_contractor_profile(profile.user, company_name="Nairobi Builders Ltd")
        qs = services.list_contractors(search="Nairobi Builders")
        assert qs.filter(id=profile.id).exists()


@pytest.mark.django_db
class TestPortfolioService:

    def test_add_portfolio_project(self, profile):
        project = services.add_portfolio_project(
            profile,
            title="Westlands Office Renovation",
            description="Full interior fit-out of 3-storey office building.",
            category="interior_design",
            location="Westlands, Nairobi",
        )
        assert project.contractor == profile
        assert project.title == "Westlands Office Renovation"

    def test_update_portfolio_project(self, profile):
        project = services.add_portfolio_project(
            profile,
            title="Original Title",
            description="Desc.",
            category="general",
        )
        updated = services.update_portfolio_project(
            str(project.id), profile, title="Updated Title"
        )
        assert updated.title == "Updated Title"

    def test_delete_portfolio_project(self, profile):
        project = services.add_portfolio_project(
            profile, title="To Delete", description="x", category="general"
        )
        pid = project.id
        services.delete_portfolio_project(str(pid), profile)
        assert not PortfolioProject.objects.filter(id=pid).exists()

    def test_wrong_contractor_cannot_update_portfolio(self, db, profile):
        other_contractor = User.objects.create_user(
            email="other@test.com", name="Other", password="x", role="contractor"
        )
        other_profile = services.get_or_create_contractor_profile(other_contractor)
        project = services.add_portfolio_project(
            profile, title="Mine", description="x", category="general"
        )
        from rest_framework.exceptions import NotFound
        with pytest.raises(NotFound):
            services.update_portfolio_project(str(project.id), other_profile, title="Stolen")


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestContractorAPI:
    list_url = "/api/v1/contractors/"

    def test_list_contractors_public(self, api_client, profile):
        response = api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] >= 1

    def test_list_contractors_filter_location(self, api_client, profile):
        response = api_client.get(self.list_url + "?location=Nairobi")
        assert response.status_code == status.HTTP_200_OK
        ids = [r["id"] for r in response.json()["results"]]
        assert str(profile.id) in ids

    def test_get_contractor_detail_public(self, api_client, profile):
        response = api_client.get(f"{self.list_url}{profile.id}/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert "portfolio_projects" in data
        assert "rating" in data

    def test_get_my_profile_as_contractor(self, contractor_client):
        response = contractor_client.get("/api/v1/contractors/me/")
        assert response.status_code == status.HTTP_200_OK

    def test_homeowner_cannot_access_contractor_me(self, homeowner_client):
        response = homeowner_client.get("/api/v1/contractors/me/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_contractor_profile(self, contractor_client):
        response = contractor_client.patch(
            "/api/v1/contractors/me/",
            {
                "company_name": "Elite Builders Kenya",
                "category": "electrical",
                "years_experience": 8,
                "hourly_rate": "2500.00",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["company_name"] == "Elite Builders Kenya"

    def test_add_portfolio_project_api(self, contractor_client):
        response = contractor_client.post(
            "/api/v1/contractors/me/portfolio/",
            {
                "title": "Karen Estate Renovation",
                "description": "Full renovation of 4-bed house in Karen.",
                "category": "renovation",
                "location": "Karen, Nairobi",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["title"] == "Karen Estate Renovation"

    def test_list_portfolio_projects_api(self, contractor_client, profile):
        PortfolioProject.objects.create(
            contractor=profile,
            title="Project A",
            description="Desc",
            category="general",
        )
        response = contractor_client.get("/api/v1/contractors/me/portfolio/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) >= 1

    def test_pagination_works(self, api_client, db):
        # Create 25 contractors
        for i in range(25):
            u = User.objects.create_user(
                email=f"c{i}@test.com", name=f"Contractor {i}",
                password="Passw0rd!", role="contractor",
            )
            ContractorProfile.objects.create(user=u)
        response = api_client.get(self.list_url + "?page_size=10")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 10
        assert response.json()["total_pages"] >= 3
