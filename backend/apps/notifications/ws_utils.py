"""
WebSocket push utilities.

These helpers are called from synchronous service/task code and use
asgiref's async_to_sync wrapper to push into the channel layer.
"""

from __future__ import annotations

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def _get_layer():
    layer = get_channel_layer()
    if layer is None:
        logger.warning("Channel layer not configured — WebSocket push skipped.")
    return layer


def push_notification_to_user(user, notification) -> None:
    """
    Push a persisted Notification object to the user's personal WS group.
    Safe to call from sync code (views, services, Celery tasks).
    """
    layer = _get_layer()
    if layer is None:
        return

    from apps.notifications.serializers import NotificationSerializer
    payload = NotificationSerializer(notification).data

    try:
        async_to_sync(layer.group_send)(
            f"user_{user.id}",
            {
                "type": "notification_message",
                "data": payload,
            },
        )
    except Exception as exc:
        logger.exception("Failed to push notification to user %s: %s", user.id, exc)


def broadcast_project_event(
    project_id: str,
    event_type: str,
    payload: dict,
) -> None:
    """
    Broadcast an event to all WebSocket clients watching a project.

    Args:
        project_id: UUID string of the project.
        event_type: e.g. 'milestone_updated', 'member_added', 'status_changed'
        payload: Arbitrary serialisable dict.
    """
    layer = _get_layer()
    if layer is None:
        return

    try:
        async_to_sync(layer.group_send)(
            f"project_{project_id}",
            {
                "type": "project_event",
                "event_type": event_type,
                "data": payload,
            },
        )
    except Exception as exc:
        logger.exception(
            "Failed to broadcast project event %s for project %s: %s",
            event_type, project_id, exc,
        )


def push_booking_event(booking_id: str, event_type: str, recipient_ids: list[str]) -> None:
    """
    Push a booking event to specific users' personal WS groups.
    """
    layer = _get_layer()
    if layer is None:
        return

    for uid in recipient_ids:
        try:
            async_to_sync(layer.group_send)(
                f"user_{uid}",
                {
                    "type": "notification_message",
                    "data": {
                        "event_type": event_type,
                        "booking_id": booking_id,
                    },
                },
            )
        except Exception as exc:
            logger.exception("Failed to push booking event to user %s: %s", uid, exc)
