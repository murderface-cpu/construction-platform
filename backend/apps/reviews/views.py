"""Reviews views."""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import success_response
from core.pagination import StandardResultsPagination

from . import services
from .models import Review
from .serializers import CreateReviewSerializer, ReviewSerializer


class ReviewListCreateView(APIView):
    """
    POST /api/v1/reviews/                      — create review
    GET  /api/v1/reviews/?contractor_id={id}   — list reviews for a contractor
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request: Request) -> Response:
        contractor_id = request.query_params.get("contractor_id")
        qs = Review.objects.select_related("reviewer", "contractor")
        if contractor_id:
            qs = qs.filter(contractor_id=contractor_id)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(ReviewSerializer(page, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        review = services.create_review(
            reviewer=request.user,
            contractor_id=str(d["contractor_id"]),
            rating=d["rating"],
            comment=d.get("comment", ""),
            booking_id=str(d["booking_id"]) if d.get("booking_id") else None,
        )
        return Response(
            {"success": True, "data": ReviewSerializer(review).data},
            status=status.HTTP_201_CREATED,
        )
