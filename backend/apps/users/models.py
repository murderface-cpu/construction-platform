"""
Custom User model for the construction platform.

Roles:
    - homeowner: A client who hires contractors and manages projects.
    - contractor: A professional who offers services and gets hired.
"""

from __future__ import annotations

import uuid
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.mixins import TimestampedModel


class UserManager(BaseUserManager):
    """Custom manager for the User model (email as username)."""

    def create_user(
        self,
        email: str,
        password: str,
        role: str = "homeowner",
        **extra_fields,
    ) -> "User":
        if not email:
            raise ValueError("Email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", User.Role.HOMEOWNER)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    """
    Platform user.  Email is the unique identifier; username is not used.
    """

    class Role(models.TextChoices):
        HOMEOWNER = "homeowner", "Homeowner"
        CONTRACTOR = "contractor", "Contractor"

    # Core identity
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.HOMEOWNER)

    # Profile
    location = models.CharField(max_length=255, blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Rating (aggregated via signals/services; stored for fast reads)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    reviews_count = models.PositiveIntegerField(default=0)

    # Auth flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"

    @property
    def is_homeowner(self) -> bool:
        return self.role == self.Role.HOMEOWNER

    @property
    def is_contractor(self) -> bool:
        return self.role == self.Role.CONTRACTOR

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        db_table = "password_reset_tokens"

    def is_valid(self) -> bool:
        """Tokens expire after 30 minutes."""
        return not self.used and timezone.now() < self.created_at + timedelta(minutes=30)
