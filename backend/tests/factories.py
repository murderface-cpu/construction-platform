"""
factory_boy factories for all domain models.
Import these in any test module to get realistic test data without repeating setup.

Usage:
    from tests.factories import UserFactory, ContractorProfileFactory, BookingFactory
    homeowner = UserFactory(role="homeowner")
    contractor = UserFactory(role="contractor")
    booking = BookingFactory(homeowner=homeowner, contractor=contractor)
"""

from __future__ import annotations

import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class UserFactory(DjangoModelFactory):
    class Meta:
        model = "users.User"
        django_get_or_create = ("email",)

    email = factory.LazyAttribute(lambda _: fake.unique.email())
    name = factory.LazyAttribute(lambda _: fake.name())
    password = factory.PostGenerationMethodCall("set_password", "Passw0rd!")
    role = "homeowner"
    location = factory.LazyAttribute(lambda _: fake.city())
    is_active = True


class HomeownerFactory(UserFactory):
    role = "homeowner"


class ContractorUserFactory(UserFactory):
    role = "contractor"


# ---------------------------------------------------------------------------
# Marketplace
# ---------------------------------------------------------------------------

class ContractorProfileFactory(DjangoModelFactory):
    class Meta:
        model = "marketplace.ContractorProfile"

    user = factory.SubFactory(ContractorUserFactory)
    company_name = factory.LazyAttribute(lambda _: fake.company())
    category = "general"
    years_experience = factory.LazyAttribute(lambda _: fake.random_int(1, 20))
    hourly_rate = factory.LazyAttribute(lambda _: fake.pydecimal(left_digits=3, right_digits=2, positive=True))
    availability_status = "available"


class PortfolioProjectFactory(DjangoModelFactory):
    class Meta:
        model = "marketplace.PortfolioProject"

    contractor = factory.SubFactory(ContractorProfileFactory)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    description = factory.LazyAttribute(lambda _: fake.paragraph())
    category = "general"
    location = factory.LazyAttribute(lambda _: fake.city())


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------

class AvailabilitySlotFactory(DjangoModelFactory):
    class Meta:
        model = "bookings.AvailabilitySlot"

    contractor = factory.SubFactory(ContractorUserFactory)
    start_time = factory.LazyFunction(
        lambda: fake.future_datetime(end_date="+30d", tzinfo=None)
    )
    end_time = factory.LazyAttribute(
        lambda obj: obj.start_time + __import__("datetime").timedelta(hours=4)
    )
    is_booked = False


class BookingFactory(DjangoModelFactory):
    class Meta:
        model = "bookings.Booking"

    homeowner = factory.SubFactory(HomeownerFactory)
    contractor = factory.SubFactory(ContractorUserFactory)
    scheduled_start = factory.LazyFunction(
        lambda: fake.future_datetime(end_date="+30d", tzinfo=__import__("pytz").UTC)
    )
    scheduled_end = factory.LazyAttribute(
        lambda obj: obj.scheduled_start + __import__("datetime").timedelta(hours=3)
    )
    status = "pending"
    description = factory.LazyAttribute(lambda _: fake.paragraph())
    location = factory.LazyAttribute(lambda _: fake.address())


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = "projects.Project"

    owner = factory.SubFactory(HomeownerFactory)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=5))
    description = factory.LazyAttribute(lambda _: fake.paragraph())
    category = "renovation"
    location = factory.LazyAttribute(lambda _: fake.address())
    status = "active"


class MilestoneFactory(DjangoModelFactory):
    class Meta:
        model = "projects.Milestone"

    project = factory.SubFactory(ProjectFactory)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    description = factory.LazyAttribute(lambda _: fake.paragraph())
    status = "todo"
    priority = "medium"


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = "reviews.Review"

    reviewer = factory.SubFactory(HomeownerFactory)
    contractor = factory.SubFactory(ContractorUserFactory)
    rating = factory.LazyAttribute(lambda _: fake.random_int(1, 5))
    comment = factory.LazyAttribute(lambda _: fake.paragraph())


# ---------------------------------------------------------------------------
# Designs
# ---------------------------------------------------------------------------

class DesignTemplateFactory(DjangoModelFactory):
    class Meta:
        model = "designs.DesignTemplate"

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    description = factory.LazyAttribute(lambda _: fake.paragraph())
    category = "interior"
    is_published = True


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = "notifications.Notification"

    recipient = factory.SubFactory(HomeownerFactory)
    notification_type = "system"
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=5))
    message = factory.LazyAttribute(lambda _: fake.paragraph())
    is_read = False
