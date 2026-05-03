"""Designs views."""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import success_response
from core.pagination import StandardResultsPagination

from . import services
from .models import SavedDesign
from .serializers import DesignDetailSerializer, DesignListSerializer


class DesignListView(APIView):
    """GET /api/v1/designs/"""
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        qs = services.list_designs(
            category=request.query_params.get("category", ""),
            search=request.query_params.get("search", ""),
        )
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(DesignListSerializer(page, many=True).data)


class DesignDetailView(APIView):
    """GET /api/v1/designs/{id}/"""
    permission_classes = [AllowAny]

    def get(self, request: Request, pk: str) -> Response:
        design = services.get_design(pk)
        return success_response(DesignDetailSerializer(design).data)


class SaveDesignView(APIView):
    """
    POST   /api/v1/designs/{id}/save/    — bookmark
    DELETE /api/v1/designs/{id}/save/    — remove bookmark
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk: str) -> Response:
        services.save_design(request.user, pk)
        return Response({"success": True, "message": "Design saved."}, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, pk: str) -> Response:
        services.unsave_design(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MySavedDesignsView(APIView):
    """GET /api/v1/designs/saved/"""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        saved = SavedDesign.objects.filter(user=request.user).select_related("design")
        designs = [s.design for s in saved]
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(designs, request)
        return paginator.get_paginated_response(DesignListSerializer(page, many=True).data)
