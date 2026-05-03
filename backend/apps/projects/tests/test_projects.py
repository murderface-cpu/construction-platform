"""
Tests for the projects app — models, services, and API endpoints.
"""

from __future__ import annotations

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Milestone, Project, ProjectMember, ProjectUpdate
from apps.projects import services
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
        email="owner@project.test",
        name="Project Owner",
        password="Passw0rd!",
        role=User.Role.HOMEOWNER,
    )


@pytest.fixture
def contractor(db) -> User:
    return User.objects.create_user(
        email="builder@project.test",
        name="Site Builder",
        password="Passw0rd!",
        role=User.Role.CONTRACTOR,
    )


@pytest.fixture
def other_homeowner(db) -> User:
    return User.objects.create_user(
        email="other@project.test",
        name="Other Owner",
        password="Passw0rd!",
        role=User.Role.HOMEOWNER,
    )


@pytest.fixture
def owner_client(api_client, homeowner) -> APIClient:
    api_client.force_authenticate(user=homeowner)
    return api_client


@pytest.fixture
def contractor_client(api_client, contractor) -> APIClient:
    api_client.force_authenticate(user=contractor)
    return api_client


@pytest.fixture
def project(homeowner) -> Project:
    return services.create_project(
        owner=homeowner,
        title="Kitchen Renovation",
        description="Full kitchen remodel including cabinets and countertops.",
        category=Project.Category.RENOVATION,
        location="15 Acacia Avenue, Nairobi",
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProjectModel:

    def test_project_creation(self, project):
        assert project.title == "Kitchen Renovation"
        assert project.status == Project.Status.DRAFT
        assert project.owner is not None

    def test_progress_with_no_milestones(self, project):
        assert project.progress_percentage == 0

    def test_progress_calculation(self, project):
        Milestone.objects.create(
            project=project, title="Demo", status=Milestone.Status.COMPLETED
        )
        Milestone.objects.create(
            project=project, title="Plumbing", status=Milestone.Status.TODO
        )
        Milestone.objects.create(
            project=project, title="Tiling", status=Milestone.Status.COMPLETED
        )
        # Refresh from DB to recalculate
        project.refresh_from_db()
        assert project.progress_percentage == 66  # 2/3 = 66%

    def test_project_str(self, project):
        assert "Kitchen Renovation" in str(project)


# ---------------------------------------------------------------------------
# Service layer tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProjectService:

    def test_create_project_success(self, homeowner):
        proj = services.create_project(
            owner=homeowner,
            title="Bathroom Remodel",
            description="Replace tiles and fixtures.",
            category="renovation",
            location="10 Test St",
        )
        assert proj.id is not None
        # Should have created an activity log entry
        assert ProjectUpdate.objects.filter(project=proj).count() == 1

    def test_contractor_cannot_create_project(self, contractor):
        from rest_framework.exceptions import ValidationError
        with pytest.raises(ValidationError, match="homeowners"):
            services.create_project(
                owner=contractor,
                title="Should Fail",
                description="Contractors can't own projects.",
                category="renovation",
                location="Nowhere",
            )

    def test_get_project_as_owner(self, homeowner, project):
        fetched = services.get_project(str(project.id), homeowner)
        assert fetched.id == project.id

    def test_get_project_denied_for_non_member(self, other_homeowner, project):
        from rest_framework.exceptions import PermissionDenied
        with pytest.raises(PermissionDenied):
            services.get_project(str(project.id), other_homeowner)

    def test_get_project_as_member(self, homeowner, contractor, project):
        ProjectMember.objects.create(
            project=project, user=contractor, role=ProjectMember.Role.CONTRACTOR
        )
        fetched = services.get_project(str(project.id), contractor)
        assert fetched.id == project.id

    def test_list_projects_includes_owned_and_member(self, homeowner, contractor, project):
        # Contractor added as member
        ProjectMember.objects.create(
            project=project, user=contractor, role=ProjectMember.Role.CONTRACTOR
        )
        contractor_projects = services.list_projects(contractor)
        assert any(p.id == project.id for p in contractor_projects)

    def test_update_project_status_creates_log(self, homeowner, project):
        services.update_project(str(project.id), homeowner, status=Project.Status.ACTIVE)
        project.refresh_from_db()
        assert project.status == Project.Status.ACTIVE
        logs = ProjectUpdate.objects.filter(
            project=project,
            event_type=ProjectUpdate.EventType.STATUS_CHANGED,
        )
        assert logs.count() == 1

    def test_assign_contractor_success(self, homeowner, contractor, project):
        member = services.assign_contractor(
            str(project.id), homeowner, str(contractor.id)
        )
        assert member.user == contractor
        assert member.role == ProjectMember.Role.CONTRACTOR

    def test_assign_same_contractor_twice_raises(self, homeowner, contractor, project):
        from rest_framework.exceptions import ValidationError
        services.assign_contractor(str(project.id), homeowner, str(contractor.id))
        with pytest.raises(ValidationError, match="already a member"):
            services.assign_contractor(str(project.id), homeowner, str(contractor.id))


@pytest.mark.django_db
class TestMilestoneService:

    def test_create_milestone(self, homeowner, project):
        ms = services.create_milestone(
            project_id=str(project.id),
            requestor=homeowner,
            title="Foundation Work",
            description="Pour the concrete foundation.",
            priority=Milestone.Priority.HIGH,
        )
        assert ms.project == project
        assert ms.status == Milestone.Status.TODO

    def test_update_milestone_status(self, homeowner, project):
        ms = services.create_milestone(
            project_id=str(project.id),
            requestor=homeowner,
            title="Roofing",
        )
        updated = services.update_milestone(
            milestone_id=str(ms.id),
            project_id=str(project.id),
            requestor=homeowner,
            status=Milestone.Status.COMPLETED,
        )
        assert updated.status == Milestone.Status.COMPLETED
        assert updated.completed_at is not None

    def test_update_milestone_creates_activity_log(self, homeowner, project):
        ms = services.create_milestone(
            project_id=str(project.id),
            requestor=homeowner,
            title="Electrical Wiring",
        )
        services.update_milestone(
            milestone_id=str(ms.id),
            project_id=str(project.id),
            requestor=homeowner,
            status=Milestone.Status.IN_PROGRESS,
        )
        logs = ProjectUpdate.objects.filter(
            project=project,
            event_type=ProjectUpdate.EventType.MILESTONE_UPDATED,
        )
        assert logs.count() >= 1

    def test_delete_milestone(self, homeowner, project):
        ms = services.create_milestone(
            project_id=str(project.id),
            requestor=homeowner,
            title="Demolition",
        )
        services.delete_milestone(str(ms.id), str(project.id), homeowner)
        assert not Milestone.objects.filter(id=ms.id).exists()

    def test_non_member_cannot_create_milestone(self, other_homeowner, project):
        from rest_framework.exceptions import PermissionDenied
        with pytest.raises(PermissionDenied):
            services.create_milestone(
                project_id=str(project.id),
                requestor=other_homeowner,
                title="Sneaky Milestone",
            )


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProjectAPI:
    list_url = "/api/v1/projects/"

    def test_create_project(self, owner_client):
        payload = {
            "title": "New Build Home",
            "description": "Build a 3-bedroom house from scratch.",
            "category": "new_build",
            "location": "Plot 45, Karen, Nairobi",
        }
        response = owner_client.post(self.list_url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert data["title"] == "New Build Home"
        assert data["status"] == "draft"

    def test_list_projects(self, owner_client, project):
        response = owner_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] >= 1

    def test_get_project_detail(self, owner_client, project):
        response = owner_client.get(f"{self.list_url}{project.id}/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["id"] == str(project.id)
        assert "milestones" in data
        assert "members" in data

    def test_update_project(self, owner_client, project):
        response = owner_client.patch(
            f"{self.list_url}{project.id}/",
            {"status": "active", "title": "Updated Kitchen Reno"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["status"] == "active"

    def test_assign_contractor(self, owner_client, contractor, project):
        response = owner_client.post(
            f"{self.list_url}{project.id}/assign/",
            {"contractor_id": str(contractor.id), "role": "contractor"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert ProjectMember.objects.filter(project=project, user=contractor).exists()

    def test_unauthenticated_cannot_list_projects(self, api_client):
        response = api_client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMilestoneAPI:

    @pytest.fixture
    def active_project(self, homeowner) -> Project:
        return services.create_project(
            owner=homeowner,
            title="Active Project",
            description="An active construction project.",
            category="renovation",
            location="Test Location",
            status=Project.Status.ACTIVE,
        )

    def test_create_milestone(self, owner_client, active_project):
        url = f"/api/v1/projects/{active_project.id}/milestones/"
        payload = {
            "title": "Site Preparation",
            "description": "Clear the site and set up temporary fencing.",
            "priority": "high",
        }
        response = owner_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["title"] == "Site Preparation"

    def test_list_milestones(self, owner_client, active_project):
        Milestone.objects.create(project=active_project, title="Step 1")
        Milestone.objects.create(project=active_project, title="Step 2")
        url = f"/api/v1/projects/{active_project.id}/milestones/"
        response = owner_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) == 2

    def test_update_milestone_via_api(self, owner_client, active_project):
        ms = Milestone.objects.create(
            project=active_project, title="Install Windows", status="todo"
        )
        url = f"/api/v1/projects/{active_project.id}/milestones/{ms.id}/"
        response = owner_client.patch(url, {"status": "in_progress"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["status"] == "in_progress"

    def test_delete_milestone_via_api(self, owner_client, active_project):
        ms = Milestone.objects.create(project=active_project, title="To Delete")
        url = f"/api/v1/projects/{active_project.id}/milestones/{ms.id}/"
        response = owner_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Milestone.objects.filter(id=ms.id).exists()

    def test_contractor_member_can_update_milestone(self, contractor_client, contractor, active_project):
        ProjectMember.objects.create(
            project=active_project, user=contractor, role=ProjectMember.Role.CONTRACTOR
        )
        ms = Milestone.objects.create(project=active_project, title="Plumbing Rough-In")
        url = f"/api/v1/projects/{active_project.id}/milestones/{ms.id}/"
        response = contractor_client.patch(url, {"status": "completed"}, format="json")
        assert response.status_code == status.HTTP_200_OK
