import { useState } from "react";
import { format } from "date-fns";
import { CalendarIcon, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { bookingsApi } from "@/lib/api";
import { useBookingsStore } from "@/store/bookingsStore";
import type { Contractor } from "@/lib/data/contractors";

const TIME_SLOTS = [
  "9:00 AM", "10:00 AM", "11:00 AM",
  "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM",
];

interface BookingModalProps {
  contractor: Contractor & { [k: string]: any };
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BookingModal({ contractor, open, onOpenChange }: BookingModalProps) {
  const addBooking = useBookingsStore((s) => s.addBooking);
  const qc = useQueryClient();
  const [date, setDate] = useState<Date | undefined>(undefined);
  const [slot, setSlot] = useState<string | null>(null);
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const reset = () => { setDate(undefined); setSlot(null); setNotes(""); };

  const handleSubmit = async () => {
    if (!date || !slot) { toast.error("Pick a date and time slot"); return; }
    setSubmitting(true);
    const payload = {
      contractor_id: contractor.id,
      date: format(date, "yyyy-MM-dd"),
      time_slot: slot,
      notes: notes.trim() || undefined,
    };
    try {
      const { data } = await bookingsApi.create(payload);
      addBooking({
        ...data,
        id: data.id ?? `bk_${Math.random().toString(36).slice(2, 10)}`,
        contractorId: contractor.id,
        contractorName: contractor.name,
        contractorAvatarUrl: contractor.avatarUrl,
        date: format(date, "yyyy-MM-dd"),
        timeSlot: slot,
        notes: notes.trim() || undefined,
        status: data.status ?? "pending",
        createdAt: data.created_at ?? new Date().toISOString(),
      });
      qc.invalidateQueries({ queryKey: ["bookings"] });
      toast.success("Booking request sent!", { description: `${contractor.name} will confirm shortly.` });
      reset();
      onOpenChange(false);
    } catch (err: any) {
      // Fallback to local-only if backend down
      addBooking({
        id: `bk_${Math.random().toString(36).slice(2, 10)}`,
        contractorId: contractor.id,
        contractorName: contractor.name,
        contractorAvatarUrl: contractor.avatarUrl,
        date: format(date, "yyyy-MM-dd"),
        timeSlot: slot,
        notes: notes.trim() || undefined,
        status: "pending",
        createdAt: new Date().toISOString(),
      });
      toast.success("Booking request saved locally.");
      reset();
      onOpenChange(false);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => { onOpenChange(o); if (!o) reset(); }}>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>Book a consultation</DialogTitle>
          <DialogDescription>
            Schedule a 30-minute intro call with {contractor.name}.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-5 py-2">
          <div className="space-y-2">
            <Label>Date</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !date && "text-muted-foreground")}>
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {date ? format(date, "PPP") : "Pick a date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={date}
                  onSelect={setDate}
                  disabled={(d) => d < new Date(new Date().setHours(0, 0, 0, 0))}
                  initialFocus
                  className={cn("p-3 pointer-events-auto")}
                />
              </PopoverContent>
            </Popover>
          </div>

          <div className="space-y-2">
            <Label>Time slot</Label>
            <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
              {TIME_SLOTS.map((t) => (
                <button key={t} type="button" onClick={() => setSlot(t)}
                  className={cn(
                    "rounded-md border px-2 py-2 text-xs font-medium transition",
                    slot === t
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border bg-card hover:border-primary/50 hover:bg-muted"
                  )}>
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes (optional)</Label>
            <Textarea
              id="notes"
              placeholder="Briefly describe your project, scope, and timeline…"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={submitting}>
            {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Request booking
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
