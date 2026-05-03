"""
Project management service layer.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.users.models import User

from .models import Milestone, Project, ProjectMember, ProjectUpdate


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------

def create_project(owner: User, **fields) -> Project:
    """Create a new project and log the creation event."""
    if not owner.is_homeowner:
        raise ValidationError("Only homeowners can create projects.")

    with transaction.atomic():
        project = Project.objects.create(owner=owner, **fields)
        ProjectUpdate.objects.create(
            project=project,
            author=owner,
            event_type=ProjectUpdate.EventType.CREATED,
            message=f'Project "{project.title}" was created.',
        )
    return project


def get_project(project_id: str, user: User) -> Project:
    """
    Retrieve a project, checking that the user is the owner or a member.
    """
    try:
        project = Project.objects.prefetch_related(
            "milestones", "members__user", "updates"
        ).get(id=project_id)
    except Project.DoesNotExist:
        raise NotFound("Project not found.")

    is_owner = project.owner == user
    is_member = project.members.filter(user=user).exists()
    if not is_owner and not is_member:
        raise PermissionDenied("You do not have access to this project.")

    return project


def list_projects(user: User) -> list[Project]:
    """Return all projects the user owns or is a member of."""
    owned = Project.objects.filter(owner=user)
    member_of = Project.objects.filter(members__user=user)
    return (owned | member_of).distinct().select_related("owner").prefetch_related("milestones")


def update_project(project_id: str, owner: User, **fields) -> Project:
    try:
        project = Project.objects.get(id=project_id, owner=owner)
    except Project.DoesNotExist:
        raise NotFound("Project not found or you are not the owner.")

    old_status = project.status
    for key, value in fields.items():
        setattr(project, key, value)
    project.save()

    if "status" in fields and fields["status"] != old_status:
        ProjectUpdate.objects.create(
            project=project,
            author=owner,
            event_type=ProjectUpdate.EventType.STATUS_CHANGED,
            message=f'Project status changed from "{old_status}" to "{fields["status"]}".',
            metadata={"old": old_status, "new": fields["status"]},
        )
    return project


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

def assign_contractor(project_id: str, owner: User, contractor_id: str, role: str = ProjectMember.Role.CONTRACTOR) -> ProjectMember:
    """Add a contractor (or other member) to a project."""
    try:
        project = Project.objects.get(id=project_id, owner=owner)
    except Project.DoesNotExist:
        raise NotFound("Project not found.")

    try:
        contractor = User.objects.get(id=contractor_id)
    except User.DoesNotExist:
        raise NotFound("User not found.")

    if ProjectMember.objects.filter(project=project, user=contractor).exists():
        raise ValidationError("This user is already a member of the project.")

    with transaction.atomic():
        member = ProjectMember.objects.create(project=project, user=contractor, role=role)
        ProjectUpdate.objects.create(
            project=project,
            author=owner,
            event_type=ProjectUpdate.EventType.MEMBER_ADDED,
            message=f"{contractor.name} was added as {role}.",
        )
    return member


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------

def create_milestone(project_id: str, requestor: User, **fields) -> Milestone:
    project = _get_project_for_member(project_id, requestor)
    milestone = Milestone.objects.create(project=project, **fields)
    ProjectUpdate.objects.create(
        project=project,
        author=requestor,
        event_type=ProjectUpdate.EventType.MILESTONE_UPDATED,
        message=f'Milestone "{milestone.title}" was created.',
    )
    return milestone


def update_milestone(milestone_id: str, project_id: str, requestor: User, **fields) -> Milestone:
    project = _get_project_for_member(project_id, requestor)
    try:
        milestone = Milestone.objects.get(id=milestone_id, project=project)
    except Milestone.DoesNotExist:
        raise NotFound("Milestone not found.")

    old_status = milestone.status
    for key, value in fields.items():
        setattr(milestone, key, value)

    if "status" in fields and fields["status"] == Milestone.Status.COMPLETED:
        milestone.completed_at = timezone.now()

    milestone.save()

    if "status" in fields and fields["status"] != old_status:
        ProjectUpdate.objects.create(
            project=project,
            author=requestor,
            event_type=ProjectUpdate.EventType.MILESTONE_UPDATED,
            message=f'Milestone "{milestone.title}" moved to "{fields["status"]}".',
            metadata={"milestone_id": str(milestone_id), "old": old_status, "new": fields["status"]},
        )

        # Push real-time WebSocket event
        from apps.notifications.ws_utils import broadcast_project_event
        broadcast_project_event(
            project_id=str(project_id),
            event_type="milestone_updated",
            payload={
                "milestone_id": str(milestone.id),
                "title": milestone.title,
                "status": milestone.status,
            },
        )

    return milestone


def delete_milestone(milestone_id: str, project_id: str, owner: User) -> None:
    try:
        project = Project.objects.get(id=project_id, owner=owner)
        milestone = Milestone.objects.get(id=milestone_id, project=project)
        milestone.delete()
    except (Project.DoesNotExist, Milestone.DoesNotExist):
        raise NotFound("Milestone not found.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_project_for_member(project_id: str, user: User) -> Project:
    """Return project if user is owner or member, else raise."""
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise NotFound("Project not found.")
    is_owner = project.owner == user
    is_member = project.members.filter(user=user).exists()
    if not is_owner and not is_member:
        raise PermissionDenied("You are not a member of this project.")
    return project
