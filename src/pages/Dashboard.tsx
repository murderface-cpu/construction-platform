import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BookingStatusBadge } from "@/components/ui/booking-status-badge";
import {
  ArrowUpRight, CalendarCheck, FolderKanban, Bell,
  Loader2, Sparkles, ChevronRight,
} from "lucide-react";
import { bookingsApi, projectsApi, notificationsApi } from "@/lib/api";
import { useBookingsStore } from "@/store/bookingsStore";
import { format } from "date-fns";

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const isContractor = user?.role === "contractor";
  const { bookings, setBookings } = useBookingsStore();

  const { data: bookingData, isLoading: bookingsLoading } = useQuery({
    queryKey: ["bookings"],
    queryFn: async () => {
      try {
        const { data } = await bookingsApi.list();
        const list = Array.isArray(data) ? data : data?.results ?? [];
        if (list.length > 0) {
          const normalized = list.map((b: any) => ({
            ...b,
            id: b.id,
            contractorId: b.contractor_id ?? b.contractor?.id,
            contractorName: b.contractor_name ?? b.contractor?.name ?? "Contractor",
            contractorAvatarUrl: b.contractor_avatar ?? b.contractor?.avatar_url ?? "",
            date: b.date,
            timeSlot: b.time_slot ?? b.timeSlot,
            status: b.status,
            createdAt: b.created_at,
          }));
          setBookings(normalized);
          return normalized;
        }
      } catch {}
      return bookings;
    },
  });

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: async () => {
      try {
        const { data } = await projectsApi.list();
        return Array.isArray(data) ? data : data?.results ?? [];
      } catch { return []; }
    },
  });

  const { data: notifications } = useQuery({
    queryKey: ["notifications"],
    queryFn: async () => {
      try {
        const { data } = await notificationsApi.list(true);
        return Array.isArray(data) ? data : data?.results ?? [];
      } catch { return []; }
    },
    refetchInterval: 60_000,
  });

  const displayBookings = bookingData ?? bookings;
  const pendingBookings = displayBookings.filter((b: any) => b.status === "pending");
  const activeProjects = (projects ?? []).filter((p: any) => p.status === "active" || p.status === "in_progress");
  const unreadNotifs = (notifications ?? []).length;

  const stats = isContractor
    ? [
        { label: "Pending requests", value: pendingBookings.length, icon: CalendarCheck, gradient: "from-amber-500/20 to-orange-500/10", accent: "text-amber-500", href: "/bookings" },
        { label: "Active jobs", value: activeProjects.length, icon: FolderKanban, gradient: "from-blue-500/20 to-cyan-500/10", accent: "text-blue-500", href: "/projects" },
        { label: "Notifications", value: unreadNotifs, icon: Bell, gradient: "from-violet-500/20 to-purple-500/10", accent: "text-violet-500", href: "/bookings" },
      ]
    : [
        { label: "Active projects", value: activeProjects.length, icon: FolderKanban, gradient: "from-blue-500/20 to-cyan-500/10", accent: "text-blue-500", href: "/projects" },
        { label: "Upcoming bookings", value: pendingBookings.length, icon: CalendarCheck, gradient: "from-emerald-500/20 to-teal-500/10", accent: "text-emerald-500", href: "/bookings" },
        { label: "Notifications", value: unreadNotifs, icon: Bell, gradient: "from-violet-500/20 to-purple-500/10", accent: "text-violet-500", href: "/dashboard" },
      ];

  const recentBookings = displayBookings.slice(0, 5);
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  return (
    <div className="min-h-full bg-background">
      {/* Hero header */}
      <div className="relative overflow-hidden border-b border-border/50 bg-gradient-to-br from-background via-background to-muted/30 px-6 pb-8 pt-8 md:px-10 md:pt-10">
        {/* Subtle background orb */}
        <div className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full bg-gradient-to-br from-primary/5 to-transparent blur-3xl" />
        <div className="relative flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="mb-1 text-xs font-medium uppercase tracking-widest text-muted-foreground/70">
              {greeting}
            </p>
            <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
              {user?.name ? user.name.split(" ")[0] : "Welcome"}{" "}
              <span className="inline-block animate-[wave_2s_ease-in-out_once]">👋</span>
            </h1>
            <p className="mt-1.5 text-sm text-muted-foreground">
              Your{" "}
              <Badge variant="secondary" className="capitalize font-medium">
                {user?.role}
              </Badge>{" "}
              workspace — here's today's overview.
            </p>
          </div>
          {!isContractor && (
            <Button asChild className="shrink-0 gap-2 shadow-sm" size="sm">
              <Link to="/contractors">
                <Sparkles className="h-3.5 w-3.5" />
                Find a contractor
              </Link>
            </Button>
          )}
        </div>
      </div>

      <div className="space-y-8 px-6 py-8 md:px-10">
        {/* Stat cards */}
        <div className="grid gap-4 sm:grid-cols-3">
          {stats.map((s) => (
            <Link key={s.label} to={s.href} className="group">
              <Card className={`relative overflow-hidden border-border/60 bg-gradient-to-br ${s.gradient} shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md`}>
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                        {s.label}
                      </p>
                      <div className="mt-2 text-4xl font-semibold tracking-tight">
                        {bookingsLoading || projectsLoading ? (
                          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                        ) : (
                          s.value
                        )}
                      </div>
                    </div>
                    <div className={`rounded-xl bg-background/60 p-2.5 backdrop-blur-sm ${s.accent}`}>
                      <s.icon className="h-4 w-4" />
                    </div>
                  </div>
                  <div className="mt-3 flex items-center gap-1 text-xs text-muted-foreground transition-colors group-hover:text-foreground">
                    View all <ArrowUpRight className="h-3 w-3" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {/* Notifications banner */}
        {unreadNotifs > 0 && (
          <div className="flex items-start gap-3 rounded-xl border border-amber-500/20 bg-amber-500/5 px-4 py-3">
            <Bell className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
            <div className="flex-1 text-sm">
              <span className="font-medium text-foreground">
                {unreadNotifs} unread notification{unreadNotifs > 1 ? "s" : ""}
              </span>
              <div className="mt-1 divide-y divide-border/50">
                {(notifications ?? []).slice(0, 2).map((n: any) => (
                  <p key={n.id} className="py-1 text-xs text-muted-foreground">
                    {n.message ?? n.text ?? n.title}
                  </p>
                ))}
              </div>
            </div>
            {unreadNotifs > 2 && (
              <Badge variant="secondary" className="shrink-0 text-xs">
                +{unreadNotifs - 2} more
              </Badge>
            )}
          </div>
        )}

        {/* Recent bookings */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold tracking-tight">Recent bookings</h2>
            <Button asChild variant="ghost" size="sm" className="h-8 gap-1 text-xs text-muted-foreground hover:text-foreground">
              <Link to="/bookings">
                View all <ChevronRight className="h-3.5 w-3.5" />
              </Link>
            </Button>
          </div>

          <Card className="overflow-hidden border-border/60 shadow-sm">
            <CardContent className="p-0">
              {bookingsLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              ) : recentBookings.length === 0 ? (
                <div className="px-6 py-12 text-center">
                  <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-muted">
                    <CalendarCheck className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <p className="text-sm font-medium">No bookings yet</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {isContractor
                      ? "Booking requests will appear here."
                      : "Browse contractors to schedule your first consultation."}
                  </p>
                  {!isContractor && (
                    <Button asChild size="sm" className="mt-4">
                      <Link to="/contractors">Browse contractors</Link>
                    </Button>
                  )}
                </div>
              ) : (
                <div>
                  {recentBookings.map((b: any, i: number) => (
                    <div
                      key={b.id}
                      className={`flex items-center justify-between px-5 py-4 transition-colors hover:bg-muted/40 ${
                        i < recentBookings.length - 1 ? "border-b border-border/50" : ""
                      }`}
                    >
                      <div className="flex items-center gap-3.5">
                        {b.contractorAvatarUrl ? (
                          <img
                            src={b.contractorAvatarUrl}
                            alt={b.contractorName}
                            className="h-9 w-9 rounded-xl object-cover ring-1 ring-border"
                          />
                        ) : (
                          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 text-sm font-semibold text-primary ring-1 ring-border">
                            {(b.contractorName ?? "?").slice(0, 1)}
                          </div>
                        )}
                        <div>
                          <p className="text-sm font-medium leading-none">
                            {b.contractorName ?? "Contractor"}
                          </p>
                          <p className="mt-1 text-xs text-muted-foreground">
                            {b.date ? format(new Date(b.date), "MMM d, yyyy") : ""}
                            {b.timeSlot ? ` · ${b.timeSlot}` : ""}
                          </p>
                        </div>
                      </div>
                      <BookingStatusBadge status={b.status} />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick actions */}
        <div className="grid gap-3 sm:grid-cols-2">
          <Link
            to="/projects"
            className="group flex items-center justify-between rounded-xl border border-border/60 bg-card px-5 py-4 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500/10 text-blue-500">
                <FolderKanban className="h-4 w-4" />
              </div>
              <div>
                <p className="text-sm font-medium">Projects</p>
                <p className="text-xs text-muted-foreground">{activeProjects.length} active</p>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
          </Link>
          <Link
            to="/bookings"
            className="group flex items-center justify-between rounded-xl border border-border/60 bg-card px-5 py-4 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-500">
                <CalendarCheck className="h-4 w-4" />
              </div>
              <div>
                <p className="text-sm font-medium">Bookings</p>
                <p className="text-xs text-muted-foreground">{pendingBookings.length} pending</p>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
