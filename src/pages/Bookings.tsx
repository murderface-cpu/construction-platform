import { Link } from "react-router-dom";
import { format } from "date-fns";
import { CalendarCheck, MessageSquare, CheckCircle2, XCircle, Ban, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { BookingStatusBadge } from "@/components/ui/booking-status-badge";
import { useBookingsStore, type BookingStatus } from "@/store/bookingsStore";
import { useAuthStore } from "@/store/authStore";
import { bookingsApi } from "@/lib/api";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useState } from "react";

export default function Bookings() {
  const { bookings, setBookings, updateBooking, removeBooking } = useBookingsStore();
  const role = useAuthStore((s) => s.user?.role);
  const isContractor = role === "contractor";
  const qc = useQueryClient();
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Fetch real bookings and merge into store
  const { isLoading } = useQuery({
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
            notes: b.notes,
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

  const doAction = async (id: string, action: "accept" | "reject" | "cancel" | "complete") => {
    setActionLoading(id + action);
    try {
      if (action === "accept") await bookingsApi.updateStatus(id, "accepted");
      else if (action === "reject") await bookingsApi.updateStatus(id, "rejected");
      else if (action === "cancel") await bookingsApi.cancel(id);
      else if (action === "complete") await bookingsApi.complete(id);
      updateBooking(id, { status: (action === "accept" ? "accepted" : action === "reject" ? "rejected" : action === "cancel" ? "cancelled" : "completed") as BookingStatus });
      qc.invalidateQueries({ queryKey: ["bookings"] });
      toast.success(`Booking ${action}ed`);
    } catch {
      // Fallback local update
      updateBooking(id, { status: (action === "accept" ? "accepted" : action === "reject" ? "rejected" : action === "cancel" ? "cancelled" : "completed") as BookingStatus });
      toast.success(`Booking ${action}ed`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRemove = async (id: string) => {
    try { await bookingsApi.cancel(id); } catch {}
    removeBooking(id);
    toast.success("Removed");
  };

  return (
    <div className="space-y-6 p-6 md:p-8">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {isContractor ? "Incoming bookings" : "Your bookings"}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            {isContractor ? "Review and respond to consultation requests." : "Track requests you've sent to contractors."}
          </p>
        </div>
        {!isContractor && (
          <Button asChild variant="outline" size="sm">
            <Link to="/contractors">Find more contractors</Link>
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center p-16">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : bookings.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border bg-muted/30 p-12 text-center">
          <CalendarCheck className="mx-auto mb-3 h-8 w-8 text-muted-foreground" />
          <h3 className="text-base font-semibold">No bookings yet</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            {isContractor
              ? "When homeowners request consultations, they'll show up here."
              : "Book a consultation from a contractor's profile to get started."}
          </p>
          {!isContractor && (
            <Button asChild size="sm" className="mt-4">
              <Link to="/contractors">Browse contractors</Link>
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {bookings.map((b) => (
            <Card key={b.id} className="shadow-sm transition hover:shadow-md">
              <CardContent className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center">
                {b.contractorAvatarUrl ? (
                  <img src={b.contractorAvatarUrl} alt={b.contractorName} loading="lazy"
                    className="h-14 w-14 shrink-0 rounded-lg object-cover" />
                ) : (
                  <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-secondary text-lg font-bold">
                    {(b.contractorName ?? "?").slice(0, 1)}
                  </div>
                )}
                <div className="min-w-0 flex-1 space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    {b.contractorId ? (
                      <Link to={`/contractors/${b.contractorId}`} className="text-sm font-semibold hover:underline">
                        {b.contractorName ?? "Contractor"}
                      </Link>
                    ) : (
                      <span className="text-sm font-semibold">{b.contractorName ?? "Contractor"}</span>
                    )}
                    <BookingStatusBadge status={b.status} />
                  </div>
                  {b.date && (
                    <div className="text-xs text-muted-foreground">
                      {format(new Date(b.date), "EEEE, MMM d, yyyy")}
                      {b.timeSlot ? ` · ${b.timeSlot}` : ""}
                    </div>
                  )}
                  {b.notes && (
                    <p className="line-clamp-2 text-xs text-muted-foreground">
                      <MessageSquare className="mr-1 inline h-3 w-3" />{b.notes}
                    </p>
                  )}
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  {isContractor && b.status === "pending" && (
                    <>
                      <Button size="sm" onClick={() => doAction(b.id, "accept")}
                        disabled={actionLoading === b.id + "accept"}>
                        {actionLoading === b.id + "accept" ? <Loader2 className="h-3 w-3 animate-spin" /> : <CheckCircle2 className="mr-1 h-3.5 w-3.5" />}
                        Accept
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => doAction(b.id, "reject")}
                        disabled={actionLoading === b.id + "reject"}>
                        {actionLoading === b.id + "reject" ? <Loader2 className="h-3 w-3 animate-spin" /> : <XCircle className="mr-1 h-3.5 w-3.5" />}
                        Decline
                      </Button>
                    </>
                  )}
                  {isContractor && b.status === "accepted" && (
                    <Button size="sm" variant="outline" onClick={() => doAction(b.id, "complete")}
                      disabled={actionLoading === b.id + "complete"}>
                      {actionLoading === b.id + "complete" ? <Loader2 className="h-3 w-3 animate-spin" /> : <CheckCircle2 className="mr-1 h-3.5 w-3.5" />}
                      Mark complete
                    </Button>
                  )}
                  {!isContractor && b.status === "pending" && (
                    <Button size="sm" variant="outline" onClick={() => doAction(b.id, "cancel")}
                      disabled={actionLoading === b.id + "cancel"}>
                      <Ban className="mr-1 h-3.5 w-3.5" /> Cancel
                    </Button>
                  )}
                  <Button size="sm" variant="ghost" onClick={() => handleRemove(b.id)}
                    className="text-muted-foreground hover:text-destructive">
                    Remove
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
