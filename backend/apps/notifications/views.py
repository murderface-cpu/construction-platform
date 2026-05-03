"""Notification REST views."""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import success_response
from core.pagination import StandardResultsPagination

from . import services
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    """
    GET /api/v1/notifications/
    Returns paginated notifications for the authenticated user.
    Query params:
        unread=true   — filter to unread only
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        qs = Notification.objects.filter(recipient=request.user)
        if request.query_params.get("unread", "").lower() == "true":
            qs = qs.filter(is_read=False)

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = NotificationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class NotificationUnreadCountView(APIView):
    """GET /api/v1/notifications/unread-count/"""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        count = services.get_unread_count(request.user)
        return success_response({"unread_count": count})


class MarkNotificationReadView(APIView):
    """
    PATCH /api/v1/notifications/{id}/read/  — mark one as read
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, pk: str) -> Response:
        notification = services.mark_read(request.user, pk)
        return success_response(
            NotificationSerializer(notification).data,
            message="Notification marked as read.",
        )


class MarkAllNotificationsReadView(APIView):
    """POST /api/v1/notifications/mark-all-read/"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        count = services.mark_all_read(request.user)
        return success_response(
            {"updated_count": count},
            message=f"{count} notification(s) marked as read.",
        )
