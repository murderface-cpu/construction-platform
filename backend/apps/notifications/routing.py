"""WebSocket URL routing for Django Channels."""

from django.urls import re_path
from .consumers import NotificationConsumer, ProjectConsumer

websocket_urlpatterns = [
    re_path(r"^ws/notifications/$", NotificationConsumer.as_asgi()),
    re_path(r"^ws/projects/(?P<project_id>[0-9a-f-]+)/$", ProjectConsumer.as_asgi()),
]
