"""
Marketplace views — contractor profiles and portfolios.
"""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from core.mixins import success_response
from core.pagination import StandardResultsPagination
from core.permissions import IsContractor
from core.storage import generate_presigned_upload_url

from . import services
from .serializers import (
    ContractorListSerializer,
    ContractorProfileSerializer,
    ContractorProfileUpdateSerializer,
    PortfolioProjectSerializer,
    PortfolioProjectWriteSerializer,
)


class ContractorListView(APIView):
    """
    GET /api/v1/contractors/
    Public listing with filtering and pagination.
    """

    permission_classes = [AllowAny]
    serializer_class = ContractorListSerializer

    @extend_schema(responses={200: ContractorListSerializer(many=True)})
    def get(self, request: Request) -> Response:
        qs = services.list_contractors(
            location=request.query_params.get("location", ""),
            category=request.query_params.get("category", ""),
            min_rating=request.query_params.get("min_rating"),
            search=request.query_params.get("search", ""),
            availability=request.query_params.get("availability", ""),
        )

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ContractorListSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class ContractorDetailView(APIView):
    """
    GET /api/v1/contractors/{id}/
    Full contractor profile including portfolio.
    """

    permission_classes = [AllowAny]
    serializer_class = ContractorProfileSerializer

    @extend_schema(responses={200: ContractorProfileSerializer})
    def get(self, request: Request, pk: str) -> Response:
        profile = services.get_contractor_profile(pk)
        serializer = ContractorProfileSerializer(profile, context={"request": request})
        return success_response(serializer.data)


class MyContractorProfileView(APIView):
    """
    GET  /api/v1/contractors/me/   — view own profile
    PATCH /api/v1/contractors/me/  — update own profile
    """

    permission_classes = [IsAuthenticated, IsContractor]
    serializer_class = ContractorProfileSerializer

    @extend_schema(responses={200: ContractorProfileSerializer})
    def get(self, request: Request) -> Response:
        profile = services.get_or_create_contractor_profile(request.user)
        serializer = ContractorProfileSerializer(profile, context={"request": request})
        return success_response(serializer.data)

    @extend_schema(request=ContractorProfileUpdateSerializer, responses={200: ContractorProfileSerializer})
    def patch(self, request: Request) -> Response:
        serializer = ContractorProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = services.update_contractor_profile(request.user, **serializer.validated_data)
        return success_response(
            ContractorProfileSerializer(profile, context={"request": request}).data,
            message="Profile updated.",
        )


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

class PortfolioView(APIView):
    """
    GET  /api/v1/contractors/me/portfolio/         — list own portfolio projects
    POST /api/v1/contractors/me/portfolio/         — add a portfolio project
    """

    permission_classes = [IsAuthenticated, IsContractor]
    serializer_class = PortfolioProjectSerializer

    @extend_schema(responses={200: PortfolioProjectSerializer(many=True)})
    def get(self, request: Request) -> Response:
        profile = services.get_or_create_contractor_profile(request.user)
        projects = profile.portfolio_projects.prefetch_related("images").all()
        serializer = PortfolioProjectSerializer(projects, many=True, context={"request": request})
        return success_response(serializer.data)

    @extend_schema(request=PortfolioProjectWriteSerializer, responses={201: PortfolioProjectSerializer})
    def post(self, request: Request) -> Response:
        profile = services.get_or_create_contractor_profile(request.user)
        serializer = PortfolioProjectWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = services.add_portfolio_project(profile, **serializer.validated_data)
        return Response(
            {"success": True, "data": PortfolioProjectSerializer(project, context={"request": request}).data},
            status=status.HTTP_201_CREATED,
        )


class PortfolioProjectDetailView(APIView):
    """
    PATCH  /api/v1/contractors/me/portfolio/{id}/
    DELETE /api/v1/contractors/me/portfolio/{id}/
    """

    permission_classes = [IsAuthenticated, IsContractor]
    serializer_class = PortfolioProjectWriteSerializer

    @extend_schema(request=PortfolioProjectWriteSerializer, responses={200: PortfolioProjectSerializer})
    def patch(self, request: Request, pk: str) -> Response:
        profile = services.get_or_create_contractor_profile(request.user)
        serializer = PortfolioProjectWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        project = services.update_portfolio_project(pk, profile, **serializer.validated_data)
        return success_response(PortfolioProjectSerializer(project, context={"request": request}).data)

    @extend_schema(responses={204: None})
    def delete(self, request: Request, pk: str) -> Response:
        profile = services.get_or_create_contractor_profile(request.user)
        services.delete_portfolio_project(pk, profile)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PortfolioImageUploadURLView(APIView):
    """
    POST /api/v1/contractors/me/portfolio/{id}/upload-url/
    Returns a presigned S3 URL for uploading a portfolio image.
    """

    permission_classes = [IsAuthenticated, IsContractor]

    @extend_schema(request=None, responses={200: None})
    def post(self, request: Request, pk: str) -> Response:
        filename = request.data.get("filename", "image.jpg")
        content_type = request.data.get("content_type", "image/jpeg")
        result = generate_presigned_upload_url(
            folder=f"portfolio/{request.user.id}/{pk}",
            filename=filename,
            content_type=content_type,
        )
        return success_response(result)
