# BuildHub Construction Platform

BuildHub is a full-stack construction marketplace that connects homeowners with contractors, supports consultation bookings, and provides project-management workflows for construction jobs.

The repository contains two runnable applications:

- **Frontend:** React + TypeScript + Vite single-page app in `src/`.
- **Backend:** Django REST Framework API with WebSocket notifications, Celery tasks, PostgreSQL, and Redis in `backend/`.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Frontend Setup](#frontend-setup)
- [Backend Setup](#backend-setup)
- [Environment Variables](#environment-variables)
- [Useful Commands](#useful-commands)
- [API and WebSocket Overview](#api-and-websocket-overview)
- [Testing](#testing)
- [Commenting Guidelines](#commenting-guidelines)

## Features

### Marketplace and Frontend

- Landing page for homeowners and contractors.
- Authentication pages for login and registration.
- Protected dashboard and app shell navigation.
- Contractor directory with detail pages and booking entry points.
- Booking management for homeowners and contractors.
- Design discovery and project pages.
- Responsive UI built with Tailwind CSS and shadcn/ui components.

### Backend API

- JWT authentication with refresh-token support.
- Contractor profiles, portfolio management, reviews, and design bookmarks.
- Booking lifecycle with availability slots and double-booking safeguards.
- Project milestones, members, updates, and status tracking.
- In-app notifications with WebSocket delivery.
- Celery background jobs and scheduled task support.
- Swagger and ReDoc API documentation.

## Tech Stack

| Layer | Tools |
| --- | --- |
| Frontend | React 18, TypeScript, Vite, React Router, TanStack Query |
| Styling | Tailwind CSS, shadcn/ui, Radix UI primitives, Lucide icons |
| Frontend state | Zustand, Axios interceptors, React Hook Form, Zod |
| Backend | Django, Django REST Framework, Simple JWT, drf-spectacular |
| Async / realtime | Celery, Redis, Django Channels, Daphne |
| Data / storage | PostgreSQL, django-redis, optional AWS S3 media storage |
| Testing | Vitest, Testing Library, pytest, pytest-django |
| Quality | ESLint, TypeScript strict mode, service-layer backend structure |

## Repository Structure

```text
.
├── src/                         # React frontend source
│   ├── components/              # Cards, forms, layout, and shadcn/ui components
│   ├── hooks/                   # Shared React hooks
│   ├── lib/                     # API client, utilities, and mock data
│   ├── pages/                   # Route-level frontend pages
│   ├── store/                   # Zustand stores
│   └── test/                    # Vitest setup and sample tests
├── backend/
│   ├── apps/                    # Django domain apps
│   │   ├── bookings/            # Availability and booking lifecycle
│   │   ├── designs/             # Design discovery and saved designs
│   │   ├── marketplace/         # Contractors and portfolios
│   │   ├── notifications/       # Notifications, WebSockets, Celery tasks
│   │   ├── projects/            # Projects, members, milestones, updates
│   │   ├── reviews/             # Contractor reviews
│   │   └── users/               # Auth and custom user model
│   ├── config/                  # Django settings, URLs, ASGI, WSGI, Celery app
│   ├── core/                    # Shared permissions, pagination, storage, mixins
│   ├── scripts/                 # Seed data helpers
│   └── tests/                   # Shared backend test helpers and factories
├── public/                      # Static frontend assets
├── package.json                 # Frontend scripts and dependencies
└── backend/requirements.txt     # Backend Python dependencies
```

## Prerequisites

- Node.js 20+ and npm.
- Python 3.11+.
- PostgreSQL 14+.
- Redis 7+.
- Docker and Docker Compose, if you prefer containerized backend services.

## Frontend Setup

Install dependencies from the repository root:

```bash
npm install
```

Create a frontend environment file if you need to override the API URL:

```bash
cat > .env.local <<'EOF_ENV'
VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF_ENV
```

Run the Vite development server:

```bash
npm run dev
```

Common frontend URLs:

| URL | Purpose |
| --- | --- |
| `http://localhost:8080/` | Landing page |
| `http://localhost:8080/auth/login` | Login |
| `http://localhost:8080/dashboard` | Protected dashboard |

## Backend Setup

### Option 1: Local Python environment

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python scripts/seed.py
```

Run the API with WebSocket support:

```bash
daphne -b 127.0.0.1 -p 8000 config.asgi:application
```

For HTTP-only development, you can also use Django's development server:

```bash
python manage.py runserver
```

Run background workers in separate terminals when testing async flows:

```bash
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

### Option 2: Docker Compose

```bash
cd backend
cp .env.example .env
docker-compose up --build
```

Seed demo data after the services are healthy:

```bash
docker-compose exec web python scripts/seed.py
```

Demo credentials created by the seed script:

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@constructionplatform.com` | `Admin1234!` |

## Environment Variables

### Frontend

| Variable | Default | Description |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `/api/v1` | Base URL used by the Axios API client. |

### Backend

The backend reads `backend/.env`. Start from `backend/.env.example` and update secrets before deploying.

| Variable | Description |
| --- | --- |
| `SECRET_KEY` | Django secret key. Use a long random value outside local development. |
| `DEBUG` | Enables Django debug mode when `True`. |
| `ALLOWED_HOSTS` | Comma-separated hostnames Django may serve. |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection settings. |
| `REDIS_URL` | Redis URL for caching and Channels. |
| `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | Celery Redis broker and result backend URLs. |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES`, `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | JWT lifetime configuration. |
| `AWS_*` | Optional S3 configuration for private media uploads. |
| `EMAIL_*` | Optional SMTP settings for email tasks. |
| `FRONTEND_URL` | Frontend origin used by backend integrations. |

## Useful Commands

### Frontend

| Command | Description |
| --- | --- |
| `npm run dev` | Start Vite development server. |
| `npm run build` | Create a production frontend build. |
| `npm run build:dev` | Create an unminified development build. |
| `npm run preview` | Preview the built frontend locally. |
| `npm run lint` | Run ESLint. |
| `npm test` | Run Vitest once. |
| `npm run test:watch` | Run Vitest in watch mode. |

### Backend

Run these from `backend/`:

| Command | Description |
| --- | --- |
| `python manage.py migrate` | Apply database migrations. |
| `python scripts/seed.py` | Seed demo users and sample marketplace data. |
| `python manage.py runserver` | Start HTTP-only Django development server. |
| `daphne -b 127.0.0.1 -p 8000 config.asgi:application` | Start ASGI server with WebSocket support. |
| `celery -A config worker --loglevel=info` | Start Celery worker. |
| `celery -A config beat --loglevel=info` | Start Celery Beat scheduler. |
| `pytest` | Run backend tests. |

## API and WebSocket Overview

Backend base URL:

```text
http://localhost:8000/api/v1/
```

Interactive API documentation:

- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

Primary REST areas:

| Area | Example endpoints |
| --- | --- |
| Authentication | `/auth/login/`, `/auth/register/`, `/auth/me/` |
| Contractors | `/contractors/`, `/contractors/{id}/`, `/contractors/me/portfolio/` |
| Bookings | `/bookings/`, `/bookings/{id}/status/`, `/bookings/availability/` |
| Projects | `/projects/`, `/projects/{id}/milestones/`, `/projects/{id}/assign/` |
| Designs | `/designs/`, `/designs/{id}/save/`, `/designs/saved/` |
| Reviews | `/reviews/?contractor_id=<id>` |
| Notifications | `/notifications/`, `/notifications/unread-count/` |

WebSocket channels use JWT access tokens in the query string:

```javascript
const notifications = new WebSocket(
  'ws://localhost:8000/ws/notifications/?token=<access_token>'
);

const projectEvents = new WebSocket(
  'ws://localhost:8000/ws/projects/<project_id>/?token=<access_token>'
);
```

## Testing

Run frontend checks from the repository root:

```bash
npm run lint
npm test
npm run build
```

Run backend checks from `backend/`:

```bash
pytest
pytest apps/bookings/tests/
pytest apps/projects/tests/
```

## Commenting Guidelines

Comments should explain intent, assumptions, constraints, or non-obvious tradeoffs. Prefer descriptive names and clear code over comments that repeat what the code already says. When a comment is needed, keep it close to the relevant code, concise, and up to date.
