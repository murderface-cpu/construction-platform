import type { BookingStatus } from "@/store/bookingsStore";
import { Badge } from "@/components/ui/badge";
import { Check, Clock, X, Ban } from "lucide-react";
import { cn } from "@/lib/utils";

const config: Record<
  BookingStatus,
  { label: string; cls: string; Icon: React.ComponentType<{ className?: string }> }
> = {
  pending:   { label: "Pending",   cls: "bg-warning/15 text-warning border-warning/30",     Icon: Clock },
  accepted:  { label: "Accepted",  cls: "bg-success/15 text-success border-success/30",     Icon: Check },
  rejected:  { label: "Rejected",  cls: "bg-destructive/15 text-destructive border-destructive/30", Icon: X },
  cancelled: { label: "Cancelled", cls: "bg-muted text-muted-foreground border-border",     Icon: Ban },
};

export function BookingStatusBadge({ status }: { status: BookingStatus }) {
  const { label, cls, Icon } = config[status];
  return (
    <Badge variant="outline" className={cn("gap-1 font-medium", cls)}>
      <Icon className="h-3 w-3" />
      {label}
    </Badge>
  );
}
