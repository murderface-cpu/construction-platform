import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BookingStatusBadge } from "@/components/ui/booking-status-badge";
import {
  ArrowUpRight, CalendarCheck, FolderKanban, Users, Bell,
  TrendingUp, Clock, Loader2, CheckCircle2,
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
        { label: "Pending requests", value: pendingBookings.length, icon: CalendarCheck, tone: "text-info", href: "/bookings" },
        { label: "Active jobs", value: activeProjects.length, icon: FolderKanban, tone: "text-accent", href: "/projects" },
        { label: "Notifications", value: unreadNotifs, icon: Bell, tone: "text-warning", href: "/bookings" },
      ]
    : [
        { label: "Active projects", value: activeProjects.length, icon: FolderKanban, tone: "text-accent", href: "/projects" },
        { label: "Upcoming bookings", value: pendingBookings.length, icon: CalendarCheck, tone: "text-info", href: "/bookings" },
        { label: "Notifications", value: unreadNotifs, icon: Bell, tone: "text-warning", href: "/dashboard" },
      ];

  const recentBookings = displayBookings.slice(0, 5);

  return (
    <div className="space-y-8 p-6 md:p-8">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          Welcome back{user?.name ? `, ${user.name.split(" ")[0]}` : ""} 👋
        </h1>
        <p className="text-sm text-muted-foreground">
          Here's what's happening on your{" "}
          <Badge variant="secondary" className="capitalize">{user?.role}</Badge>{" "}
          workspace today.
        </p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map((s) => (
          <Link key={s.label} to={s.href}>
            <Card className="shadow-card cursor-pointer transition hover:shadow-elegant hover:-translate-y-0.5">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  {s.label}
                </CardTitle>
                <s.icon className={`h-4 w-4 ${s.tone}`} />
              </CardHeader>
              <CardContent className="flex items-end justify-between">
                <div className="text-3xl font-semibold tracking-tight">
                  {bookingsLoading || projectsLoading ? (
                    <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                  ) : s.value}
                </div>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground/50" />
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* Recent bookings */}
      <Card className="shadow-card">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Recent bookings</CardTitle>
          <Button asChild variant="ghost" size="sm" className="h-7 text-xs">
            <Link to="/bookings">View all <ArrowUpRight className="ml-1 h-3 w-3" /></Link>
          </Button>
        </CardHeader>
        <CardContent>
          {bookingsLoading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : recentBookings.length === 0 ? (
            <div className="rounded-lg border border-dashed border-border bg-muted/30 p-8 text-center">
              <CalendarCheck className="mx-auto mb-2 h-6 w-6 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">No bookings yet.</p>
              {!isContractor && (
                <Button asChild size="sm" className="mt-3">
                  <Link to="/contractors">Browse contractors</Link>
                </Button>
              )}
            </div>
          ) : (
            <div className="divide-y divide-border">
              {recentBookings.map((b: any) => (
                <div key={b.id} className="flex items-center justify-between py-3">
                  <div className="flex items-center gap-3">
                    {b.contractorAvatarUrl ? (
                      <img src={b.contractorAvatarUrl} alt={b.contractorName}
                        className="h-9 w-9 rounded-lg object-cover" />
                    ) : (
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-secondary text-xs font-bold">
                        {(b.contractorName ?? "?").slice(0, 1)}
                      </div>
                    )}
                    <div>
                      <p className="text-sm font-medium">{b.contractorName ?? "Contractor"}</p>
                      <p className="text-xs text-muted-foreground">
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

      {/* Notifications */}
      {unreadNotifs > 0 && (
        <Card className="shadow-card border-warning/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Bell className="h-4 w-4 text-warning" /> Notifications
              <Badge variant="secondary" className="ml-auto">{unreadNotifs} unread</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="divide-y divide-border">
            {(notifications ?? []).slice(0, 3).map((n: any) => (
              <div key={n.id} className="py-2.5 text-sm">{n.message ?? n.text ?? n.title}</div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
