"""
Role-based permission classes used across the platform.
"""

from rest_framework.permissions import BasePermission

from apps.users.models import User


class IsHomeowner(BasePermission):
    """Grants access only to users with the 'homeowner' role."""

    message = "Only homeowners can perform this action."

    def has_permission(self, request, view) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.HOMEOWNER
        )


class IsContractor(BasePermission):
    """Grants access only to users with the 'contractor' role."""

    message = "Only contractors can perform this action."

    def has_permission(self, request, view) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.CONTRACTOR
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission: allow full access to the object owner,
    read-only access to everyone else.

    Assumes the model has an `owner` or `user` field.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        owner = getattr(obj, "owner", None) or getattr(obj, "user", None)
        return owner == request.user


class IsParticipant(BasePermission):
    """
    Object-level permission that checks if the requesting user is a participant
    in the relevant booking / project.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        # Works for Booking (homeowner / contractor fields)
        if hasattr(obj, "homeowner") and hasattr(obj, "contractor"):
            return obj.homeowner == user or obj.contractor == user
        # Works for Project (owner or ProjectMember)
        if hasattr(obj, "owner"):
            if obj.owner == user:
                return True
            if hasattr(obj, "members"):
                return obj.members.filter(user=user).exists()
        return False
