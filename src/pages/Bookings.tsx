import { Link } from "react-router-dom";
import { format } from "date-fns";
import {
  CalendarCheck, MessageSquare, CheckCircle2, XCircle, Ban,
  Loader2, Clock, Plus, ArrowUpRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { BookingStatusBadge } from "@/components/ui/booking-status-badge";
import { useBookingsStore, type BookingStatus } from "@/store/bookingsStore";
import { useAuthStore } from "@/store/authStore";
import { bookingsApi } from "@/lib/api";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useState } from "react";

type BookingAction = "accept" | "reject" | "cancel" | "complete";

function statusToValue(action: BookingAction): BookingStatus {
  const map: Record<BookingAction, BookingStatus> = {
    accept: "accepted",
    reject: "rejected",
    cancel: "cancelled",
    complete: "completed",
  };
  return map[action];
}

export default function Bookings() {
  const { bookings, setBookings, updateBooking, removeBooking } = useBookingsStore();
  const role = useAuthStore((s) => s.user?.role);
  const isContractor = role === "contractor";
  const qc = useQueryClient();
  const [actionLoading, setActionLoading] = useState<string | null>(null);

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

  const doAction = async (id: string, action: BookingAction) => {
    setActionLoading(id + action);
    try {
      if (action === "accept") await bookingsApi.updateStatus(id, "accepted");
      else if (action === "reject") await bookingsApi.updateStatus(id, "rejected");
      else if (action === "cancel") await bookingsApi.cancel(id);
      else if (action === "complete") await bookingsApi.complete(id);
      updateBooking(id, { status: statusToValue(action) });
      qc.invalidateQueries({ queryKey: ["bookings"] });
      toast.success(`Booking ${action}ed`);
    } catch {
      updateBooking(id, { status: statusToValue(action) });
      toast.success(`Booking ${action}ed`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRemove = async (id: string) => {
    try { await bookingsApi.cancel(id); } catch {}
    removeBooking(id);
    toast.success("Booking removed");
  };

  const pendingCount = bookings.filter((b) => b.status === "pending").length;

  return (
    <div className="min-h-full bg-background">
      {/* Page header */}
      <div className="border-b border-border/50 px-6 py-7 md:px-10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              {isContractor ? "Booking requests" : "Your bookings"}
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {isContractor
                ? "Review and respond to consultation requests from homeowners."
                : "Track and manage your contractor consultation requests."}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {pendingCount > 0 && (
              <span className="flex h-6 items-center gap-1.5 rounded-full bg-amber-500/10 px-3 text-xs font-medium text-amber-600 dark:text-amber-400">
                <Clock className="h-3 w-3" />
                {pendingCount} pending
              </span>
            )}
            {!isContractor && (
              <Button asChild size="sm" className="gap-1.5 shadow-sm">
                <Link to="/contractors">
                  <Plus className="h-3.5 w-3.5" />
                  New booking
                </Link>
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="px-6 py-7 md:px-10">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center gap-3 py-20">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Loading bookings…</p>
          </div>
        ) : bookings.length === 0 ? (
          <div className="mx-auto max-w-sm py-16 text-center">
            <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-muted">
              <CalendarCheck className="h-6 w-6 text-muted-foreground" />
            </div>
            <h3 className="text-base font-semibold">
              {isContractor ? "No requests yet" : "No bookings yet"}
            </h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {isContractor
                ? "When homeowners request consultations with you, they'll appear here."
                : "Browse contractors and request a consultation to get your project started."}
            </p>
            {!isContractor && (
              <Button asChild className="mt-5 gap-2">
                <Link to="/contractors">
                  Browse contractors
                  <ArrowUpRight className="h-3.5 w-3.5" />
                </Link>
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {bookings.map((b) => (
              <div
                key={b.id}
                className="group relative flex flex-col gap-4 rounded-xl border border-border/60 bg-card p-5 shadow-sm transition-all hover:border-border hover:shadow-md sm:flex-row sm:items-center"
              >
                {/* Avatar */}
                {b.contractorAvatarUrl ? (
                  <img
                    src={b.contractorAvatarUrl}
                    alt={b.contractorName}
                    loading="lazy"
                    className="h-12 w-12 shrink-0 rounded-xl object-cover ring-1 ring-border"
                  />
                ) : (
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 text-base font-semibold text-primary ring-1 ring-border">
                    {(b.contractorName ?? "?").slice(0, 1)}
                  </div>
                )}

                {/* Info */}
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    {b.contractorId ? (
                      <Link
                        to={`/contractors/${b.contractorId}`}
                        className="text-sm font-semibold hover:underline"
                      >
                        {b.contractorName ?? "Contractor"}
                      </Link>
                    ) : (
                      <span className="text-sm font-semibold">
                        {b.contractorName ?? "Contractor"}
                      </span>
                    )}
                    <BookingStatusBadge status={b.status} />
                  </div>

                  {b.date && (
                    <div className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
                      <CalendarCheck className="h-3 w-3" />
                      {format(new Date(b.date), "EEEE, MMM d, yyyy")}
                      {b.timeSlot && (
                        <>
                          <span className="text-border">·</span>
                          {b.timeSlot}
                        </>
                      )}
                    </div>
                  )}

                  {b.notes && (
                    <p className="mt-1.5 line-clamp-2 text-xs text-muted-foreground">
                      <MessageSquare className="mr-1 inline h-3 w-3" />
                      {b.notes}
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex flex-wrap items-center gap-2">
                  {isContractor && b.status === "pending" && (
                    <>
                      <Button
                        size="sm"
                        className="gap-1.5 shadow-sm"
                        onClick={() => doAction(b.id, "accept")}
                        disabled={actionLoading === b.id + "accept"}
                      >
                        {actionLoading === b.id + "accept" ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : (
                          <CheckCircle2 className="h-3.5 w-3.5" />
                        )}
                        Accept
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="gap-1.5"
                        onClick={() => doAction(b.id, "reject")}
                        disabled={actionLoading === b.id + "reject"}
                      >
                        {actionLoading === b.id + "reject" ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : (
                          <XCircle className="h-3.5 w-3.5" />
                        )}
                        Decline
                      </Button>
                    </>
                  )}

                  {isContractor && b.status === "accepted" && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="gap-1.5"
                      onClick={() => doAction(b.id, "complete")}
                      disabled={actionLoading === b.id + "complete"}
                    >
                      {actionLoading === b.id + "complete" ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                      )}
                      Mark complete
                    </Button>
                  )}

                  {!isContractor && b.status === "pending" && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="gap-1.5 text-muted-foreground hover:text-destructive"
                      onClick={() => doAction(b.id, "cancel")}
                      disabled={actionLoading === b.id + "cancel"}
                    >
                      <Ban className="h-3.5 w-3.5" />
                      Cancel
                    </Button>
                  )}

                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleRemove(b.id)}
                    className="text-muted-foreground/60 hover:text-destructive"
                    title="Remove booking"
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
