import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Plus, FolderKanban, Loader2, ChevronRight,
  Calendar, Users2, MapPin, DollarSign, Layers,
} from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { projectsApi } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { toast } from "sonner";
import { format } from "date-fns";

function StatusBadge({ status }: { status: string }) {
  const configs: Record<string, { label: string; className: string }> = {
    active: { label: "Active", className: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20" },
    in_progress: { label: "In progress", className: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20" },
    completed: { label: "Completed", className: "bg-muted text-muted-foreground border-border" },
    cancelled: { label: "Cancelled", className: "bg-destructive/10 text-destructive border-destructive/20" },
    pending: { label: "Pending", className: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20" },
  };
  const cfg = configs[status] ?? configs.pending;
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${cfg.className}`}>
      {cfg.label}
    </span>
  );
}

const CATEGORIES = [
  { value: "renovation", label: "Renovation" },
  { value: "new_build", label: "New Build" },
  { value: "repair", label: "Repair" },
  { value: "landscaping", label: "Landscaping" },
  { value: "interior", label: "Interior Design" },
  { value: "commercial", label: "Commercial" },
  { value: "other", label: "Other" },
];

export default function Projects() {
  const isContractor = useAuthStore((s) => s.user?.role === "contractor");
  const qc = useQueryClient();
  const [createOpen, setCreateOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("renovation");
  const [location, setLocation] = useState("");
  const [budget, setBudget] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [creating, setCreating] = useState(false);

  const { data: projects = [], isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: async () => {
      try {
        const { data } = await projectsApi.list();
        return Array.isArray(data) ? data : data?.results ?? [];
      } catch { return []; }
    },
  });

  const handleCreate = async () => {
    if (!title.trim()) { toast.error("Enter a project title"); return; }
    if (!location.trim()) { toast.error("Enter a project location"); return; }
    setCreating(true);
    try {
      await projectsApi.create({
        title, description, category, location,
        budget: budget ? parseFloat(budget) : null,
        start_date: startDate || null,
        end_date: endDate || null,
      });
      qc.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Project created!");
      setCreateOpen(false);
      resetForm();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  const resetForm = () => {
    setTitle(""); setDescription(""); setCategory("renovation");
    setLocation(""); setBudget(""); setStartDate(""); setEndDate("");
  };

  const activeCount = projects.filter((p: any) => p.status === "active" || p.status === "in_progress").length;

  return (
    <div className="min-h-full bg-background">
      {/* Header */}
      <div className="border-b border-border/50 px-6 py-7 md:px-10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {isContractor
                ? "Projects you've been assigned to by homeowners."
                : "Plan and track your construction and renovation projects."}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {activeCount > 0 && (
              <span className="text-xs text-muted-foreground">
                {activeCount} active
              </span>
            )}
            {!isContractor && (
              <Button onClick={() => setCreateOpen(true)} className="gap-2 shadow-sm">
                <Plus className="h-4 w-4" />
                New project
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="px-6 py-7 md:px-10">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center gap-3 py-20">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Loading projects…</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="mx-auto max-w-sm py-16 text-center">
            <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-muted">
              <FolderKanban className="h-6 w-6 text-muted-foreground" />
            </div>
            <h3 className="text-base font-semibold">No projects yet</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {isContractor
                ? "You haven't been assigned to any projects yet. Make sure your profile is complete to attract homeowners."
                : "Create your first project to start organizing your work and finding the right contractors."}
            </p>
            {!isContractor && (
              <Button onClick={() => setCreateOpen(true)} className="mt-5 gap-2">
                <Plus className="h-4 w-4" />
                Create your first project
              </Button>
            )}
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p: any) => (
              <Link
                key={p.id}
                to={`/projects/${p.id}`}
                className="group flex flex-col rounded-xl border border-border/60 bg-card shadow-sm transition-all hover:-translate-y-0.5 hover:border-border hover:shadow-md"
              >
                {/* Card header */}
                <div className="flex items-start justify-between gap-3 p-5 pb-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Layers className="h-4 w-4" />
                  </div>
                  <StatusBadge status={p.status ?? "pending"} />
                </div>

                {/* Card body */}
                <div className="flex-1 px-5 pb-4">
                  <h3 className="font-semibold leading-snug tracking-tight">
                    {p.title ?? p.name}
                  </h3>
                  {p.description && (
                    <p className="mt-1.5 line-clamp-2 text-xs text-muted-foreground leading-relaxed">
                      {p.description}
                    </p>
                  )}
                </div>

                {/* Meta */}
                <div className="border-t border-border/50 px-5 py-3">
                  <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                    {p.location && (
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {p.location}
                      </span>
                    )}
                    {p.budget && (
                      <span className="flex items-center gap-1">
                        <DollarSign className="h-3 w-3" />
                        {Number(p.budget).toLocaleString()}
                      </span>
                    )}
                    {p.created_at && (
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {format(new Date(p.created_at), "MMM d, yyyy")}
                      </span>
                    )}
                    {p.members_count != null && (
                      <span className="flex items-center gap-1">
                        <Users2 className="h-3 w-3" />
                        {p.members_count}
                      </span>
                    )}
                  </div>
                  <div className="mt-2.5 flex items-center text-xs font-medium text-primary transition-colors group-hover:text-primary/80">
                    View project
                    <ChevronRight className="ml-0.5 h-3 w-3 transition-transform group-hover:translate-x-0.5" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Create project dialog */}
      <Dialog open={createOpen} onOpenChange={(o) => { setCreateOpen(o); if (!o) resetForm(); }}>
        <DialogContent className="sm:max-w-[520px]">
          <DialogHeader>
            <DialogTitle className="text-lg">Create new project</DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-1">
            <div className="space-y-1.5">
              <Label className="text-sm font-medium">
                Project title <span className="text-destructive">*</span>
              </Label>
              <Input
                placeholder="Kitchen renovation"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="h-10"
              />
            </div>

            <div className="space-y-1.5">
              <Label className="text-sm font-medium">Category</Label>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger className="h-10">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map((c) => (
                    <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <Label className="text-sm font-medium">
                Location <span className="text-destructive">*</span>
              </Label>
              <div className="relative">
                <MapPin className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  className="h-10 pl-9"
                  placeholder="123 Main St, Nairobi"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <Label className="text-sm font-medium">Budget (optional)</Label>
              <div className="relative">
                <DollarSign className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  className="h-10 pl-9"
                  placeholder="50,000"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-sm font-medium">Start date</Label>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="h-10"
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-sm font-medium">End date</Label>
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="h-10"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <Label className="text-sm font-medium">Description (optional)</Label>
              <Textarea
                placeholder="Describe the scope of work, materials needed, or any special requirements…"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className="resize-none"
              />
            </div>
          </div>

          <DialogFooter className="gap-2">
            <Button
              variant="ghost"
              onClick={() => { setCreateOpen(false); resetForm(); }}
            >
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={creating} className="gap-2 shadow-sm">
              {creating && <Loader2 className="h-4 w-4 animate-spin" />}
              Create project
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
