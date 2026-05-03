"""URL routes for the bookings app."""

from django.urls import path

from .views import (
    AvailabilitySlotView,
    BookingCancelView,
    BookingCompleteView,
    BookingDetailView,
    BookingListCreateView,
    BookingStatusView,
)

urlpatterns = [
    path("", BookingListCreateView.as_view(), name="booking-list-create"),
    path("<uuid:pk>/", BookingDetailView.as_view(), name="booking-detail"),
    path("<uuid:pk>/status/", BookingStatusView.as_view(), name="booking-status"),
    path("<uuid:pk>/complete/", BookingCompleteView.as_view(), name="booking-complete"),
    path("<uuid:pk>/cancel/", BookingCancelView.as_view(), name="booking-cancel"),
    path("availability/", AvailabilitySlotView.as_view(), name="availability-slots"),
]
