"""Serializers for the projects app."""

from __future__ import annotations

from rest_framework import serializers

from apps.users.serializers import PublicUserSerializer

from .models import Milestone, Project, ProjectMember, ProjectUpdate


class MilestoneSerializer(serializers.ModelSerializer):
    assigned_to = PublicUserSerializer(read_only=True)
    assigned_to_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Milestone
        fields = [
            "id", "title", "description", "status", "priority",
            "due_date", "assigned_to", "assigned_to_id",
            "completed_at", "order", "created_at",
        ]
        read_only_fields = ["id", "completed_at", "created_at"]


class ProjectMemberSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]


class ProjectUpdateSerializer(serializers.ModelSerializer):
    author = PublicUserSerializer(read_only=True)

    class Meta:
        model = ProjectUpdate
        fields = ["id", "author", "event_type", "message", "metadata", "created_at"]
        read_only_fields = fields


class ProjectListSerializer(serializers.ModelSerializer):
    owner = PublicUserSerializer(read_only=True)
    progress = serializers.IntegerField(source="progress_percentage", read_only=True)
    milestone_count = serializers.IntegerField(source="milestones.count", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "title", "category", "status", "location",
            "start_date", "end_date", "budget", "progress",
            "milestone_count", "owner", "created_at",
        ]
        read_only_fields = ["id", "progress", "milestone_count", "created_at"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    owner = PublicUserSerializer(read_only=True)
    members = ProjectMemberSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    updates = ProjectUpdateSerializer(many=True, read_only=True)
    progress = serializers.IntegerField(source="progress_percentage", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "category", "status",
            "location", "budget", "actual_cost", "start_date", "end_date",
            "cover_image_key", "progress", "owner", "members",
            "milestones", "updates", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "progress", "created_at", "updated_at"]


class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "title", "description", "category", "location",
            "budget", "start_date", "end_date",
        ]


class AssignContractorSerializer(serializers.Serializer):
    contractor_id = serializers.UUIDField()
    role = serializers.ChoiceField(
        choices=ProjectMember.Role.choices,
        default=ProjectMember.Role.CONTRACTOR,
    )
