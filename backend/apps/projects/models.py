"""
Project management models.

Project       — a construction/renovation project owned by a homeowner.
ProjectMember — participants (contractor, supervisor, etc.) on a project.
Milestone     — trackable deliverable within a project.
ProjectUpdate — activity log / feed entries for a project.
"""

from __future__ import annotations

from django.db import models

from apps.users.models import User
from core.mixins import BaseModel


class Project(BaseModel):
    """A construction/renovation project managed on the platform."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Category(models.TextChoices):
        RENOVATION = "renovation", "Renovation"
        NEW_BUILD = "new_build", "New Build"
        REPAIR = "repair", "Repair"
        LANDSCAPING = "landscaping", "Landscaping"
        INTERIOR = "interior", "Interior Design"
        COMMERCIAL = "commercial", "Commercial"
        OTHER = "other", "Other"

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        limit_choices_to={"role": User.Role.HOMEOWNER},
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.RENOVATION)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # Budget
    budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    # Timeline
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Cover image
    cover_image_key = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = "projects"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
        ]

    def __str__(self) -> str:
        return f"Project: {self.title} ({self.status})"

    @property
    def progress_percentage(self) -> int:
        """Calculate % of milestones completed."""
        milestones = self.milestones.all()
        total = milestones.count()
        if total == 0:
            return 0
        completed = milestones.filter(status=Milestone.Status.COMPLETED).count()
        return int((completed / total) * 100)


class ProjectMember(BaseModel):
    """A user who has been assigned to a project (typically the contractor)."""

    class Role(models.TextChoices):
        CONTRACTOR = "contractor", "Contractor"
        SUPERVISOR = "supervisor", "Supervisor"
        CONSULTANT = "consultant", "Consultant"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CONTRACTOR)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_members"
        unique_together = [("project", "user")]

    def __str__(self) -> str:
        return f"{self.user.name} on {self.project.title} ({self.role})"


class Milestone(BaseModel):
    """A trackable deliverable within a project."""

    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        BLOCKED = "blocked", "Blocked"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_milestones",
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "milestones"
        ordering = ["order", "due_date"]

    def __str__(self) -> str:
        return f"Milestone: {self.title} ({self.status})"


class ProjectUpdate(BaseModel):
    """Activity feed entry — records what happened on a project."""

    class EventType(models.TextChoices):
        CREATED = "project_created", "Project Created"
        STATUS_CHANGED = "status_changed", "Status Changed"
        MILESTONE_UPDATED = "milestone_updated", "Milestone Updated"
        MEMBER_ADDED = "member_added", "Member Added"
        FILE_UPLOADED = "file_uploaded", "File Uploaded"
        COMMENT = "comment", "Comment"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="updates")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="project_updates")
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "project_updates"
        ordering = ["-created_at"]
