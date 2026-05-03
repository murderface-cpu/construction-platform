"""
Seed script — populate the database with realistic demo data.

Usage:
    python manage.py shell < scripts/seed.py
    # or
    python scripts/seed.py   (if run directly with DJANGO_SETTINGS_MODULE set)

Creates:
    - 3 homeowners
    - 6 contractors (various specialities)
    - Contractor profiles + portfolio projects
    - Design templates (10)
    - Projects with milestones
    - Bookings in various states
    - Reviews and ratings
    - Notifications
"""

import os
import sys
import django
import datetime
import decimal
import random

# ---------------------------------------------------------------------------
# Bootstrap Django when run as a standalone script
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

import pytz
from django.utils import timezone

from apps.users.models import User
from apps.marketplace.models import ContractorProfile, PortfolioProject
from apps.projects.models import Milestone, Project, ProjectMember
from apps.bookings.models import AvailabilitySlot, Booking
from apps.reviews.models import Review
from apps.designs.models import DesignTemplate, SavedDesign
from apps.notifications.models import Notification
from apps.users.services import update_user_rating

UTC = pytz.UTC


def clear_data():
    print("🗑️  Clearing existing seed data...")
    Notification.objects.all().delete()
    Review.objects.all().delete()
    Booking.objects.all().delete()
    AvailabilitySlot.objects.all().delete()
    Milestone.objects.all().delete()
    ProjectMember.objects.all().delete()
    Project.objects.all().delete()
    SavedDesign.objects.all().delete()
    DesignTemplate.objects.all().delete()
    PortfolioProject.objects.all().delete()
    ContractorProfile.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    print("   Done.\n")


def create_homeowners():
    print("👷 Creating homeowners...")
    homeowners_data = [
        {
            "email": "amara.odhiambo@example.com",
            "name": "Amara Odhiambo",
            "location": "Karen, Nairobi",
            "bio": "Interior design enthusiast renovating my family home in Karen.",
            "phone": "+254 712 345 678",
        },
        {
            "email": "david.mwangi@example.com",
            "name": "David Mwangi",
            "location": "Westlands, Nairobi",
            "bio": "Property investor building rental units across Nairobi.",
            "phone": "+254 722 987 654",
        },
        {
            "email": "grace.kamau@example.com",
            "name": "Grace Kamau",
            "location": "Kilimani, Nairobi",
            "bio": "Architect turned homeowner, passionate about sustainable design.",
            "phone": "+254 733 456 789",
        },
    ]
    homeowners = []
    for data in homeowners_data:
        user = User.objects.create_user(
            email=data["email"],
            name=data["name"],
            password="Demo1234!",
            role=User.Role.HOMEOWNER,
            location=data["location"],
            bio=data["bio"],
            phone=data["phone"],
        )
        homeowners.append(user)
        print(f"   ✅ {user.name} ({user.email})")
    return homeowners


def create_contractors():
    print("\n🔨 Creating contractors...")
    contractors_data = [
        {
            "email": "john.otieno@example.com",
            "name": "John Otieno",
            "location": "Industrial Area, Nairobi",
            "company_name": "Otieno General Contractors",
            "category": "general",
            "skills": ["Concrete Work", "Masonry", "Project Management"],
            "years_experience": 15,
            "hourly_rate": "3500",
            "bio": "15 years of experience in general contracting across East Africa.",
        },
        {
            "email": "fatuma.hassan@example.com",
            "name": "Fatuma Hassan",
            "location": "Mombasa Road, Nairobi",
            "company_name": "Hassan Electrical Solutions",
            "category": "electrical",
            "skills": ["Wiring", "Solar Installation", "Lighting Design", "Panel Upgrades"],
            "years_experience": 10,
            "hourly_rate": "4000",
            "bio": "Certified electrician specialising in solar and smart home systems.",
        },
        {
            "email": "peter.ngugi@example.com",
            "name": "Peter Ngugi",
            "location": "Parklands, Nairobi",
            "company_name": "Ngugi Interior Designs",
            "category": "interior_design",
            "skills": ["Space Planning", "3D Rendering", "Furniture Sourcing", "Colour Consulting"],
            "years_experience": 8,
            "hourly_rate": "5000",
            "bio": "Award-winning interior designer with projects in Nairobi and beyond.",
        },
        {
            "email": "esther.wanjiku@example.com",
            "name": "Esther Wanjiku",
            "location": "Ruaka, Nairobi",
            "company_name": "Wanjiku Plumbing & Sanitation",
            "category": "plumbing",
            "skills": ["Pipe Installation", "Drainage Systems", "Borehole Plumbing", "Water Tanks"],
            "years_experience": 12,
            "hourly_rate": "3000",
            "bio": "Expert plumber with experience in residential and commercial projects.",
        },
        {
            "email": "samuel.kipchoge@example.com",
            "name": "Samuel Kipchoge",
            "location": "Rongai, Kajiado",
            "company_name": "Kipchoge Landscaping",
            "category": "landscaping",
            "skills": ["Garden Design", "Irrigation Systems", "Tree Surgery", "Hardscaping"],
            "years_experience": 6,
            "hourly_rate": "2500",
            "bio": "Passionate landscaper transforming outdoor spaces into paradise.",
        },
        {
            "email": "mary.achieng@example.com",
            "name": "Mary Achieng",
            "location": "Kisumu",
            "company_name": "Achieng Roofing Specialists",
            "category": "roofing",
            "skills": ["Metal Roofing", "Waterproofing", "Roof Repairs", "Gutters"],
            "years_experience": 9,
            "hourly_rate": "3200",
            "bio": "Experienced roofer covering Western Kenya and Nairobi.",
        },
    ]

    contractors = []
    for data in contractors_data:
        user = User.objects.create_user(
            email=data["email"],
            name=data["name"],
            password="Demo1234!",
            role=User.Role.CONTRACTOR,
            location=data["location"],
            bio=data["bio"],
        )
        profile = ContractorProfile.objects.create(
            user=user,
            company_name=data["company_name"],
            category=data["category"],
            skills=data["skills"],
            years_experience=data["years_experience"],
            hourly_rate=decimal.Decimal(data["hourly_rate"]),
            availability_status="available",
        )
        contractors.append((user, profile))
        print(f"   ✅ {user.name} — {profile.company_name}")
    return contractors


def create_portfolio_projects(contractors):
    print("\n🖼️  Creating portfolio projects...")
    portfolios = [
        # John - General
        [
            {
                "title": "Westlands Office Complex",
                "description": "Complete construction of a 4-storey commercial building in Westlands.",
                "category": "general",
                "location": "Westlands, Nairobi",
                "project_cost": "45000000",
            },
            {
                "title": "Karen Residential Development",
                "description": "50-unit residential estate with shared amenities.",
                "category": "general",
                "location": "Karen, Nairobi",
                "project_cost": "120000000",
            },
        ],
        # Fatuma - Electrical
        [
            {
                "title": "Gigiri Solar Installation",
                "description": "10kW solar system for embassy residence in Gigiri.",
                "category": "electrical",
                "location": "Gigiri, Nairobi",
                "project_cost": "850000",
            },
            {
                "title": "Runda Smart Home Wiring",
                "description": "Full smart home electrical system for luxury villa.",
                "category": "electrical",
                "location": "Runda, Nairobi",
                "project_cost": "1200000",
            },
        ],
        # Peter - Interior
        [
            {
                "title": "Kilimani Penthouse Interior",
                "description": "High-end interior fit-out for a 3-bed penthouse apartment.",
                "category": "interior_design",
                "location": "Kilimani, Nairobi",
                "project_cost": "4500000",
            },
        ],
        # Esther - Plumbing
        [
            {
                "title": "Lavington Plumbing Overhaul",
                "description": "Complete replacement of plumbing system for 1960s property.",
                "category": "plumbing",
                "location": "Lavington, Nairobi",
                "project_cost": "350000",
            },
        ],
        # Samuel - Landscaping
        [
            {
                "title": "Muthaiga Garden Redesign",
                "description": "Transformed 1-acre garden with indigenous plants and irrigation.",
                "category": "landscaping",
                "location": "Muthaiga, Nairobi",
                "project_cost": "780000",
            },
        ],
        # Mary - Roofing
        [
            {
                "title": "Nyali Beach House Roofing",
                "description": "Full metal roof replacement and waterproofing for coastal property.",
                "category": "roofing",
                "location": "Nyali, Mombasa",
                "project_cost": "650000",
            },
        ],
    ]

    for (user, profile), projects in zip(contractors, portfolios):
        for p_data in projects:
            PortfolioProject.objects.create(
                contractor=profile,
                title=p_data["title"],
                description=p_data["description"],
                category=p_data["category"],
                location=p_data["location"],
                project_cost=decimal.Decimal(p_data["project_cost"]),
                completion_date=datetime.date.today() - datetime.timedelta(days=random.randint(30, 400)),
                is_featured=random.choice([True, False]),
            )
    print("   ✅ Portfolio projects created.")


def create_design_templates():
    print("\n🎨 Creating design templates...")
    templates = [
        {
            "title": "Modern Minimalist Living Room",
            "category": "interior",
            "style_tags": ["modern", "minimalist", "neutral tones"],
            "description": "Clean lines, neutral palette, and purposeful furniture placement.",
        },
        {
            "title": "Tropical Garden Oasis",
            "category": "landscaping",
            "style_tags": ["tropical", "lush", "indigenous plants"],
            "description": "East African native plants with stone pathways and water features.",
        },
        {
            "title": "Contemporary Kitchen Design",
            "category": "kitchen",
            "style_tags": ["contemporary", "open plan", "marble"],
            "description": "Island kitchen with marble countertops and integrated appliances.",
        },
        {
            "title": "Coastal Exterior Facade",
            "category": "exterior",
            "style_tags": ["coastal", "white render", "shutters"],
            "description": "Mediterranean-inspired exterior with cool whites and ocean-blue accents.",
        },
        {
            "title": "Luxury Master Bedroom Suite",
            "category": "bedroom",
            "style_tags": ["luxury", "en suite", "walk-in wardrobe"],
            "description": "Expansive bedroom with reading nook, dressing room and spa bathroom.",
        },
        {
            "title": "Home Office Productivity Space",
            "category": "office",
            "style_tags": ["productivity", "biophilic", "standing desk"],
            "description": "Ergonomic home office with natural light, plants and cable management.",
        },
        {
            "title": "Spa-Inspired Bathroom",
            "category": "bathroom",
            "style_tags": ["spa", "freestanding tub", "stone tiles"],
            "description": "Serene bathroom retreat with rainfall shower and natural stone.",
        },
        {
            "title": "Open-Plan Living & Dining",
            "category": "living",
            "style_tags": ["open plan", "double volume", "statement lighting"],
            "description": "Seamless living and dining space with double-volume ceilings.",
        },
        {
            "title": "Scandinavian Kids Bedroom",
            "category": "bedroom",
            "style_tags": ["scandinavian", "kids", "playful", "safe"],
            "description": "Bright, fun and safe children's bedroom with smart storage.",
        },
        {
            "title": "Drought-Resistant Front Garden",
            "category": "landscaping",
            "style_tags": ["drought resistant", "low maintenance", "gravel"],
            "description": "Beautiful low-water front garden using succulents and ornamental grasses.",
        },
    ]

    for t in templates:
        DesignTemplate.objects.create(
            title=t["title"],
            category=t["category"],
            style_tags=t["style_tags"],
            description=t["description"],
            is_published=True,
        )
    print(f"   ✅ {len(templates)} design templates created.")
    return list(DesignTemplate.objects.all())


def create_projects_and_milestones(homeowners, contractors):
    print("\n🏗️  Creating projects and milestones...")
    john_user, john_profile = contractors[0]
    peter_user, peter_profile = contractors[2]

    # Project 1 — Active renovation
    p1 = Project.objects.create(
        owner=homeowners[0],  # Amara
        title="Karen Family Home Renovation",
        description=(
            "Complete renovation of a 4-bedroom family home including new kitchen, "
            "bathrooms, and master bedroom suite."
        ),
        category=Project.Category.RENOVATION,
        location="Karen, Nairobi",
        status=Project.Status.ACTIVE,
        budget=decimal.Decimal("8500000"),
        start_date=datetime.date.today() - datetime.timedelta(days=30),
        end_date=datetime.date.today() + datetime.timedelta(days=90),
    )
    ProjectMember.objects.create(project=p1, user=john_user, role=ProjectMember.Role.CONTRACTOR)
    ProjectMember.objects.create(project=p1, user=peter_user, role=ProjectMember.Role.CONSULTANT)

    milestones_p1 = [
        ("Demolition & Site Prep", "in_progress", "high", -25),
        ("Foundation & Structural Work", "todo", "critical", 10),
        ("Roofing", "todo", "high", 30),
        ("Electrical Rough-In", "todo", "high", 35),
        ("Plumbing Rough-In", "todo", "high", 37),
        ("Wall & Ceiling Finishes", "todo", "medium", 55),
        ("Kitchen Installation", "todo", "medium", 65),
        ("Bathroom Tiling & Fixtures", "todo", "medium", 70),
        ("Painting", "todo", "low", 80),
        ("Snagging & Handover", "todo", "high", 90),
    ]
    for title, ms_status, priority, days_offset in milestones_p1:
        Milestone.objects.create(
            project=p1,
            title=title,
            status=ms_status,
            priority=priority,
            due_date=datetime.date.today() + datetime.timedelta(days=days_offset),
            assigned_to=john_user if ms_status == "in_progress" else None,
        )

    # Project 2 — Draft
    p2 = Project.objects.create(
        owner=homeowners[1],  # David
        title="Westlands Commercial Block",
        description="New 6-storey commercial building with retail on ground floor.",
        category=Project.Category.NEW_BUILD,
        location="Westlands, Nairobi",
        status=Project.Status.DRAFT,
        budget=decimal.Decimal("75000000"),
    )

    # Project 3 — Completed
    p3 = Project.objects.create(
        owner=homeowners[2],  # Grace
        title="Kilimani Apartment Fit-Out",
        description="Full interior fit-out of a 2-bed apartment.",
        category=Project.Category.INTERIOR,
        location="Kilimani, Nairobi",
        status=Project.Status.COMPLETED,
        budget=decimal.Decimal("3200000"),
        actual_cost=decimal.Decimal("3150000"),
        start_date=datetime.date.today() - datetime.timedelta(days=120),
        end_date=datetime.date.today() - datetime.timedelta(days=10),
    )
    ProjectMember.objects.create(project=p3, user=peter_user, role=ProjectMember.Role.CONTRACTOR)
    for title in ["Design Concept", "Procurement", "Installation", "Snagging"]:
        Milestone.objects.create(
            project=p3, title=title, status="completed",
            completed_at=timezone.now() - datetime.timedelta(days=random.randint(10, 60)),
        )

    print(f"   ✅ 3 projects with milestones created.")
    return [p1, p2, p3]


def create_bookings(homeowners, contractors):
    print("\n📅 Creating bookings...")
    john_user, _ = contractors[0]
    fatuma_user, _ = contractors[1]
    esther_user, _ = contractors[3]
    now = timezone.now()

    # Booking 1: Pending
    b1 = Booking.objects.create(
        homeowner=homeowners[0],
        contractor=john_user,
        scheduled_start=now + datetime.timedelta(days=7),
        scheduled_end=now + datetime.timedelta(days=7, hours=4),
        description="Initial site visit for the Karen renovation project.",
        location="15 Acacia Close, Karen, Nairobi",
        estimated_budget=decimal.Decimal("8500000"),
        status=Booking.Status.PENDING,
    )

    # Booking 2: Accepted
    b2 = Booking.objects.create(
        homeowner=homeowners[1],
        contractor=fatuma_user,
        scheduled_start=now + datetime.timedelta(days=3),
        scheduled_end=now + datetime.timedelta(days=3, hours=6),
        description="Solar panel assessment and installation quote for Westlands property.",
        location="Plot 44, Westlands, Nairobi",
        estimated_budget=decimal.Decimal("950000"),
        status=Booking.Status.ACCEPTED,
    )

    # Booking 3: Completed
    b3 = Booking.objects.create(
        homeowner=homeowners[2],
        contractor=esther_user,
        scheduled_start=now - datetime.timedelta(days=30),
        scheduled_end=now - datetime.timedelta(days=29),
        description="Emergency plumbing repair — burst pipe in utility room.",
        location="Apt 12B, Kilimani Court, Nairobi",
        estimated_budget=decimal.Decimal("45000"),
        status=Booking.Status.COMPLETED,
    )

    # Booking 4: Rejected
    b4 = Booking.objects.create(
        homeowner=homeowners[0],
        contractor=fatuma_user,
        scheduled_start=now - datetime.timedelta(days=5),
        scheduled_end=now - datetime.timedelta(days=5) + datetime.timedelta(hours=3),
        description="Lighting upgrade for living areas.",
        location="Karen, Nairobi",
        status=Booking.Status.REJECTED,
        rejection_reason="Already committed to another project during that period.",
    )

    print("   ✅ 4 bookings created (pending, accepted, completed, rejected).")
    return [b1, b2, b3, b4]


def create_reviews(homeowners, contractors, bookings):
    print("\n⭐ Creating reviews...")
    esther_user, _ = contractors[3]
    samuel_user, _ = contractors[4]
    peter_user, _ = contractors[2]

    reviews_data = [
        # Completed booking review
        {
            "reviewer": homeowners[2],
            "contractor": esther_user,
            "booking": bookings[2],  # b3 - completed
            "rating": 5,
            "comment": (
                "Esther was absolutely fantastic. She arrived within an hour of my call, "
                "diagnosed the burst pipe quickly, and fixed it cleanly. "
                "Highly recommend her for any plumbing work!"
            ),
        },
        {
            "reviewer": homeowners[0],
            "contractor": peter_user,
            "booking": None,
            "rating": 4,
            "comment": (
                "Peter did a great job on our apartment fit-out. Very creative and "
                "detail-oriented. Minor delays on procurement but final result was beautiful."
            ),
        },
        {
            "reviewer": homeowners[1],
            "contractor": samuel_user,
            "booking": None,
            "rating": 5,
            "comment": (
                "Samuel transformed our garden completely. He has a great eye for "
                "indigenous plants and the irrigation system he installed is superb."
            ),
        },
    ]

    for r in reviews_data:
        review = Review.objects.create(
            reviewer=r["reviewer"],
            contractor=r["contractor"],
            booking=r["booking"],
            rating=r["rating"],
            comment=r["comment"],
        )
        update_user_rating(r["contractor"])
        print(f"   ✅ {r['reviewer'].name} → {r['contractor'].name}: {r['rating']}★")


def create_saved_designs(homeowners, templates):
    print("\n💾 Creating saved designs...")
    saves = [
        (homeowners[0], 0),
        (homeowners[0], 1),
        (homeowners[0], 4),
        (homeowners[1], 2),
        (homeowners[2], 3),
        (homeowners[2], 6),
        (homeowners[2], 7),
    ]
    for user, idx in saves:
        if idx < len(templates):
            SavedDesign.objects.get_or_create(user=user, design=templates[idx])
    print(f"   ✅ {len(saves)} designs saved by homeowners.")


def create_notifications(homeowners, contractors, bookings):
    print("\n🔔 Creating notifications...")
    john_user, _ = contractors[0]

    notifs = [
        Notification(
            recipient=john_user,
            notification_type=Notification.Type.BOOKING_NEW,
            title="New Booking Request",
            message=f"{homeowners[0].name} has sent you a booking request.",
            metadata={"booking_id": str(bookings[0].id)},
            is_read=False,
        ),
        Notification(
            recipient=homeowners[1],
            notification_type=Notification.Type.BOOKING_ACCEPTED,
            title="Booking Accepted",
            message=f"Your booking with {contractors[1][0].name} has been accepted!",
            metadata={"booking_id": str(bookings[1].id)},
            is_read=False,
        ),
        Notification(
            recipient=homeowners[2],
            notification_type=Notification.Type.BOOKING_COMPLETED,
            title="Booking Completed",
            message="Your plumbing booking has been completed. Please leave a review!",
            metadata={"booking_id": str(bookings[2].id)},
            is_read=True,
        ),
        Notification(
            recipient=contractors[3][0],
            notification_type=Notification.Type.NEW_REVIEW,
            title="New 5★ Review",
            message=f"{homeowners[2].name} left you a 5-star review!",
            is_read=False,
        ),
        Notification(
            recipient=homeowners[0],
            notification_type=Notification.Type.MILESTONE_UPDATED,
            title="Milestone Updated",
            message='"Demolition & Site Prep" is now in progress.',
            is_read=False,
        ),
    ]
    Notification.objects.bulk_create(notifs)
    print(f"   ✅ {len(notifs)} notifications created.")


def create_superuser():
    print("\n🔑 Creating superuser...")
    if not User.objects.filter(email="admin@constructionplatform.com").exists():
        User.objects.create_superuser(
            email="admin@constructionplatform.com",
            password="Admin1234!",
            name="Platform Admin",
        )
        print("   ✅ admin@constructionplatform.com / Admin1234!")
    else:
        print("   ⏭️  Superuser already exists.")


def run():
    print("=" * 60)
    print("  Construction Platform — Database Seed Script")
    print("=" * 60)
    print()

    clear_data()
    create_superuser()

    homeowners = create_homeowners()
    contractors = create_contractors()
    create_portfolio_projects(contractors)
    templates = create_design_templates()
    projects = create_projects_and_milestones(homeowners, contractors)
    bookings = create_bookings(homeowners, contractors)
    create_reviews(homeowners, contractors, bookings)
    create_saved_designs(homeowners, templates)
    create_notifications(homeowners, contractors, bookings)

    print()
    print("=" * 60)
    print("  ✅ Seed complete!")
    print()
    print("  Demo credentials (all passwords: Demo1234!):")
    print("  homeowner:  amara.odhiambo@example.com")
    print("  contractor: john.otieno@example.com")
    print("  admin:      admin@constructionplatform.com  (Admin1234!)")
    print("=" * 60)


if __name__ == "__main__":
    run()
