"""
Celery tasks for the notifications app.

All heavy I/O (email sending, bulk notification creation) runs here
so request/response cycles stay fast.
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Booking notification tasks
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_booking_notification(self, booking_id: str, event_type: str) -> None:
    """
    Create in-app notification + optional email for a booking event.

    event_type options:
        new_booking, booking_accepted, booking_rejected, booking_completed
    """
    try:
        from apps.bookings.models import Booking
        from apps.notifications.services import (
            notify_booking_status_change,
            notify_new_booking,
        )

        booking = (
            Booking.objects
            .select_related("homeowner", "contractor")
            .get(id=booking_id)
        )

        if event_type == "new_booking":
            notify_new_booking(booking)
            send_booking_email.delay(booking_id, event_type)
        else:
            notify_booking_status_change(booking)
            send_booking_email.delay(booking_id, event_type)

    except Exception as exc:
        logger.exception("send_booking_notification failed for booking %s", booking_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def send_booking_email(self, booking_id: str, event_type: str) -> None:
    """Send an email about a booking status change."""
    try:
        from apps.bookings.models import Booking

        booking = (
            Booking.objects
            .select_related("homeowner", "contractor")
            .get(id=booking_id)
        )

        subject_map = {
            "new_booking":         "New Booking Request",
            "booking_accepted":    "Your Booking Has Been Accepted",
            "booking_rejected":    "Your Booking Was Rejected",
            "booking_completed":   "Booking Completed",
        }

        # For new_booking, email goes to contractor; otherwise to homeowner
        if event_type == "new_booking":
            recipient = booking.contractor
            subject = f"New booking request from {booking.homeowner.name}"
        else:
            recipient = booking.homeowner
            subject = subject_map.get(event_type, "Booking Update")

        if not recipient.email:
            return

        message = _build_booking_email_body(booking, event_type, recipient)
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info("Booking email sent to %s for event %s", recipient.email, event_type)

    except Exception as exc:
        logger.exception("send_booking_email failed for booking %s", booking_id)
        raise self.retry(exc=exc)


def _build_booking_email_body(booking, event_type: str, recipient) -> str:
    lines = [
        f"Hello {recipient.name},",
        "",
    ]
    if event_type == "new_booking":
        lines += [
            f"{booking.homeowner.name} has sent you a booking request.",
            f"Scheduled: {booking.scheduled_start.strftime('%d %b %Y %H:%M')} – "
            f"{booking.scheduled_end.strftime('%H:%M')}",
            f"Location: {booking.location}",
            f"Description: {booking.description}",
            "",
            "Please log in to accept or reject this request.",
        ]
    elif event_type == "booking_accepted":
        lines += [
            f"Your booking with {booking.contractor.name} has been accepted!",
            f"Scheduled: {booking.scheduled_start.strftime('%d %b %Y %H:%M')}",
            f"Location: {booking.location}",
        ]
    elif event_type == "booking_rejected":
        lines += [
            f"Unfortunately, {booking.contractor.name} has rejected your booking request.",
        ]
        if booking.rejection_reason:
            lines.append(f"Reason: {booking.rejection_reason}")
    elif event_type == "booking_completed":
        lines += [
            f"Your booking with {booking.contractor.name} has been marked as completed.",
            "We'd love to hear your feedback — please leave a review!",
        ]

    lines += ["", "— The Construction Platform Team"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Milestone notification task
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_milestone_notification(self, milestone_id: str, project_id: str, actor_id: str) -> None:
    """Create in-app notifications for all project members when a milestone changes."""
    try:
        from apps.notifications.services import notify_milestone_update
        from apps.projects.models import Milestone, Project
        from apps.users.models import User

        milestone = Milestone.objects.select_related("project").get(id=milestone_id)
        project = Project.objects.prefetch_related("members__user").get(id=project_id)
        actor = User.objects.get(id=actor_id)

        notify_milestone_update(project, milestone, actor)

        # Real-time WS broadcast
        from apps.notifications.ws_utils import broadcast_project_event
        broadcast_project_event(
            project_id=str(project.id),
            event_type="milestone_updated",
            payload={
                "milestone_id": str(milestone.id),
                "title": milestone.title,
                "status": milestone.status,
                "updated_by": actor.name,
            },
        )
    except Exception as exc:
        logger.exception("send_milestone_notification failed for milestone %s", milestone_id)
        raise self.retry(exc=exc)


# ---------------------------------------------------------------------------
# Review notification task
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_review_notification(self, review_id: str) -> None:
    """Notify contractor of a new review and optionally email them."""
    try:
        from apps.notifications.services import notify_new_review
        from apps.reviews.models import Review

        review = Review.objects.select_related("reviewer", "contractor").get(id=review_id)
        notify_new_review(review)

        # Optional email
        if review.contractor.email:
            send_mail(
                subject=f"New {review.rating}★ review from {review.reviewer.name}",
                message=(
                    f"Hello {review.contractor.name},\n\n"
                    f"{review.reviewer.name} left you a {review.rating}-star review.\n\n"
                    f'"{review.comment}"\n\n'
                    "— The Construction Platform Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[review.contractor.email],
                fail_silently=True,
            )
    except Exception as exc:
        logger.exception("send_review_notification failed for review %s", review_id)
        raise self.retry(exc=exc)


# ---------------------------------------------------------------------------
# Periodic / housekeeping tasks
# ---------------------------------------------------------------------------

@shared_task
def cleanup_old_notifications() -> None:
    """
    Delete read notifications older than 90 days.
    Registered in Celery Beat to run weekly.
    """
    from datetime import timedelta

    from django.utils import timezone

    from apps.notifications.models import Notification

    cutoff = timezone.now() - timedelta(days=90)
    deleted, _ = Notification.objects.filter(is_read=True, created_at__lt=cutoff).delete()
    logger.info("Cleaned up %d old notifications", deleted)


@shared_task
def send_upcoming_booking_reminders() -> None:
    """
    Send reminder emails/notifications for bookings starting in the next 24 hours.
    Registered in Celery Beat to run every hour.
    """
    from datetime import timedelta

    from django.utils import timezone

    from apps.bookings.models import Booking
    from apps.notifications.services import create_notification
    from apps.notifications.models import Notification

    now = timezone.now()
    window_end = now + timedelta(hours=24)

    upcoming = Booking.objects.filter(
        status=Booking.Status.ACCEPTED,
        scheduled_start__gte=now,
        scheduled_start__lte=window_end,
    ).select_related("homeowner", "contractor")

    for booking in upcoming:
        starts_in = booking.scheduled_start - now
        hours = int(starts_in.total_seconds() / 3600)

        for recipient in [booking.homeowner, booking.contractor]:
            # Avoid duplicate reminders
            already_sent = Notification.objects.filter(
                recipient=recipient,
                notification_type=Notification.Type.SYSTEM,
                metadata__booking_id=str(booking.id),
                metadata__reminder=True,
            ).exists()
            if already_sent:
                continue

            create_notification(
                recipient=recipient,
                notification_type=Notification.Type.SYSTEM,
                title="Upcoming Booking Reminder",
                message=f"You have a booking in approximately {hours} hour(s).",
                metadata={"booking_id": str(booking.id), "reminder": True},
            )
