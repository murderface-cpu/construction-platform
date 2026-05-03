"""
User service layer.

All business logic lives here; views remain thin.
"""

from __future__ import annotations

from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import ValidationError

from .models import User


def register_user(
    email: str,
    name: str,
    password: str,
    role: str = User.Role.HOMEOWNER,
    location: str = "",
    phone: str = "",
) -> User:
    """
    Create a new user account.

    Raises:
        ValidationError: If the email is already taken.
    """
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError({"email": "A user with this email already exists."})

    user = User.objects.create_user(
        email=email,
        name=name,
        password=password,
        role=role,
        location=location,
        phone=phone,
    )
    return user


def update_profile(user: User, **fields) -> User:
    """
    Update allowed profile fields on a user instance.

    Returns the updated user.
    """
    allowed = {"name", "location", "bio", "phone", "profile_image"}
    for key, value in fields.items():
        if key in allowed:
            setattr(user, key, value)
    user.save(update_fields=list(fields.keys()))
    return user


def change_password(user: User, old_password: str, new_password: str) -> None:
    """
    Verify the old password and set a new one.

    Raises:
        ValidationError: If the old password is incorrect.
    """
    if not user.check_password(old_password):
        raise ValidationError({"old_password": "Current password is incorrect."})
    user.set_password(new_password)
    user.save(update_fields=["password"])


def update_user_rating(user: User) -> None:
    """
    Recalculate and persist the aggregated rating for a contractor.
    Called by the reviews service after a review is created/updated.
    """
    from apps.reviews.models import Review  # avoid circular import

    from django.db.models import Avg, Count

    agg = Review.objects.filter(contractor=user).aggregate(
        avg_rating=Avg("rating"), total=Count("id")
    )
    user.rating = agg["avg_rating"] or 0
    user.reviews_count = agg["total"] or 0
    user.save(update_fields=["rating", "reviews_count"])
