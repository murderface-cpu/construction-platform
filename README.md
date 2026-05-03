# BuildHub - Construction Marketplace Frontend

A modern React frontend for BuildHub, a platform that connects homeowners with trusted contractors, project managers, and suppliers for construction projects.

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 8
- **Routing**: React Router v6
- **Styling**: Tailwind CSS + shadcn/ui components (Radix UI primitives)
- **State Management**: Zustand (auth store)
- **Server State**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod + @hookform/resolvers
- **HTTP Client**: Axios (with auth interceptors)
- **Icons**: Lucide React
- **Charts**: Recharts
- **Testing**: Vitest + Testing Library
- **Code Quality**: ESLint + TypeScript strict mode

## Features

- Landing page (`/`) showcasing the platform
- User authentication - Login (`/auth/login`) and Register (`/auth/register`)
- Protected dashboard (`/dashboard`)
- Contractor directory (`/contractors`) with search/browse
- Contractor detail pages (`/contractors/:id`)
- Booking management (`/bookings`)
- Mobile-responsive sidebar navigation
- Dark-mode aware (via `next-themes`)
- Toast notifications (Sonner + Radix Toast)

## Project Structure

```
src/
  assets/           # Static images (contractor photos, portfolio)
  components/
    cards/          # ContractorCard, ContractorCardSkeleton
    forms/          # BookingModal
    layout/         # AppLayout, AppSidebar, AuthLayout, ProtectedRoute
    ui/             # shadcn/ui component library (40+ components)
    NavLink.tsx
  hooks/
    use-mobile.tsx
    use-toast.ts
  lib/
    api.ts          # Axios client with auth interceptors
    utils.ts        # cn() helper, date formatting
    data/           # Mock data (contractors.ts, portfolio.ts)
  pages/
    Index.tsx       # Landing page
    Dashboard.tsx
    Bookings.tsx
    NotFound.tsx
    auth/           # Login.tsx, Register.tsx
    contractors/    # Contractors.tsx, ContractorDetail.tsx
  store/
    authStore.ts    # Zustand auth state
  test/
    example.test.ts
    setup.ts
  App.tsx           # Route definitions
  main.tsx          # Entry point
  index.css         # Tailwind directives + base styles
```

## API Configuration

The Axios client is pre-wired with:
- Base URL from `VITE_API_BASE_URL` env variable (falls back to `/api`)
- Bearer token injection from Zustand auth store
- Auto-logout on 401 responses

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Getting Started

```bash
# Install dependencies
npm install

# Start dev server (port 8080)
npm run dev

# Build for production
npm run build

# Build for development (unminified)
npm run build:dev

# Run tests
npm test

# Watch tests
npm run test:watch

# Lint
npm run lint

# Preview production build
npm run preview
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `/api` | Backend API base URL |

## Routing

| Path | Component | Auth Required |
|---|---|---|
| `/` | Index (landing) | No |
| `/auth/login` | Login | No |
| `/auth/register` | Register | No |
| `/dashboard` | Dashboard | Yes |
| `/contractors` | Contractors list | Yes |
| `/contractors/:id` | Contractor detail | Yes |
| `/bookings` | Bookings | Yes |
| `*` | NotFound | - |
