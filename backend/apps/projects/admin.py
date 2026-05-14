"""Admin configuration for projects app."""

from django.contrib import admin
from .models import Project, ProjectMember, Milestone, ProjectUpdate


class MilestoneInline(admin.TabularInline):
    """Inline for Milestone."""

    model = Milestone
    extra = 0
    fields = ["title", "status", "priority", "due_date", "assigned_to"]


class ProjectMemberInline(admin.TabularInline):
    """Inline for ProjectMember."""

    model = ProjectMember
    extra = 1
    fields = ["user", "role", "joined_at"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for Project."""

    list_display = ["title", "owner", "category", "status", "budget", "start_date", "end_date", "created_at"]
    list_filter = ["status", "category", "created_at"]
    search_fields = ["title", "description", "owner__email", "owner__name"]
    raw_id_fields = ["owner"]
    inlines = [ProjectMemberInline, MilestoneInline]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """Admin for ProjectMember."""

    list_display = ["user", "project", "role", "joined_at"]
    list_filter = ["role", "joined_at"]
    search_fields = ["user__email", "user__name", "project__title"]
    raw_id_fields = ["user", "project"]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    """Admin for Milestone."""

    list_display = ["title", "project", "status", "priority", "due_date", "assigned_to", "created_at"]
    list_filter = ["status", "priority", "created_at"]
    search_fields = ["title", "description", "project__title"]
    raw_id_fields = ["project", "assigned_to"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    """Admin for ProjectUpdate."""

    list_display = ["project", "event_type", "author", "created_at"]
    list_filter = ["event_type", "created_at"]
    search_fields = ["message", "project__title", "author__name"]
    raw_id_fields = ["project", "author"]