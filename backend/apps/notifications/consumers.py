"""
Django Channels WebSocket consumer for real-time notifications.

Connection flow:
  1. Client connects to ws://host/ws/notifications/?token=<JWT>
  2. Consumer validates the token and joins the user's personal group.
  3. Server pushes JSON events to the group whenever something happens.
  4. Client can send {"action": "mark_read", "notification_id": "..."} to
     acknowledge a notification.

Group naming convention:
  - Per-user:    user_<user_id>
  - Per-project: project_<project_id>
"""

from __future__ import annotations

import json
import logging

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """Personal notification channel for a single authenticated user."""

    async def connect(self) -> None:
        user = await self._authenticate()
        if user is None:
            await self.close(code=4001)
            return

        self.user = user
        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send unread count on connect so client can badge the icon immediately
        unread = await self._get_unread_count()
        await self.send(text_data=json.dumps({"type": "connected", "unread_count": unread}))
        logger.info("WS connected: user=%s group=%s", user.id, self.group_name)

    async def disconnect(self, close_code: int) -> None:
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info("WS disconnected: code=%s", close_code)

    async def receive(self, text_data: str) -> None:
        """Handle messages sent from the client."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error("Invalid JSON.")
            return

        action = data.get("action")
        if action == "mark_read":
            await self._handle_mark_read(data.get("notification_id"))
        elif action == "mark_all_read":
            await self._handle_mark_all_read()
        elif action == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))
        else:
            await self._send_error(f"Unknown action: {action}")

    # ------------------------------------------------------------------
    # Channel layer event handlers (called by group_send from services)
    # ------------------------------------------------------------------

    async def notification_message(self, event: dict) -> None:
        """Push a new notification payload to this client."""
        await self.send(text_data=json.dumps({
            "type": "notification",
            "data": event["data"],
        }))

    async def project_event(self, event: dict) -> None:
        """Push a project-scoped event (milestone update, new member, etc.)."""
        await self.send(text_data=json.dumps({
            "type": "project_event",
            "event_type": event["event_type"],
            "data": event["data"],
        }))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _authenticate(self):
        """
        Validate JWT from query string and return the User instance, or None.
        """
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from rest_framework_simplejwt.tokens import AccessToken

        token_str = self._get_token_from_query()
        if not token_str:
            return None
        try:
            token = AccessToken(token_str)
            user_id = token["user_id"]
            return await self._get_user(user_id)
        except (InvalidToken, TokenError, Exception) as exc:
            logger.warning("WS auth failed: %s", exc)
            return None

    def _get_token_from_query(self) -> str | None:
        query_string = self.scope.get("query_string", b"").decode()
        for part in query_string.split("&"):
            if part.startswith("token="):
                return part[6:]
        return None

    @database_sync_to_async
    def _get_user(self, user_id: str):
        from apps.users.models import User
        try:
            return User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def _get_unread_count(self) -> int:
        from apps.notifications.models import Notification
        return Notification.objects.filter(recipient=self.user, is_read=False).count()

    @database_sync_to_async
    def _mark_notification_read(self, notification_id: str):
        from apps.notifications.models import Notification
        Notification.objects.filter(
            id=notification_id, recipient=self.user
        ).update(is_read=True)

    @database_sync_to_async
    def _mark_all_read(self) -> int:
        from apps.notifications.models import Notification
        return Notification.objects.filter(
            recipient=self.user, is_read=False
        ).update(is_read=True)

    async def _handle_mark_read(self, notification_id: str | None) -> None:
        if not notification_id:
            await self._send_error("notification_id is required.")
            return
        await self._mark_notification_read(notification_id)
        await self.send(text_data=json.dumps({
            "type": "marked_read",
            "notification_id": notification_id,
        }))

    async def _handle_mark_all_read(self) -> None:
        count = await self._mark_all_read()
        await self.send(text_data=json.dumps({
            "type": "all_marked_read",
            "count": count,
        }))

    async def _send_error(self, message: str) -> None:
        await self.send(text_data=json.dumps({"type": "error", "message": message}))


class ProjectConsumer(AsyncWebsocketConsumer):
    """
    Project-scoped channel — all members of a project receive live updates.
    ws://host/ws/projects/<project_id>/
    """

    async def connect(self) -> None:
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        user = await NotificationConsumer._authenticate(self)  # reuse JWT logic
        if user is None:
            await self.close(code=4001)
            return

        # Verify the user is actually a member of the project
        has_access = await self._check_project_access(user, self.project_id)
        if not has_access:
            await self.close(code=4003)
            return

        self.user = user
        self.group_name = f"project_{self.project_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data: str) -> None:
        """Clients can send comments / pings through the project socket."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if data.get("action") == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    async def project_event(self, event: dict) -> None:
        await self.send(text_data=json.dumps({
            "type": "project_event",
            "event_type": event["event_type"],
            "data": event["data"],
        }))

    @database_sync_to_async
    def _check_project_access(self, user, project_id: str) -> bool:
        from apps.projects.models import Project
        try:
            project = Project.objects.get(id=project_id)
            return project.owner == user or project.members.filter(user=user).exists()
        except Project.DoesNotExist:
            return False
