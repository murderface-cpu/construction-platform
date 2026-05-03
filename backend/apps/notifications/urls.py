"""URL routes for the notifications app."""

from django.urls import path

from .views import (
    MarkAllNotificationsReadView,
    MarkNotificationReadView,
    NotificationListView,
    NotificationUnreadCountView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("unread-count/", NotificationUnreadCountView.as_view(), name="notification-unread-count"),
    path("mark-all-read/", MarkAllNotificationsReadView.as_view(), name="notification-mark-all-read"),
    path("<uuid:pk>/read/", MarkNotificationReadView.as_view(), name="notification-mark-read"),
]
