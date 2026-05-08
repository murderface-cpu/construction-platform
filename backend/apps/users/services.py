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

def request_password_reset(email: str) -> None:
    """
    Generate a reset token and email it to the user.
    Silently does nothing if the email doesn't exist (no account enumeration).
    """
    from django.core.mail import send_mail
    from django.conf import settings
    from .models import PasswordResetToken

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return  # Intentionally silent

    # Invalidate any existing unused tokens for this user
    PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

    token_obj = PasswordResetToken.objects.create(user=user)
    reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token_obj.token}"

    send_mail(
        subject="Reset your BuildHub password",
        message=f"Click the link to reset your password (expires in 30 minutes):\n\n{reset_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def confirm_password_reset(token: str, new_password: str) -> None:
    """
    Validate the reset token and set the new password.

    Raises:
        ValidationError: If the token is invalid, expired, or already used.
    """
    from .models import PasswordResetToken

    try:
        token_obj = PasswordResetToken.objects.select_related("user").get(token=token)
    except PasswordResetToken.DoesNotExist:
        raise ValidationError({"token": "Invalid or expired reset link."})

    if not token_obj.is_valid():
        raise ValidationError({"token": "This reset link has expired. Please request a new one."})

    token_obj.user.set_password(new_password)
    token_obj.user.save(update_fields=["password"])
    token_obj.used = True
    token_obj.save(update_fields=["used"])
