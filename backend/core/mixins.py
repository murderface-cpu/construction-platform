"""
Reusable mixins and utility helpers for the construction platform.
"""

from __future__ import annotations

import uuid
from typing import Any

from django.db import models
from rest_framework.response import Response


# ---------------------------------------------------------------------------
# Abstract Model Mixins
# ---------------------------------------------------------------------------

class UUIDModel(models.Model):
    """
    Abstract base model that replaces the default integer PK with a UUID.
    Using UUID4 avoids enumeration attacks on public-facing IDs.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    """Abstract model that auto-populates created_at and updated_at fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampedModel):
    """
    Combines UUID primary key + timestamps.
    All domain models should inherit from this.
    """

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# View response helpers
# ---------------------------------------------------------------------------

def success_response(data: Any = None, message: str = "Success", status: int = 200) -> Response:
    """Wrap data in a consistent success envelope."""
    payload: dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return Response(payload, status=status)


def error_response(message: str, code: str = "error", status: int = 400) -> Response:
    """Return a consistent error envelope (for non-exception paths)."""
    return Response(
        {"success": False, "error": {"code": code, "message": message}},
        status=status,
    )
