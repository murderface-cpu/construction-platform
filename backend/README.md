# 🏗️ Construction Platform API

A production-grade backend for a construction marketplace and project management platform — inspired by **Houzz** (design discovery), **Procore** (project tracking), and **Upwork** (contractor hiring).

---

## 📐 Architecture Overview

```
construction_platform/
├── apps/
│   ├── users/          # Auth, custom User model, roles
│   ├── marketplace/    # Contractor profiles, portfolios
│   ├── projects/       # Projects, milestones, members
│   ├── bookings/       # Booking lifecycle, availability
│   ├── reviews/        # Ratings, reviews
│   ├── designs/        # Design discovery (Houzz-style)
│   └── notifications/  # In-app + WebSocket + Celery email
├── config/             # Settings, URLs, ASGI, Celery
├── core/               # Shared pagination, permissions, mixins, storage
├── scripts/            # Seed data
└── tests/              # Shared factories
```

Each app follows the **service layer pattern**:
- `models.py` — data shape
- `serializers.py` — validation & serialization
- `services.py` — all business logic (views stay thin)
- `views.py` — HTTP request/response only
- `urls.py` — route mapping
- `tests/` — unit + integration tests

---

## 🚀 Quick Start (Local without Docker)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### 2. Clone & virtual environment
```bash
git clone <repo-url>
cd construction_platform
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment variables
```bash
cp .env.example .env
# Edit .env with your DB credentials and secret key
```

Minimum required variables:
```env
SECRET_KEY=your-long-random-secret-key
DB_NAME=construction_platform
DB_USER=postgres
DB_PASSWORD=your_password
REDIS_URL=redis://localhost:6379/0
```

### 4. Database setup
```bash
createdb construction_platform          # PostgreSQL
python manage.py migrate
```

### 5. Seed demo data
```bash
python scripts/seed.py
```

This creates:
- Superuser: `admin@constructionplatform.com` / `Admin1234!`
- 3 homeowners + 6 contractors with full profiles
- Design templates, projects, bookings, reviews, notifications

### 6. Run development server (HTTP + WebSocket)
```bash
# Option A — Daphne (ASGI, supports WebSockets)
daphne -b 127.0.0.1 -p 8000 config.asgi:application

# Option B — Django dev server (HTTP only, no WebSockets)
python manage.py runserver
```

### 7. Run Celery worker (background tasks + email)
```bash
# In a separate terminal
celery -A config worker --loglevel=info

# Optional: Celery Beat for periodic tasks
celery -A config beat --loglevel=info
```

---

## 🐳 Quick Start (Docker Compose)

```bash
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY

docker-compose up --build
```

Services started:
| Service | Port | Description |
|---------|------|-------------|
| Django (Daphne) | 8000 | API + WebSocket server |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache + message broker |
| Celery Worker | — | Background tasks |
| Celery Beat | — | Scheduled tasks |
| Flower | 5555 | Celery monitoring UI |

Then seed the database:
```bash
docker-compose exec web python scripts/seed.py
```

---

## 🔌 API Reference

Base URL: `http://localhost:8000/api/v1/`

Interactive docs:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Create account (returns JWT) |
| POST | `/auth/login/` | Login (returns JWT) |
| POST | `/auth/logout/` | Blacklist refresh token |
| POST | `/auth/token/refresh/` | Refresh access token |
| GET  | `/auth/me/` | Get own profile |
| PATCH | `/auth/me/` | Update own profile |
| POST | `/auth/change-password/` | Change password |

### Contractors / Marketplace
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/contractors/` | List contractors (filterable) |
| GET | `/contractors/{id}/` | Full contractor profile |
| GET | `/contractors/me/` | Own profile (contractor) |
| PATCH | `/contractors/me/` | Update own profile |
| GET | `/contractors/me/portfolio/` | List portfolio projects |
| POST | `/contractors/me/portfolio/` | Add portfolio project |
| PATCH | `/contractors/me/portfolio/{id}/` | Update portfolio project |
| DELETE | `/contractors/me/portfolio/{id}/` | Delete portfolio project |
| POST | `/contractors/me/portfolio/{id}/upload-url/` | S3 presigned upload URL |

**Filters**: `?location=Nairobi&category=electrical&min_rating=4&search=builder&availability=available`

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects/` | List own/member projects |
| POST | `/projects/` | Create project |
| GET | `/projects/{id}/` | Full project detail |
| PATCH | `/projects/{id}/` | Update project |
| POST | `/projects/{id}/assign/` | Assign contractor |
| GET | `/projects/{id}/milestones/` | List milestones |
| POST | `/projects/{id}/milestones/` | Create milestone |
| PATCH | `/projects/{id}/milestones/{mid}/` | Update milestone |
| DELETE | `/projects/{id}/milestones/{mid}/` | Delete milestone |

### Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/bookings/` | List own bookings |
| POST | `/bookings/` | Create booking (homeowner) |
| GET | `/bookings/{id}/` | Booking detail |
| PATCH | `/bookings/{id}/status/` | Accept/reject (contractor) |
| POST | `/bookings/{id}/complete/` | Mark completed |
| POST | `/bookings/{id}/cancel/` | Cancel |
| GET | `/bookings/availability/` | Own availability slots |
| POST | `/bookings/availability/` | Add availability slot |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reviews/` | List reviews (`?contractor_id=`) |
| POST | `/reviews/` | Create review (homeowner) |

### Designs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/designs/` | Browse designs (`?category=&search=`) |
| GET | `/designs/{id}/` | Design detail |
| POST | `/designs/{id}/save/` | Bookmark design |
| DELETE | `/designs/{id}/save/` | Remove bookmark |
| GET | `/designs/saved/` | My saved designs |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications/` | List notifications (`?unread=true`) |
| GET | `/notifications/unread-count/` | Unread badge count |
| PATCH | `/notifications/{id}/read/` | Mark one read |
| POST | `/notifications/mark-all-read/` | Mark all read |

---

## 🔌 WebSocket API

Connect with JWT in query string:

```javascript
// Personal notifications channel
const ws = new WebSocket('ws://localhost:8000/ws/notifications/?token=<access_token>');

// Project real-time updates channel
const ws = new WebSocket('ws://localhost:8000/ws/projects/<project_id>/?token=<access_token>');
```

### Events received from server

```json
// On connect
{"type": "connected", "unread_count": 3}

// New notification
{"type": "notification", "data": {"id": "...", "title": "...", "message": "...", ...}}

// Project event (milestone update, member added, etc.)
{"type": "project_event", "event_type": "milestone_updated", "data": {...}}
```

### Messages sent to server

```json
// Mark one notification read
{"action": "mark_read", "notification_id": "<uuid>"}

// Mark all notifications read
{"action": "mark_all_read"}

// Keepalive ping
{"action": "ping"}
```

---

## 🧪 Running Tests

```bash
# Full test suite with coverage
pytest

# Single app
pytest apps/users/tests/
pytest apps/bookings/tests/
pytest apps/projects/tests/

# Verbose with no coverage
pytest -v --no-cov apps/marketplace/tests/

# Skip slow tests
pytest -m "not slow"
```

Coverage report opens at `htmlcov/index.html`.

---

## 🛡️ Security Features

| Feature | Implementation |
|---------|---------------|
| Authentication | JWT (access + refresh), token blacklist on logout |
| Role-based access | `IsHomeowner`, `IsContractor`, `IsOwnerOrReadOnly` permission classes |
| Double-booking prevention | `select_for_update()` + DB-level unique constraint |
| Rate limiting | DRF throttling (100/hr anon, 1000/hr authenticated) |
| Input validation | DRF serializers on all write endpoints |
| Private media | AWS S3 presigned URLs (1-hour expiry) |
| WebSocket auth | JWT validated in `connect()` before accepting |
| SQL injection | Django ORM (parameterised queries) |
| Password strength | Django's built-in validators + min 8 chars |

---

## ⚡ Performance Features

| Feature | Detail |
|---------|--------|
| Redis caching | Contractor list cached for 5 min (invalidated on profile update) |
| N+1 prevention | `select_related` + `prefetch_related` on all list views |
| Pagination | All list endpoints paginated (default 20, max 100) |
| Celery async | Email + notification dispatch off the request thread |
| DB indexes | On `(homeowner, status)`, `(contractor, status)`, `(recipient, is_read)` |

---

## 📅 Celery Scheduled Tasks (Beat)

| Task | Schedule | Description |
|------|----------|-------------|
| `cleanup_old_notifications` | Weekly (Sunday 2am) | Delete read notifications > 90 days |
| `send_upcoming_booking_reminders` | Every hour | Remind users of bookings in next 24h |

Register via Django admin → Periodic Tasks, or programmatically.

---

## 🗃️ Database Schema Summary

```
users              → Custom user (email PK, role, rating, profile_image)
contractor_profiles → OneToOne → users, category, skills, rates
portfolio_projects  → FK → contractor_profiles
portfolio_images    → FK → portfolio_projects, s3_key
availability_slots  → FK → users (contractor), start/end, is_booked
bookings           → FK → homeowner, contractor, slot; status state machine
projects           → FK → owner (homeowner), status, milestones
project_members    → FK → project + user (M2M with role)
milestones         → FK → project, status, priority, due_date
project_updates    → FK → project (activity log)
reviews            → FK → reviewer + contractor, rating 1-5
design_templates   → category, style_tags, images
design_images      → FK → design_templates, s3_key
saved_designs      → FK → user + design (unique together)
notifications      → FK → recipient, type, is_read, metadata JSON
```

All models use **UUID primary keys** and **created_at/updated_at** timestamps.
