"""
Notifications service layer.

Creates persisted Notification records and pushes them over WebSocket.
"""

from __future__ import annotations

from apps.users.models import User

from .models import Notification


def create_notification(
    recipient: User,
    notification_type: str,
    title: str,
    message: str,
    metadata: dict | None = None,
) -> Notification:
    """
    Persist a notification and push it to the user's WebSocket channel.
    """
    notif = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        metadata=metadata or {},
    )

    # Push to WebSocket (fire-and-forget; failures are non-fatal)
    try:
        from .ws_utils import push_notification_to_user
        push_notification_to_user(recipient, notif)
    except Exception:
        pass  # WebSocket push failing should not break the main flow

    return notif


def mark_read(user: User, notification_id: str) -> Notification:
    from rest_framework.exceptions import NotFound

    try:
        notif = Notification.objects.get(id=notification_id, recipient=user)
    except Notification.DoesNotExist:
        raise NotFound("Notification not found.")
    notif.is_read = True
    notif.save(update_fields=["is_read"])
    return notif


def mark_all_read(user: User) -> int:
    """Mark all unread notifications for a user as read. Returns count updated."""
    return Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)


def get_unread_count(user: User) -> int:
    return Notification.objects.filter(recipient=user, is_read=False).count()


# ---------------------------------------------------------------------------
# Domain-specific factory helpers
# ---------------------------------------------------------------------------

def notify_new_booking(booking) -> None:
    """Notify contractor of a new booking request."""
    create_notification(
        recipient=booking.contractor,
        notification_type=Notification.Type.BOOKING_NEW,
        title="New Booking Request",
        message=f"{booking.homeowner.name} has sent you a booking request.",
        metadata={"booking_id": str(booking.id)},
    )


def notify_booking_status_change(booking) -> None:
    """Notify homeowner when contractor accepts or rejects."""
    type_map = {
        "accepted": Notification.Type.BOOKING_ACCEPTED,
        "rejected": Notification.Type.BOOKING_REJECTED,
        "completed": Notification.Type.BOOKING_COMPLETED,
    }
    notif_type = type_map.get(booking.status, Notification.Type.SYSTEM)
    verb = booking.status.capitalize()
    create_notification(
        recipient=booking.homeowner,
        notification_type=notif_type,
        title=f"Booking {verb}",
        message=f"Your booking with {booking.contractor.name} has been {booking.status}.",
        metadata={"booking_id": str(booking.id)},
    )


def notify_milestone_update(project, milestone, actor: User) -> None:
    """Notify all project members (except the actor) about a milestone change."""
    members = list(
        project.members.select_related("user").exclude(user=actor)
    )
    # Also notify the project owner if they weren't the actor
    recipients = {m.user for m in members}
    if project.owner != actor:
        recipients.add(project.owner)

    for recipient in recipients:
        create_notification(
            recipient=recipient,
            notification_type=Notification.Type.MILESTONE_UPDATED,
            title="Milestone Updated",
            message=f'"{milestone.title}" is now {milestone.status} on project "{project.title}".',
            metadata={
                "project_id": str(project.id),
                "milestone_id": str(milestone.id),
            },
        )


def notify_new_review(review) -> None:
    """Notify contractor about a new review."""
    create_notification(
        recipient=review.contractor,
        notification_type=Notification.Type.NEW_REVIEW,
        title="New Review",
        message=f"{review.reviewer.name} left you a {review.rating}★ review.",
        metadata={"review_id": str(review.id)},
    )
