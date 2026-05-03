"""Project management views."""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import success_response
from core.pagination import StandardResultsPagination

from . import services
from .serializers import (
    AssignContractorSerializer,
    MilestoneSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectWriteSerializer,
)


class ProjectListCreateView(APIView):
    """
    GET  /api/v1/projects/  — list projects the user owns or is member of
    POST /api/v1/projects/  — create a project (homeowner)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        projects = services.list_projects(request.user)
        status_filter = request.query_params.get("status")
        if status_filter:
            projects = [p for p in projects if p.status == status_filter]

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(projects, request)
        return paginator.get_paginated_response(
            ProjectListSerializer(page, many=True).data
        )

    def post(self, request: Request) -> Response:
        serializer = ProjectWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = services.create_project(request.user, **serializer.validated_data)
        return Response(
            {"success": True, "data": ProjectDetailSerializer(project).data},
            status=status.HTTP_201_CREATED,
        )


class ProjectDetailView(APIView):
    """
    GET   /api/v1/projects/{id}/  — full project details
    PATCH /api/v1/projects/{id}/  — update project (owner only)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk: str) -> Response:
        project = services.get_project(pk, request.user)
        return success_response(ProjectDetailSerializer(project).data)

    def patch(self, request: Request, pk: str) -> Response:
        serializer = ProjectWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        project = services.update_project(pk, request.user, **serializer.validated_data)
        return success_response(ProjectDetailSerializer(project).data)


class AssignContractorView(APIView):
    """POST /api/v1/projects/{id}/assign/"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk: str) -> Response:
        serializer = AssignContractorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = services.assign_contractor(
            project_id=pk,
            owner=request.user,
            contractor_id=str(serializer.validated_data["contractor_id"]),
            role=serializer.validated_data["role"],
        )
        return Response(
            {"success": True, "message": "Contractor assigned successfully."},
            status=status.HTTP_201_CREATED,
        )


class MilestoneListCreateView(APIView):
    """
    GET  /api/v1/projects/{id}/milestones/
    POST /api/v1/projects/{id}/milestones/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk: str) -> Response:
        project = services.get_project(pk, request.user)
        milestones = project.milestones.select_related("assigned_to").all()
        return success_response(MilestoneSerializer(milestones, many=True).data)

    def post(self, request: Request, pk: str) -> Response:
        serializer = MilestoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        milestone = services.create_milestone(
            project_id=pk, requestor=request.user, **data
        )
        return Response(
            {"success": True, "data": MilestoneSerializer(milestone).data},
            status=status.HTTP_201_CREATED,
        )


class MilestoneDetailView(APIView):
    """
    PATCH  /api/v1/projects/{id}/milestones/{mid}/
    DELETE /api/v1/projects/{id}/milestones/{mid}/
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, pk: str, mid: str) -> Response:
        serializer = MilestoneSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        milestone = services.update_milestone(
            milestone_id=mid,
            project_id=pk,
            requestor=request.user,
            **serializer.validated_data,
        )
        return success_response(MilestoneSerializer(milestone).data)

    def delete(self, request: Request, pk: str, mid: str) -> Response:
        services.delete_milestone(mid, pk, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
