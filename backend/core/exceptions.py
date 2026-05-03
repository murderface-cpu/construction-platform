"""
Custom exception handler that returns consistent error shapes across the API.

All error responses follow the format:
{
    "success": false,
    "error": {
        "code": "validation_error",
        "message": "...",
        "details": { ... }   # optional field-level errors
    }
}
"""

from typing import Any

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """
    Wrap DRF's default exception handler with a consistent response envelope.
    """
    # Let DRF handle the exception first
    response = exception_handler(exc, context)

    # Convert Django's own 404/403 if DRF didn't catch them
    if response is None:
        if isinstance(exc, Http404):
            response = Response(status=status.HTTP_404_NOT_FOUND)
            response.data = {}
        elif isinstance(exc, PermissionDenied):
            response = Response(status=status.HTTP_403_FORBIDDEN)
            response.data = {}
        elif isinstance(exc, ValidationError):
            response = Response(status=status.HTTP_400_BAD_REQUEST)
            response.data = {"detail": exc.message}
        else:
            return None

    error_payload = _build_error_payload(exc, response)
    response.data = {"success": False, "error": error_payload}
    return response


def _build_error_payload(exc: Exception, response: Response) -> dict[str, Any]:
    """Build a normalised error dict from an exception + DRF response."""
    http_status = response.status_code
    original_data = response.data if hasattr(response, "data") else {}

    if http_status == status.HTTP_400_BAD_REQUEST:
        code = "validation_error"
        message = "One or more fields are invalid."
        details = original_data
    elif http_status == status.HTTP_401_UNAUTHORIZED:
        code = "authentication_failed"
        message = _extract_detail(original_data, "Authentication credentials were not provided.")
        details = None
    elif http_status == status.HTTP_403_FORBIDDEN:
        code = "permission_denied"
        message = _extract_detail(original_data, "You do not have permission to perform this action.")
        details = None
    elif http_status == status.HTTP_404_NOT_FOUND:
        code = "not_found"
        message = _extract_detail(original_data, "The requested resource was not found.")
        details = None
    elif http_status == status.HTTP_429_TOO_MANY_REQUESTS:
        code = "throttled"
        message = _extract_detail(original_data, "Request was throttled.")
        details = None
    elif http_status >= 500:
        code = "server_error"
        message = "An internal server error occurred."
        details = None
    else:
        code = "error"
        message = _extract_detail(original_data, str(exc))
        details = original_data

    payload: dict[str, Any] = {"code": code, "message": message}
    if details:
        payload["details"] = details
    return payload


def _extract_detail(data: Any, fallback: str) -> str:
    """Pull a human-readable message out of DRF error data."""
    if isinstance(data, dict):
        detail = data.get("detail", "")
        if detail:
            return str(detail)
    if isinstance(data, list) and data:
        return str(data[0])
    return fallback
